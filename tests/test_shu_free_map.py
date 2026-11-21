"""CPU regressions for the P1 free atlas, with synthetic command caps."""

from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

import pytest
import test_shu_runtime as transport
import torch
import yaml
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


def test_reward_masks_follow_current_tile_not_spawn_without_command_caps():
    names = ("flat", "rough", "grid", "slope", "pyramid_up", "pyramid_down", "pyramid_up_lip", "pyramid_down_lip")
    generator = NS(
        size=(12, 12),
        num_rows=10,
        num_cols=len(names),
        border_width=5,
        curriculum=True,
        sub_terrains={name: NS(proportion=1) for name in names},
    )
    m = ShuFreeMap(generator, {}, "cpu")
    # One robot driving across the atlas and then onto its flat exterior border.
    xy = torch.tensor([[0, -48 + i * 12] for i in range(8)] + [[60, 3], [0, 48]])
    nonflat, pyramid = m.reward_masks_at(xy)
    assert nonflat.tolist() == [False, True, True, True, True, True, True, True, False, False]
    assert pyramid.tolist() == [False] * 4 + [True] * 4 + [False] * 2


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


def test_flat_replay_never_inherits_atlas_height_or_edge(runtime):
    e = mixed_runtime(runtime)
    e.shu.flat_replay[:2] = torch.tensor([True, False])
    e.terrain.env_origins[0, 2] = -32
    e.robot.data.root_pos_w[:2, 2] = torch.tensor([-31.75, 0.25])
    e.scanner = NS(data=NS(ray_hits_w=torch.zeros(e.num_envs, 77, 3)))
    # Off the scanned atlas there is no ray hit. The lower layer is still level ground.
    e.scanner.data.ray_hits_w[0, :, 2] = torch.inf
    e.robot.data.root_pos_w[:2, 0] = 80  # both outside the atlas; only the upper-layer round is cut
    torch.testing.assert_close(e._measure()["base_height"][:2], torch.tensor([0.25, 0.25]))
    e.shu.observe_commands(e._measure()["yaw"])
    _, timeout = e._get_dones()
    assert timeout[:2].tolist() == [False, True]
    obs = e._get_observations()
    torch.testing.assert_close(obs["critic"][0, -77:], torch.full((77,), 0.25))


@pytest.mark.parametrize("iteration", [0, 6000])
def test_mixed_map_baseline_uses_separate_clocks_flat_replay_keeps_coupled_event(runtime, iteration):
    e = mixed_runtime(runtime)
    n = e.num_envs
    config = Path(__file__).resolve().parents[1] / "config"
    p1 = yaml.safe_load((config / "policies/p1/policy_meta.yaml").read_text(encoding="utf-8"))
    e.disturbance_phase = p1["stages"]["stairs"]["disturbance_phase"]
    assert e.disturbance_phase == 1
    e.training_iteration_offset, e.common_step_counter = iteration, 0
    e.training.settings.update(rollout_steps=48, disturbance=p1["training"]["disturbance"])
    e.training.shared["randomization"] = yaml.safe_load((config / "robot.yaml").read_text(encoding="utf-8"))[
        "training"
    ]["randomization"]
    for name in ("push_timer", "map_wrench_timer", "collision_timer", "push_remaining", "collision_remaining"):
        setattr(e, name, torch.zeros(n))
    for name in ("push_force", "push_torque", "collision_force"):
        setattr(e, name, torch.zeros(n, 1, 3))
    e.robot.data.root_vel_w = torch.zeros(n, 6)
    e.robot.write_root_velocity_to_sim = Mock()
    # 0=flat push + wrench, 1=map push only, 2=map wrench only, 3=both, 4=flat neither
    e.shu.flat_replay.zero_()
    e.shu.flat_replay[[0, 4]] = True
    e.push_timer.fill_(2)
    e.push_timer[[0, 1, 3]] = 0
    e.map_wrench_timer.fill_(3)
    e.map_wrench_timer[[2, 3, 4]] = 0
    torch.manual_seed(5)
    runtime[0]._push(e)
    v, ids = e.robot.write_root_velocity_to_sim.call_args.args
    assert ids.tolist() == [0, 1, 3] and v[:, :2].abs().max() <= 0.25
    assert not v[:, 2:].any() and not e.collision_remaining.any()
    wrench_ids = [0, 2, 3]
    assert e.push_remaining.nonzero().flatten().tolist() == wrench_ids
    assert (e.push_remaining[wrench_ids] == 10).all()
    assert e.push_force.abs().max() <= 10 and e.push_torque.abs().max() <= 1
    for timer in (e.push_timer[ids], e.map_wrench_timer[[2, 3]]):
        assert ((5 <= timer) & (timer <= 10)).all()
    assert e.push_timer[3] != e.map_wrench_timer[3]


def test_both_slope_signs_use_the_same_free_command_cap():
    generator = NS(
        size=(12, 12),
        num_rows=10,
        num_cols=3,
        border_width=5,
        curriculum=True,
        sub_terrains=dict.fromkeys(("slope", "flat", "slope_inverted")),
    )
    m = ShuFreeMap(generator, {"command_limits": {"slope": {"vx_abs_max_m_s": 2, "wz_abs_max_rad_s": torch.pi}}}, "cpu")
    points = torch.tensor([[0, -12], [0, 0], [0, 12]])
    torch.testing.assert_close(
        m.limits_at(points), torch.tensor([[2, torch.pi], [torch.inf, torch.inf], [2, torch.pi]])
    )
