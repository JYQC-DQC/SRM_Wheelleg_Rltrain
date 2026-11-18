"""Exercise the SHU P1 callbacks with scripted articulation/contact data, not simulated dynamics."""

import importlib.util
import sys
from dataclasses import asdict, replace
from math import pi
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest
import torch

from wheelleg.actor import DeployedPolicy, policy_contract
from wheelleg.checkpoints import load_landing_transfer
from wheelleg.config import load_policy, load_robot
from wheelleg.history import HistoryBuffer
from wheelleg.shu_rewards import AIR, CATCH, DRIVE, RELEASE, RISE
from wheelleg.shu_spawn import LEG_JOINT_ORDER, SpawnConfig

ROOT = Path(__file__).resolve().parents[1]
N, SUBSTEPS = 32, 5
ACTIVE = [6, 9, 14, 3, 2, 15]
LEG = [6, 3, 9, 2, 0, 1, 4, 5, 7, 8, 10, 11]
SPRINGS, WHEELS, CONTACT_WHEELS = [12, 13], [1, 3], [4, 0]
BODIES = ["base", "wheel_l", "guide", "wheel_r", "leg"]
CONTACT_BODIES = ["wheel_r", "leg", "base", "guide", "wheel_l"]


def quat_apply(q, v):
    # Unit wxyz, independent Torch math for the fake transport only.
    xyz = q[..., 1:].expand_as(v)
    t = 2 * torch.cross(xyz, v, dim=-1)
    return v + q[..., :1] * t + torch.cross(xyz, t, dim=-1)


def quat_inverse(q, v):
    return quat_apply(torch.cat((q[..., :1], -q[..., 1:]), -1), v)


def euler(q):
    w, x, y, z = q.unbind(-1)
    return (
        torch.atan2(2 * (w * x + y * z), 1 - 2 * (x.square() + y.square())),
        torch.asin((2 * (w * y - z * x)).clamp(-1, 1)),
        torch.atan2(2 * (w * z + x * y), 1 - 2 * (y.square() + z.square())),
    )


class DirectTransport:
    def reset(self, seed=None, options=None):
        if seed is not None:
            torch.manual_seed(seed)
        self._reset_idx(torch.arange(self.num_envs))
        return self._get_observations(), self.extras

    def _reset_idx(self, ids):
        self.episode_length_buf[ids] = 0


@pytest.fixture
def runtime(monkeypatch):
    try:
        from isaaclab.envs import DirectRLEnv
    except (ImportError, RuntimeError):
        modules = {
            "isaaclab": {},
            "isaaclab.sim": {},
            "isaaclab.assets": dict.fromkeys(("Articulation", "RigidObject", "RigidObjectCfg")),
            "isaaclab.envs": {"DirectRLEnv": DirectTransport},
            "isaaclab.sensors": dict.fromkeys(("ContactSensor", "RayCaster")),
            "isaaclab.utils": {},
            "isaaclab.utils.buffers": {"DelayBuffer": None},
            "isaaclab.utils.math": {
                "quat_apply_inverse": quat_inverse,
                "euler_xyz_from_quat": euler,
                "quat_from_euler_xyz": None,  # not reached for P1
                "wrap_to_pi": lambda x: (x + pi) % (2 * pi) - pi,
            },
        }
        for name, entries in modules.items():
            module = ModuleType(name)
            vars(module).update(entries)
            monkeypatch.setitem(sys.modules, name, module)
        # Load a private module copy so fake Isaac bindings do not leak into other tests.
        bindings = {}
        for name in ("shu", "env"):
            fq = f"isaac.wheelleg_tasks.{name}"
            path = ROOT / f"isaac/wheelleg_tasks/{name}.py"
            spec = importlib.util.spec_from_file_location(fq, path)
            module = importlib.util.module_from_spec(spec)
            monkeypatch.setitem(sys.modules, fq, module)
            spec.loader.exec_module(module)
            bindings[name] = module
        return bindings["env"].WheelLegEnv, bindings["shu"].ShuP1
    from isaac.wheelleg_tasks.env import WheelLegEnv
    from isaac.wheelleg_tasks.shu import ShuP1

    monkeypatch.setattr(DirectRLEnv, "_reset_idx", DirectTransport._reset_idx)
    monkeypatch.setattr(DirectRLEnv, "reset", DirectTransport.reset)
    return WheelLegEnv, ShuP1


class Articulation:
    def __init__(self):
        root = torch.zeros(N, 13)
        root[:, 2:4] = torch.tensor([0.27, 1.0])
        self.root = root.clone()
        self.data = SimpleNamespace(
            default_root_state=root,
            default_joint_pos=torch.zeros(N, 16),
            default_joint_vel=torch.zeros(N, 16),
            joint_pos_limits=torch.tensor([-10.0, 10.0]).expand(N, 16, 2).clone(),
            joint_pos=torch.zeros(N, 16),
            joint_vel=torch.zeros(N, 16),
            root_pos_w=self.root[:, :3],
            root_quat_w=self.root[:, 3:7],
            root_lin_vel_w=self.root[:, 7:10],
            root_lin_vel_b=torch.zeros(N, 3),
            root_ang_vel_b=torch.zeros(N, 3),
            projected_gravity_b=torch.zeros(N, 3),
            body_pos_w=torch.zeros(N, 5, 3),
            body_lin_vel_w=torch.zeros(N, 5, 3),
        )
        self.effort = torch.zeros(N, 16)
        self.joint_names = ["unused"] * 16
        for i, name in zip(LEG, LEG_JOINT_ORDER, strict=True):
            self.joint_names[i] = name

    def find_joints(self, names, preserve_order):
        assert preserve_order
        return [self.joint_names.index(name) for name in names], names

    def find_bodies(self, names, preserve_order):
        assert preserve_order
        return [BODIES.index(name) for name in names], names

    def refresh(self):
        d = self.data
        d.root_lin_vel_b.copy_(quat_inverse(d.root_quat_w, d.root_lin_vel_w))
        d.root_ang_vel_b.copy_(quat_inverse(d.root_quat_w, self.root[:, 10:13]))
        d.projected_gravity_b.copy_(quat_inverse(d.root_quat_w, self.root.new_tensor([0, 0, -1]).expand(N, 3)))
        wheels_b = self.root.new_tensor([[0.02, 0.11, -0.245], [0.02, -0.11, -0.245]]).expand(N, 2, 3)
        d.body_pos_w[:] = d.root_pos_w[:, None]
        d.body_pos_w[:, WHEELS] += quat_apply(d.root_quat_w[:, None], wheels_b)
        d.body_lin_vel_w[:] = d.root_lin_vel_w[:, None]

    def write_root_pose_to_sim(self, values, ids):
        self.root[ids, :7] = values
        self.refresh()

    def write_root_velocity_to_sim(self, values, ids):
        self.root[ids, 7:] = values
        self.refresh()

    def write_joint_state_to_sim(self, q, qd, *, env_ids):
        self.data.joint_pos[env_ids], self.data.joint_vel[env_ids] = q, qd

    def set_joint_effort_target(self, effort, *, joint_ids):
        self.effort[:, joint_ids] = effort


class TransportDelay:
    def __init__(self):
        self.time_lags = torch.zeros(N, dtype=torch.long)

    def reset(self, ids):
        self.time_lags[ids] = 0

    def compute(self, values):
        return values


def make_runtime(runtime, stage, proof=None):
    cls, shu_cls = runtime

    # Bypass Isaac scene/kit initialization; all exercised WheelLegEnv hooks are real.
    class Runtime(cls):
        num_envs = N
        device = "cpu"
        physics_dt = 0.002
        step_dt = 0.01
        max_episode_length = 2000
        max_episode_length_s = 20.0

        def _apply_wrench(self):
            pass

        def _randomize_controls(self, ids):
            pass

        def _push(self):
            pass

    e = Runtime.__new__(Runtime)
    e.cfg = SimpleNamespace(evaluation=False, flat_transfer=proof)
    e.robot = Articulation()
    force = torch.zeros(N, len(CONTACT_BODIES), 3)
    e.contact = SimpleNamespace(
        body_names=CONTACT_BODIES,
        data=SimpleNamespace(net_forces_w=force, net_forces_w_history=force[:, None]),
        find_bodies=lambda names, preserve_order: ([CONTACT_BODIES.index(name) for name in names], names),
    )
    e.terrain = SimpleNamespace(env_origins=torch.zeros(N, 3))
    e.terrain.env_origins[:, 0] = torch.arange(N) * 4
    e.joints, e.springs, e.wheels, e.contact_wheels = ACTIVE, SPRINGS, WHEELS, CONTACT_WHEELS
    e.contact_bad = e.contact_terminal = [1, 2, 3]
    e.legs, e.wheel_channels = [0, 1, 3, 4], [2, 5]
    policy = load_policy(ROOT / "config/policies/p1/policy_meta.yaml")
    policy = replace(policy, torque_limit_nm=(8.0,) * 6)
    robot = load_robot(ROOT / "config/robot.yaml")
    robot = replace(robot, q_default_rad=(0.0,) * 6)
    spawn = asdict(
        SpawnConfig(
            ik_branch="symmetric_five_bar_v1",
            link_lengths_m=(0.12, 0.12, 0.2),
            angle_offsets_rad=(0.0,) * 6,
            hip_pivot_positions_b_m=((0.02, 0.11, -0.025), (0.02, -0.11, -0.025)),
            wheel_radius_m=0.04,
            min_root_height_m=0.14,
            spawn_clearance_m=0.01,
            ordinary_length_m=(0.12, 0.20),
            ordinary_angle_rad=(-0.4, 0.5),
            ordinary_tilt_rad=0.25,
            air_length_m=(0.11, 0.35),
            recovery_length_m=(0.13, 0.24),
            recovery_forward_leg_height_m=(-0.07, -0.02),
            recovery_rear_leg_height_m=(-0.02, 0.04),
            recovery_root_height_m=0.19,
            wheel_angle_rad=(-2, 2),
            wheel_speed_rad_s=(-5, 5),
            leg_speed_rad_s=(-1, 1),
        )
    )
    geometry = {key: spawn.pop(key) for key in ("hip_pivot_positions_b_m", "wheel_radius_m", "spawn_clearance_m")}
    commands = dict(
        segment_probabilities=[0, 1, 0, 0, 0, 0],
        segment_duration_s=[2, 2],
        height_duration_s=[2, 2],
        vx_range_m_s=[4.0, 4.0],
        wz_range_rad_s=[-5.0, 5.0],
        dash_speed_abs_m_s=[2.0, 3.0],
        height_range_m=[0.27, 0.27],
        combined_wz_limit_rad_s=2.0,
        linear_slew_m_s2=2.0,
        angular_slew_rad_s2=10.0,
        heading_kp=2.0,
        heading_max_wz=3.0,
    )
    shared = dict(
        **geometry,
        shu_spawn=spawn,
        # Synthetic fixture only: mirrored axes, nonzero zeros, and two coaxial pin pairs.
        shu_reset_map=dict(
            mode="planar_rear_knee_coaxial_v1",
            canonical_to_asset_sign=[1, -1] * 7,
            canonical_zero_in_asset_rad=[i * 0.019 for i in range(14)],
            auxiliary_joint_names=[],
            fixed_pin_xz_m=[[-0.1, 0.0], [-0.11, 0.0]],
            knee_pivot_xz_m=[[0.0, 0.0], [0.0, 0.0]],
            moving_pin_knee0_xz_m=[[0.03, 0.0], [0.03, 0.0]],
            knee_rotation_sign=[1, -1],
            zero_pin_distance_m=[0.08, 0.08],
            extension_sign=[1, -1],
            slider_safe_range_m=[[-0.1, 0.1], [-0.1, 0.1]],
            hinge_zero_xz_rad=[],
            hinge_asset_sign=[],
        ),
        spawn_clearance_max_m=0.1,
        wheel_rim_sign=(1, -1),
        shu_contact=dict(contact_force_n=3.0, wheel_contact_force_n=2.0, support_force_n=20.0, release_s=0.02),
        termination=dict(contact_force_n=4.0, tilt_rad=0.7, duration_s=0.4, decay_s=2.0),
        numerical_safety=dict(
            joint_velocity_abs_max=200, base_linear_velocity_abs_max=20, base_angular_velocity_abs_max=20
        ),
        airborne=dict(contact_force_n=2.0),
        critic_torque_scale=0.05,
        wheel_speed_limit_rad_s=30.0,
        no_load_speed_rad_s=(100.0,) * 6,
        saturation_torque_nm=(8.0,) * 6,
        spring=dict(
            direction=(1, -1),
            reference_q_m=(0.0, 0.0),
            f0_n=(1.0, 1.0),
            stiffness_n_m=(2.0, 2.0),
            damping_n_s_m=(0.0, 0.0),
            hysteresis_n=(0.0, 0.0),
            force_limit_n=(10.0, 10.0),
        ),
    )
    rewards = dict(
        vx_tol_max=0.5,
        vx_tol_knee=0.5,
        wz_tol_max=0.5,
        wz_tol_knee=0.5,
        vx_error_sigma=2.5,
        wz_error_sigma=2.5,
        height_wide_weight=1.0,
        height_gate_shape=1.0,
    )
    e.training = SimpleNamespace(
        task=stage,
        policy=policy,
        robot=robot,
        shared=shared,
        stage=dict(
            initial_fraction=0.5,
            min_segments=1,
            recovery_probability=0.4,
            error_floor=[0.2] * 3,
            relative_error=[0.1] * 3,
            height_edges_m=[0.05, 0.12, 0.2, 0.3, 0.45],
        ),
        settings=dict(commands=commands, shu_rewards=rewards, episode_length_s=20.0),
        asset=dict(shu_leg_reset_joint_names=LEG_JOINT_ORDER, guide_body_names=["guide"], leg_body_names=["leg"]),
    )
    e.commands_fixed, e.fixed_command = False, None
    e.extras, e.reward_sums = {}, {}
    e.jump = e.scanner = e.mixed_curriculum = e.transition_states = None
    e.sensor_counter = e.history_tick = -1
    e._sim_step_counter = 0
    e.spawn_checked = False
    e.spawn_check_mask = torch.ones(N, dtype=torch.bool)
    e.policy_history = HistoryBuffer(N, "cpu")
    for key in ("episode_length_buf", "action_ticks"):
        setattr(e, key, torch.zeros(N, dtype=torch.long))
    for key in ("airborne", "stuck", "bad_action", "numerical_bad", "obstacle_hit"):
        setattr(e, key, torch.zeros(N, dtype=torch.bool))
    for key in (
        "air_enter",
        "air_exit",
        "air_elapsed",
        "fall_counter",
        "stuck_time",
    ):
        setattr(e, key, torch.zeros(N))
    for key, width in dict(
        raw_action=6,
        previous_action=6,
        torque=6,
        kp=6,
        kd=6,
        contact_peaks=5,
        initial_position=3,
        previous_position=3,
        stuck_start=3,
        mass_ratio=1,
        wheel_material=3,
        spring_bias=2,
        zero_bias=4,
        imu_bias=2,
        voltage_drop=1,
        delayed_sensor=18,
        noise=26,
    ).items():
        setattr(e, key, torch.zeros(N, width))
    e.iteration_raw_action_max = torch.zeros(())
    e.iteration_numerical_terminations = torch.zeros((), dtype=torch.long)
    e.kp.fill_(3.0)
    e.kd.fill_(0.2)
    e.voltage = e.power_scale = torch.ones(N, 1)
    e.output_scale = torch.ones(N, 6)
    e.default_q = torch.zeros(6)
    e.action_scale = torch.tensor(policy.action_scales)
    e.lower = e.target_lower = torch.full((6,), -6.0)
    e.upper = e.target_upper = torch.full((6,), 6.0)
    e.obs_delay, e.act_delay = TransportDelay(), TransportDelay()
    e.shu = shu_cls(e, e.cfg.flat_transfer)
    e.commands = e.shu.commands
    return e


def reset(e, seed):
    return e.reset(seed=seed)[0]


def interval(e, support):
    old = e.policy_history.flat().clone()
    e._pre_physics_step(torch.full((N, 6), 0.25))
    efforts = []
    for _ in range(SUBSTEPS):
        e._sim_step_counter += 1
        e._apply_action()
        efforts.append(e.robot.effort[:, ACTIVE].clone())
        # This is the post-physics contact read for the incremented tick.
        e.contact.data.net_forces_w[:, CONTACT_WHEELS, 2] = 30.0 * support[:, None]
    e.episode_length_buf += 1
    terminated, timeout = e._get_dones()
    reward = e._get_rewards()
    assert not (terminated | timeout).any()
    assert torch.isfinite(reward).all()
    obs = e._get_observations()
    torch.testing.assert_close(obs["history"][:, :-26], old[:, 26:])
    check_obs(e, obs)
    return torch.stack(efforts), obs


def check_obs(e, obs):
    assert set(obs) == {"policy", "critic", "history", "estimator_target"}
    assert obs["history"].shape == (N, 130)
    torch.testing.assert_close(obs["history"][:, -26:], obs["policy"][:, :26])
    assert not obs["policy"][:, 26:].any()
    torch.testing.assert_close(
        obs["policy"][:, :3], e.commands.value * e.raw_action.new_tensor(e.training.policy.command_scale)
    )
    torch.testing.assert_close(obs["policy"][:, 3:4], e.commands.height * e.training.policy.height_scale)
    torch.testing.assert_close(obs["estimator_target"], e.robot.data.root_lin_vel_b)


def checkpoint(e, path):
    torch.save(
        {
            "model_state_dict": DeployedPolicy(e.training.policy).state_dict(),
            "infos": {
                "observation_contract": {"task": e.training.task, "policy": policy_contract(e.training.policy)},
                "shu_curriculum": e.shu.curriculum_state_dict(),
            },
        },
        path,
    )


def test_flat_first_reset_and_landing_checkpoint_gate(runtime, tmp_path):
    flat = make_runtime(runtime, "p1-flat")
    obs = reset(flat, 32)
    check_obs(flat, obs)
    torch.testing.assert_close(obs["history"], obs["policy"][:, :26].repeat(1, 5))
    assert not flat.shu.event.air_birth.any()
    assert flat.shu.event.preset_birth.any() and (~flat.shu.event.preset_birth).any()
    c = flat.commands.value.clone()
    torch.testing.assert_close(flat._get_observations()["policy"], obs["policy"])
    torch.testing.assert_close(flat.commands.value, c)
    interval(flat, ~flat.shu.event.preset_birth)
    source = tmp_path / "flat.pt"
    checkpoint(flat, source)
    args = dict(source_task="p1-flat", commands=flat.training.settings["commands"])
    with pytest.raises(ValueError, match="all flat command buckets"):
        load_landing_transfer(source, flat.training.policy, **args)
    flat.shu.flat.fraction.fill_(1)
    checkpoint(flat, source)
    with pytest.raises(ValueError, match="matching commands"):
        changed = flat.training.settings["commands"] | {"linear_slew_m_s2": 3.0}
        load_landing_transfer(source, flat.training.policy, **(args | {"commands": changed}))
    proof = load_landing_transfer(source, flat.training.policy, **args)
    assert proof["fractions"] == [1.0] * 6
    landing = make_runtime(runtime, "p1-landing", proof)
    assert landing.shu.flat is None
    checkpoint(landing, source)
    assert load_landing_transfer(source, flat.training.policy, **(args | {"source_task": "p1-landing"})) == proof


def test_landing_births_release_touch_and_handoff_keep_history(runtime):
    flat = make_runtime(runtime, "p1-flat")
    flat.shu.flat.fraction.fill_(1)
    e = make_runtime(runtime, "p1-landing", flat.shu.commands.transfer_metadata())
    obs = reset(e, 17)
    check_obs(e, obs)
    torch.testing.assert_close(obs["history"], obs["policy"][:, :26].repeat(1, 5))
    event = e.shu.event
    air, preset = event.air_birth.clone(), event.preset_birth.clone()
    ordinary = ~(air | preset)
    assert air.any() and preset.any() and ordinary.any()
    assert (event.phase[air] == AIR).all() and (event.phase[preset] == RELEASE).all()
    assert (event.phase[ordinary] == DRIVE).all() and (e.shu.band[~air] == -1).all()
    assert (e.shu.band[air] == 0).all() and (e.robot.root[air, 9] == 0).all()
    assert (e.commands.value[air, 0] == 2.5).all()
    assert (e.commands.value[preset] == 0).all() and (e.commands.value[ordinary, 0] > 0).all()
    assert not torch.allclose(obs["estimator_target"][air], e.robot.data.root_lin_vel_w[air])
    # Script settled attitude/height and support, but leave air rows unsupported for one policy interval.
    e.robot.root[:, 2:4] = torch.tensor([0.27, 1.0])
    e.robot.root[:, 4:13] = 0
    e.robot.refresh()
    efforts, _ = interval(e, ~air)
    assert (efforts[:, preset] == 0).all() and (efforts[:, ordinary] != 0).any()
    assert (event.phase[preset] == RELEASE).all() and (event.touch_tick == -1).all()
    efforts, _ = interval(e, torch.ones(N, dtype=torch.bool))
    assert (efforts[:, preset] == 0).all()
    assert (event.phase[preset] == RISE).all() and (event.reward_phase[preset] == RELEASE).all()
    assert (event.takeover_tick[preset] == 10).all()
    assert (event.phase[air] == CATCH).all() and (event.touch_tick[air] == 6).all()
    assert (event.touch_tick[~air] == -1).all()
    assert not e.extras["landing"]["resolved"].any()
    efforts, _ = interval(e, torch.ones(N, dtype=torch.bool))
    assert (efforts[:, preset] != 0).any()
    for _ in range(49):
        _, obs = interval(e, torch.ones(N, dtype=torch.bool))
    assert (event.phase == DRIVE).all()
    report = e.extras["landing"]
    torch.testing.assert_close(report["succeeded"], air)
    torch.testing.assert_close(report["rise_succeeded"], preset)
    assert report["success_count"] == air.sum() and e.shu.drop.events == int(air.sum())
    assert (e.commands.value[preset, 0] > 0).all()
    # A genuine subset reset on the same observation tick clears only that subset.
    kept = obs["history"].clone()
    ids = torch.tensor([0])
    e._reset_idx(ids)
    after = e._get_observations()
    torch.testing.assert_close(after["history"][ids], after["policy"][ids, :26].repeat(1, 5))
    torch.testing.assert_close(after["history"][1:, :-26], kept[1:, :-26])
    torch.testing.assert_close(report["succeeded"], air)  # cloned pre-reset disclosure


def test_same_tick_subset_reset_does_not_reissue_surviving_commands(runtime):
    e = make_runtime(runtime, "p1-flat")
    reset(e, 32)
    _, obs = interval(e, ~e.shu.event.preset_birth)
    survivors = torch.arange(N) != 0
    command = e.commands.value.clone()
    frame = obs["policy"].clone()
    e._reset_idx(torch.tensor([0]))
    repeated = e._get_observations()
    torch.testing.assert_close(e.commands.value[survivors], command[survivors], atol=0, rtol=0)
    torch.testing.assert_close(repeated["policy"][survivors, :4], frame[survivors, :4], atol=0, rtol=0)


def test_landing_report_identifies_all_birth_cohorts(runtime):
    flat = make_runtime(runtime, "p1-flat")
    flat.shu.flat.fraction.fill_(1)
    e = make_runtime(runtime, "p1-landing", flat.shu.commands.transfer_metadata())
    reset(e, 17)
    event = e.shu.event
    interval(e, ~event.air_birth)
    report = e.extras["landing"]
    torch.testing.assert_close(report["air_birth"], event.air_birth)
    torch.testing.assert_close(report["preset_birth"], event.preset_birth)
    assert (~(report["air_birth"] | report["preset_birth"])).any()


def test_landing_fixed_command_evaluation_exercises_specialist_births(runtime):
    flat = make_runtime(runtime, "p1-flat")
    flat.shu.flat.fraction.fill_(1)
    e = make_runtime(runtime, "p1-landing", flat.shu.commands.transfer_metadata())
    e.cfg.evaluation = e.commands_fixed = True
    e.fixed_command = (torch.tensor([4.0, 0.0, 3.0]), 0.27)
    reset(e, 17)
    air, preset = e.shu.event.air_birth, e.shu.event.preset_birth
    assert air.any() and preset.any() and (~(air | preset)).any()
    assert (e.commands.value[air, 0].abs() <= 2.5).all()
    assert (e.commands.value[air, 2].abs() <= pi / 2).all()
    assert (e.commands.value[preset] == 0).all()


def test_invalid_velocity_label_can_be_filtered_by_encoder_update(runtime):
    e = make_runtime(runtime, "p1-flat")
    reset(e, 32)
    e.robot.data.root_lin_vel_b[0] = torch.tensor([torch.inf, torch.nan, 0.0])
    target = e._get_observations()["estimator_target"]
    # VelocityPPO filters a whole row only if at least one component is nonfinite.
    keep = torch.isfinite(target).all(-1)
    assert not keep[0] and keep[1:].all(), target[0]


def test_shu_reset_writes_all_asset_axes_and_actual_slider_rates(runtime, monkeypatch):
    # Capture the canonical sample to independently compare what was actually written to the articulation.
    e = make_runtime(runtime, "p1-flat")
    reset_module = sys.modules[type(e.shu).__module__]
    generate = reset_module.sample_spawn
    samples = []

    def capture(*args):
        state = generate(*args)
        samples.append(state)
        return state

    monkeypatch.setattr(reset_module, "sample_spawn", capture)
    d = e.robot.data
    d.default_joint_pos.fill_(91.0)
    d.default_joint_vel.fill_(-92.0)  # stale defaults must never leak
    reset(e, 73)
    sample = samples[-1]
    config = e.training.shared["shu_reset_map"]
    sign = torch.tensor(config["canonical_to_asset_sign"])
    zeros = torch.tensor(config["canonical_zero_in_asset_rad"])
    # Explicit ID permutation: including passive axes and both independently signed wheels.
    rot = LEG + [ACTIVE[2], ACTIVE[5]]
    expected_q = zeros + sign * torch.cat((sample.leg_q, sample.drive_q[:, [2, 5]]), -1)
    expected_vel = sign * torch.cat((sample.leg_qd, sample.drive_qd[:, [2, 5]]), -1)
    torch.testing.assert_close(d.joint_pos[:, rot], expected_q)
    torch.testing.assert_close(d.joint_vel[:, rot], expected_vel)
    # Synthetic pin distance via law of cosines (not the solver's coordinate decomposition).
    q = sample.leg_q[:, -2:]
    v = sample.leg_qd[:, -2:]
    base = q.new_tensor([0.1, 0.11])
    radius = 0.03
    dist = (base.square() + radius**2 + 2 * base * radius * q.cos()).sqrt()
    ex = q.new_tensor([1.0, -1.0])
    torch.testing.assert_close(d.joint_pos[:, SPRINGS], (dist - 0.08) * ex)
    torch.testing.assert_close(d.joint_vel[:, SPRINGS], -base * radius * q.sin() * v / dist * ex)
    assert (d.joint_vel[:, SPRINGS].abs() > 0).all()
    # The USD hard limit of just ONE selected env is not masked by the generic CAD stroke.
    d.joint_pos_limits[8, SPRINGS[1], 0] = 1.0
    with pytest.raises(ValueError, match="out-of-range"):
        e._reset_idx(torch.tensor([1, 8]))
