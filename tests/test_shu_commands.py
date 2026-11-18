"""CPU only. Command bounds, durations and success predicates here are synthetic test inputs."""

from math import pi

import pytest
import torch

from wheelleg.shu_commands import ShuCommands
from wheelleg.shu_curriculum import BRAKE_REVERSE, COMBINED, STAND, STRAIGHT, TURN, FlatCommandCurriculum


def settings(kind=STRAIGHT, **overrides):
    cfg = dict(
        segment_probabilities=[float(i == kind) for i in range(6)],
        segment_duration_s=(0.03, 0.03),
        height_duration_s=(0.02, 0.02),
        vx_range_m_s=(-4, 4),
        wz_range_rad_s=(-5, 5),
        dash_range_m_s=(-4.5, 4.5),
        height_range_m=(0.16, 0.36),
        combined_wz_limit_rad_s=2.0,
        linear_slew_m_s2=2.0,
        angular_slew_rad_s2=10.0,
        height_slew_m_s=0.3,
        heading_kp=2.0,
        heading_max_wz=3.0,
    )
    return dict(cfg, **overrides)


def ordinary(c, yaw=None):
    z = torch.zeros_like(c.kind, dtype=torch.bool)
    c.prepare(c.value[:, 0] * 0 if yaw is None else yaw, ~z, z, z, c.steps)


def observed(c):
    return torch.stack((c.value[:, 0], c.value[:, 2], c.height[:, 0]), -1)


def test_exact_100hz_segments_and_actual_issued_errors_not_endpoint_or_raw_target():
    c = ShuCommands(settings(vx_range_m_s=(1.5, 1.5)), 1, "cpu", flat=FlatCommandCurriculum(0.4, 5, "cpu"))
    c.reset(torch.tensor([0]))
    z = torch.tensor([False])
    received = []

    def criterion(kind, mae, mag):
        received.append((kind.clone(), mae.clone(), mag.clone()))
        return (mae[:, 0] < 0.1) & (mae[:, 2] < 0.01)

    for tick in range(3):
        ordinary(c)
        assert c.value[0, 0].item() == pytest.approx((tick + 1) * 0.02)
        actual = observed(c)
        actual[0, 0] += 0.18 if tick == 0 else 0.03
        c.finish(actual, z, z, criterion)
        assert len(received) == int(tick == 2)
    kind, mae, mag = received[0]
    assert kind.item() == STRAIGHT and mae[0].tolist() == pytest.approx([0.08, 0, 0])
    assert mag[0, 0].item() == pytest.approx(0.04) and c.flat.successes[STRAIGHT] == 1
    ordinary(c)
    assert c.steps.item() == 0 and c.remaining.item() == 3


def test_falls_win_on_last_tick_and_early_interrupt_not_a_success():
    n = 5
    flat = FlatCommandCurriculum(0.5, 10, "cpu")
    c = ShuCommands(settings(), n, "cpu", flat=flat)
    ids = torch.arange(n)
    c.reset(ids)
    seen = []

    def criterion(k, mae, mag):
        seen.extend(k.tolist())
        return torch.ones_like(k, dtype=torch.bool)

    for tick in range(3):
        ordinary(c)
        fell = ((ids == 0) & (tick == 0)) | ((ids == 1) & (tick == 2))
        cut = ((ids == 2) & (tick == 1)) | ((ids == 3) & (tick == 2))
        c.finish(observed(c), fell, cut, criterion)
        if tick < 2:
            c.reset(ids[fell | cut])
    # id0/id2 started new segments and haven't finished. id1 final-tick fall is not a success.
    assert flat.completed[STRAIGHT] == 2 and flat.successes[STRAIGHT] == 2 and flat.attempts[STRAIGHT] == 4
    assert flat.falls[STRAIGHT] == 2 and flat.interruptions[STRAIGHT] == 1 and seen == [STRAIGHT, STRAIGHT]


def test_exact_wrap_straight_handoff_at_real_yaw_and_no_heading_pure_turn():
    c = ShuCommands.for_mixed(settings(segment_duration_s=(1.0, 1.0)), 2, "cpu")
    ids = torch.arange(2)
    c.reset(ids)
    c.kind[1] = TURN
    c.target[1, 2] = 1.0
    y = torch.tensor([0.1, -0.2])
    air = torch.tensor([True, True])
    z = ~air
    c.prepare(y, z, z, air, ids * 0)
    assert not c.heading_active.any()
    y2 = torch.tensor([pi - 0.04, 0.6])
    c.handoff(air, y2)
    assert c.reference_yaw.tolist() == pytest.approx([pi - 0.04, 0.0]) and c.heading_active.tolist() == [True, False]
    assert c.value[0, 2] == 0 and c.value[1, 2].item() == pytest.approx(1.0)
    c.finish(observed(c), z, z)
    c.prepare(torch.tensor([-pi + 0.04, 1.1]), air, z, air, ids * 0 + 1)
    assert c.value[0, 2].item() == pytest.approx(-0.16, abs=2e-6)
    assert c.reference_yaw[1] == 0 and c.value[1, 2].item() == pytest.approx(1.0)


def test_air_limit_by_birth_age_not_contact_or_drive_no_freeze_other_groups():
    c = ShuCommands.for_mixed(
        settings(
            COMBINED,
            segment_duration_s=(4, 4),
            combined_wz_limit_rad_s=5.0,
            linear_slew_m_s2=1000,
            angular_slew_rad_s2=1000,
        ),
        4,
        "cpu",
    )
    ids = torch.arange(4)
    c.reset(ids)
    c.target[:] = torch.tensor([4.0, 0.0, -4.0])
    air = ids < 2
    rise = ids == 2
    c.prepare(ids.float(), ~rise, rise, air, torch.tensor([299, 300, 0, 123]))
    assert c.value[:, 0].tolist() == pytest.approx([2.5, 4, 0, 4])
    assert c.value[:, 2].tolist() == pytest.approx([-pi / 2, -4, 0, -4])
    c.finish(observed(c), ids < 0, ids < 0)
    c.target[0, 0] = -0.23
    c.prepare(ids.float(), ids == 3, rise, air, ids * 0 + 1)
    assert c.value[0, 0].item() == pytest.approx(-0.23)


def test_preset_holds_height_and_zero_motion_through_handoff_no_partial_flat_score():
    c = ShuCommands(settings(height_duration_s=(0.01, 0.01)), 2, "cpu", flat=FlatCommandCurriculum(1.0, 100, "cpu"))
    ids = torch.arange(2)
    rise = ids == 0
    z = ids < 0
    c.reset(ids)
    initial = c.height[0, 0].item()
    torch.manual_seed(17)
    for tick in range(8):  # many height boundaries and two motion changes in ordinary env 1
        c.prepare(ids.float(), ~rise, rise, z, ids * 0 + tick)
        assert c.height[0, 0] == initial and c.height_target[0, 0] == initial and c.height_rate[0] == 0
        assert c.value[0].eq(0).all() and c.zero_translation[0]
        if tick == 7:
            c.handoff(rise, torch.tensor([1.4, 2.0]))
            assert c.reference_yaw[0].item() == pytest.approx(1.4)
        c.finish(observed(c), z, z, lambda k, e, m: e.sum(-1) == 0)
    assert c.height_remaining[0] == 1 and c.height[0, 0] == initial
    for tick in range(2):
        ordinary(c)
        c.finish(observed(c), z, z, lambda k, e, m: e.sum(-1) == 0)
    assert c.flat.completed[STRAIGHT] == 3  # no credit for recovery/handoff fragment
    assert c.height[0, 0].item() != initial


def test_tiny_nonzero_semantics_and_brake_reverse_depend_on_previous_effective_vx():
    torch.manual_seed(22)
    c = ShuCommands.for_mixed(settings(BRAKE_REVERSE, segment_duration_s=(0.01, 0.01)), 100, "cpu")
    ids = torch.arange(100)
    c.reset(ids)
    ordinary(c)
    assert (c.kind == STRAIGHT).all() and not c.zero_translation.any()
    z = ids < 0
    c.finish(observed(c), z, z)
    c.value[:, 0] = 0.00003
    ordinary(c)
    assert (c.kind == BRAKE_REVERSE).all()
    assert (
        (c.target[:, 0] == 0).any()
        and (c.target[:, 0] == -0.00003).any()
        and torch.equal(c.zero_translation, c.target[:, 0] == 0)
    )
    assert torch.equal(c.heading_active, ~c.zero_translation)


def test_per_bucket_ranges_stand_height_expands_landing_gate_mixed_factory_and_reserved_vy():
    n = 2000
    torch.manual_seed(9)
    p = settings(STAND)
    flat = FlatCommandCurriculum([0.2, 1, 1, 1, 1, 1], 10, "cpu")
    c = ShuCommands(p, n, "cpu", flat=flat)
    c.reset(torch.arange(n))
    assert c.height.min() >= 0.239999 and c.height.max() <= 0.280001 and c.target.eq(0).all()
    meta = c.transfer_metadata()
    assert not meta["all_full"]
    for bad in (meta, dict(meta, all_full=True), {}, dict(meta, fractions=[1.0] * 6, all_full=1)):
        with pytest.raises(ValueError, match="landing"):
            ShuCommands(p, n, "cpu", landing_metadata=bad)
    flat.fraction.fill_(1.0)
    meta = c.transfer_metadata()
    with pytest.raises(ValueError, match="same final"):
        ShuCommands(dict(p, height_range_m=[0.16, 0.35]), n, "cpu", landing_metadata=meta)
    for driver in [ShuCommands(p, n, "cpu", landing_metadata=meta), ShuCommands.for_mixed(p, n, "cpu")]:
        ids = torch.arange(n)
        driver.reset(ids)
        assert driver.flat is None and (driver.fraction == 1).all()
        assert driver.height.min() < 0.17 and driver.height.max() > 0.35
        assert not driver.value[:, 1].any()  # vy_cmd reserved
        with pytest.raises(ValueError):
            driver.transfer_metadata()


def test_brake_only_profile_completes_real_transition_from_rest_for_curriculum():
    torch.manual_seed(993)
    n = 124
    flat = FlatCommandCurriculum(0.4, 1000, "cpu")
    c = ShuCommands(settings(BRAKE_REVERSE, segment_duration_s=(0.02, 0.02)), n, "cpu", flat=flat)
    ids = torch.arange(n)
    c.reset(ids)
    z = ids < 0
    for _ in range(2):
        ordinary(c)
        c.finish(observed(c), z, z, lambda k, e, m: e.sum(-1) == 0)
    incoming = c.value[:, 0].clone()
    assert incoming.ne(0).all() and flat.completed[BRAKE_REVERSE] == 0
    ordinary(c)
    assert (c.kind == BRAKE_REVERSE).all() and c.zero_translation.any() and (~c.zero_translation).any()
    torch.testing.assert_close(c.target[~c.zero_translation, 0], -incoming[~c.zero_translation])
    c.finish(observed(c), z, z, lambda k, e, m: e.sum(-1) == 0)
    ordinary(c)
    c.finish(observed(c), z, z, lambda k, e, m: e.sum(-1) == 0)
    assert flat.completed[BRAKE_REVERSE] == n and flat.successes[BRAKE_REVERSE] == n


def test_true_air_reset_starts_at_capped_target_but_a_later_air_segment_still_slews():
    c = ShuCommands.for_mixed(settings(COMBINED, segment_duration_s=(0.01, 0.01)), 2, "cpu")
    ids = torch.arange(2)
    air = ids == 0
    z = ids < 0
    c.reset(ids)
    c.target[:] = torch.tensor([3.0, 0.0, -4.0])
    c.prepare(ids.float(), ~air, z, air, ids * 0)
    torch.testing.assert_close(c.value[0], torch.tensor([2.5, 0, -pi / 2]))
    torch.testing.assert_close(c.value[1], torch.tensor([0.02, 0.0, -0.1]))
    c.finish(observed(c), z, z)
    c.prepare(ids.float(), ~air, z, air, ids * 0 + 1)
    assert 2.48 - 1e-6 <= c.value[0, 0] <= 2.5 and -pi / 2 - 1e-6 <= c.value[0, 2] <= -pi / 2 + 0.1 + 1e-6
    c.reset(ids[:1])
    c.target[0] = torch.tensor([-1.4, 0.0, 0.43])
    c.prepare(ids.float(), ~air, z, air, ids * 0)
    torch.testing.assert_close(c.value[0], torch.tensor([-1.4, 0.0, 0.43]))


def test_bad_sample_cannot_win_on_exact_segment_boundary_even_if_criterion_accepts():
    c = ShuCommands(settings(segment_duration_s=(0.01, 0.01)), 3, "cpu", flat=FlatCommandCurriculum(0.4, 100, "cpu"))
    ids = torch.arange(3)
    c.reset(ids)
    ordinary(c)
    observed_state = observed(c)
    observed_state[1, 2] = float("nan")
    c.finish(observed_state, ids < 0, ids >= 0, lambda k, e, m: k >= 0, invalid=ids == 0)
    assert c.flat.interruptions[STRAIGHT] == 2 and c.flat.attempts[STRAIGHT] == 1 and c.flat.successes[STRAIGHT] == 1


def test_mixed_route_label_uses_own_speed_and_world_heading_without_changing_free_turns():
    c = ShuCommands.for_mixed(
        settings(TURN, wz_range_rad_s=(1.0, 1.0)),
        2,
        "cpu",
        route=dict(vx_range_m_s=(0.5, 0.5), heading_kp=2.0, heading_max_wz_rad_s=0.3),
    )
    ids = torch.arange(2)
    open_route = torch.tensor([False, True])
    no = torch.zeros(2, dtype=torch.bool)
    c.reset(ids, route=open_route)
    assert c.kind.tolist() == [TURN, STRAIGHT]
    torch.testing.assert_close(c.target, torch.tensor([[0.0, 0.0, 1.0], [0.5, 0.0, 0.0]]))
    yaw = torch.full((2,), 0.4)
    for _ in range(30):
        c.prepare(yaw, ~no, no, no, c.steps, route_open=open_route)
        c.finish(observed(c), no, no)
    torch.testing.assert_close(c.value, torch.tensor([[0.0, 0.0, 1.0], [0.5, 0.0, -0.3]]))
    assert c.heading_active.tolist() == [False, True]
    assert c.reference_yaw[1] == 0 and c.vx_active.tolist() == [False, True]
    c.prepare(yaw, ~no, no, no, c.steps, route_open=no)
    assert not c.value[1].any() and not c.vx_active[1]
    assert c.value[0, 2] == 1.0
    c.reset(ids[1:], route=no[1:])
    assert not c.route.any() and c.kind.tolist() == [TURN, TURN]


def test_prepare_reset_rows_isolates_survivors_keeps_route_gate_and_matches_first_full_prepare():
    from copy import deepcopy

    torch.manual_seed(19)
    n = 7
    ids = torch.arange(n)
    born = torch.tensor([5, 1, 3, 2, 6])  # nonconsecutive, non-sorted global IDs
    keep = torch.tensor([0, 4])
    z = ids < 0
    route = (ids == 1) | (ids == 4) | (ids == 6)
    c = ShuCommands.for_mixed(
        settings(vx_range_m_s=(3.8, 3.8), segment_duration_s=(0.05, 0.05)),
        n,
        "cpu",
        route=dict(vx_range_m_s=(0.5, 0.5), heading_kp=2.0, heading_max_wz_rad_s=0.3),
    )
    c.reset(ids, route=route)
    c.prepare(ids.float(), ~z, z, z, ids * 0, route_open=route)
    c.finish(observed(c), z, z)
    # This observation tick has already advanced both slew axes for survivors.
    c.height_target[keep] = c.height[keep] + 0.01
    c.prepare(ids.float(), ~z, z, z, ids * 0 + 1, route_open=route)
    before_h = c.height[keep].clone()
    assert (c.height_rate[keep] > 0).all()
    c.reset(born, route=route[born])
    air, rise = ids == 3, ids == 2
    new_gate = ids == 6  # request a changed gate for survivor 4 too; subset path must ignore it
    yaw = ids.float() / 10
    args = (yaw, ~(air | rise), rise, air, ids * 0)
    oracle = deepcopy(c)
    oracle.prepare(*args, route_open=new_gate)
    # No resampling/promotion or extra interval clock on either a subset issue or a repeated read.
    rng = torch.get_rng_state().clone()
    remaining = c.remaining.clone()

    def rows(sel):
        return {k: v[sel].clone() for k, v in vars(c).items() if torch.is_tensor(v) and v.ndim and v.size(0) == n}

    survivors = rows(keep)
    c.prepare_reset_rows(born, *args, route_open=new_gate)
    for name, old in survivors.items():
        assert torch.equal(getattr(c, name)[keep], old), name
    assert torch.equal(c.height[keep], before_h)
    for name in rows(born):
        assert torch.equal(getattr(c, name)[born], getattr(oracle, name)[born]), name
    assert c.value[3, 0] == 2.5 and c.value[2].eq(0).all() and c.value[1].eq(0).all()
    assert c.value[5, 0].item() == pytest.approx(0.02) and c.reference_yaw[5] == yaw[5]
    assert c.value[6, 0] > 0 and c.reference_yaw[6] == 0 and c._route_open[4]
    first = rows(ids)
    c.prepare_reset_rows(born, *args, route_open=z)
    c.prepare_reset_rows(born[:0], *args)
    for name, old in first.items():
        assert torch.equal(getattr(c, name), old), name
    assert torch.equal(c.remaining, remaining) and torch.equal(torch.get_rng_state(), rng)
