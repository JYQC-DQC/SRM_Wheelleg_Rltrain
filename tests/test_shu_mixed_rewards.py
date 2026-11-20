"""Terrain-specific P1 reward math and adapter coverage without Isaac physics."""

from math import exp, expm1, pi, radians, sin
from types import SimpleNamespace

import test_shu_route_spawn as route_spawn
import torch
from test_shu_rewards import _DT, assert_rates, inputs

from wheelleg.shu_map import ShuFreeMap
from wheelleg.shu_rewards import DRIVE, shu_reward_terms

runtime = route_spawn.runtime


def test_mixed_terrain_only_changes_selected_reward_terms():
    s, p = inputs(4)
    # Flat, ordinary nonflat, pyramid, and a hard cross-step on a pyramid.
    nonflat = torch.tensor([False, True, True, True])
    pyramid = torch.tensor([False, False, True, True])
    phase = torch.full((4,), DRIVE)
    s["height_error"].fill_(0.05)
    s["height_target_rate"].fill_(0.2)
    s["velocity_w"][:, 0] = s["vx_cmd"][:] = 0.8
    s["velocity_w"][:, 2] = 0.7
    s["velocity"] = s["velocity_w"].clone()
    s["velocity"][:, 2] = s["height_error"].new_tensor([-2, -2, -2, -4])
    s["angular_velocity"][:, 0] = 0.5
    s["angular_velocity"][:3, 1] = 1.0
    s["angular_velocity"][3, 1] = 5.0
    s["angular_velocity"][:, 2] = s["wz_cmd"][:] = 0.25
    s["vx_active"].fill_(True)
    s["wz_active"].fill_(True)
    s["gravity"][:, 0] = 0.08
    s["gravity"][3, 0] = sin(radians(25))
    s["gravity"][:, 1] = 0.03
    s["wheel_x_b"][:, 0] = 0.08
    s["fork_threshold_enabled"].fill_(True)
    s["leg_or_guide_contact"].fill_(True)
    s["other_undesired_contact"].fill_(True)
    s["action"].fill_(0.5)

    terms = shu_reward_terms(s, phase, p, _DT, terrain_masks=(nonflat, pyramid))
    gate_mid = (exp(-0.5) - exp(-2)) / (1 - exp(-2))
    assert_rates(
        terms,
        track_lin_vel=[gate_mid, gate_mid, 1, 1],
        track_ang_vel=[gate_mid, gate_mid, 1, 1],
        track_height=[exp(-2.5)] * 4,
        vertical_velocity=[-0.25, -0.4, -0.4, -1],
        angular_xy=[-0.25, -0.0625, -0.0625, -1],
        orientation=[-0.73, -0.146, -0.146, -1],
        no_fork=[-1, -1, 0, 0],
        no_fork_square=[-0.16] * 4,
        undesired_contact=[-2] * 4,
        action_rate=[-0.015] * 4,
    )
    legacy = shu_reward_terms(s, phase, p, _DT)
    changed = {"track_lin_vel", "track_ang_vel", "vertical_velocity", "angular_xy", "orientation", "no_fork"}
    for name, value in terms.items():
        torch.testing.assert_close(value[0], legacy[name][0])
        if name not in changed:
            torch.testing.assert_close(value, legacy[name])


def test_mixed_signed_horizontal_speed_and_zero_yaw_vs_free_heading():
    s, p = inputs(4)
    s["yaw"].fill_(pi / 2)  # The longitudinal axis is world +Y, not +X or the tilted body X.
    s["velocity_w"][:] = s["velocity_w"].new_tensor([[0.5, -1, 0.4], [0.5, 1, 0.4], [0.4, 0.3, 0], [0, 1, 0]])
    s["velocity"] = s["velocity_w"].clone()
    s["vx_cmd"][:] = s["vx_cmd"].new_tensor([-1, -1, 0, 1])
    s["vx_active"] = s["vx_cmd"] != 0
    s["angular_velocity"][:, 2] = s["yaw"].new_tensor([0.4, 0.4, 0.0, 0.25])
    s["heading_active"][-1] = True
    s["heading_wz_cmd"] = s["yaw"].new_tensor([0, 0, 0, 0.25])
    s["height_error"][:3] = 0.1
    pyramid = torch.tensor([True, True, True, False])
    terms = shu_reward_terms(s, torch.full((4,), DRIVE), p, _DT, terrain_masks=(pyramid, pyramid))
    assert_rates(
        terms,
        track_lin_vel=[1, exp(-56.25), 0, 1],
        lin_vel_error=[0, expm1(-4 / 2.5), 0, 0],
        track_ang_vel=[0, 0, 0, 0],
        ang_vel_error=[expm1(-0.16), expm1(-0.16), 0, 0],
        stand_still=[0, 0, -0.7, 0],
    )


def test_adapter_uses_current_surface_and_mixed_height_kernel_stays_annealed(runtime):
    e = route_spawn.stairs_runtime(runtime)
    generator = SimpleNamespace(
        size=(12.0, 12.0),
        num_rows=1,
        num_cols=3,
        border_width=5.0,
        sub_terrains=dict.fromkeys(("flat", "rough", "pyramid_up_lip")),
    )
    e.shu.free_map = ShuFreeMap(generator, {}, e.device)
    e.cfg.evaluation = True  # all flat replay births are ordinary in this driving-only comparison
    e._reset_idx(torch.arange(e.num_envs))
    e.shu.observe_commands(e._measure()["yaw"])
    free = ~e.mixed_curriculum.traverse
    assert free.any() and (~free).any()
    torch.testing.assert_close(e.commands.fraction, torch.ones_like(e.commands.fraction))

    # Keep the same birth cohorts but give the free drivers a pyramid and the routes flat ground.
    # All measurements come from the adapter's existing state inputs.
    e.robot.data.root_pos_w[:, 0] = 0
    e.robot.data.root_pos_w[free, 1] = 12
    e.robot.data.root_pos_w[~free, 1] = -12
    e.robot.data.root_lin_vel_w[:, 2] = 0.7
    e.robot.data.root_lin_vel_b[:, 2] = -2.0
    e.commands.height_rate.fill_(0.2)
    s = e._measure()
    s["height_error"].fill_(0.05)
    s["ground"].fill_(0.3)
    terms = e.shu.rewards(s)
    torch.testing.assert_close(
        terms["vertical_velocity"], torch.where(free & ~e.shu.flat_replay, -0.4, -0.25) * e.step_dt
    )
    torch.testing.assert_close(terms["track_height"], torch.full_like(s["height_error"], exp(-2.5) * e.step_dt))

    # Leave the tile for the flat border without resetting or changing the issued commands.
    e.robot.data.root_pos_w[:, 0] = 7
    on_border = e.shu.rewards(s)
    torch.testing.assert_close(on_border["vertical_velocity"], torch.full_like(s["height_error"], -0.25 * e.step_dt))
    s["height_error"].zero_()
    s["ground"].zero_()
    torch.testing.assert_close(e.extras["p1_mixed"]["height_error_m"], torch.full_like(s["height_error"], 0.05))
    torch.testing.assert_close(e.extras["p1_mixed"]["ground_z_w_m"], torch.full_like(s["ground"], 0.3))
