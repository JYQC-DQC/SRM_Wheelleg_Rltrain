"""CPU regressions for the P1 free atlas, with synthetic command caps."""

from types import SimpleNamespace as NS
from unittest.mock import Mock

import pytest
import test_shu_runtime as transport
import torch
from test_shu_commands import settings

from wheelleg.shu_commands import ShuCommands
from wheelleg.shu_curriculum import DASH, TURN
from wheelleg.shu_map import ShuFreeMap

runtime = transport.runtime


def atlas(**settings):
    generator = NS(
        size=(12.0, 12.0),
        num_rows=10,
        num_cols=4,
        border_width=5.0,
        curriculum=True,
        sub_terrains={name: NS(proportion=weight) for name, weight in (("flat", 2), ("slope", 1), ("slope_alt", 1))},
    )
    return ShuFreeMap(generator, settings, "cpu")


def capped_atlas():
    return atlas(
        command_limits={
            "slope": dict(vx_abs_max_m_s=0.8, wz_abs_max_rad_s=0.4),
            "slope_alt": dict(vx_abs_max_m_s=1.6, wz_abs_max_rad_s=None),
        }
    )


def test_full_mesh_edges_and_actual_variant_columns():
    m = capped_atlas()
    points = torch.tensor(
        [
            [-59, -18, 0],  # first flat column
            [12, -6, 0],  # next flat column, another difficulty row
            [-48, 0, 0],  # at the seam: enter slope
            [59, 12, 0],  # at the next seam: enter its variant
            [61, 6, 0],  # outer border mesh, not a slope tile
            [64.5, 28.5, 0],
            [-64.51, 0, 0],
            [0, -28.51, 0],
        ]
    )
    assert m.outside(points).tolist() == [False] * 6 + [True, True]
    inf = torch.inf
    torch.testing.assert_close(
        m.limits_at(points), torch.tensor([[inf, inf], [inf, inf], [0.8, 0.4], [1.6, inf]] + [[inf, inf]] * 4)
    )
    assert atlas(edge_margin_m=None).outside(torch.tensor([[65.0, 29.0, 0.0]])).tolist() == [False]
    assert atlas().limits_at(points) is None


@pytest.mark.parametrize("kind", [DASH, TURN])
def test_current_tile_caps_final_dash_heading_and_turn_without_changing_route(kind):
    ids = torch.arange(3)
    route = torch.tensor([False, False, True])
    drive = torch.ones_like(route)
    no = ~drive
    c = ShuCommands.for_mixed(
        settings(kind, linear_slew_m_s2=1000.0, angular_slew_rad_s2=1000.0),
        len(ids),
        "cpu",
        route=dict(vx_range_m_s=(2.1, 2.1)),
    )
    c.reset(ids, route=route)
    c.prepare(torch.zeros(3), drive, no, no, c.steps, route_open=route)
    c.finish(c._issued, no, no)
    c.target[:2, 2 if kind == TURN else 0] = torch.tensor([-3.0, 3.0])
    c.free_limits = capped_atlas().limits_at(torch.tensor([[0.0, 1, 0], [0, 1, 0], [0, 1, 0]]))
    c.prepare(torch.tensor([1.0, -1.0, 1.0]), drive, no, no, c.steps, route_open=route)
    expected = [[-0.8, 0.0, -0.4], [0.8, 0.0, 0.4]] if kind == DASH else [[0, 0, -0.4], [0, 0, 0.4]]
    torch.testing.assert_close(c.value, torch.tensor([*expected, [2.1, 0.0, 0.0]]))
    torch.testing.assert_close(c._issued[:, :2], c.value[:, (0, 2)])

    # Exit across a column seam mid-segment: restore the target without waiting for resampling.
    c.free_limits = capped_atlas().limits_at(torch.tensor([[0.0, -1, 0], [0, 1, 0], [0, 1, 0]]))
    c.prepare(torch.tensor([1.0, -1.0, 1.0]), drive, no, no, c.steps, route_open=route)
    assert c.value[0, 2 if kind == TURN else 0] == -3
    torch.testing.assert_close(c.value[1], torch.tensor(expected[1]))


def mixed_runtime(runtime):
    e = transport.make_runtime(runtime, "p1-flat")
    e.training.task = "p1-stairs"
    e.shu.free_map = capped_atlas()
    e.shu.flat = None
    e.shu.commands = e.commands = ShuCommands.for_mixed(settings(), e.num_envs, "cpu", route=dict(vx_range_m_s=(2, 2)))
    ids = torch.arange(e.num_envs)
    traverse = (ids == 3) | (ids == 4)
    reverse = ids == 4
    e.mixed_curriculum = NS(traverse=traverse, reverse_descent=reverse, route_open=traverse.clone(), step=Mock())
    e.commands.reset(ids, route=traverse, reverse_descent=reverse)
    ordinary = torch.zeros_like(traverse)
    e.shu.event.reset(ids, ordinary, ordinary, 0)
    return e


def test_fixed_special_command_respects_current_variants_and_same_tick_reset(runtime):
    e = mixed_runtime(runtime)
    e.commands_fixed, e.fixed_command = True, (torch.tensor([-4.0, 7.0, 5.0]), 0.28)
    e.robot.data.root_pos_w[:5, 1] = torch.tensor([1.0, -1.0, 13.0, 1.0, 1.0])
    yaw = torch.full((e.num_envs,), 0.43)
    e.shu.observe_commands(yaw)
    c, mix = e.commands, e.mixed_curriculum
    torch.testing.assert_close(
        c.value[:5], torch.tensor([[-0.8, 0, 0.4], [-4, 0, 5], [-1.6, 0, 5], [0.02, 0, 0], [-0.02, 0, 0]])
    )
    assert not c.heading_active[:5].any() and not c.wz_active[3:5].any()
    torch.testing.assert_close(c.height[3:5], c.height_target[3:5])
    old = c.value.clone()

    # Same tick: one free row changes column and the reverse route resets in place.
    ids = torch.tensor([4, 1])
    c.reset(ids, route=mix.traverse[ids], reverse_descent=mix.reverse_descent[ids])
    e.robot.data.root_pos_w[ids, 1] = 1
    e.fixed_command = (torch.tensor([4.0, -7.0, -5.0]), 0.29)
    e.shu.reset_rows[ids] = True
    e.shu.observe_commands(yaw)
    torch.testing.assert_close(c.value[ids], torch.tensor([[-0.02, 0, 0], [0.8, 0, -0.4]]))
    survivors = ~torch.isin(torch.arange(e.num_envs), ids)
    torch.testing.assert_close(c.value[survivors], old[survivors])
    torch.testing.assert_close(c.height[:3, 0], torch.tensor([0.28, 0.29, 0.28]))

    mix.route_open[3:5] = False
    e._sim_step_counter += e.training.robot.decimation
    e.shu.observe_commands(yaw)
    assert not c.value[3:5].any() and not c.vx_active[3:5].any()


@pytest.mark.parametrize("at_horizon", [False, True])
def test_free_outer_edge_adds_timeout_and_physical_failure_wins(runtime, at_horizon):
    e = mixed_runtime(runtime)
    e._sim_step_counter = (e.max_episode_length - int(not at_horizon)) * e.training.robot.decimation
    e.robot.data.root_pos_w[:4, 0] = torch.tensor([12.0, 65.0, -65.0, 65.0])
    e.robot.data.root_pos_w[4, 0] = -65
    e.robot.data.root_lin_vel_b[4, 0] = torch.nan
    e.shu.event.fall_steps[2] = 100  # an already sustained fall persists on the boundary tick
    e.robot.data.root_quat_w[2] = torch.tensor([0.0, 1.0, 0.0, 0.0])
    e.shu.observe_commands(torch.zeros(e.num_envs))
    terminated, timeout = e._get_dones()
    assert terminated[:5].tolist() == [False, False, True, False, True]
    assert timeout[:5].tolist() == [at_horizon, True, False, True, False]
    assert e.shu.event.physical_failure[2]
