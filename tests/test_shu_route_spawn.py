"""P1 stair births through the real reset/observation hooks with CPU articulation transport."""

from math import pi, radians
from types import SimpleNamespace as NS
from unittest.mock import Mock

import pytest
import test_shu_runtime as transport
import torch

from wheelleg.shu_terrain import FREE_PROFILES, MIXED_PROFILES, STAIR_PROFILES, mixed_columns

runtime = transport.runtime


def stairs_runtime(runtime, *, up=(0.27, 0.32), down=(0.19, 0.24), clearance_m=0.25):
    e = transport.make_runtime(runtime, "p1-flat")
    terrain = dict(
        route=dict(
            vx_range_m_s=(0.5, 2.5),
            up_height_range_m=up,
            down_height_range_m=down,
            straight_spawn_probability=0.5,
            max_spawn_yaw_offset_rad=radians(25),
            clearance_m=clearance_m,
        ),
        profiles={
            name: {"geometry": {"platform_width_m": 4.0}} if name in STAIR_PROFILES else {} for name in MIXED_PROFILES
        },
    )
    e.training.settings["commands"]["height_duration_s"] = (2.0, 6.0)
    e.training.task = "p1-stairs"
    e.training.stage["terrain"] = terrain
    columns = mixed_columns(terrain)
    generator = NS(size=(12.0, 12.0), num_rows=1, num_cols=len(columns), border_width=5.0, sub_terrains={"flat": NS()})
    e.cfg.terrain = NS(terrain_generator=generator)
    # Four free terrains and the three route cohorts, each with and without lips.
    cohorts = [(name, False, False) for name in FREE_PROFILES] + [
        (name, lip, reverse)
        for lip in (False, True)
        for name, reverse in (("pyramid_down", False), ("pyramid_up", False), ("pyramid_up", True))
    ]
    births = [cohorts[i % len(cohorts)] for i in range(e.num_envs)]
    traverse = torch.tensor([name in STAIR_PROFILES for name, _, _ in births])
    reverse = torch.tensor([backward for _, _, backward in births])
    e.terrain.terrain_types = torch.tensor(
        [columns.index((name, lip, name in STAIR_PROFILES)) for name, lip, _ in births]
    )
    e.terrain.env_origins[:, 1] = 15.5
    e.terrain.env_origins[:, 2] = torch.tensor(
        [{"pyramid_up": 1.5, "pyramid_down": -1.5}.get(name, 0.0) for name, _, _ in births]
    )
    e.mixed_curriculum = NS(traverse=traverse, reverse_descent=reverse, route_open=traverse, reset=Mock())
    e.stair_tracking_sum = torch.zeros(e.num_envs)
    e.reset_terminated = torch.zeros_like(traverse)
    e.reset_time_outs = torch.zeros_like(traverse)
    e.shu = runtime[1](e, None)
    e.commands = e.shu.commands
    return e


def test_real_root_spawn_center_xy_jitter_yaw_mixture_and_zero_velocity(runtime):
    torch.manual_seed(193)
    e = stairs_runtime(runtime)
    mix = e.mixed_curriculum
    ids = torch.arange(e.num_envs - 1, -1, -1)
    e.robot.data.default_root_state[:, 7:] = torch.arange(1.0, 7.0)
    e.robot.data.default_joint_vel.fill_(2.0)
    e.robot.data.default_root_state[:, 3:7] = torch.tensor([0.6, 0.0, 0.0, 0.8])
    default = e.robot.data.default_root_state
    default[:, :2] = torch.tensor([0.2, -0.35])
    origin = e.terrain.env_origins
    offsets = []
    xy = []
    for _ in range(256):
        e._reset_idx(ids)
        quat = e.robot.data.root_quat_w
        pos = e.robot.data.root_pos_w
        torch.testing.assert_close(pos[:, 2], origin[:, 2] + default[:, 2])
        torch.testing.assert_close(pos[~mix.traverse, :2], (origin + default[:, :3])[~mix.traverse, :2])
        torch.testing.assert_close(e.initial_position, pos)
        xy.append(pos[mix.traverse, :2] - origin[mix.traverse, :2])
        torch.testing.assert_close(quat[~mix.traverse], e.robot.data.default_root_state[~mix.traverse, 3:7])
        assert not quat[mix.traverse, 1:3].any()
        torch.testing.assert_close(quat.norm(dim=-1), torch.ones(e.num_envs))
        yaw = transport.euler(quat)[2]
        error = yaw - mix.reverse_descent * pi
        offsets.append(torch.atan2(error.sin(), error.cos()))
    assert not e.robot.root[:, 7:].any() and not e.robot.data.joint_vel.any()
    assert not e.robot.data.root_lin_vel_b.any() and not e.robot.data.root_ang_vel_b.any()

    samples = torch.stack(xy).flatten(0, 1)
    assert (samples.abs() <= 1).all()
    # The joint histogram exercises uniform marginals and independence across both axes.
    bins = ((samples + 1) * 2).long().clamp_max(3)
    frequencies = torch.bincount(4 * bins[:, 0] + bins[:, 1], minlength=16) / len(samples)
    assert ((0.045 < frequencies) & (frequencies < 0.08)).all()

    limit = radians(25)
    for cohort in (mix.traverse & ~mix.reverse_descent, mix.reverse_descent):
        errors = torch.stack(offsets)[:, cohort].flatten()
        straight = errors.abs() < 1e-6
        assert 0.45 < straight.float().mean() < 0.55
        angled = errors[~straight]
        assert (angled.abs() <= limit).all()
        # Both signs and both halves of each sign have comparable probability.
        quarters = torch.histc(angled, bins=4, min=-limit, max=limit) / len(angled)
        assert ((0.19 < quarters) & (quarters < 0.31)).all()


def test_pyramid_height_ranges_and_resampling_for_center_out_routes(runtime):
    up, down = (0.27, 0.32), (0.19, 0.24)  # deliberately disjoint
    e = stairs_runtime(runtime, up=up, down=down)
    mix, c = e.mixed_curriculum, e.commands
    ids = mix.traverse.nonzero().flatten().flip(0)  # non-sorted subset, covers both lip variants
    survivors = ~mix.traverse
    old_root = e.robot.root[survivors].clone()
    e._reset_idx(ids)
    torch.testing.assert_close(e.robot.root[survivors], old_root)
    bounds = torch.where(e.terrain.env_origins[ids, 2, None] < 0, torch.tensor(up), torch.tensor(down))
    torch.testing.assert_close(c.route_height_bounds[ids], bounds)
    assert not c.upstairs[ids].any()  # ascent must not hold the height clock
    assert not c.reverse_descent[survivors].any()
    sign = torch.where(mix.reverse_descent[ids], -1.0, 1.0)
    torch.testing.assert_close(c.target[ids, 0].sign(), sign)
    assert ((200 <= c.height_remaining[ids]) & (c.height_remaining[ids] <= 600)).all()
    assert ((bounds[:, :1] <= c.height[ids]) & (c.height[ids] <= bounds[:, 1:])).all()

    e.shu.observe_commands(e._measure()["yaw"])
    c.height_remaining[ids] = c.remaining[ids] = 1
    before = c.height[ids].clone()
    c.finish(c._issued, e.reset_terminated, e.reset_time_outs)
    assert not c.height_remaining[ids].any()
    e._sim_step_counter += e.training.robot.decimation
    e.shu.observe_commands(e._measure()["yaw"])
    assert (c.height[ids] != before).all()
    assert ((200 <= c.height_remaining[ids]) & (c.height_remaining[ids] <= 600)).all()
    assert ((bounds[:, :1] <= c.height[ids]) & (c.height[ids] <= bounds[:, 1:])).all()
    torch.testing.assert_close(c.value[ids, 0].sign(), sign)


def test_jitter_must_fit_full_square_after_clearance(runtime):
    stairs_runtime(runtime, clearance_m=1.0)
    with pytest.raises(ValueError, match="center XY jitter does not fit"):
        stairs_runtime(runtime, clearance_m=1.01)


def test_route_rewards_penalize_yaw_rate_not_absolute_yaw(runtime):
    e = stairs_runtime(runtime)
    e._reset_idx(torch.arange(e.num_envs))
    s = e._measure()
    route = e.mixed_curriculum.traverse
    e.shu.observe_commands(s["yaw"])
    assert not e.commands.heading_active[route].any()
    s["angular_velocity"] = torch.zeros_like(s["angular_velocity"])
    zero_rate = e.shu.rewards(s)
    s["angular_velocity"][:, 2] = 0.4
    actual_rate = e.shu.rewards(s)
    s["yaw"] = s["yaw"] + 0.6
    offset_yaw = e.shu.rewards(s)
    assert not zero_rate["ang_vel_error"][route].any()
    assert not offset_yaw["track_ang_vel"][route].any()
    assert (offset_yaw["ang_vel_error"][route] < 0).all()
    torch.testing.assert_close(actual_rate["ang_vel_error"][route], offset_yaw["ang_vel_error"][route])
