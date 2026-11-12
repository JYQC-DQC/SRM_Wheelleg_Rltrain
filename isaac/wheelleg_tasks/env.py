"""SRM closed-chain tasks; DirectRLEnv lifecycle follows Isaac Lab 2.3.2.

The 500 Hz spring/delay/control ordering follows SCUT wheelbipe25_v3,
but all robot parameters and joint mappings come from this project's YAML.
"""

import re

import isaaclab.sim as sim_utils
import numpy as np
import torch
from isaaclab.assets import Articulation, RigidObject, RigidObjectCfg
from isaaclab.envs import DirectRLEnv
from isaaclab.sensors import ContactSensor, RayCaster
from isaaclab.utils.buffers import DelayBuffer
from isaaclab.utils.math import euler_xyz_from_quat, quat_apply, quat_apply_inverse, quat_from_euler_xyz, wrap_to_pi

from wheelleg.commands import Commands, uniform
from wheelleg.curriculum import AirHeightCurriculum, CommandCurriculum, JumpCurriculum
from wheelleg.history import HistoryBuffer
from wheelleg.jump import JumpEvent, tunnel_landing
from wheelleg.landing import FirstLanding
from wheelleg.landing_rewards import FEATURES as LANDING_FEATURES
from wheelleg.landing_rewards import LandingRewards
from wheelleg.observation import OBS_DIM
from wheelleg.randomization import disturbance_progress, perturb_sensors
from wheelleg.rewards import EVENT_TERMS, compute_rewards
from wheelleg.safety import airborne_enabled, nonfinite_pose, numerical_failure
from wheelleg.tasks import TASKS
from wheelleg.tensor_ops import (
    action_targets,
    clipped_component,
    five_bar_joint_angles,
    ground_from_hits,
    motor_torque,
    observation_noise,
    observation_tensor,
    outside_terrain,
    reference_pd_torque,
    rotate_xy,
    smooth_height,
    smooth_height_rate,
    spring_force,
    terrain_half_extent,
)


class WheelLegEnv(DirectRLEnv):
    def __init__(self, cfg, render_mode: str | None = None, **kwargs):
        self.training = cfg.training
        super().__init__(cfg, render_mode, **kwargs)
        t, n, d = self.training, self.num_envs, self.device
        self.family = TASKS[t.task].policy
        self.joints, _ = self.robot.find_joints(list(t.asset["active_joint_names"]), preserve_order=True)
        self.springs, _ = self.robot.find_joints(list(t.asset["spring_joint_names"]), preserve_order=True)
        self.wheels, _ = self.robot.find_bodies(list(t.asset["wheel_body_names"]), preserve_order=True)
        self.base, _ = self.robot.find_bodies(t.asset["base_body_name"])
        self.contact_wheels, _ = self.contact.find_bodies(list(t.asset["wheel_body_names"]), preserve_order=True)
        self.contact_bad, _ = self.contact.find_bodies(list(t.asset["undesired_contact_body_names"]))
        # 改自 SCUT wheelbipe_V14/env.py:134-145: 平地终止名单含机身、云台和导轮，不只是机身。
        self.contact_terminal, _ = self.contact.find_bodies(list(t.asset["termination_contact_body_names"]))
        self.termination_duration_steps = round(t.shared["termination"]["duration_s"] / self.step_dt)
        self.termination_steps = torch.zeros(n, device=d)  # 累计的触地/倾倒步数，可为小数
        # 没有触地/倾倒的每一步，计数回落这么多：满计数要 release_s 才清空。
        self.termination_leak = t.shared["termination"]["duration_s"] / t.shared["termination"]["release_s"]
        if not cfg.evaluation or cfg.evaluation_random_reset:
            self.leg_reset_joints, _ = self.robot.find_joints(
                list(t.shared["leg_reset"]["joint_names"]), preserve_order=True
            )
        if len(self.joints) != 6 or len(self.springs) != 2 or len(self.wheels) != 2 or len(self.base) != 1:
            raise ValueError("USD must resolve exactly 6 active joints, 2 springs, 2 wheels and 1 base")
        self.legs, self.wheel_channels = list(t.robot.leg_indices), list(t.robot.wheel_indices)
        self.default_q = torch.tensor(t.robot.q_default_rad, device=d)
        self.action_scale = torch.tensor(t.policy.action_scales, device=d)
        self.lower = torch.tensor(t.shared["joint_lower_rad"], device=d)
        self.upper = torch.tensor(t.shared["joint_upper_rad"], device=d)
        self.target_lower, self.target_upper = self.lower.clone(), self.upper.clone()
        self.target_lower[self.legs] += t.shared["joint_target_margin_rad"]
        self.target_upper[self.legs] -= t.shared["joint_target_margin_rad"]
        if t.asset.get("reference_preset") != "scut_v14_2":
            self.robot.write_joint_position_limit_to_sim(
                torch.stack((self.lower[self.legs], self.upper[self.legs]), -1).expand(n, -1, -1),
                joint_ids=[self.joints[i] for i in self.legs],
            )
        self.nominal_friction = torch.tensor(t.shared["joint_coulomb_friction"], device=d)
        self.nominal_dynamic_friction = torch.tensor(t.shared["joint_dynamic_friction"], device=d)
        self.nominal_viscous_friction = torch.tensor(t.shared["joint_viscous_friction"], device=d)
        self.kp = torch.tensor(t.policy.kp, dtype=torch.float32, device=d).expand(n, -1).clone()
        self.kd = torch.tensor(t.policy.kd, dtype=torch.float32, device=d).expand(n, -1).clone()
        self.output_scale = torch.ones(n, 6, device=d)
        self.power_scale = torch.ones(n, 1, device=d)
        self.voltage = torch.ones(n, 1, device=d)
        self.voltage_drop = torch.zeros(n, 1, device=d)
        self.spring_bias = torch.zeros(n, 2, device=d)
        self.zero_bias = torch.zeros(n, 4, device=d)
        self.imu_bias = torch.zeros(n, 2, device=d)
        self.torque = torch.zeros(n, 6, device=d)
        self.raw_action = torch.zeros_like(self.torque)
        self.previous_action = torch.zeros_like(self.torque)
        self.previous_previous_action = torch.zeros_like(self.torque)
        self.bad_action = torch.zeros(n, dtype=torch.bool, device=d)
        self.numerical_bad = torch.zeros(n, dtype=torch.bool, device=d)
        self.iteration_raw_action_max = torch.zeros((), device=d)
        self.iteration_numerical_terminations = torch.zeros((), dtype=torch.long, device=d)
        # Generated terrain is a finite tile grid with nothing beyond its border; leaving it is a timeout.
        self.bounded_terrain = self.cfg.terrain.terrain_type == "generator"
        self.out_of_bounds = torch.zeros(n, dtype=torch.bool, device=d)
        self.last_ground = self.terrain.env_origins[:, 2].clone()
        self.spawn_checked = False
        self.spawn_check_mask = torch.ones(n, dtype=torch.bool, device=d)
        self.action_ticks = torch.zeros(n, dtype=torch.long, device=d)
        self.commands = Commands(t, n, d)
        # 改自 SCUT V14/env_cfg.py:1662-1668: 落地及之后的阶段把平滑惩罚降到约 1/5，给落地缓冲留出动作空间。
        self.reward_weights = dict(t.settings["rewards"])
        if self.family == "p1":
            self.reward_weights.update(t.stage["reward_overrides"])
        landing_gate = (
            t.stage["command_curriculum_landing_gate"] if t.task == "p1-landing" and not cfg.evaluation else None
        )
        self.command_curriculum = (
            CommandCurriculum(t.settings["command_curriculum"], landing_gate) if self.family == "p1" else None
        )
        self.jump = JumpEvent(t.stage, n, d) if self.family == "p3" else None
        levels = (
            tuple(h + t.stage["tunnel"]["clearance_margin_m"] for h in t.stage["tunnel"]["height_curriculum_m"])
            if t.task == "p3-tunnel"
            else None
        )
        self.jump_curriculum = JumpCurriculum(t.stage, d, levels) if self.family == "p3" else None
        self.jump_bins = torch.zeros(n, dtype=torch.long, device=d)
        self.command_error_sum = torch.zeros(n, 3, device=d)  # |vx 误差| m/s, |wz 误差| rad/s, |高度误差| m
        self.command_abs_sum = torch.zeros(n, 2, device=d)  # |vx 指令| m/s, |wz 指令| rad/s
        self.command_sample_count = torch.zeros(n, dtype=torch.long, device=d)
        self.airborne = torch.zeros(n, dtype=torch.bool, device=d)
        self.air_enter = torch.zeros(n, device=d)
        self.air_exit = torch.zeros(n, device=d)
        self.air_elapsed = torch.zeros(n, device=d)
        self.recovery_episode = self.airborne.clone()
        self.recovery_start_height = torch.zeros(n, device=d)
        self.stair_signal = torch.zeros(n, device=d)
        self.height_boost_remaining = torch.zeros(n, device=d)
        self.command_limit_remaining = torch.zeros(n, device=d)  # 空中出生后指令限幅的剩余时间, s
        self.obstacle_hit = self.airborne.clone()
        self.obstacle_top_hit = self.airborne.clone()
        self.contact_peaks = torch.zeros(n, len(self.contact.body_names), device=d)
        landing = t.task == "p1-landing" and not cfg.evaluation
        bodies = list(self.contact.body_names)
        guides = (
            [i for i, name in enumerate(bodies) if re.fullmatch(t.stage["landing_reward"]["guide_body_regex"], name)]
            if landing
            else []
        )
        self.first_landing = (
            FirstLanding(n, bodies, self.contact_wheels, guides, t.stage["landing_diagnostics"], d) if landing else None
        )
        self.landing_reward = (
            LandingRewards(n, self.contact_wheels, guides, len(bodies), t.stage["landing_reward"], d)
            if landing
            else None
        )
        # Articulation body ids of the guide wheels, in the contact sensor's order, for their pre-contact speed.
        self.guide_robot_ids = (
            self.robot.find_bodies([bodies[i] for i in guides], preserve_order=True)[0] if guides else []
        )
        # Evaluation keeps the full air_height_offset_m range.
        self.air_height_curriculum = (
            AirHeightCurriculum(t.stage["air_height_offset_m"][0], t.stage["air_height_curriculum"])
            if self.landing_reward is not None
            else None
        )
        self.air_height_offset = torch.zeros(n, device=d)  # sampled air-birth height offset, m; 0 for ground births
        self.commands_fixed = False
        self.fixed_command = None
        self.fixed_jump_height = None
        self.reward_sums = {}
        self.state = {}
        self.initial_position = torch.zeros(n, 3, device=d)
        self.previous_position = torch.zeros_like(self.initial_position)
        self.previous_hip_velocity = torch.zeros(n, len(self.legs), device=d)  # rad/s, last policy step
        self.stuck_start = torch.zeros_like(self.initial_position)
        self.stuck_time = torch.zeros(n, device=d)
        self.stuck = self.airborne.clone()
        self.guidance_scale = torch.ones(n, device=d)
        self.training_iteration_offset = 0
        r = t.shared["randomization"]
        obs_history = (
            t.settings["evaluation"]["observation_delay_steps"] if cfg.evaluation else r["observation_delay_steps"][1]
        )
        act_history = t.settings["evaluation"]["action_delay_steps"] if cfg.evaluation else r["action_delay_steps"][1]
        if cfg.evaluation:
            obs_history = max(obs_history, cfg.evaluation_delay_capacity[0])
            act_history = max(act_history, cfg.evaluation_delay_capacity[1])
        self.obs_delay = DelayBuffer(obs_history, n, d)
        self.act_delay = DelayBuffer(act_history, n, d)
        self.history = None
        if t.policy.history_frames:
            self.history = HistoryBuffer(n, t.policy.history_frames, OBS_DIM, d)
            self.history_tick = -1
        self.noise = observation_noise(t.robot, t.policy, t.shared["observation_noise"], d)
        self.delayed_sensor = torch.zeros(n, 18, device=d)
        self.sensor_counter = -1
        self.push_timer = torch.zeros(n, device=d)
        self.push_remaining = torch.zeros(n, device=d)
        self.push_force = torch.zeros(n, 1, 3, device=d)
        self.push_torque = torch.zeros_like(self.push_force)
        self.collision_timer = torch.zeros(n, device=d)
        self.collision_remaining = torch.zeros(n, device=d)
        self.collision_force = torch.zeros(n, 1, 3, device=d)
        self.disturbance_phase = t.stage["disturbance_phase"]
        self.transition_states = None
        transition = t.settings["transition_reset"]
        if transition["probability"] > 0:
            with np.load(transition["states_npz"], allow_pickle=False) as data:
                if list(data["joint_names"]) != list(self.robot.joint_names):
                    raise ValueError("Transition library must match every USD joint in order")
                self.transition_states = {
                    key: torch.as_tensor(data[key], device=d)
                    for key in ("root_state", "joint_position", "joint_velocity")
                }
        # Static privileged quantities are read after startup randomization.
        masses = self.robot.root_physx_view.get_masses().to(d)
        self.mass_ratio = masses[:, self.base] / self.robot.data.default_mass.to(d)[:, self.base]
        shape_counts = [
            self.robot._physics_sim_view.create_rigid_body_view(path).max_shapes
            for path in self.robot.root_physx_view.link_paths[0]
        ]
        material = self.robot.root_physx_view.get_material_properties().to(d)
        self.wheel_material = torch.cat(
            [material[:, sum(shape_counts[:i]) : sum(shape_counts[: i + 1])].mean(1) for i in self.wheels], -1
        )
        if t.task == "p3-tunnel":
            self.beam_start_x = torch.zeros(n, device=d)
            self.beam_top_z = torch.zeros(n, device=d)
            if set(t.asset["collision_body_names"]) != set(self.robot.body_names):
                raise ValueError("collision_body_names must include every USD robot body")
            self.tunnel_bins = torch.zeros(n, dtype=torch.long, device=d)

    def _setup_scene(self) -> None:
        self.robot = Articulation(self.cfg.robot)
        self.scene.articulations["robot"] = self.robot
        self.contact = ContactSensor(self.cfg.contact_sensor)
        self.scene.sensors["contact"] = self.contact
        self.scanner = None
        if self.cfg.height_scanner is not None:
            self.scanner = RayCaster(self.cfg.height_scanner)
            self.scene.sensors["height"] = self.scanner
        # 改自 SCUT wheelbipe25_v3/env.py:2731-2741: explicit terrain, then one clone.
        self.cfg.terrain.num_envs = self.scene.cfg.num_envs
        self.cfg.terrain.env_spacing = self.scene.cfg.env_spacing
        self.terrain = self.cfg.terrain.class_type(self.cfg.terrain)
        self.obstacle_contacts = {}
        if self.training.task == "p3-tunnel":
            self._spawn_tunnel()
            for name, sensor_cfg in self.cfg.obstacle_contact_sensors.items():
                sensor = ContactSensor(sensor_cfg)
                self.obstacle_contacts[name] = sensor
                self.scene.sensors[f"obstacle_{name}"] = sensor
        self.scene.clone_environments(copy_from_source=False)
        if self.device == "cpu":
            self.scene.filter_collisions(global_prim_paths=["/World/ground"])
        light = sim_utils.DomeLightCfg(intensity=2000.0, color=(0.75, 0.75, 0.75))
        light.func("/World/Light", light)

    def _spawn_tunnel(self) -> None:
        p = self.training.stage["tunnel"]
        x = p["approach_distance_m"]
        box = sim_utils.CuboidCfg(
            size=(p["beam_length_m"], p["lane_width_m"], p["beam_thickness_m"]),
            collision_props=sim_utils.CollisionPropertiesCfg(),
            rigid_props=sim_utils.RigidBodyPropertiesCfg(kinematic_enabled=True, disable_gravity=True),
        )
        self.beam = RigidObject(
            RigidObjectCfg(
                prim_path="/World/envs/env_.*/TunnelBeam",
                spawn=box,
                init_state=RigidObjectCfg.InitialStateCfg(
                    pos=(x + p["beam_length_m"] / 2, 0.0, p["beam_height_m"] - p["beam_thickness_m"] / 2)
                ),
            )
        )
        self.scene.rigid_objects["beam"] = self.beam
        rail = sim_utils.CuboidCfg(
            size=(p["lane_length_m"], p["rail_thickness_m"], p["rail_height_m"]),
            collision_props=sim_utils.CollisionPropertiesCfg(),
        )
        for side, sign in (("Left", 1), ("Right", -1)):
            rail.func(
                f"/World/envs/env_0/Rail{side}",
                rail,
                translation=(x, sign * (p["lane_width_m"] + p["rail_thickness_m"]) / 2, p["rail_height_m"] / 2),
            )

    def _sensors(self) -> torch.Tensor:
        return torch.cat(
            (
                self.robot.data.root_ang_vel_b,
                self.robot.data.projected_gravity_b,
                self.robot.data.joint_pos[:, self.joints],
                self.robot.data.joint_vel[:, self.joints],
            ),
            -1,
        )

    def _sample_sensors(self, tick: int) -> None:
        if self.sensor_counter != tick:
            sensor = perturb_sensors(self._sensors(), self.zero_bias, self.imu_bias, self.legs)
            self.delayed_sensor = self.obs_delay.compute(sensor)
            self.sensor_counter = tick

    def _pre_physics_step(self, actions: torch.Tensor) -> None:
        t = self.training
        maximum = torch.nan_to_num(actions.abs(), nan=float("inf"), posinf=float("inf")).amax()
        self.iteration_raw_action_max = torch.maximum(self.iteration_raw_action_max, maximum)
        self.previous_previous_action.copy_(self.previous_action)
        self.previous_action.copy_(self.raw_action)
        self.bad_action = ~torch.isfinite(actions).all(-1)
        self.raw_action.copy_(torch.where(self.bad_action[:, None], 0.0, actions))
        self.contact_peaks.zero_()
        if self.first_landing is not None:
            self.first_landing.begin_step()
        if self.landing_reward is not None:
            self.landing_reward.begin_step()
        self.obstacle_hit.zero_()
        self.obstacle_top_hit.zero_()
        age = self.episode_length_buf * self.step_dt
        if self.jump is not None:
            was_active = self.jump.active.clone()
            allowed = torch.ones(self.num_envs, dtype=torch.bool, device=self.device)
            if self.training.task == "p3-tunnel":
                p = self.training.stage["tunnel"]
                x = self.robot.data.root_pos_w[:, 0] - self.terrain.env_origins[:, 0]
                allowed = (self.beam_start_x - x <= p["trigger_distance_m"]) & (x < self.beam_start_x)
            tunnel_height = self.beam_top_z + t.stage["tunnel"]["clearance_margin_m"] if t.task == "p3-tunnel" else None
            self.jump.trigger(
                age,
                self.robot.data.root_pos_w[:, 2],
                allowed,
                target_height=tunnel_height,
                require_trigger_time=t.task != "p3-tunnel",
            )
            started = (self.jump.active & ~was_active).nonzero().flatten()
            if t.task == "p3-tunnel":
                self.jump.height[started] = self.beam_top_z[started] + t.stage["tunnel"]["clearance_margin_m"]
                self.jump_bins[started] = self.tunnel_bins[started]
            elif not self.cfg.evaluation and len(started):
                bins, heights = self.jump_curriculum.sample(len(started))
                self.jump_bins[started] = bins
                self.jump.height[started] = heights
            iteration = self.training_iteration_offset + self.common_step_counter / t.settings["rollout_steps"]
            self.guidance_scale = self.jump_curriculum.guidance(self.jump_bins, iteration)
            if self.fixed_jump_height is not None and t.task != "p3-tunnel":
                self.jump.height[self.jump.active & ~was_active] = self.fixed_jump_height
        frozen = self.jump.active if self.jump is not None else torch.zeros_like(self.airborne)
        if self.landing_reward is not None:
            # Hold the birth command through the whole landing window (also after an early success): a new
            # speed/height target inside it would be graded as a landing failure by the diagnostics.
            frozen = frozen | self.landing_reward.hold
        if not self.commands_fixed:
            self.commands.step(self.step_dt, frozen)
        if self.family == "p1" and t.stage["air_reset_probability"] > 0:
            # 改自 SCUT V14/env_cfg.py:1510-1516 (predefined_reset_air command_limits)：空中出生后的一段时间内
            # 限制前向速度和转向指令，落地过程中不要求高速转向。
            limit = self.commands.value.new_tensor(
                [t.stage["air_command_vx_limit_m_s"], float("inf"), t.stage["air_command_wz_limit_rad_s"]]
            )
            limited = (self.command_limit_remaining > 0)[:, None]
            self.commands.value = torch.where(limited, self.commands.value.clamp(-limit, limit), self.commands.value)
            self.command_limit_remaining = (self.command_limit_remaining - self.step_dt).clamp_min(0)
        if self.training.task == "p1-recovery":
            self.commands.value[self.recovery_episode & (age < self.training.stage["rise_duration_s"])] = 0
        if not self.cfg.evaluation:
            self._push()

    def _push(self) -> None:
        r = self.training.shared["randomization"]
        schedule = self.training.settings["disturbance"]
        iteration = self.training_iteration_offset + self.common_step_counter / self.training.settings["rollout_steps"]
        ramp_iteration = iteration - schedule["phase2_start_iteration"] if self.disturbance_phase == 2 else 0
        alpha = disturbance_progress(ramp_iteration, self.disturbance_phase, schedule["ramp_iterations"])
        amplitude = r["push_velocity_m_s"] + alpha * (schedule["final_push_velocity_m_s"] - r["push_velocity_m_s"])
        self.push_timer -= self.step_dt
        ids = (self.push_timer <= 0).nonzero().flatten()
        if len(ids):
            velocity = self.robot.data.root_vel_w[ids].clone()
            velocity[:, :2] += uniform((-amplitude, amplitude), (len(ids), 2), self.device)
            self.robot.write_root_velocity_to_sim(velocity, ids)
            force = uniform((-r["external_force_n"], r["external_force_n"]), (len(ids), 1, 3), self.device)
            torque = uniform((-r["external_torque_nm"], r["external_torque_nm"]), (len(ids), 1, 3), self.device)
            self.push_force[ids], self.push_torque[ids] = force, torque
            self.push_remaining[ids] = r["external_wrench_duration_s"]
            self.push_timer[ids] = uniform(r["push_interval_s"], (len(ids),), self.device)
        if self.disturbance_phase == 2:
            self.collision_timer -= self.step_dt
            collision_ids = (self.collision_timer <= 0).nonzero().flatten()
            count = len(collision_ids)
            if count:
                force_range = schedule["collision_force_range_n"]
                magnitude = force_range[0] + alpha * (force_range[1] - force_range[0])
                angle = uniform((-torch.pi, torch.pi), (count,), self.device)
                lateral = torch.rand(count, device=self.device) < schedule["lateral_probability"]
                sign = torch.where(torch.rand(count, device=self.device) < 0.5, -1.0, 1.0)
                angle = torch.where(lateral, sign * torch.pi / 2, angle)
                self.collision_force[collision_ids, 0, 0] = magnitude * angle.cos()
                self.collision_force[collision_ids, 0, 1] = magnitude * angle.sin()
                self.collision_remaining[collision_ids] = schedule["collision_duration_s"]
                self.collision_timer[collision_ids] = uniform(schedule["collision_interval_s"], (count,), self.device)

    def _apply_wrench(self) -> None:
        # 改自 SCUT manager/mdp/isaaclab/events.py:438-488: local-frame force/torque sampling.
        # Isaac 2.3.2 events.py:1038-1043 and wrench_composer.py:221 verify the new API.
        # Scale the last partial physics step to preserve the configured impulse.
        push_fraction = (self.push_remaining / self.physics_dt).clamp(0, 1)[:, None, None]
        collision_fraction = (self.collision_remaining / self.physics_dt).clamp(0, 1)[:, None, None]
        self.robot.permanent_wrench_composer.set_forces_and_torques(
            forces=self.push_force * push_fraction + self.collision_force * collision_fraction,
            torques=self.push_torque * push_fraction,
            body_ids=self.base,
            is_global=False,
        )
        self.push_remaining = (self.push_remaining - self.physics_dt).clamp_min(0)
        self.collision_remaining = (self.collision_remaining - self.physics_dt).clamp_min(0)

    def _apply_action(self) -> None:
        self._apply_wrench()
        self._sample_sensors(self._sim_step_counter - 1)
        self._record_contacts(self._sim_step_counter - 1)
        t = self.training
        delayed = self.act_delay.compute(self.raw_action)
        delayed = torch.where((self.action_ticks < self.act_delay.time_lags)[:, None], 0.0, delayed)
        self.action_ticks += 1
        q_ref, qd_ref = action_targets(
            delayed,
            self.default_q,
            self.action_scale,
            t.policy.action_clip,
            self.legs,
            self.wheel_channels,
            self.target_lower,
            self.target_upper,
            t.shared["wheel_speed_limit_rad_s"],
        )
        q = self.robot.data.joint_pos[:, self.joints]
        qd = self.robot.data.joint_vel[:, self.joints]
        fraction = (self.episode_length_buf / self.max_episode_length)[:, None]
        hip_limit_scale = 1 - self.voltage_drop * fraction
        limit = q.new_tensor(t.policy.torque_limit_nm).expand_as(q).clone()
        limit[:, self.wheel_channels] *= self.power_scale
        limit[:, self.legs] *= hip_limit_scale
        if t.asset.get("reference_preset") == "scut_v14_2":
            commanded_torque = reference_pd_torque(
                q, qd, q_ref, qd_ref, self.kp, self.kd, limit, self.output_scale, self.wheel_channels
            )
        else:
            speed = q.new_tensor(t.shared["no_load_speed_rad_s"]) * self.voltage
            commanded_torque = motor_torque(
                q,
                qd,
                q_ref,
                qd_ref,
                self.kp,
                self.kd,
                limit,
                q.new_tensor(t.shared["saturation_torque_nm"]),
                speed,
                self.output_scale,
                self.wheel_channels,
            )
        self.torque = commanded_torque
        if t.task == "p1-recovery":
            disabled = self.recovery_episode & (self.episode_length_buf * self.step_dt < t.stage["zero_torque_s"])
            self.torque[disabled] = 0
        self.torque[self.bad_action] = 0
        self.robot.set_joint_effort_target(self.torque, joint_ids=self.joints)
        force = spring_force(
            self.robot.data.joint_pos[:, self.springs],
            self.robot.data.joint_vel[:, self.springs],
            t.shared["spring"],
            self.spring_bias,
            t.robot.spring_stroke_m,
        )
        self.robot.set_joint_effort_target(force, joint_ids=self.springs)

    def _record_contacts(self, tick: int) -> None:
        forces = torch.linalg.vector_norm(self.contact.data.net_forces_w_history, dim=-1).amax(1)
        self.contact_peaks = torch.maximum(self.contact_peaks, forces)
        if self.first_landing is not None or self.landing_reward is not None:
            # Current normal force, independently shared by reward and diagnostic observers.
            current = self.contact.data.net_forces_w.norm(dim=-1)
        if self.first_landing is not None:
            self.first_landing.sample_contacts(tick, self.physics_dt, current, self.torque[:, self.legs])
        if self.landing_reward is not None:
            guide_down = -self.robot.data.body_lin_vel_w[:, self.guide_robot_ids, 2]
            self.landing_reward.sample(tick, self.physics_dt, current, guide_down)
        if self.training.task != "p3-tunnel":
            return
        threshold = self.training.shared["termination"]["contact_force_n"]
        # contact_sensor_data.py:102-111: (N, one sensing body, three filters, XYZ).
        for sensor in self.obstacle_contacts.values():  # Fixed body count, never a loop over environments.
            filtered = sensor.data.force_matrix_w[:, 0]
            self.obstacle_hit |= (filtered.norm(dim=-1) > threshold).any(-1)
            # A horizontal beam's top applies an upward normal force on the robot.
            self.obstacle_top_hit |= filtered[:, 0, 2] > threshold

    def _measure(self) -> dict:
        t = self.training
        data = self.robot.data
        q = data.root_quat_w
        roll, pitch, yaw = euler_xyz_from_quat(q)
        roll, pitch = wrap_to_pi(roll), wrap_to_pi(pitch)
        wheels_w = data.body_pos_w[:, self.wheels]
        relative = wheels_w - data.root_pos_w[:, None]
        wheel_b = quat_apply_inverse(q[:, None].expand(-1, 2, -1).reshape(-1, 4), relative.reshape(-1, 3)).reshape(
            -1, 2, 3
        )
        wheel_vel = quat_apply_inverse(
            q[:, None].expand(-1, 2, -1).reshape(-1, 4), data.body_lin_vel_w[:, self.wheels].reshape(-1, 3)
        ).reshape(-1, 2, 3)
        ground = self.terrain.env_origins[:, 2]
        if self.scanner is not None:
            ground = ground_from_hits(self.scanner.data.ray_hits_w[:, :, 2], self.last_ground)
            # In-place: buffers reassigned under the rollout's inference_mode cannot be reset outside it.
            self.last_ground.copy_(ground)
        base_height = data.root_pos_w[:, 2] - ground
        clearance = wheels_w[:, :, 2] - ground[:, None] - t.shared["wheel_radius_m"]
        force = self.contact_peaks[:, self.contact_wheels]
        contact = force > t.shared["airborne"]["contact_force_n"]
        height_target = self.commands.height[:, 0]
        # Height-reference rate for the vertical velocity term. The stairs boost is a step change with no rate.
        height_rate = self.commands.height_rate
        if t.task in ("p1-stairs", "p1-recovery"):
            height_target = height_target + t.stage["step_height_boost_m"] * (self.height_boost_remaining > 0)
            height_target = height_target.clamp(max=t.settings["commands"]["height_range_m"][1])
        age = self.episode_length_buf * self.step_dt
        if t.task == "p1-recovery":
            rise = smooth_height(self.recovery_start_height, height_target, age, t.stage["rise_duration_s"])
            rise_rate = smooth_height_rate(
                self.recovery_start_height, height_target, height_rate, age, t.stage["rise_duration_s"]
            )
            height_target = torch.where(self.recovery_episode, rise, height_target)
            height_rate = torch.where(self.recovery_episode, rise_rate, height_rate)
        # 改自 SCUT wheelbipe25_v3/env.py:3573-3582: 死区内的指令按 0 跟踪，避免同时要求“跟小速度”和“别动”。
        deadzone = t.settings["reward_parameters"]["stand_deadzone"]
        tracked = torch.where(self.commands.value.abs() < deadzone, 0.0, self.commands.value)
        # World velocity in the yaw-only heading frame. The body-frame vx * cos(pitch) used before (SCUT V14) leaks
        # vertical velocity into forward speed whenever the body pitches, which bobbing in phase with pitch exploits.
        heading_velocity = rotate_xy(data.root_lin_vel_w[:, :2], -yaw)
        linear_error = heading_velocity[:, 0] - tracked[:, 0]
        angular_error = data.root_ang_vel_b[:, 2] - tracked[:, 2]
        height_error = base_height - height_target
        leg_vector = wheel_b - wheel_b.new_tensor(t.shared["hip_pivot_positions_b_m"])
        second_difference = self.raw_action - 2 * self.previous_action + self.previous_previous_action
        return dict(
            tracked_command=tracked[:, [0, 2]],
            leg_action_second_difference=second_difference[:, self.legs],
            wheel_action_second_difference=second_difference[:, self.wheel_channels],
            velocity=data.root_lin_vel_b,
            velocity_w=data.root_lin_vel_w,
            heading_velocity=heading_velocity,
            height_target_rate=height_rate,
            angular_velocity=data.root_ang_vel_b,
            gravity=data.projected_gravity_b,
            roll=roll,
            pitch=pitch,
            yaw=yaw,
            base_height=base_height,
            ground=ground,
            wheel_position_w=wheels_w,
            wheel_position_b=wheel_b,
            # Wheel x in the yaw-only heading frame: zero means directly below the base along gravity.
            wheel_heading_x=relative[:, :, 0] * yaw.cos()[:, None] + relative[:, :, 1] * yaw.sin()[:, None],
            wheel_velocity_b=wheel_vel,
            clearance=clearance,
            wheel_contact=contact,
            wheel_force=force,
            linear_error=linear_error,
            angular_error=angular_error,
            height_error=height_error,
            undesired_force=self.contact_peaks[:, self.contact_bad],
            leg_length=leg_vector[:, :, [0, 2]].norm(dim=-1),
            leg_angle=torch.atan2(leg_vector[:, :, 0], -leg_vector[:, :, 2]),
            torque=self.torque,
            wheel_torque=self.torque[:, self.wheel_channels],
            wheel_velocity=data.joint_vel[:, self.joints][:, self.wheel_channels],
            hip_torque=self.torque[:, self.legs],
            hip_velocity=data.joint_vel[:, self.joints][:, self.legs],
            action=self.raw_action,
            previous_action=self.previous_action,
        )

    def _get_dones(self) -> tuple[torch.Tensor, torch.Tensor]:
        self.numerical_bad = numerical_failure(
            self.robot.data.joint_vel,
            self.robot.data.root_lin_vel_b,
            self.robot.data.root_ang_vel_b,
            self.training.shared["numerical_safety"],
        ) | nonfinite_pose(self.robot.data.root_pos_w, self.robot.data.root_quat_w, self.robot.data.joint_pos)
        self.iteration_numerical_terminations += self.numerical_bad.sum()
        self._record_contacts(self._sim_step_counter)
        s = self._measure()
        t, dt = self.training, self.step_dt
        if airborne_enabled(t.task):
            air = t.shared["airborne"]
            candidate = ~s["wheel_contact"].any(-1) & (s["clearance"].amin(-1) > air["wheel_clearance_m"])
            candidate &= s["base_height"] > air["base_height_m"]
            self.air_enter = torch.where(candidate, self.air_enter + dt, 0)
            self.air_exit = torch.where(s["wheel_contact"].any(-1), self.air_exit + dt, 0)
            self.airborne |= self.air_enter >= air["enter_duration_s"]
            self.air_elapsed = torch.where(self.airborne, self.air_elapsed + dt, 0)
            self.airborne &= (self.air_exit < air["exit_duration_s"]) & (self.air_elapsed < air["max_duration_s"])
            tilt_limit = torch.where(
                self.airborne, t.shared["termination"]["airborne_tilt_rad"], t.shared["termination"]["tilt_rad"]
            )
        else:
            self.airborne.zero_()
            tilt_limit = t.shared["termination"]["tilt_rad"]
        tilt_fail = (s["roll"].abs() > tilt_limit) | (s["pitch"].abs() > tilt_limit)
        body_hit = (self.contact_peaks[:, self.contact_terminal] > t.shared["termination"]["contact_force_n"]).any(-1)
        # 改自 SCUT wheelbipe25_v3/env.py:4863-4895, 5017-5022: 倾倒/触地累计满 duration_s 才终止，
        # 否则随机出生的瞬时触地会让回合立刻结束；数值异常仍立即终止。
        # 与 SCUT 不同：条件中断时计数慢慢回落而不是清零。清零时策略靠“碰一下抬一下”
        # 在约 40% 的时间里撑地也从不终止（standup2 的曲线）。
        physical = (tilt_fail | body_hit) & ~self.recovery_episode
        # 随机腿姿出生后先落地，起立窗口内不按倾倒/触地终止；触地惩罚照常累计。所有任务共用。
        if self.landing_reward is not None:
            # PPO randomizes the episode clock; landing grace uses real physics age instead.
            birth_age = (self._sim_step_counter - self.landing_reward.born) * self.physics_dt
            physical &= birth_age >= t.shared["leg_reset"]["settle_s"]
        else:
            physical &= self.episode_length_buf * dt >= t.shared["leg_reset"]["settle_s"]
        self.termination_steps = torch.where(
            physical, self.termination_steps + 1, (self.termination_steps - self.termination_leak).clamp_min(0)
        )
        terminated = (self.termination_steps >= self.termination_duration_steps) | self.bad_action | self.numerical_bad
        timeout = self.episode_length_buf >= self.max_episode_length - 1
        if t.task == "p1-recovery":
            timeout |= self.recovery_episode & (self.episode_length_buf * dt >= t.stage["recovery_timeout_s"])
        if self.bounded_terrain:
            # Timeout, not termination: no penalty, and PPO bootstraps the value at the edge.
            terrain = t.stage["terrain"]
            self.out_of_bounds.copy_(
                outside_terrain(
                    self.robot.data.root_pos_w[:, :2], terrain_half_extent(terrain), terrain["boundary_margin_m"]
                )
            )
            timeout |= self.out_of_bounds
        if self.jump is not None:
            stable = (s["roll"].abs() < t.stage["landing_tilt_rad"]) & (s["pitch"].abs() < t.stage["landing_tilt_rad"])
            stable &= (s["linear_error"].abs() < t.stage["landing_speed_error_m_s"]) & ~terminated
            stable &= self.jump.apex_z - self.jump.start_z >= self.jump.height - t.stage["height_tolerance_m"]
            valid = torch.ones_like(stable)
            if t.task == "p3-tunnel":
                p = t.stage["tunnel"]
                end = self.terrain.env_origins[:, 0] + self.beam_start_x + p["beam_length_m"]
                valid = tunnel_landing(
                    s["wheel_position_w"],
                    t.shared["wheel_radius_m"],
                    self.robot.data.body_pos_w,
                    end,
                    self.terrain.env_origins[:, 2],
                    p["landing_margin_m"],
                    p["clearance_margin_m"],
                )
            self.jump.update(
                dt,
                self.episode_length_buf * dt,
                self.robot.data.root_pos_w[:, 2],
                s["velocity_w"][:, 2],
                s["wheel_contact"],
                stable,
                valid,
                self.obstacle_hit,
            )
            if not self.cfg.evaluation:
                finished = self.jump.finished.nonzero().flatten()
                iteration = self.training_iteration_offset + self.common_step_counter / t.settings["rollout_steps"]
                self.jump_curriculum.record(self.jump_bins[finished], self.jump.landing_pulse[finished], iteration)
        if self.first_landing is not None:
            self.first_landing.update(
                self._sim_step_counter,
                self.physics_dt,
                dt,
                s,
                terminated,
                timeout,
                self.numerical_bad | self.bad_action,
            )
        if self.landing_reward is not None:
            self.landing_reward.update(
                self._sim_step_counter,
                self.physics_dt,
                dt,
                s,
                terminated,
                timeout,
                self.numerical_bad | self.bad_action,
            )
            resolved = self.landing_reward.resolved
            offsets, succeeded = self.air_height_offset[resolved], self.landing_reward.succeeded[resolved]
            # The command gate counts the newest height band only, so speed cannot outrun the hardest landings.
            # The band is read before the height curriculum may promote on this same batch; after a promotion the
            # gate's open window held the old band only, so it is discarded and refilled from the new band.
            newest = offsets >= self.air_height_curriculum.band_floor
            self.command_curriculum.record_landing(succeeded[newest])
            if self.air_height_curriculum.record(offsets, succeeded):
                self.command_curriculum.discard_landing()
        s["terminated"] = terminated
        self.state = s
        return terminated, timeout

    def _get_rewards(self) -> torch.Tensor:
        t, s = self.training, self.state
        n = self.num_envs
        one = torch.ones(n, device=self.device)
        relaxed = torch.zeros_like(self.airborne)
        if self.landing_reward is not None:
            flight = self.landing_reward.flight()
            relaxed = flight | self.landing_reward.cushion()
        # The command curriculum grades driving under commands; flight and cushion steps, where the tracking
        # rewards are off, are left out of its averages.
        counted = ~relaxed[:, None]
        errors = torch.stack((s["linear_error"].abs(), s["angular_error"].abs(), s["height_error"].abs()), -1)
        self.command_error_sum += torch.where(counted, errors, 0.0)
        self.command_abs_sum += torch.where(counted, s["tracked_command"].abs(), 0.0)
        self.command_sample_count += (~relaxed).long()
        # Hip acceleration by policy-step differencing (100 Hz): physics-rate joint_acc is dominated by contact and
        # PD jitter at 500 Hz, while leg bobbing sits at a few Hz. Read once per step here, never in _measure.
        s["hip_acceleration"] = (s["hip_velocity"] - self.previous_hip_velocity) / self.step_dt
        self.previous_hip_velocity.copy_(s["hip_velocity"])
        s.update(
            tracking_mask=one,
            height_mask=one,
            height_gate=one,
            # 改自 SCUT V14/env_cfg.py:1549-1562 (airborne reward_scales)：腾空时关闭俯仰惩罚和高度平方惩罚，
            # 空中机身高度和俯仰不由策略决定，继续罚只会干扰落地动作。
            ground_mask=(~self.airborne).float(),
            requested_speed=self.commands.value[:, :2].norm(dim=-1),
            airborne=self.airborne,
            contact_multiplier=torch.where(self.airborne, 25.0, 1.0),
            termination_multiplier=torch.where(self.airborne, 6.0, 1.0),
        )
        if self.family in ("p1", "p2"):
            # 改自 SCUT wheelbipe25_v3/env.py:3842-3866 (linear_band)：高度没到位时压低速度/转速跟踪奖励，
            # 防止趴低追速度。与 SCUT env.py:3887-3893 一致，跟踪奖励和误差惩罚都乘门控。
            # P1 的全部阶段和 P2 共用；腾空时高度误差没有意义，门控置 1。
            p = t.settings["reward_parameters"]
            band = p["height_gate_zero_error_m"] - p["height_gate_full_error_m"]
            gate = ((p["height_gate_zero_error_m"] - s["height_error"].abs()) / band).clamp(0, 1)
            # Landing uses its own flight/cushion phases, not the airborne classifier's exit dwell.
            free = relaxed if self.landing_reward is not None else self.airborne
            s["height_gate"] = torch.where(free, 1.0, gate)
        if self.family == "p2":
            actual = rotate_xy(s["velocity_w"][:, :2], -self.commands.reference_yaw)
            target = self.commands.translation
            s["translation_error"] = actual - target
            s["requested_speed"] = target.norm(dim=-1)
            s["speed_error"] = actual.norm(dim=-1) - s["requested_speed"]
            s["heading_error"] = wrap_to_pi(
                torch.atan2(actual[:, 1], actual[:, 0]) - torch.atan2(target[:, 1], target[:, 0])
            )
            s["linear_error"] = s["translation_error"].norm(dim=-1)
        if self.jump is not None:
            s["jump"] = self.jump
            s["jump_ref"] = self.jump.references(
                s["velocity_w"][:, 2], s["clearance"].amin(-1), t.shared["gravity_m_s2"]
            )
            s["height_mask"] = (~self.jump.active).float()
            s["tracking_mask"] = torch.where(self.jump.active, 1.0, t.stage["non_event_tracking_scale"])
            s["guidance_scale"] = self.guidance_scale
        if t.task == "p1-landing":
            # Stable penalty scales cannot depend on an airborne-classifier dwell timer: the heavier contact cost is
            # gated by the landing window (birth to first contact + window_s), where the cushioning collisions occur.
            s["contact_multiplier"] = (
                torch.where(self.landing_reward.hold, t.stage["landing_reward"]["contact_multiplier"], 1.0)
                if self.landing_reward is not None
                else one
            )
            s["termination_multiplier"] = one
        if self.landing_reward is not None:
            # Flight and the one-shot cushion after first touch relax tracking/height targets; attitude rewards stay on.
            # Pitch penalty is off only in flight (SCUT V14/env_cfg.py:1551), not while cushioning on the wheels.
            # Still on the airborne classifier: air_joint_limits and the airborne tilt termination limit.
            s["tracking_mask"] = (~relaxed).float()
            s["height_mask"] = (~relaxed).float()
            s["ground_mask"] = (~flight).float()
        weights = self.reward_weights
        if t.task == "p1-flat":
            # 宽核高度奖励在起立阶段提供梯度；站稳后它接近常数，按训练轮数线性退到 final_weight，
            # 保留一个下限是因为每回合仍从随机腿姿起立。
            anneal = t.settings["height_wide_anneal"]
            iteration = self.training_iteration_offset + self.common_step_counter / t.settings["rollout_steps"]
            progress = min(max((iteration - anneal["start_iteration"]) / anneal["ramp_iterations"], 0.0), 1.0)
            initial = weights["track_height_wide"]
            weights = {**weights, "track_height_wide": initial + progress * (anneal["final_weight"] - initial)}
        terms = compute_rewards(s, t.settings["reward_parameters"], weights, self.step_dt, t.settings["reward_clip"])
        if t.task in ("p1-landing", "p1-stairs", "p1-recovery", "p3-jump", "p3-tunnel"):
            ar = t.settings["air_rewards"]
            terms["air_wheel_torque"] = (
                ar["wheel_torque"]
                * self.step_dt
                * torch.exp(-s["wheel_torque"].square().sum(-1) / ar["wheel_torque_sigma"])
                * self.airborne
            )
            excess = (self.lower[self.legs] - self.robot.data.joint_pos[:, self.joints][:, self.legs]).clamp_min(0)
            excess += (self.robot.data.joint_pos[:, self.joints][:, self.legs] - self.upper[self.legs]).clamp_min(0)
            terms["air_joint_limits"] = ar["joint_limit"] * self.step_dt * excess.sum(-1) * self.airborne
            terms["air_wheel_center"] = (
                ar["wheel_center"]
                * self.step_dt
                * torch.exp(-s["wheel_position_b"][:, :, 0].square().sum(-1) / ar["wheel_center_sigma"])
                * self.airborne
            )
            wheel_speed_error = s["wheel_velocity"] * t.shared["wheel_radius_m"] - s["velocity"][:, 0:1]
            terms["air_wheel_alignment"] = (
                ar["wheel_speed_alignment"] * self.step_dt * wheel_speed_error.square().sum(-1) * self.airborne
            )
        if t.task == "p1-landing":
            # Remove the old +20/s and +10/s airborne bounties and unconstrained wheel-speed loss.
            for key in ("air_wheel_torque", "air_wheel_center", "air_wheel_alignment"):
                terms[key] = torch.zeros_like(one)
            if self.landing_reward is not None:
                terms["stand_still"] = torch.where(relaxed, 0.0, terms["stand_still"])
                terms.update(self.landing_reward.terms(s, t.shared["wheel_radius_m"], self.step_dt))
        if t.task in ("p1-stairs", "p1-recovery"):
            position = self.robot.data.root_pos_w
            delta_b = quat_apply_inverse(self.robot.data.root_quat_w, position - self.previous_position)
            terms["progress"] = t.stage["progress_weight"] * delta_b[:, 0] * self.commands.value[:, 0].sign()
            self.stuck_time += self.step_dt
            ready = self.stuck_time >= t.stage["stuck_window_s"]
            moved = (position - self.stuck_start)[:, :2].norm(dim=-1)
            self.stuck = torch.where(
                ready, (moved < t.stage["stuck_distance_m"]) & (self.commands.value[:, 0].abs() > 0.1), self.stuck
            )
            self.stuck_start[ready] = position[ready]
            self.stuck_time[ready] = 0
            terms["stuck"] = t.stage["stuck_weight"] * self.step_dt * self.stuck
            terms["stair_impact"] = t.stage["impact_weight"] * self.step_dt * s["hip_torque"].square().amax(-1)
        if t.task == "p3-tunnel":
            p = t.stage["tunnel"]
            terms["tunnel_crossing"] = p["crossing_weight"] * self.jump.landing_pulse
            terms["obstacle_contact"] = p["obstacle_contact_weight"] * self.step_dt * self.obstacle_hit
            terms["obstacle_top_contact"] = p["top_contact_weight"] * self.step_dt * self.obstacle_top_hit
        self.previous_position.copy_(self.robot.data.root_pos_w)
        for name, value in terms.items():
            terms[name] = (
                value if name in EVENT_TERMS else value.clamp(-t.settings["reward_clip"], t.settings["reward_clip"])
            )
            # SCUT wheelbipe25_v3/env.py:4007-4018: mask with where, never NaN * 0.
            if t.task == "p1-landing" and name == "termination":
                # Numerical escape must still pay the existing, finite termination cost.
                terms[name] = torch.where(self.numerical_bad, float(t.settings["rewards"]["termination"]), terms[name])
            elif t.task == "p1-landing" and name == "landing_outcome":
                pass  # The event module already emits a finite cost, once, only for active events.
            else:
                terms[name] = torch.where(self.numerical_bad, 0.0, terms[name])
            if name not in self.reward_sums:
                self.reward_sums[name] = torch.zeros(n, device=self.device)
            self.reward_sums[name] += terms[name]
        # Preserve pre-reset measurements for evaluation; reset environments cannot contaminate metrics.
        self.extras["evaluation"] = {
            "errors": torch.stack((s["linear_error"], s["angular_error"], s["height_error"]), -1).detach().clone(),
            "failed": s["terminated"].detach().clone(),
            "position": self.robot.data.root_pos_w.detach().clone(),
            "jump_success": self.jump.landing_pulse.clone()
            if self.jump is not None
            else torch.zeros_like(self.airborne),
        }
        if self.cfg.evaluation and t.task == "p1-flat":
            # DirectRLEnv.step resets before returning: capture diagnostics before that reset.
            self.extras["evaluation"].update(
                attitude=torch.stack((s["roll"], s["pitch"], s["yaw"]), -1).detach().clone(),
                velocity=s["velocity"].detach().clone(),
                angular_velocity=s["angular_velocity"].detach().clone(),
                height=s["base_height"].detach().clone(),
                contact_force=s["undesired_force"].amax(-1).detach().clone(),
                wheel_force=s["wheel_force"].detach().clone(),
                torque=self.torque.detach().clone(),
                joint_velocity=self.robot.data.joint_vel[:, self.joints].detach().clone(),
                numerical_failure=(self.numerical_bad | self.bad_action).detach().clone(),
            )
        return torch.stack(list(terms.values())).sum(0)

    def _get_observations(self) -> dict[str, torch.Tensor]:
        self._sample_sensors(self._sim_step_counter)
        s = self._measure()
        t = self.training
        if t.task in ("p1-stairs", "p1-recovery"):
            hits = self.scanner.data.ray_hits_w
            hit = torch.isfinite(hits).all(-1)
            hits = torch.where(hit[..., None], hits, self.robot.data.root_pos_w[:, None])
            points_b = quat_apply_inverse(
                self.robot.data.root_quat_w[:, None].expand(-1, hits.shape[1], -1).reshape(-1, 4),
                (hits - self.robot.data.root_pos_w[:, None]).reshape(-1, 3),
            ).reshape(self.num_envs, -1, 3)
            ahead = hit & (points_b[:, :, 0] > 0) & (points_b[:, :, 0] < t.stage["stair_detection_distance_m"])
            rise = hits[:, :, 2] - s["ground"][:, None]
            detected = (ahead & (rise >= t.stage["stair_detection_height_m"])).any(-1)
            if not self.cfg.evaluation:
                detected = (
                    detected & (torch.rand(self.num_envs, device=self.device) >= t.stage["stair_false_negative"])
                ) | (torch.rand(self.num_envs, device=self.device) < t.stage["stair_false_positive"])
            self.stair_signal = detected.float()
            close = hit & (points_b[:, :, 0] > 0) & (points_b[:, :, 0] < t.stage["step_height_trigger_distance_m"])
            trigger = (close & (rise >= t.stage["stair_detection_height_m"])).any(-1)
            self.height_boost_remaining = torch.where(
                trigger, t.stage["step_height_hold_s"], (self.height_boost_remaining - self.step_dt).clamp_min(0)
            )
        active = self.jump.active if self.jump is not None else torch.zeros_like(self.airborne)
        jump_height = self.jump.height if self.jump is not None else torch.zeros_like(self.air_enter)
        phase = self.jump.phase if self.jump is not None else torch.zeros_like(self.air_enter)
        recovering = self.recovery_episode.clone()
        if t.task == "p1-recovery":
            recovering &= self.episode_length_buf * self.step_dt < t.stage["rise_duration_s"]
        mode = self.commands.mode(s["yaw"], self.stair_signal, recovering, active, jump_height, phase)
        sensor = self._sensors()

        def make_fields(values):
            height = self.commands.height
            if t.task in ("p1-stairs", "p1-recovery"):
                height = (height + t.stage["step_height_boost_m"] * (self.height_boost_remaining > 0)[:, None]).clamp(
                    max=t.settings["commands"]["height_range_m"][1]
                )
            return dict(
                command=self.commands.value,
                height=height,
                angular_velocity=values[:, :3],
                gravity=values[:, 3:6],
                joint_position=values[:, 6:12],
                joint_velocity=values[:, 12:18],
                previous_action=self.raw_action,
                mode=mode,
            )

        clean = observation_tensor(t.robot, t.policy, make_fields(sensor))
        noise = None if self.cfg.evaluation else (2 * torch.rand_like(clean) - 1) * self.noise
        actor = observation_tensor(t.robot, t.policy, make_fields(self.delayed_sensor), noise=noise)
        clips = dict(t.robot.observation_clip)

        def component(name, value, scale=1.0):
            return clipped_component(value, clips[name], scale)

        privileged = torch.cat(
            (
                component("kp", self.kp),
                component("kd", self.kd),
                component("torque", self.torque, t.shared["critic_torque_scale"]),
                component("delay_steps", self.obs_delay.time_lags[:, None]),
                component("delay_steps", self.act_delay.time_lags[:, None]),
                component("wheel_linear_velocity", s["wheel_velocity_b"].flatten(1)),
                component("wheel_contact", s["wheel_contact"].float()),
                component("mass_ratio", self.mass_ratio),
                component("material", self.wheel_material),
                component("spring_force", self.spring_bias),
                component("voltage_scale", self.voltage),
                component("power_scale", self.power_scale),
            ),
            -1,
        )
        critic = torch.cat(
            (
                clean,
                component("base_linear_velocity", s["velocity"]),
                component("base_height", s["base_height"][:, None]),
                privileged,
                component("command_error", torch.stack((s["linear_error"], s["angular_error"], s["height_error"]), -1)),
            ),
            -1,
        )
        if self.scanner is not None:
            hit_z = self.scanner.data.ray_hits_w[:, :, 2]
            hit_z = torch.where(torch.isfinite(hit_z), hit_z, s["ground"][:, None])
            scan = self.robot.data.root_pos_w[:, 2:3] - hit_z
            critic = torch.cat((critic, component("height_scan", scan)), -1)
        if t.task == "p1-landing":
            # Landing payouts depend on event history; evaluation has no event and keeps the same width with zeros.
            event = (
                self.landing_reward.features()
                if self.landing_reward is not None
                else critic.new_zeros(self.num_envs, LANDING_FEATURES)
            )
            critic = torch.cat((critic, event), -1)
        observations = {"policy": actor, "critic": critic}
        if self.history is not None:
            # Evaluation re-reads observations within a policy step after rewriting commands; only a new step appends.
            self.history.update(actor, new_step=self._sim_step_counter != self.history_tick)
            self.history_tick = self._sim_step_counter
            observations["history"] = self.history.flat()
            # Training label only (simulator truth); never part of the deployed inputs.
            observations["estimator_target"] = torch.cat((s["velocity"], s["wheel_contact"].float()), -1)
        return observations

    def reset(self, seed: int | None = None, options: dict | None = None):
        # DirectRLEnv.reset (api_reference/direct_env.py:313-331) calls sim.forward before returning.
        result = super().reset(seed=seed, options=options)
        if not self.spawn_checked:
            clearance = (
                self.robot.data.body_pos_w[:, self.wheels, 2]
                - self.terrain.env_origins[:, 2:3]
                - self.training.shared["wheel_radius_m"]
            )
            values = clearance[self.spawn_check_mask]
            maximum = self.training.shared["spawn_clearance_max_m"]
            bad = ~torch.isfinite(values) | (values > maximum)
            if bad.any():
                measured = values[bad].detach().cpu().tolist()
                raise ValueError(
                    f"Initial wheel-bottom clearance exceeds {maximum} m or is non-finite: {measured[:16]} m"
                )
            self.spawn_checked = True
        return result

    def _reset_idx(self, env_ids: torch.Tensor) -> None:
        t = self.training
        curriculum_log = {}
        if self.family == "p1" and not self.cfg.evaluation:
            ran = self.command_sample_count[env_ids] > 0
            completed = env_ids[ran]
            if len(completed):
                curriculum = t.settings["command_curriculum"]
                count = self.command_sample_count[completed, None]
                error = self.command_error_sum[completed] / count
                # 允许误差 = 固定底限 + 比例 × 平均指令幅值。原地不动时误差等于指令幅值，无法靠不动升级；
                # 高度误差把“趴在地上滑行”排除在成功之外。
                allowed = curriculum["relative_error"] * self.command_abs_sum[completed] / count + error.new_tensor(
                    [curriculum["velocity_error_threshold_m_s"], curriculum["yaw_error_threshold_rad_s"]]
                )
                checks = torch.stack(
                    (
                        error[:, 0] < allowed[:, 0],
                        error[:, 1] < allowed[:, 1],
                        error[:, 2] < curriculum["height_error_threshold_m"],
                        ~self.reset_terminated[completed],
                    ),
                    -1,
                )  # (K, 4): 速度、转速、高度、未终止
                passed = checks.all(-1)
                self.commands.command_fraction = self.command_curriculum.record(passed)
                # 课程停住时要能看出是哪个条件没过；数值是本步结束的回合里的通过比例。
                rates = checks.float().mean(0)
                curriculum_log = {
                    "Curriculum/pass_rate": passed.float().mean(),
                    "Curriculum/pass_velocity": rates[0],
                    "Curriculum/pass_yaw_rate": rates[1],
                    "Curriculum/pass_height": rates[2],
                    "Curriculum/pass_survived": rates[3],
                }
        self.command_error_sum[env_ids] = 0
        self.command_abs_sum[env_ids] = 0
        self.command_sample_count[env_ids] = 0
        if self.jump is not None and not self.cfg.evaluation:
            interrupted = env_ids[self.jump.active[env_ids]]
            iteration = self.training_iteration_offset + self.common_step_counter / t.settings["rollout_steps"]
            self.jump_curriculum.record(
                self.jump_bins[interrupted],
                torch.zeros(len(interrupted), dtype=torch.bool, device=self.device),
                iteration,
            )
        if self.reward_sums:
            self.extras["log"] = curriculum_log | {
                f"Episode_Reward/{k}": v[env_ids].mean() / self.max_episode_length_s
                for k, v in self.reward_sums.items()
            }
            if self.bounded_terrain:
                self.extras["log"]["Episode_Termination/out_of_bounds"] = self.out_of_bounds[env_ids].float().mean()
            for value in self.reward_sums.values():
                value[env_ids] = 0
        if t.task in ("p1-stairs", "p1-recovery") and not self.cfg.evaluation:
            distance = (self.robot.data.root_pos_w[env_ids] - self.initial_position[env_ids])[:, :2].norm(dim=-1)
            size = t.stage["terrain"]["tile_size_m"][0]
            # Episodes cut at the grid edge keep their level: the distance reached there says nothing about the tile.
            ran = (self.episode_length_buf[env_ids] > 0) & ~self.out_of_bounds[env_ids]
            self.terrain.update_env_origins(env_ids, (distance > size / 2) & ran, (distance < size / 4) & ran)
        super()._reset_idx(env_ids)
        # Before spawn sampling: landing air births take their forward speed from the new command.
        self.commands.reset(env_ids)
        n = len(env_ids)
        self.spawn_check_mask[env_ids] = True
        root = self.robot.data.default_root_state[env_ids].clone()
        root[:, :3] += self.terrain.env_origins[env_ids]
        q, qd = self.robot.data.default_joint_pos[env_ids].clone(), self.robot.data.default_joint_vel[env_ids].clone()
        self.recovery_episode[env_ids] = False
        air = torch.zeros(n, dtype=torch.bool, device=self.device)
        if self.cfg.evaluation and not self.cfg.evaluation_random_reset:
            # 评测保持默认零位出生；空中出生只给高度和前向速度，评测口径不变。
            if self.family == "p1" and t.stage["air_reset_probability"] > 0:
                air = torch.rand(n, device=self.device) < t.stage["air_reset_probability"]
                self.spawn_check_mask[env_ids[air]] = False
                root[:, 2] += uniform(t.stage["air_height_offset_m"], (n,), self.device) * air
                root[:, 7] = torch.where(air, uniform(t.stage["air_vx_range_m_s"], (n,), self.device), root[:, 7])
        else:
            # 改自 SCUT wheelbipe25_v3/env.py:5380-5541 和 V14/env_cfg.py:342-353: 随机腿长/摆角加机身倾角出生，
            # 否则每回合都从腿全折叠的零位开始，策略学不到起立。两条腿独立采样；所有任务的训练回合共用。
            r, stage = t.shared["leg_reset"], t.stage
            length = uniform(r["length_range_m"], (n, 2), self.device)  # 髋轴中点到轮心, m
            angle = uniform(r["angle_range_rad"], (n, 2), self.device)  # 正值时轮心在髋轴后方, rad
            tilt = uniform((-r["root_tilt_rad"], r["root_tilt_rad"]), (n, 2), self.device)  # roll, pitch, rad
            air = torch.zeros(n, dtype=torch.bool, device=self.device)
            recover = air.clone()
            if self.family == "p1" and stage["air_reset_probability"] > 0:
                # 改自 SCUT V14/env_cfg.py:1488-1521 (predefined_reset_air)：空中出生同时随机机身倾角、
                # 横向速度、角速度和腿姿，而不只是高度和前向速度。
                air = torch.rand(n, device=self.device) < stage["air_reset_probability"]
                length = torch.where(
                    air[:, None], uniform(stage["air_leg_length_range_m"], (n, 2), self.device), length
                )
                angle = torch.where(air[:, None], uniform(stage["air_leg_angle_range_rad"], (n, 2), self.device), angle)
                air_tilt = uniform((-1.0, 1.0), (n, 2), self.device) * tilt.new_tensor(stage["air_tilt_rad"])
                tilt = torch.where(air[:, None], air_tilt, tilt)
            if t.task == "p1-recovery":
                # 改自 SCUT V14/cfg_utils.py:198-226 和 wheelbipe25_v3/env.py:5465-5523 (predefined_reset_ground)：
                # 腿接近水平、机身水平地从 recovery_root_height_m 落下，趴在地上再起身。不再需要接管状态库。
                recover = torch.rand(n, device=self.device) < stage["recovery_probability"]
                air &= ~recover
                forward = torch.rand(n, 2, device=self.device) < stage["recovery_forward_probability"]
                drop = torch.where(
                    forward,
                    uniform(stage["recovery_forward_leg_height_m"], (n, 2), self.device),
                    uniform(stage["recovery_leg_height_m"], (n, 2), self.device),
                )  # 轮心低于髋轴的距离 m；负值表示轮心高于髋轴
                lying_length = uniform(stage["recovery_leg_length_m"], (n, 2), self.device)
                lying_angle = torch.where(forward, -1.0, 1.0) * torch.arccos(drop / lying_length)
                length = torch.where(recover[:, None], lying_length, length)
                angle = torch.where(recover[:, None], lying_angle, angle)
                tilt = torch.where(recover[:, None], 0.0, tilt)
            if self.family == "p1" and stage["air_reset_probability"] > 0:
                self.command_limit_remaining[env_ids] = stage["air_command_limit_s"] * air
                if t.task == "p1-landing":
                    # The landing starts at a command already reached; it stays frozen through the landing window.
                    limit = root.new_tensor(
                        [stage["air_command_vx_limit_m_s"], float("inf"), stage["air_command_wz_limit_rad_s"]]
                    )
                    held = self.commands.target[env_ids].clamp(-limit, limit)
                    self.commands.value[env_ids] = torch.where(air[:, None], held, self.commands.value[env_ids])
            q[:, self.leg_reset_joints] = five_bar_joint_angles(
                length, angle, r["link_lengths_m"], r["angle_offsets_rad"]
            )
            yaw = uniform((-torch.pi, torch.pi), (n,), self.device)
            root[:, 3:7] = quat_from_euler_xyz(tilt[:, 0], tilt[:, 1], yaw)
            wheel_b = root.new_tensor(t.shared["hip_pivot_positions_b_m"]).expand(n, 2, 3).clone()
            wheel_b[:, :, 0] -= length * angle.sin()
            wheel_b[:, :, 2] -= length * angle.cos()
            wheel_z = quat_apply(root[:, None, 3:7].expand(-1, 2, -1).reshape(-1, 4), wheel_b.reshape(-1, 3)).reshape(
                n, 2, 3
            )[:, :, 2]
            # 较低的轮底离地 spawn_clearance_m；min_root_height_m 防止短腿大摆角时机身和连杆出生在地面以下。
            height = (t.shared["wheel_radius_m"] + t.shared["spawn_clearance_m"] - wheel_z.amin(-1)).clamp_min(
                r["min_root_height_m"]
            )
            self.air_height_offset[env_ids] = 0
            if air.any():
                bounds = stage["air_height_offset_m"]
                if self.air_height_curriculum is not None:
                    bounds = (bounds[0], self.air_height_curriculum.upper)
                offset = uniform(bounds, (n,), self.device) * air
                self.air_height_offset[env_ids] = offset
                height = height + offset
                velocity_b = torch.zeros(n, 3, device=self.device)  # 航向系（只含 yaw）线速度 m/s
                velocity_b[:, 0] = uniform(stage["air_vx_range_m_s"], (n,), self.device)
                if t.task == "p1-landing":
                    # Driving off a ledge: the actor sees no body velocity, so most births fly at the command speed.
                    follow = torch.rand(n, device=self.device) < stage["air_vx_command_probability"]
                    matched = self.commands.value[env_ids, 0] + stage["air_vx_command_noise_m_s"] * torch.randn(
                        n, device=self.device
                    )
                    velocity_b[:, 0] = torch.where(follow, matched.clamp(*stage["air_vx_range_m_s"]), velocity_b[:, 0])
                velocity_b[:, 1] = uniform(stage["air_vy_range_m_s"], (n,), self.device)
                rate_b = uniform((-1.0, 1.0), (n, 3), self.device) * tilt.new_tensor(
                    stage["air_angular_velocity_rad_s"]
                )  # 机体系 roll/pitch/yaw 角速度 rad/s
                # SCUT wheelbipe25_v3/env.py:5186-5207: linear velocity in the yaw-only frame, so the sampled
                # roll/pitch do not turn forward speed into a vertical one.
                heading = quat_from_euler_xyz(torch.zeros_like(yaw), torch.zeros_like(yaw), yaw)
                root[:, 7:10] = torch.where(air[:, None], quat_apply(heading, velocity_b), root[:, 7:10])
                root[:, 10:13] = torch.where(air[:, None], quat_apply(root[:, 3:7], rate_b), root[:, 10:13])
            if recover.any():
                height = torch.where(recover, stage["recovery_root_height_m"], height)
            root[:, 2] = self.terrain.env_origins[env_ids, 2] + height
            self.recovery_episode[env_ids] = recover
            self.spawn_check_mask[env_ids] = False
        if self.transition_states is not None and not self.cfg.evaluation:
            selected = torch.rand(n, device=self.device) < t.settings["transition_reset"]["probability"]
            rows = torch.randint(len(self.transition_states["root_state"]), (int(selected.sum()),), device=self.device)
            root[selected] = self.transition_states["root_state"][rows]
            root[selected, :3] += self.terrain.env_origins[env_ids[selected]]
            q[selected] = self.transition_states["joint_position"][rows]
            qd[selected] = self.transition_states["joint_velocity"][rows]
            self.recovery_episode[env_ids[selected]] = False
            air[selected] = False  # library states are not deliberately sampled air-reset events
        if self.first_landing is not None:
            self.first_landing.reset(env_ids, air, self._sim_step_counter)
        if self.landing_reward is not None:
            self.landing_reward.reset(env_ids, air, self._sim_step_counter)
        if self.jump is not None:
            self.jump.reset(env_ids)
        if t.task == "p3-tunnel":
            self._reset_tunnel(env_ids)
            yaw = uniform(t.stage["tunnel"]["initial_yaw_range_rad"], (n,), self.device)
            root[:, 3:7] = quat_from_euler_xyz(torch.zeros_like(yaw), torch.zeros_like(yaw), yaw)
        self.robot.write_root_pose_to_sim(root[:, :7], env_ids)
        self.robot.write_root_velocity_to_sim(root[:, 7:], env_ids)
        self.robot.write_joint_state_to_sim(q, qd, env_ids=env_ids)
        self.previous_hip_velocity[env_ids] = qd[:, self.joints][:, self.legs]
        self.initial_position[env_ids] = root[:, :3]
        self.out_of_bounds[env_ids] = False
        self.last_ground[env_ids] = self.terrain.env_origins[env_ids, 2]
        self.previous_position[env_ids] = root[:, :3]
        self.stuck_start[env_ids] = root[:, :3]
        self.recovery_start_height[env_ids] = root[:, 2] - self.terrain.env_origins[env_ids, 2]
        if self.commands_fixed:
            self.commands.value[env_ids] = self.fixed_command[0]
            self.commands.height[env_ids] = self.fixed_command[1]
        for value in (
            self.airborne,
            self.air_enter,
            self.air_exit,
            self.air_elapsed,
            self.stuck,
            self.stuck_time,
            self.raw_action,
            self.previous_action,
            self.previous_previous_action,
            self.termination_steps,
            self.bad_action,
            self.torque,
            self.contact_peaks,
            self.action_ticks,
            self.height_boost_remaining,
        ):
            value[env_ids] = 0
        self._randomize_controls(env_ids)
        self.obs_delay.reset(env_ids)
        self.act_delay.reset(env_ids)
        if self.history is not None:
            self.history.reset(env_ids)
        self.delayed_sensor[env_ids] = perturb_sensors(self._sensors(), self.zero_bias, self.imu_bias, self.legs)[
            env_ids
        ]

    def _reset_tunnel(self, ids: torch.Tensor) -> None:
        p = self.training.stage["tunnel"]
        count = len(ids)
        if self.cfg.evaluation:
            self.beam_start_x[ids] = p["approach_distance_m"]
            self.beam_top_z[ids] = p["beam_height_m"]
            self.tunnel_bins[ids] = 0
        else:
            self.beam_start_x[ids] = p["approach_distance_m"] + uniform(p["approach_jitter_m"], (count,), self.device)
            levels = self.raw_action.new_tensor(p["height_curriculum_m"])
            rows = torch.randint(min(self.jump_curriculum.maximum_level + 1, len(levels)), (count,), device=self.device)
            self.tunnel_bins[ids] = rows
            self.beam_top_z[ids] = levels[rows] + uniform(p["height_jitter_m"], (count,), self.device)
        pose = self.beam.data.default_root_state[ids, :7].clone()
        pose[:, :3] = self.terrain.env_origins[ids]
        pose[:, 0] += self.beam_start_x[ids] + p["beam_length_m"] / 2
        pose[:, 2] += self.beam_top_z[ids] - p["beam_thickness_m"] / 2
        # Decide once at episode reset, not after the last requested jump is consumed.
        no_jump = self.jump.remaining[ids] == 0
        pose[no_jump] = pose.new_tensor(p["no_jump_beam_pose"])
        pose[no_jump, :3] += self.terrain.env_origins[ids[no_jump]]
        self.beam.write_root_pose_to_sim(pose, ids)

    def _randomize_controls(self, ids: torch.Tensor) -> None:
        t, n, d = self.training, len(ids), self.device
        r = t.shared["randomization"]
        self.kp[ids] = torch.tensor(t.policy.kp, dtype=torch.float32, device=d)
        self.kd[ids] = torch.tensor(t.policy.kd, dtype=torch.float32, device=d)
        self.output_scale[ids] = 1
        self.power_scale[ids] = 1
        self.voltage[ids] = 1
        self.voltage_drop[ids] = 0
        self.spring_bias[ids] = 0
        self.zero_bias[ids] = 0
        self.imu_bias[ids] = 0
        self.collision_remaining[ids] = 0
        self.collision_force[ids] = 0
        self.push_remaining[ids] = 0
        self.push_force[ids] = 0
        self.push_torque[ids] = 0
        if self.cfg.evaluation:
            self.obs_delay.set_time_lag(t.settings["evaluation"]["observation_delay_steps"], ids)
            self.act_delay.set_time_lag(t.settings["evaluation"]["action_delay_steps"], ids)
            return
        static_friction = self.nominal_friction.expand(n, -1).clone()
        dynamic_friction = self.nominal_dynamic_friction.expand(n, -1).clone()
        viscous_friction = self.nominal_viscous_friction.expand(n, -1).clone()
        static_friction[:, self.legs] += uniform(r["hip_static_friction_add"], (n, 4), d)
        dynamic_friction[:, self.legs] += uniform(r["hip_dynamic_friction_add"], (n, 4), d)
        viscous_friction[:, self.legs] += uniform(r["hip_viscous_friction_add"], (n, 4), d)
        static_friction[:, self.wheel_channels] += uniform(r["wheel_static_friction_add"], (n, 2), d)
        dynamic_friction = torch.minimum(dynamic_friction, static_friction)
        # PhysX checks static >= dynamic on EACH setter, including the previous reset values.
        self.robot.write_joint_dynamic_friction_coefficient_to_sim(
            torch.zeros_like(dynamic_friction), joint_ids=self.joints, env_ids=ids
        )
        self.robot.write_joint_friction_coefficient_to_sim(static_friction, joint_ids=self.joints, env_ids=ids)
        self.robot.write_joint_dynamic_friction_coefficient_to_sim(dynamic_friction, joint_ids=self.joints, env_ids=ids)
        self.robot.write_joint_viscous_friction_coefficient_to_sim(viscous_friction, joint_ids=self.joints, env_ids=ids)
        self.kp[ids] *= uniform(r["gain_scale"], (n, 6), d)
        self.kd[ids] *= uniform(r["gain_scale"], (n, 6), d)
        scale = torch.ones(n, 6, device=d)
        scale[:, self.legs] = uniform(r["hip_torque_scale"], (n, 4), d)
        scale[:, self.wheel_channels] = uniform(r["wheel_torque_scale"], (n, 2), d)
        self.output_scale[ids] = scale
        self.power_scale[ids] = uniform(r["wheel_power_scale"], (n, 1), d)
        self.voltage[ids] = uniform(r["voltage_scale"], (n, 1), d)
        self.voltage_drop[ids] = uniform(r["episode_voltage_drop"], (n, 1), d)
        self.spring_bias[ids] = uniform(r["spring_bias_n"], (n, 2), d)
        self.zero_bias[ids] = uniform(r["joint_zero_bias_rad"], (n, 4), d)
        self.imu_bias[ids] = uniform(r["imu_roll_pitch_bias_rad"], (n, 2), d)
        self.collision_timer[ids] = uniform(self.training.settings["disturbance"]["collision_interval_s"], (n,), d)
        self.push_timer[ids] = uniform(r["push_interval_s"], (n,), d)
        for buffer, bounds in (
            (self.obs_delay, r["observation_delay_steps"]),
            (self.act_delay, r["action_delay_steps"]),
        ):
            buffer.set_time_lag(
                torch.randint(bounds[0], bounds[1] + 1, (n,), device=d, dtype=buffer.time_lags.dtype), ids
            )
