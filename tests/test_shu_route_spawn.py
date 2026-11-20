"""P1 stair births through the real reset/observation hooks with CPU articulation transport."""

from math import pi, radians
from types import SimpleNamespace as NS
from unittest.mock import Mock

import pytest
import test_shu_runtime as transport
import torch

from wheelleg.shu_rewards import DRIVE, RELEASE, RISE
from wheelleg.shu_terrain import MIXED_PROFILES, STAIR_PROFILES, mixed_columns

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
    e.training.flat_recovery_probability = 0.20
    e.training.stage["terrain"] = terrain
    columns = mixed_columns(terrain)
    names = [f"{name}_lip" if lip else name for name, lip, _ in columns]
    generator = NS(
        size=(12.0, 12.0),
        num_rows=1,
        num_cols=len(columns),
        border_width=5.0,
        sub_terrains={name: NS() for name in names},
        curriculum=True,
    )
    e.cfg.terrain = NS(terrain_generator=generator)
    # Five free columns and the three route cohorts, each with and without lips.
    cohorts = [(name, False, False) for name, _, pyramid in columns if not pyramid] + [
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
    e.mixed_curriculum = NS(traverse=traverse, reverse_descent=reverse, route_open=traverse, reset=Mock(), step=Mock())
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
    cols = e.terrain.terrain_types
    nonflat = ~e.shu.flat_columns[cols]
    slopes = e.shu.slope_columns[cols]
    ids = nonflat.nonzero().flatten().flip(0)
    e.robot.data.default_root_state[:, 7:] = torch.arange(1.0, 7.0)
    e.robot.data.default_joint_vel.fill_(2.0)
    e.robot.data.default_root_state[:, 3:7] = torch.tensor([0.6, 0.0, 0.0, 0.8])
    default = e.robot.data.default_root_state
    default[:, :2] = torch.tensor([0.2, -0.35])
    origin = e.terrain.env_origins
    offsets = []
    xy = []
    slope_xy = []
    untouched = nonflat & ~(mix.traverse | slopes)
    for _ in range(256):
        e._reset_idx(ids)
        quat = e.robot.data.root_quat_w
        pos = e.robot.data.root_pos_w
        torch.testing.assert_close(pos[ids, 2], origin[ids, 2] + default[ids, 2])
        torch.testing.assert_close(pos[untouched, :2], (origin + default[:, :3])[untouched, :2])
        torch.testing.assert_close(e.initial_position[ids], pos[ids])
        xy.append(pos[mix.traverse, :2] - origin[mix.traverse, :2])
        slope_xy.append(pos[slopes, :2] - origin[slopes, :2])
        ordinary_ground = nonflat & ~mix.traverse
        torch.testing.assert_close(quat[ordinary_ground], default[ordinary_ground, 3:7])
        assert not quat[mix.traverse, 1:3].any()
        torch.testing.assert_close(quat[ids].norm(dim=-1), torch.ones(len(ids)))
        yaw = transport.euler(quat)[2]
        error = yaw - mix.reverse_descent * pi
        offsets.append(torch.atan2(error.sin(), error.cos()))
    assert not e.robot.root[ids, 7:].any() and not e.robot.data.joint_vel[ids].any()
    assert not e.robot.data.root_lin_vel_b[ids].any() and not e.robot.data.root_ang_vel_b[ids].any()

    # The joint histogram exercises uniform marginals and independence across both axes.
    slope_cols = cols[slopes]
    assert len(slope_cols.unique()) == 2
    slope_samples = torch.stack(slope_xy)
    for samples in [torch.stack(xy), *(slope_samples[:, slope_cols == col] for col in slope_cols.unique())]:
        samples = samples.flatten(0, 1)
        assert (samples.abs() <= 1).all()
        bins = ((samples + 1) * 2).long().clamp_max(3)
        frequencies = torch.bincount(4 * bins[:, 0] + bins[:, 1], minlength=16) / len(samples)
        assert ((0.035 < frequencies) & (frequencies < 0.10)).all()

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


@pytest.mark.parametrize("evaluation", [False, True])
def test_flat_replay_matches_full_flat_reset_commands_and_rewards(runtime, evaluation):
    mixed = stairs_runtime(runtime)
    flat = transport.make_runtime(runtime, "p1-flat")
    # Force the recovery branch in training and verify that eval overrides this very same source.
    mixed.training.flat_recovery_probability = flat.training.stage["recovery_probability"] = 1.0
    flat.training.settings["commands"]["height_duration_s"] = (2.0, 6.0)
    flat.shu = runtime[1](flat, None)
    flat.shu.flat.fraction.fill_(1)
    flat.commands = flat.shu.commands
    mixed.cfg.evaluation = flat.cfg.evaluation = evaluation
    if evaluation:
        mixed.commands_fixed = flat.commands_fixed = True
        mixed.fixed_command = flat.fixed_command = torch.tensor([1.5, 0.0, -2.0]), 0.26

    assert not mixed.shu.flat_replay.any() and not flat.shu.flat_replay.any()
    replay = mixed.shu.flat_columns[mixed.terrain.terrain_types]
    ids = replay.nonzero().flatten().flip(0)
    torch.manual_seed(19)
    mixed._reset_idx(ids)
    flat.terrain.env_origins[ids] = mixed.terrain.env_origins[ids]
    torch.manual_seed(19)
    flat._reset_idx(ids)
    assert mixed.shu.flat_replay.equal(replay) and not flat.shu.flat_replay.any()
    assert not mixed.spawn_check_mask[ids].any()
    assert mixed.shu.event.preset_birth[ids].all().item() is not evaluation
    assert not mixed.shu.event.air_birth.any() and mixed.shu.flat is None
    assert mixed.shu.curriculum_state_dict() == {}
    for key in ("root_pos_w", "root_quat_w", "root_lin_vel_w", "joint_pos", "joint_vel"):
        torch.testing.assert_close(getattr(mixed.robot.data, key)[ids], getattr(flat.robot.data, key)[ids])
    for key in ("value", "target", "kind", "remaining", "height_remaining", "height", "fraction"):
        torch.testing.assert_close(getattr(mixed.commands, key)[ids], getattr(flat.commands, key)[ids])
    if evaluation:
        torch.testing.assert_close(mixed.commands.height[ids], torch.full((len(ids), 1), 0.26))
        mixed_obs, flat_obs = mixed._get_observations(), flat._get_observations()
        for key in ("policy", "critic", "history"):
            torch.testing.assert_close(mixed_obs[key][ids], flat_obs[key][ids], msg=key)

    # Put both rows at like-for-like XY, which the mixed atlas classifies as slope or pyramid.
    # Even there, replay must not inherit caps, faster tilting, or the pyramid's reward gates.
    cols = mixed_columns(mixed.training.stage["terrain"])
    slope, pyramid = [next(i for i, (n, _, _) in enumerate(cols) if n == name) for name in ("slope", "pyramid_up")]
    mixed.shu.free_map.column_caps = torch.full((len(cols), 2), 0.01)
    for e in (flat, mixed):
        e.robot.root[ids, 0] = 0.0
        at_col = torch.where(torch.arange(len(ids)) % 2 == 0, slope, pyramid)
        e.robot.root[ids, 1] = (at_col + 0.5 - len(cols) / 2) * 12.0
        e.robot.refresh()
        if not evaluation:
            e.commands.target[ids, 0] = 1.5
        e.shu.observe_commands(e._measure()["yaw"])
    nonflat, on_pyramid = mixed.shu.free_map.reward_masks_at(mixed.robot.data.root_pos_w)
    assert nonflat[ids].all() and on_pyramid[ids].any()

    seen = set()
    for step in range(1 if evaluation else 53):
        for e in (flat, mixed):
            if not evaluation and step == 2:
                # Script a successful stand after torque release; actual velocities/contacts feed the same event.
                e.robot.root[ids, 2] = e.terrain.env_origins[ids, 2] + e.commands.height[ids, 0]
                e.robot.root[ids, 7:] = 0.0
                e.robot.refresh()
            e._pre_physics_step(torch.full_like(e.raw_action, 0.25))
            for _ in range(transport.SUBSTEPS):
                e._sim_step_counter += 1
                e._apply_action()
                e.contact.data.net_forces_w[:, e.contact_wheels, 2] = 30.0
            terminated, timeout = e._get_dones()
            assert not (terminated[ids] | timeout[ids]).any()
            # Nonzero values exercise the terrain-specific penalty and fork/height gates, not just empty masks.
            s = e.state
            s["velocity"] = s["velocity"].clone()
            s["velocity"][ids, 2] = 0.5
            s["gravity"] = s["gravity"].clone()
            s["gravity"][ids, 0] = 0.02
            s["wheel_position_b"][ids, 0, 0] = 0.1
            e.test_terms = e.shu.rewards(s)
            e.shu.observe_commands(s["yaw"])
        for key in ("phase", "reward_phase", "handoff", "rise_succeeded"):
            torch.testing.assert_close(getattr(mixed.shu.event, key)[ids], getattr(flat.shu.event, key)[ids])
        for key in ("value", "height", "height_rate", "vx_active", "wz_active", "heading_active", "reference_yaw"):
            torch.testing.assert_close(getattr(mixed.commands, key)[ids], getattr(flat.commands, key)[ids])
        for key in ("remaining", "height_remaining", "steps"):
            torch.testing.assert_close(getattr(mixed.commands, key)[ids], getattr(flat.commands, key)[ids])
        torch.testing.assert_close(mixed.torque[ids], flat.torque[ids])
        assert mixed.test_terms.keys() == flat.test_terms.keys()
        for key in flat.test_terms:
            torch.testing.assert_close(mixed.test_terms[key][ids], flat.test_terms[key][ids], msg=key)
        seen.add(int(mixed.shu.event.reward_phase[ids[0]]))
        if mixed.shu.event.reward_phase[ids[0]] == RELEASE:
            assert not mixed.torque[ids].any()
    assert seen == ({DRIVE} if evaluation else {RELEASE, RISE, DRIVE})
    assert (mixed.commands.value[ids, 0].abs() > 0.01).all()


def test_flat_replay_uses_source_ratio_and_relabels_only_reset_rows(runtime):
    torch.manual_seed(117)
    e = stairs_runtime(runtime)
    cols = e.terrain.terrain_types
    flat_ids = e.shu.flat_columns[cols].nonzero().flatten()
    recoveries = 0
    for _ in range(160):
        e._reset_idx(flat_ids)
        recoveries += int(e.shu.event.preset_birth.sum())
    assert 0.15 < recoveries / (160 * len(flat_ids)) < 0.25
    switched = flat_ids[:1]
    cols[switched] = e.shu.slope_columns.nonzero().flatten()[0]
    e._reset_idx(switched)
    assert not e.shu.flat_replay[switched].any() and not e.shu.event.preset_birth[switched].any()
    assert e.shu.flat_replay[flat_ids[1:]].all()


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


def test_mixed_route_diagnostics_settle_without_entering_ppo(runtime):
    from wheelleg.shu_mixed_diagnostics import ShuMixedDiagnostics

    e = stairs_runtime(runtime)
    mix = e.mixed_curriculum
    ids = torch.arange(e.num_envs)
    cols = mixed_columns(e.training.stage["terrain"])
    e.mixed_up_columns = torch.tensor([name == "pyramid_down" for name, _, _ in cols])
    e.mixed_lip_columns = torch.tensor([lip for _, lip, _ in cols])
    e.mixed_diagnostics = ShuMixedDiagnostics(
        e.num_envs,
        e.device,
        wheels=e.contact_wheels,
        guides=e.shu.event.guides,
        body_count=len(e.contact.body_names),
        step_dt=e.step_dt,
        physics_dt=e.physics_dt,
        contact_force_n=2.0,
    )
    mix.crossed = torch.zeros_like(mix.traverse)
    mix.reverse_completed = torch.zeros_like(mix.traverse)
    mix.step = Mock()
    e._reset_idx(ids)
    e.shu.observe_commands(e._measure()["yaw"])
    e._sim_step_counter += 5
    e.episode_length_buf += 1
    e.contact.data.net_forces_w[:, e.contact_wheels, 2] = 20
    e._get_dones()
    mix.reverse_completed.copy_(
        mix.reverse_descent
    )  # supported arrival supplied by the separately tested route geometry
    reward = e._get_rewards()
    torch.testing.assert_close(reward, sum(e.reward_sums.values()))
    assert not {"progress", "stuck", "stair_impact", "completion"}.intersection(e.reward_sums)
    assert e.extras["stairs"]["reverse_descent_completed"].equal(mix.reverse_descent)
    e.reset_time_outs[:] = True
    e._reset_idx(ids)
    stats = e.mixed_diagnostics.take()
    assert sum(v for k, v in stats.items() if k.endswith("/episode_count")) == mix.traverse.sum().item()
    assert sum(v for k, v in stats.items() if k.endswith("/completed_count")) == mix.reverse_descent.sum().item()
    assert all(v == 1 for k, v in stats.items() if "/reverse_down/" in k and k.endswith("/completion_rate"))
