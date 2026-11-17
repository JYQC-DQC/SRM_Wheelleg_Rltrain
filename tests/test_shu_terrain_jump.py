from types import SimpleNamespace

import pytest
import torch

from wheelleg.jump import JumpEvent, collision_bounds_w, tunnel_geometry
from wheelleg.shu_terrain import MIXED_PROFILES, MixedTerrainRuntime, route_active, route_progress_and_stuck


def mixed_settings():
    gates = {name: dict(row=1, window=2, success_fraction=1.0) for name in MIXED_PROFILES[4:8]}
    return dict(
        rows=3,
        route=dict(
            vx_range_m_s=(0.5, 1.0), heading_kp=2.0, heading_max_wz_rad_s=1.0, corridor_width_m=2.0, clearance_m=0.2
        ),
        tile_size_m=(8.0, 8.0),
        gates=gates,
        groups=dict(rough=0.1, grid=0.1, slope=0.1, stairs=0.4),
        stair_weights=dict.fromkeys(MIXED_PROFILES[4:], 1.0),
        profiles={
            name: dict(
                row_range=[0, 2],
                command_mode="free" if i < 4 else "traverse",
                exit_distance_m=2.0,
                geometry={"spawn_x_m": 1.0, "first_edge_x_m": 1.5, "step_width_m": 0.5},
            )
            for i, name in enumerate(MIXED_PROFILES)
        },
    )


def test_mix_runtime_unlock_changes_real_sampling_and_restores_state():
    torch.manual_seed(1)
    count = 2000
    cfg = mixed_settings()
    mix = MixedTerrainRuntime(cfg, count, "cpu")
    columns = torch.arange(len(MIXED_PROFILES))
    origins = torch.zeros(3, len(columns), 3)
    origins[..., 0] = torch.arange(3).unsqueeze(-1) * 8
    origins[..., 1] = columns * 8
    terrain = SimpleNamespace(
        terrain_origins=origins,
        terrain_levels=torch.zeros(count, dtype=torch.long),
        terrain_types=torch.zeros(count, dtype=torch.long),
        env_origins=torch.zeros(count, 3),
    )
    ids = torch.arange(count)
    no = torch.zeros(count, dtype=torch.bool)
    mix.reset(terrain, ids, no, no, evaluation=False)
    assert (terrain.terrain_types < 8).all()
    assert (terrain.terrain_types == 0).float().mean().item() == pytest.approx(0.30, abs=0.04)
    before = mix.weights.clone()
    # Two successes on single-up. Double-up has one wrong row and one terminal failure.
    terrain.terrain_types[:6] = torch.tensor([4, 4, 5, 5, 5, 5])
    terrain.terrain_levels[:6] = torch.tensor([1, 1, 0, 1, 1, 1])
    terrain.env_origins[:6] = origins[terrain.terrain_levels[:6], terrain.terrain_types[:6]]
    mix.traverse[:6] = True
    position = terrain.env_origins + torch.tensor([3.0, 0.0, 0.0])
    ran, failed = ~no, no.clone()
    failed[3] = True
    mix.step(terrain, terrain.env_origins, position, torch.ones(count), failed)
    mix.reset(terrain, ids[:4], ran, failed, evaluation=False)
    assert mix.passed["single_up"] and not mix.unlocked["triple_up"]
    assert mix.counts["double_up"] == (1, 0)
    mix.reset(terrain, ids[4:5], ran, failed, evaluation=False)  # close the failed window
    assert mix.counts["double_up"] == (0, 0)
    terrain.terrain_types[4] = 5
    terrain.terrain_levels[4] = 1
    terrain.env_origins[4] = origins[1, 5]
    mix.traverse[4] = True
    mix.step(
        terrain, terrain.env_origins, terrain.env_origins + torch.tensor([3.0, 0.0, 0.0]), torch.ones(count), failed
    )
    mix.reset(terrain, ids[4:6], ran, failed, evaluation=False)
    assert mix.unlocked == {"triple_up": True, "triple_down": False}
    torch.testing.assert_close(mix.weights[[0, 1, 2, 3, 6, 7]], before[[0, 1, 2, 3, 6, 7]])
    assert mix.weights[4] + mix.weights[5] + mix.weights[8] == pytest.approx(float(before[4] + before[5]))
    restored = MixedTerrainRuntime(cfg, count, "cpu")
    restored.load_state_dict(mix.state_dict())
    restored.reset(terrain, ids, no, no, evaluation=False)
    assert (terrain.terrain_types == 8).any() and not (terrain.terrain_types == 9).any()
    assert torch.equal(terrain.env_origins, origins[terrain.terrain_levels, terrain.terrain_types])
    assert torch.equal(restored.traverse, terrain.terrain_types >= 4)
    assert route_active(torch.tensor([False, True, True]), torch.tensor([1.0, 0.0, 1.0])).tolist() == [
        False,
        False,
        True,
    ]


def test_route_crossing_cannot_pass_by_coming_back_from_another_lane():
    count = 7
    mix = MixedTerrainRuntime(mixed_settings(), count, "cpu")
    terrain = SimpleNamespace(
        terrain_types=torch.full((count,), 4, dtype=torch.long), env_origins=torch.zeros(count, 3)
    )
    mix.traverse[:6] = True
    start = torch.zeros(count, 3)
    halfway = start + torch.tensor([1.0, 0.0, 0.0])
    halfway[1, 1] = 0.81  # effective limit is 1.0 - 0.2 m
    no = torch.zeros(count, dtype=torch.bool)
    forward = torch.ones(count)
    mix.step(terrain, start, halfway, forward, no)
    assert mix.left_corridor.tolist() == [False, True, False, False, False, False, False]
    final = start + torch.tensor([2.1, 0.0, 0.0])
    final[4, 1] = 0.81
    forward[2] = 0.0
    forward[5] = -1.0
    failed_at_exit = no.clone()
    failed_at_exit[3] = True
    mix.step(terrain, halfway, final, forward, failed_at_exit)
    assert mix.crossed.tolist() == [True, False, False, False, False, False, False]
    assert mix.reward_active.tolist() == [True, False, False, False, False, False, False]
    # The crossing stays latched when braking/returning; no more progress or stuck while stopped.
    mix.step(terrain, final, start, torch.zeros(count), no)
    assert mix.crossed[0] and not mix.route_open[0] and not mix.reward_active.any()


@pytest.mark.parametrize("exit_distance", [1.2, 6.8])
def test_route_exit_must_be_past_last_riser_and_before_end_of_tile(exit_distance):
    s = mixed_settings()
    s["profiles"]["double_up"]["exit_distance_m"] = exit_distance
    with pytest.raises(ValueError, match="double_up.*route spawn and exit"):
        MixedTerrainRuntime(s, 1, "cpu")


def test_route_progress_and_stuck_are_axial_and_reset_when_inactive():
    x = torch.tensor([1.0, 0.4, 0.0, -0.1])
    prev = torch.zeros_like(x)
    active = torch.tensor([False, True, True, True])
    a = route_progress_and_stuck(
        active,
        x,
        prev,
        prev,
        torch.full_like(x, 0.5),
        torch.ones_like(active),
        dt=0.5,
        window_s=1.0,
        distance_m=0.3,
    )
    progress, start, elapsed, stuck = a
    torch.testing.assert_close(progress, torch.tensor([0.0, 0.4, 0.0, -0.1]))
    torch.testing.assert_close(start, x)
    assert not elapsed.any()
    assert stuck.tolist() == [False, False, True, True]
    b = route_progress_and_stuck(
        torch.zeros_like(active),
        x,
        x,
        start,
        elapsed,
        stuck,
        dt=0.5,
        window_s=1.0,
        distance_m=0.3,
    )
    assert not b[0].any() and not b[2].any() and not b[3].any()


def test_tunnel_rejects_early_first_touch_or_underpass_even_after_rolling_beyond():
    settings = dict(height_range_m=(0.2, 0.2), event_duration_s=1.0, landing_stable_s=0.2)
    event = JumpEvent(settings, 3, "cpu")
    yes, no = torch.ones(3, dtype=torch.bool), torch.zeros(3, dtype=torch.bool)
    z = torch.full((3,), 0.3)
    air = torch.zeros(3, 2, dtype=torch.bool)
    event.request(yes)
    event.trigger(z, before_beam=yes)

    def tick(contact, *, over=no, blocked=no, valid=yes):
        airborne = ~contact.any(-1)
        event.update(
            0.1,
            z,
            airborne.float(),
            contact,
            yes,
            valid,
            no,
            wheel_clearance=airborne.float() * 0.2,
            takeoff_clearance_m=0.02,
            above_beam=over,
            blocked_at_beam=blocked,
        )

    tick(~air)
    tick(air, over=torch.tensor([True, True, False]), blocked=torch.tensor([False, False, True]))
    tick(torch.tensor([[True, False], [True, False], [True, True]]), valid=torch.tensor([True, False, True]))
    tick(~air)
    tick(~air)
    assert event.landing_pulse.tolist() == [True, False, False]
    assert event.invalid.tolist() == [False, True, True]


def test_link_local_collision_offset_rotates_with_the_body():
    q = torch.tensor([[[2**-0.5, 0.0, 0.0, 2**-0.5]]])
    bounds = torch.tensor([[[0.0, -0.1, 0.0], [0.2, 0.1, 0.4]]])
    lo, hi = collision_bounds_w(torch.tensor([[[1.34, 0.0, 0.0]]]), q, bounds)
    torch.testing.assert_close(lo, torch.tensor([[[1.24, 0.0, 0.0]]]), atol=1e-6, rtol=0)
    torch.testing.assert_close(hi, torch.tensor([[[1.44, 0.2, 0.4]]]), atol=1e-6, rtol=0)
    settings = dict(beam_length_m=0.35, lane_width_m=0.8, clearance_margin_m=0.03, landing_margin_m=0.05)
    before, over, blocked, past = tunnel_geometry(
        (lo, hi), torch.tensor([[1.0, 0.0, 0.0]]), torch.tensor([0.27]), settings
    )
    assert not before.item() and not over.item() and blocked.item() and not past.item()
