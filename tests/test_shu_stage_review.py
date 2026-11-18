"""CPU regressions for the P2/P3 env callbacks, using scripted sensor samples."""

import ast
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock

import pytest
import torch
import yaml

from wheelleg.commands import Commands
from wheelleg.evaluation import evaluation_cases
from wheelleg.jump import JumpEvent, TrainingJumpButton
from wheelleg.rewards import compute_rewards
from wheelleg.safety import airborne_enabled, leaky_termination, numerical_failure
from wheelleg.shu_rewards import joint_costs
from wheelleg.tensor_ops import rotate_xy
from wheelleg.training import _validate_p3_button_schedule, load_training, mutable

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT
ENV = ROOT / "isaac/wheelleg_tasks/env.py"


def cfg(task):
    return load_training(task, BASE / "config/robot.yaml", ROOT / f"config/policies/{task[:2]}/policy_meta.yaml")


@pytest.fixture
def env_methods():
    # Execute actual env methods with fake sensor data, without importing or starting Isaac.
    tree = ast.parse(ENV.read_text(encoding="utf-8"), filename=str(ENV))
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "WheelLegEnv")
    names = {
        "_prepare_stage_command",
        "set_jump_button",
        "_pre_physics_step",
        "_record_contacts",
        "_sample_jump",
        "_measure",
        "_get_dones",
        "_get_rewards",
    }
    module = ast.Module(
        body=[node for node in cls.body if isinstance(node, ast.FunctionDef) and node.name in names], type_ignores=[]
    )
    namespace = dict(
        torch=torch,
        compute_rewards=compute_rewards,
        rotate_xy=rotate_xy,
        joint_costs=joint_costs,
        airborne_enabled=airborne_enabled,
        numerical_failure=numerical_failure,
        leaky_termination=leaky_termination,
        wrap_to_pi=lambda x: x,
        quat_apply_inverse=lambda q, v: v,
        euler_xyz_from_quat=lambda q: (torch.zeros_like(q[:, 0]),) * 3,
    )
    exec(compile(module, str(ENV), "exec"), namespace)
    callbacks = NS(**{name: namespace[name] for name in names})
    submit = callbacks.set_jump_button

    def set_button(env, level, **kw):
        env._get_observations = lambda: callbacks._prepare_stage_command(env)
        return submit(env, level, **kw)

    callbacks.set_jump_button = set_button
    return callbacks


def fake_env(task):
    t = cfg(task)
    settings, stage, shared = mutable(t.settings), mutable(t.stage), mutable(t.shared)
    settings["commands"].update(
        vx_range_m_s=(2.0, 2.0),
        height_range_m=(0.3, 0.3),
        segment_duration_s=(2.0, 2.0),
        height_duration_s=(3.0, 3.0),
        linear_slew_m_s2=0.5,
        angular_slew_rad_s2=1.0,
    )
    stage.update(height_range_m=(0.2, 0.2), event_duration_s=0.8, landing_stable_s=0.02, landing_tilt_rad=0.1)
    if task == "p2-spin":
        settings["evaluation"]["height_m"] = 0.3
        stage.update(spin_rates_rad_s=(-18, 0, 18), spin_probabilities=(0.3, 0.4, 0.3))
    elif task == "p3-tunnel":
        stage["tunnel"].update(vx_range_m_s=(2.0, 2.0), ground_tolerance_m=0.01)
    shared.update(wheel_radius_m=0.1, hip_pivot_positions_b_m=((0, 0, 0), (0, 0, 0)))
    shared["airborne"].update(wheel_clearance_m=0.02, base_height_m=0.1)
    shared["termination"].update(contact_force_n=20.0, airborne_tilt_rad=0.5)
    t = replace(t, settings=settings, stage=stage, shared=shared)
    commands = Commands(t, 1, "cpu")
    commands.reset(torch.tensor([0]))
    jump = JumpEvent(stage, 1, "cpu") if task.startswith("p3") else None
    zero = torch.zeros(1, dtype=torch.bool)
    vel = torch.zeros(1, 3)
    act = torch.zeros(1, 6)
    root = torch.tensor([[0.0, 0.0, 0.3]])
    env = NS(
        training=t,
        cfg=NS(evaluation=True),
        commands=commands,
        jump=jump,
        training_jump_button=None,
        _operator_jump_height=None,
        shu=None,
        scanner=None,
        robot=NS(
            data=NS(
                root_pos_w=root,
                root_quat_w=torch.tensor([[1.0, 0.0, 0.0, 0.0]]),
                root_lin_vel_w=vel,
                root_lin_vel_b=vel,
                root_ang_vel_b=vel,
                body_pos_w=torch.tensor([[[0.0, 0.0, 0.1], [0.0, 0.0, 0.1]]]),
                body_lin_vel_w=torch.zeros(1, 2, 3),
                projected_gravity_b=vel,
                joint_vel=act,
                joint_pos=act,
            )
        ),
        contact=NS(data=NS(net_forces_w_history=torch.zeros(1, 3, 3, 3), net_forces_w=torch.zeros(1, 3, 3))),
        terrain=NS(env_origins=torch.zeros(1, 3)),
        obstacle_contacts={},
        contact_peaks=torch.zeros(1, 3),
        obstacle_hit=zero.clone(),
        wheels=[0, 1],
        contact_wheels=[0, 1],
        contact_terminal=[2],
        contact_bad=[2],
        wheel_channels=[2, 5],
        joints=list(range(6)),
        legs=[0, 1, 3, 4],
        lower=torch.full((6,), -1.0),
        upper=torch.ones(6),
        num_envs=1,
        family=task[:2],
        extras={},
        reward_sums={},
        previous_position=root.clone(),
        _sim_step_counter=0,
        _stage_command_tick=-1,
        _jump_sample_tick=-1,
        jump_blocked=zero.clone(),
        physics_dt=0.002,
        step_dt=0.01,
        device="cpu",
        episode_length_buf=torch.tensor([200]),
        max_episode_length=2000,
        commands_fixed=False,
        raw_action=act.clone(),
        previous_action=act.clone(),
        second_action=act.clone(),
        prev_qd=act.clone(),
        torque=act.clone(),
        numerical_bad=zero.clone(),
        bad_action=zero.clone(),
        airborne=zero.clone(),
        air_enter=torch.zeros(1),
        air_exit=torch.zeros(1),
        air_elapsed=torch.zeros(1),
        fall_counter=torch.zeros(1),
        iteration_raw_action_max=torch.tensor(0.0),
        iteration_numerical_terminations=torch.tensor(0),
    )

    return env


def bind_jump_samples(env_methods, env):
    env._record_contacts = lambda tick: env_methods._record_contacts(env, tick)
    env._measure = lambda: env_methods._measure(env)
    env._sample_jump = lambda: env_methods._sample_jump(env)


@pytest.mark.parametrize("task", ["p2-spin", "p3-jump", "p3-tunnel"])
def test_specialists_inherit_ground_rewards_and_height_step(env_methods, task):
    e = fake_env(task)
    c = e.commands
    t = e.training
    t.settings["reward_parameters"]["contact_force_n"] = 1.0
    for key, v in t.settings["rewards"].items():
        if v is None:
            t.settings["rewards"][key] = 0
    t.stage.update(flight_tracking_scale=0.5, jump_smooth_scale=0.4)
    frozen = torch.tensor([True])
    c.height.fill_(0.2)
    c.height_remaining.zero_()
    c.step(0.01, frozen)
    assert c.height.item() == pytest.approx(0.2) and c.height_rate.item() == 0
    c.step(0.01, ~frozen)
    assert c.height.item() == pytest.approx(0.3) and c.height_rate.item() == pytest.approx(10.0)
    e.state = env_methods._measure(e)
    e.state.update(terminated=~frozen, height_error=torch.tensor([0.08]), undesired_force=torch.tensor([[2.0, 3.0]]))
    e.raw_action.fill_(1)
    e.jump_interval = ~frozen
    assert torch.isfinite(env_methods._get_rewards(e)).all()
    assert e.reward_sums["undesired_contact"].item() == pytest.approx(-0.02)
    assert e.reward_sums["vertical_velocity"].item() == pytest.approx(-0.01)
    assert e.reward_sums["action_smoothness_leg"].item() == pytest.approx(-0.002)
    if e.jump is not None:
        e.reward_sums.clear()
        e.jump_interval = frozen
        e.jump.active.fill_(True)
        env_methods._get_rewards(e)
        assert e.reward_sums["vertical_velocity"].item() == e.reward_sums["track_height"].item() == 0
        assert e.reward_sums["action_smoothness_leg"].item() == pytest.approx(-0.0008)


def sample_interval(env_methods, env, supports):
    env_methods._pre_physics_step(env, torch.zeros_like(env.raw_action))
    contact = env.contact.data
    for i, (left, right) in enumerate(supports):
        env._sim_step_counter += 1
        contact.net_forces_w[0, :2, 2] = torch.tensor([left, right]) * 50
        contact.net_forces_w_history = contact.net_forces_w_history.roll(1, dims=1)
        contact.net_forces_w_history[:, 0] = contact.net_forces_w
        if i < len(supports) - 1:
            env._record_contacts(env._sim_step_counter)
    return env_methods._get_dones(env)


def test_p3_flat_press_does_not_freeze_motion_slew(env_methods):
    env = fake_env("p3-jump")
    env.commands.target[:, 0] = 2.0  # moving cohort
    env.commands.value[:, 0] = 1.0
    env_methods.set_jump_button(env, torch.tensor([True]))
    env_methods._pre_physics_step(env, torch.zeros_like(env.raw_action))
    assert env.jump.active.item()
    assert env.commands.value[0, 0].item() == pytest.approx(1.005)


def test_p2_action_interval_uses_command_that_policy_observed(env_methods):
    env = fake_env("p2-spin")
    env.commands.target[:, 2] = 18.0
    env_methods._prepare_stage_command(env)
    before_action = env.commands.value.clone()
    assert before_action[0, 2].item() == pytest.approx(0.01)
    env_methods._prepare_stage_command(env)  # repeated reads must not advance the command clock
    env_methods._pre_physics_step(env, torch.zeros_like(env.raw_action))
    assert torch.equal(env.commands.value, before_action)
    env._sim_step_counter += 5
    env_methods._prepare_stage_command(env)
    assert env.commands.value[0, 2].item() == pytest.approx(0.02)


def test_p3_training_does_not_schedule_disturbance_on_press(env_methods):
    env = fake_env("p3-jump")
    env.cfg.evaluation = False
    env._push = Mock()
    env_methods.set_jump_button(env, torch.tensor([True]))
    env_methods._pre_physics_step(env, torch.zeros_like(env.raw_action))
    assert env.jump.active.item()
    assert not env._push.called


def test_tunnel_alternating_substep_support_cannot_settle(env_methods):
    env = fake_env("p3-tunnel")
    env.jump.active.fill_(True)
    env.jump.took_off.fill_(True)
    env.jump.crossed_over_beam.fill_(True)
    bind_jump_samples(env_methods, env)
    no, yes = torch.tensor([False]), torch.tensor([True])
    env._tunnel_geometry = lambda: (no, no, no, yes)  # geometry is wholly past the beam
    left, right, both = (True, False), (False, True), (True, True)
    for _ in range(3):
        sample_interval(env_methods, env, [left, right, left, right, left])
    # Both wheels had a peak over threshold, but never at the same time.
    assert (env.contact_peaks[:, :2] > 20).all() and not env.jump.landing_pulse.item()
    assert not env.jump.landed.item()
    sample_interval(env_methods, env, [both] * 5)
    assert env.jump.stable_time.item() == pytest.approx(0.01)
    sample_interval(env_methods, env, [both, left, both, both, both])
    assert env.jump.stable_time.item() == pytest.approx(0.006) and not env.jump.landing_pulse.item()
    sample_interval(env_methods, env, [both] * 5)
    assert not env.jump.landing_pulse.item()
    terminated, timeout = sample_interval(env_methods, env, [both] * 5)
    assert env.jump.landing_pulse.item() and terminated.item() and not timeout.item()


def test_tunnel_clean_time_limit_is_not_physical_termination(env_methods):
    env = fake_env("p3-tunnel")
    env.episode_length_buf.fill_(env.max_episode_length)
    bind_jump_samples(env_methods, env)
    no, yes = torch.tensor([False]), torch.tensor([True])
    env._tunnel_geometry = lambda: (yes, no, no, no)
    terminated, timeout = sample_interval(env_methods, env, [(True, True)] * 5)
    assert not terminated.item() and timeout.item() and not env.state["terminated"].item()
    # Even an open jump is censored, not reclassified as a beam hit or a failed task.
    env.jump.active.fill_(True)
    terminated, timeout = sample_interval(env_methods, env, [(True, True)] * 5)
    assert not terminated.item() and timeout.item()
    assert env.jump.finished.item() and not env.jump.invalid.item() and not env.jump.failed.item()


def test_tunnel_first_touch_uses_its_own_geometry_not_end_of_interval(env_methods):
    env = fake_env("p3-tunnel")
    env.jump.active.fill_(True)
    env.jump.took_off.fill_(True)
    env.jump.crossed_over_beam.fill_(True)
    bind_jump_samples(env_methods, env)
    no = torch.tensor([False])
    env._tunnel_geometry = lambda: (no, no, no, torch.tensor([env._sim_step_counter >= 3]))
    terminated, timeout = sample_interval(env_methods, env, [(True, False)] + [(True, True)] * 4)
    assert env.tunnel_past.item() and env.jump.first_touch.item()
    assert env.jump.invalid.item() and env.jump.failed.item()
    assert terminated.item() and not timeout.item() and not env.jump.landing_pulse.item()


def test_p3_event_deadline_still_pays_failure_not_truncation(env_methods):
    env = fake_env("p3-jump")
    env.jump.settings["event_duration_s"] = 0.01
    env.jump.active.fill_(True)
    bind_jump_samples(env_methods, env)
    terminated, timeout = sample_interval(env_methods, env, [(True, True)] * 5)
    assert terminated.item() and not timeout.item() and env.jump.failed.item()
    state = {**env.state, "jump": env.jump, "termination_multiplier": torch.ones(1)}
    terms = compute_rewards(state, {}, {"termination": -4, "jump_landing": 3}, env.step_dt, 2.5)
    assert terms["termination"].item() == -4 and terms["jump_landing"].item() == 0


def test_shared_p2_cases_follow_signed_yaw_only_contract():
    env = fake_env("p2-spin")
    cases = evaluation_cases(env.training)
    assert {case.command for case in cases} == {(0.0, 0.0, x) for x in (-18, 0, 18)}
    assert all(case.translation == (0.0, 0.0) for case in cases)


@pytest.mark.parametrize(
    "task, key",
    [("p2-spin", "angular_slew_rad_s2"), ("p3-jump", "linear_slew_m_s2"), ("p3-tunnel", "angular_slew_rad_s2")],
)
@pytest.mark.parametrize("value", [-10.0, 0.0, float("inf")])
def test_stage_rejects_unphysical_slew(tmp_path, task, key, value):
    family = task[:2]
    path = tmp_path / f"{family}.yaml"
    policy = yaml.safe_load((ROOT / f"config/policies/{family}/policy_meta.yaml").read_text(encoding="utf-8"))
    policy["training"]["commands"][key] = value
    path.write_text(yaml.safe_dump(policy), encoding="utf-8")
    with pytest.raises(ValueError, match=rf"commands\.{key}.*finite positive"):
        load_training(task, BASE / "config/robot.yaml", path)


def test_p2_valid_signed_rates_never_request_planar_translation():
    commands = fake_env("p2-spin").commands
    commands.value[0, :2] = torch.tensor([1.0, -1.0])
    commands.translation.fill_(1)
    commands.target[0, 2] = -18.0
    commands.remaining.fill_(torch.inf)
    commands.step(30.0, torch.tensor([False]))
    assert commands.value.tolist() == [[0.0, 0.0, -18.0]]
    assert not commands.world_translation().any()


def test_p3_first_timed_interval_uses_action_that_saw_the_press(env_methods):
    env = fake_env("p3-jump")
    # Waiting, however long, never synthesizes a button edge.
    env.episode_length_buf.fill_(1500)
    env_methods._prepare_stage_command(env)
    assert not env.jump.active.item()
    env_methods._pre_physics_step(env, torch.zeros_like(env.raw_action))
    assert not env.jump.active.item()
    # An explicit button submitted before the action is visible even on a repeated observation read.
    old_cmd = env.commands.value.clone()
    env_methods.set_jump_button(env, torch.tensor([True]))
    assert torch.equal(env.commands.value, old_cmd)
    assert env.jump.command_m.item() == pytest.approx(0.2)
    env_methods._pre_physics_step(env, torch.zeros_like(env.raw_action))
    assert env.jump.active.item() and env.jump.elapsed.item() == 0
    bind_jump_samples(env_methods, env)
    env._record_contacts(env._sim_step_counter)  # same old physics sample at the interval's start
    assert env.jump.elapsed.item() == 0
    for _ in range(5):
        env._sim_step_counter += 1
        env._record_contacts(env._sim_step_counter)
    assert env.jump.elapsed.item() == pytest.approx(0.01)


def test_p3_first_wheel_touch_ends_air_guidance():
    env = fake_env("p3-jump")
    event = env.jump
    event.active.fill_(True)
    event.took_off.fill_(True)
    event.update(
        0.01,
        torch.tensor([0.3]),
        torch.tensor([-0.2]),
        torch.tensor([[True, False]]),
        torch.tensor([True]),
        torch.tensor([True]),
        torch.tensor([False]),
        wheel_clearance=torch.tensor([0.0]),
        takeoff_clearance_m=0.02,
    )
    assert event.first_touch.item() and not event.landed.item()
    assert not event.flight.item()


def test_jump_request_expires_by_command_clock_not_event_outcome(env_methods):
    env = fake_env("p3-jump")
    env_methods.set_jump_button(env, torch.tensor([True]), target_height_m=0.2)
    env.jump.finish_step(env.physics_dt, torch.tensor([True]))  # adjudicator stopped early
    assert not env.jump.active.item()
    for step in range(82):  # 0.8 s + 0.02 s, 100 Hz
        assert env.jump.command_m.item() == pytest.approx(0.2)
        env._sim_step_counter += 5
        env_methods._prepare_stage_command(env)
        remaining = env.jump.command_remaining.clone()
        env_methods._prepare_stage_command(env)  # rereading the same observation cannot shorten the latch
        torch.testing.assert_close(env.jump.command_remaining, remaining)
    assert env.jump.command_m.item() == 0


def test_held_button_does_not_auto_retrigger_after_finish_or_reset(env_methods):
    env = fake_env("p3-jump")
    env_methods.set_jump_button(env, torch.tensor([True]))
    assert env.jump.active.item()
    env.jump.finish_step(env.physics_dt, torch.tensor([True]))
    env.jump.reset(torch.tensor([0]))
    env_methods.set_jump_button(env, torch.tensor([True]))
    assert not env.jump.active.item()
    env_methods.set_jump_button(env, torch.tensor([False]))
    env_methods.set_jump_button(env, torch.tensor([True]))
    assert env.jump.active.item()


def test_pending_templates_are_not_ready_and_p3_has_no_generated_cases():
    for task in ("p2-spin", "p3-jump", "p3-tunnel"):
        conf = cfg(task)
        missing = conf.missing()
        assert conf.settings["reward_clip"] == 1.0
        assert conf.settings["commands"]["angular_slew_rad_s2"] == 10.0
        assert not any(
            "press_time" in field or "press_distance" in field or "disturbance" in field for field in missing
        )
        if task.startswith("p3"):
            with pytest.raises(ValueError, match="explicit runtime button"):
                evaluation_cases(conf)
    tunnel = cfg("p3-tunnel")
    geometry = tunnel.stage["tunnel"]
    assert [
        geometry[key]
        for key in ("beam_bottom_m", "beam_height_m", "beam_length_m", "beam_offset_from_entrance_m", "lane_width_m")
    ] == [0.25, 0.27, 0.35, 1.35, 0.8]
    assert geometry["beam_width_m"] is None
    assert any(x.endswith(".beam_width_m") for x in tunnel.missing())


@pytest.mark.parametrize("task", ["p3-jump", "p3-tunnel"])
def test_training_opens_one_time_edge_and_manual_cannot_mix(env_methods, task):
    env = fake_env(task)
    env._tunnel_geometry = lambda: (torch.tensor([True]), None, None, None)
    env.training_jump_button = TrainingJumpButton(
        dict(press_time_range_s=(0.02, 0.02), no_press_probability=0), 1, "cpu"
    )
    env.training_jump_button.reset(torch.tensor([0]))
    for step in range(2):
        env.episode_length_buf.fill_(step)
        env._sim_step_counter = step * 5
        env.robot.data.root_pos_w[:, 0] = 9  # Distance cannot request a press.
        env_methods._prepare_stage_command(env)
        assert not env.jump.active.item()
    env.episode_length_buf.fill_(2)
    env._sim_step_counter = 10
    env_methods._prepare_stage_command(env)
    assert env.jump.active.item() and env.jump.elapsed.item() == 0
    assert not env.training_jump_button.pending.item()
    env_methods._prepare_stage_command(env)  # reads do not mutate pulse state twice
    assert env.jump.button_down.item()
    env.jump.finish_step(env.physics_dt, torch.tensor([True]))
    env._sim_step_counter += 5
    env_methods._prepare_stage_command(env)
    assert not env.jump.active.item() and not env.jump.button_down.item()
    with pytest.raises(ValueError, match="cannot be mixed"):
        env_methods.set_jump_button(env, torch.tensor([True]))


def test_training_sampler_no_press_and_subset_reset():
    schedule = TrainingJumpButton(dict(press_time_range_s=(0.0, 0.0), no_press_probability=1.0), 2, "cpu")
    schedule.reset(torch.arange(2))
    assert not schedule.step(torch.zeros(2)).any()
    schedule.no_press_probability = 0
    schedule.reset(torch.tensor([1]))
    assert schedule.step(torch.zeros(2)).tolist() == [False, True]
    assert not schedule.step(torch.ones(2)).any()


@pytest.mark.parametrize("task", ["p3-jump", "p3-tunnel"])
def test_moving_probability_applies_only_to_training(task):
    env = fake_env(task)
    t = env.training
    t.stage["moving_probability"] = 0
    commands = Commands(t, 2, "cpu", sample_jump_motion=True)
    commands.reset(torch.arange(2))
    assert not commands.target[:, 0].any()
    manual = Commands(t, 2, "cpu")
    manual.reset(torch.arange(2))
    assert (manual.target[:, 0] == 2).all()
    t.stage["moving_probability"] = 1
    commands.reset(torch.arange(2))
    assert (commands.target[:, 0] == 2).all()


def test_pending_training_keys_do_not_block_manual_rollouts():
    for task in ("p3-jump", "p3-tunnel"):
        conf = cfg(task)
        train = conf.missing(simulate_jump_button=True)
        manual = conf.missing(evaluation=True)
        for key in ("no_press_probability", "moving_probability", "press_time_range_s"):
            assert any(x.endswith(f".{key}") for x in train)
            assert not any(x.endswith(f".{key}") for x in manual)
        for key in (
            "duration_s",
            "episodes_per_case",
            "seed",
            "height_m",
            "observation_delay_steps",
            "action_delay_steps",
        ):
            assert f"policy.training.evaluation.{key}" in manual
            assert f"policy.training.evaluation.{key}" not in train


def test_schedule_rejects_no_jumps_and_inaccessible_last_press():
    conf = cfg("p3-jump")
    stage = mutable(conf.stage)
    stage.update(press_time_range_s=(1.0, 1.0), no_press_probability=0.2, moving_probability=0.5)
    _validate_p3_button_schedule(replace(conf, stage=stage))
    stage["no_press_probability"] = 1
    with pytest.raises(ValueError, match="no_press_probability"):
        _validate_p3_button_schedule(replace(conf, stage=stage))
    stage.update(no_press_probability=0.0, press_time_range_s=(1.0, conf.settings["episode_length_s"]))
    with pytest.raises(ValueError, match="actionable policy interval"):
        _validate_p3_button_schedule(replace(conf, stage=stage))


def test_operator_target_is_applied_to_same_observation(env_methods):
    env = fake_env("p3-jump")
    env.training.stage["height_range_m"] = (0.2, 0.3)
    env_methods.set_jump_button(env, torch.tensor([True]), target_height_m=0.28)
    assert env.jump.active.item() and env.jump.height.item() == pytest.approx(0.28)
    env_methods.set_jump_button(env, torch.tensor([False]))
    assert env.jump.active.item() and not env.jump.button_down.item()


def test_kuhn_rollout_accepts_only_manual_time_for_both_stages():
    path = ROOT / "isaac/scripts/evaluate.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    func = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_manual_press")
    import argparse
    from math import isfinite

    from wheelleg.tasks import TASKS

    ns = dict(TASKS=TASKS, isfinite=isfinite)
    exec(compile(ast.Module(body=[func], type_ignores=[]), str(path), "exec"), ns)
    for task in ("p3-jump", "p3-tunnel"):
        conf = fake_env(task).training
        conf.settings["evaluation"]["duration_s"] = 2.0
        args = NS(task=task, vx_m_s=2.0, no_press=False, press_time_s=0.0, jump_height_m=0.2)
        assert ns["_manual_press"](argparse.ArgumentParser(), args, conf) == (True, 0.0)
        args.press_time_s = 2.0
        with pytest.raises(SystemExit):
            ns["_manual_press"](argparse.ArgumentParser(), args, conf)
    source = path.read_text(encoding="utf-8")
    assert "--press-distance-m" not in source and "fixed_jump_press" not in source
    assert "obs = raw.set_jump_button" in source


def test_formal_train_check_only_uses_pending_button_keys(monkeypatch, capsys):
    import importlib.util
    import json
    import sys

    spec = importlib.util.spec_from_file_location("reviewed_train", ROOT / "isaac/scripts/train.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for task in ("p3-jump", "p3-tunnel"):
        monkeypatch.setattr(
            sys,
            "argv",
            [
                "train",
                "--check-only",
                "--task",
                task,
                "--robot",
                str(BASE / "config/robot.yaml"),
                "--policy",
                str(ROOT / "config/policies/p3/policy_meta.yaml"),
            ],
        )
        module.main()  # exits before Isaac imports
        data = json.loads(capsys.readouterr().out)
        for key in ("press_time_range_s", "no_press_probability", "moving_probability"):
            assert any(x.endswith(f".{key}") for x in data["missing"])
