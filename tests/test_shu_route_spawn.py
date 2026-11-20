"""P1 stair births through the real reset/observation hooks with CPU articulation transport."""

from math import pi, radians
from types import SimpleNamespace as NS
from unittest.mock import Mock

import pytest
import test_shu_runtime as transport
import torch

from wheelleg.shu_terrain import mixed_columns

runtime = transport.runtime


def stairs_runtime(runtime, *, up=(0.26, 0.32), down=(0.19, 0.29)):
    e = transport.make_runtime(runtime, "p1-flat")
    terrain = dict(
        route=dict(
            vx_range_m_s=(0.5, 2.5),
            up_height_range_m=up,
            down_height_range_m=down,
            straight_spawn_probability=0.5,
            max_spawn_yaw_offset_rad=radians(25),
        ),
        pyramid=dict(share_of_stairs=1.0),
    )
    e.training.task = "p1-stairs"
    e.training.stage["terrain"] = terrain
    columns = mixed_columns(terrain)
    generator = NS(size=(12.0, 12.0), num_rows=1, num_cols=len(columns), border_width=5.0, sub_terrains={"flat": NS()})
    e.cfg.terrain = NS(terrain_generator=generator)
    ids = torch.arange(e.num_envs)
    traverse = ids % 3 != 0
    reverse = ids % 3 == 2
    # Forward and reverse rows deliberately share the same physical column.
    pyramid_column = columns.index(("double_down", False, True))
    e.terrain.terrain_types = torch.where(traverse, pyramid_column, 0)
    e.mixed_curriculum = NS(traverse=traverse, reverse_descent=reverse, route_open=traverse, reset=Mock())
    e.reset_terminated = torch.zeros_like(traverse)
    e.reset_time_outs = torch.zeros_like(traverse)
    e.shu = runtime[1](e, None)
    e.commands = e.shu.commands
    return e


def test_real_root_spawn_yaw_mixture_about_zero_or_pi_and_zero_velocity(runtime):
    torch.manual_seed(193)
    e = stairs_runtime(runtime)
    mix = e.mixed_curriculum
    ids = torch.arange(e.num_envs - 1, -1, -1)
    e.robot.data.default_root_state[:, 7:] = torch.arange(1.0, 7.0)
    e.robot.data.default_joint_vel.fill_(2.0)
    e.robot.data.default_root_state[:, 3:7] = torch.tensor([0.6, 0.0, 0.0, 0.8])
    offsets = []
    for _ in range(128):
        e._reset_idx(ids)
        quat = e.robot.data.root_quat_w
        torch.testing.assert_close(quat[~mix.traverse], e.robot.data.default_root_state[~mix.traverse, 3:7])
        assert not quat[mix.traverse, 1:3].any()
        torch.testing.assert_close(quat.norm(dim=-1), torch.ones(e.num_envs))
        yaw = transport.euler(quat)[2]
        error = yaw - mix.reverse_descent * pi
        offsets.append(torch.atan2(error.sin(), error.cos()))
    assert not e.robot.root[:, 7:].any() and not e.robot.data.joint_vel.any()
    assert not e.robot.data.root_lin_vel_b.any() and not e.robot.data.root_ang_vel_b.any()

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


def test_reverse_height_uses_down_range_even_without_common_height(runtime):
    down = (0.19, 0.24)
    e = stairs_runtime(runtime, up=(0.27, 0.32), down=down)
    mix, c = e.mixed_curriculum, e.commands
    ids = torch.tensor([8, 2, 5])  # non-sorted subset of reverse rows
    e._reset_idx(ids)
    torch.testing.assert_close(c.route_height_bounds[ids], torch.tensor([down] * len(ids)))
    assert not c.upstairs[ids].any() and (c.target[ids, 0] < 0).all()
    assert ((down[0] <= c.height[ids]) & (c.height[ids] <= down[1])).all()
    assert not c.reverse_descent[~torch.isin(torch.arange(e.num_envs), ids)].any()
    with pytest.raises(ValueError, match="No common calibrated standing height"):
        e._reset_idx((mix.traverse & ~mix.reverse_descent).nonzero().flatten())


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
