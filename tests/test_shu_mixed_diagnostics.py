from math import pi

import pytest
import torch

from wheelleg.shu_mixed_diagnostics import FORWARD_DOWN, FORWARD_UP, FREE, REVERSE_DOWN, ShuMixedDiagnostics


def make_diagnostics(n, **window):
    return ShuMixedDiagnostics(
        n,
        "cpu",
        wheels=[2, 0],
        guides=[1],
        body_count=4,
        physics_dt=0.002,
        step_dt=0.01,
        contact_force_n=10.0,
        **window,
    )


def test_timeout_fractions_weight_all_ended_episodes_and_atlas_episodes():
    log = make_diagnostics(5)
    t = torch.tensor
    flags = dict(
        terminated=t([False, False, False, True, False]),
        timeout=t([True, True, True, False, False]),
        physical_failure=t([False, False, False, True, False]),
        numerical_failure=t([False] * 5),
        boundary_timeout=t([True, False, False, False, False]),
        normal_time_limit=t([False, True, True, False, False]),
        atlas=t([True, True, False, True, True]),
    )
    log.record_ended(t([0]), **flags)
    log.record_ended(t([1, 2, 3, 4]), **flags)
    stats = log.take()
    assert stats["Mixed/all/ended_episode_count"] == 4
    assert stats["Mixed/atlas/ended_episode_count"] == 3
    assert stats["Mixed/all/boundary_timeout_fraction"] == 1 / 4
    assert stats["Mixed/all/normal_time_limit_fraction"] == 2 / 4
    assert stats["Mixed/atlas/boundary_timeout_fraction"] == 1 / 3
    assert stats["Mixed/atlas/normal_time_limit_fraction"] == 1 / 3
    assert log.take() == {}


def births(diag, ids, route, yaw, *, lip=None, oblique=None, tick=0):
    diag.reset(
        torch.tensor(ids),
        route=torch.tensor(route),
        with_lip=torch.tensor(lip or [False] * len(ids)),
        oblique=torch.tensor(oblique or [False] * len(ids)),
        spawn_yaw_rad=torch.tensor(yaw, dtype=torch.float32),
        tick=tick,
    )


def step(diag, deltas, vx, *, complete=None, invalid=None):
    diag.step_route(
        torch.tensor(deltas, dtype=torch.float32),
        torch.tensor(vx, dtype=torch.float32),
        completed=torch.tensor(complete or [False] * len(vx)),
        invalid_motion=torch.tensor(invalid or [False] * len(vx)),
    )


def end_flags(*outcomes):
    return {
        "terminated": torch.tensor([x in ("fall", "numeric", "other") for x in outcomes]),
        "timeout": torch.tensor([x == "timeout" for x in outcomes]),
        "physical_failure": torch.tensor([x == "fall" for x in outcomes]),
        "numerical_failure": torch.tensor([x == "numeric" for x in outcomes]),
    }


def test_stall_projects_onto_signed_oblique_spawn_heading_and_requires_one_second():
    diag = make_diagnostics(6)
    births(
        diag,
        list(range(6)),
        [FORWARD_UP, REVERSE_DOWN, FORWARD_DOWN, FORWARD_UP, FREE, FORWARD_DOWN],
        [pi / 2, -pi / 2, pi / 2, pi / 2, 0, 0],
        oblique=[True] * 4 + [False, False],
    )
    # First two both advance +Y despite opposite chassis yaw and commands. The next
    # moves sideways, the fourth moves backwards, and the last is exactly at 5 cm.
    deltas = [[0, 0.001], [0, 0.001], [0.01, 0], [0, -0.001], [0, 0], [0.0005, 0]]
    vx = [1, -1, 1, 1, 1, 1]
    for _ in range(99):
        step(diag, deltas, vx)
    assert not diag.stuck_now.any()
    step(diag, deltas, vx)
    assert diag.stuck_now.tolist() == [False, False, True, True, False, False]
    assert diag.ever_stuck.tolist() == diag.stuck_now.tolist()


def test_stall_is_rolling_and_interrupted_by_zero_command_invalid_motion_or_reset():
    diag = make_diagnostics(3, window_s=0.025, distance_m=0.07)  # three 10 ms policy steps
    births(diag, [0, 1, 2], [FORWARD_UP] * 3, [0] * 3)
    still = [[0, 0]] * 3
    step(diag, [[0.08, 0]] * 3, [1] * 3)
    step(diag, still, [1] * 3)
    step(diag, still, [1] * 3)
    assert not diag.stuck_now.any()
    step(diag, still, [1, 0, 1], invalid=[False, False, True])
    assert diag.stuck_now.tolist() == [True, False, False]
    births(diag, [0], [FORWARD_DOWN], [0], tick=20)
    for _ in range(2):
        step(diag, still, [1] * 3)
    assert not diag.stuck_now.any()
    assert not diag.ever_stuck.any()
    step(diag, still, [1] * 3)
    assert diag.stuck_now.all()
    step(diag, [[0.08, 0]] * 3, [1] * 3, complete=[True, False, False])
    assert not diag.stuck_now.any()
    assert diag.ever_stuck.all()
    assert diag.completed.tolist() == [True, False, False]


def test_500hz_world_fz_is_per_wheel_and_guide_proxy_uses_net_force_magnitude():
    diag = make_diagnostics(2)
    births(diag, [0, 1], [REVERSE_DOWN, FREE], [pi, 0], lip=[True, False], oblique=[True, False], tick=5)
    a = torch.tensor([[[300.0, 0, -40], [12, 0, 0], [200, 0, 50], [0, 0, 8]]] * 2)
    b = torch.tensor([[[0.0, 0, 70], [0, 0, 0], [0, 0, 10], [0, 0, 25]]] * 2)
    diag.sample_contacts(5, a * 100)  # stale birth sample
    diag.sample_contacts(6, a)
    diag.sample_contacts(6, a * 100)  # shared action/done hook at the same tick
    diag.sample_contacts(7, b)
    diag.sample_contacts(8, b * torch.nan)
    step(diag, [[0, 0]] * 2, [-1, 1], complete=[True, True])
    diag.sample_contacts(9, b * 100)  # after first completed crossing
    torch.testing.assert_close(diag.wheel_fz_peak_n, torch.tensor([[50.0, 70], [0, 0]]))
    torch.testing.assert_close(diag.wheel_fz_impulse_ns, torch.tensor([[0.12, 0.14], [0, 0]]))
    stats = diag.summarize(torch.arange(2), **end_flags("timeout", "timeout"))
    group = (REVERSE_DOWN, 1, 1)
    assert stats["episode_count"].sum().item() == 1
    assert stats["completed_count"][group] == stats["timeout_count"][group] == 1
    assert stats["bad_force_sample_count"][group] == 1
    assert stats["guide_contact_episode_count"][group] == stats["non_main_contact_episode_count"][group] == 1
    assert stats["non_main_peak_max_n"][group] == 25
    assert stats["guide_peak_max_n"][group] == 12
    assert stats["non_main_contact_s_sum"][group].item() == pytest.approx(0.004)
    assert stats["guide_contact_s_sum"][group].item() == pytest.approx(0.002)


def test_summary_separates_termination_causes_and_keeps_birth_strata():
    diag = make_diagnostics(7, window_s=0.01)
    births(
        diag,
        list(range(7)),
        [FORWARD_UP, FORWARD_UP, FORWARD_DOWN, REVERSE_DOWN, REVERSE_DOWN, FREE, FORWARD_DOWN],
        [0, 0.1, 0, pi, pi, 0, 0],
        lip=[False, True, False, False, True, False, False],
        oblique=[False, True, False, False, False, False, False],
    )
    step(diag, [[0, 0]] * 7, [1, 1, 1, -1, -1, 1, 1], complete=[True, False, False, False, False, True, False])
    stats = diag.summarize(torch.arange(7), **end_flags("fall", "fall", "timeout", "numeric", "other", "fall", None))
    assert stats["episode_count"].shape == (3, 2, 2)
    assert stats["episode_count"].sum() == 5
    assert stats["completed_count"][FORWARD_UP, 0, 0] == stats["fall_count"][FORWARD_UP, 0, 0] == 1
    assert stats["incomplete_count"][FORWARD_UP, 0, 0] == 0
    assert stats["fall_count"][FORWARD_UP, 1, 1] == stats["stuck_episode_count"][FORWARD_UP, 1, 1] == 1
    assert stats["timeout_count"][FORWARD_DOWN, 0, 0] == 1
    assert stats["numerical_failure_count"][REVERSE_DOWN, 0, 0] == 1
    assert stats["other_termination_count"][REVERSE_DOWN, 1, 0] == 1
    assert stats["fall_count"].sum() == 2


def test_rollout_drains_ended_groups_only_and_combines_counts_weighted_means_and_peaks():
    diag = make_diagnostics(2)
    assert diag.take() == {}
    with torch.inference_mode():
        births(diag, [0, 1], [FORWARD_UP, FORWARD_DOWN], [0, 0])
        sample = torch.zeros((2, 4, 3))
        # Forward-down stays alive through the first drain but already has a stall and a measured force.
        sample[1, 2, 2] = 25
        for tick in range(1, 101):
            sample[0, 2, 2] = 50 if tick == 100 else 0
            diag.sample_contacts(tick, sample)
            step(diag, [[0, 0]] * 2, [1, 1], complete=[tick == 100, False])
        diag.record_ended(torch.tensor([0]), **end_flags("timeout", None))
        births(diag, [0], [FORWARD_UP], [0], tick=100)
        sample[0, 2, 2] = 100
        diag.sample_contacts(101, sample)
        diag.record_ended(torch.tensor([0]), **end_flags("fall", None))
        births(diag, [0], [REVERSE_DOWN], [pi], lip=[True], tick=101)
        diag.record_ended(torch.tensor([0]), **end_flags("numeric", None))
    log = diag.take()  # runner can call outside inference_mode
    prefix = "Mixed/forward_up/plain/straight/"
    assert log[prefix + "episode_count"] == 2
    assert log[prefix + "completion_rate"] == log[prefix + "fall_rate"] == 0.5
    assert log[prefix + "left_fz_impulse_ns_mean"] == pytest.approx(0.15)
    assert log[prefix + "left_fz_peak_max_n"] == 100
    reverse = "Mixed/reverse_down/lip/straight/"
    assert log[reverse + "numerical_failure_count"] == 1
    assert reverse + "left_fz_peak_max_n" not in log
    assert not any(k.startswith("Mixed/forward_down/") for k in log)
    assert diag.take() == {}
    with torch.inference_mode():
        diag.record_ended(torch.tensor([1]), **end_flags(None, "timeout"))
    next_log = diag.take()
    down = "Mixed/forward_down/plain/straight/"
    assert next_log[down + "stuck_episode_count"] == 1
    assert next_log[down + "left_fz_impulse_ns_mean"] == pytest.approx(101 * 0.002 * 25)
    assert all(k.startswith(down) for k in next_log)
