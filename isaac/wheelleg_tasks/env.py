"""SRM closed-chain tasks; DirectRLEnv lifecycle follows Isaac Lab 2.3.2.

The 500 Hz spring/delay/control ordering follows SCUT wheelbipe25_v3,
but all robot parameters and joint mappings come from this project's YAML.
"""

import isaaclab.sim as sim_utils
import torch
from isaaclab.assets import Articulation, RigidObject, RigidObjectCfg
from isaaclab.envs import DirectRLEnv
from isaaclab.sensors import ContactSensor, RayCaster
from isaaclab.utils.buffers import DelayBuffer
from isaaclab.utils.math import euler_xyz_from_quat, quat_apply_inverse, quat_from_euler_xyz, wrap_to_pi

from wheelleg.commands import Commands, uniform
from wheelleg.history import HistoryBuffer
from wheelleg.jump import JumpEvent, TrainingJumpButton, collision_bounds_w, tunnel_geometry
from wheelleg.randomization import disturbance_progress, perturb_sensors
from wheelleg.rewards import compute_rewards
from wheelleg.safety import airborne_enabled, leaky_termination, numerical_failure
from wheelleg.shu_rewards import RELEASE, joint_costs
from wheelleg.shu_terrain import MixedTerrainRuntime, route_progress_and_stuck
from wheelleg.tasks import TASKS
from wheelleg.tensor_ops import (
    action_targets,
    clipped_component,
    motor_torque,
    observation_noise,
    observation_tensor,
    rotate_xy,
    spring_force,
)

from .shu import ShuP1


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
        self.contact_base, _ = self.contact.find_bodies(t.asset["base_body_name"])
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
        self.robot.write_joint_position_limit_to_sim(
            torch.stack((self.lower[self.legs], self.upper[self.legs]), -1).expand(n, -1, -1),
            joint_ids=[self.joints[i] for i in self.legs],
        )
        self.nominal_friction = torch.tensor(t.shared["joint_coulomb_friction"], device=d)
        self.nominal_dynamic_friction = torch.tensor(t.shared["joint_dynamic_friction"], device=d)
        self.nominal_viscous_friction = torch.tensor(t.shared["joint_viscous_friction"], device=d)
        self.kp = torch.tensor(t.policy.kp, device=d).expand(n, -1).clone()
        self.kd = torch.tensor(t.policy.kd, device=d).expand(n, -1).clone()
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
        self.bad_action = torch.zeros(n, dtype=torch.bool, device=d)
        self.numerical_bad = torch.zeros(n, dtype=torch.bool, device=d)
        self.iteration_raw_action_max = torch.zeros((), device=d)
        self.iteration_numerical_terminations = torch.zeros((), dtype=torch.long, device=d)
        self.spawn_checked = False
        self.spawn_check_mask = torch.ones(n, dtype=torch.bool, device=d)
        self.action_ticks = torch.zeros(n, dtype=torch.long, device=d)
        self.contact_terminal, _ = self.contact.find_bodies(list(t.asset["termination_contact_body_names"]))
        self.fall_counter = torch.zeros(n, device=d)
        self.policy_history = HistoryBuffer(n, d)
        self.history_tick = -1
        self.shu = ShuP1(self, cfg.flat_transfer) if self.family == "p1" else None
        if self.shu is None:
            self.second_action = torch.zeros_like(self.raw_action)
            self.prev_qd = torch.zeros_like(self.raw_action)
        simulate_jump_button = cfg.simulate_jump_button
        self.commands = (
            self.shu.commands if self.shu is not None else Commands(t, n, d, sample_jump_motion=simulate_jump_button)
        )
        self.training_jump_button = TrainingJumpButton(t.stage, n, d) if simulate_jump_button else None
        self._operator_jump_height = None
        self.command_curriculum = None
        self.jump = JumpEvent(t.stage, n, d) if self.family == "p3" else None
        self.mixed_curriculum = MixedTerrainRuntime(t.stage["terrain"], n, d) if t.task == "p1-stairs" else None
        self.airborne = torch.zeros(n, dtype=torch.bool, device=d)
        self.air_enter = torch.zeros(n, device=d)
        self.air_exit = torch.zeros(n, device=d)
        self.air_elapsed = torch.zeros(n, device=d)
        self.obstacle_hit = self.airborne.clone()
        self.contact_peaks = torch.zeros(n, len(self.contact.body_names), device=d)
        self.commands_fixed = False
        self.fixed_command = None
        self.reward_sums = {}
        self.state = {}
        self.initial_position = torch.zeros(n, 3, device=d)
        self.previous_position = torch.zeros_like(self.initial_position)
        self.stuck_start = torch.zeros_like(self.initial_position)
        self.stuck_time = torch.zeros(n, device=d)
        self.stuck = self.airborne.clone()
        self._stage_command_tick = -1
        self._jump_sample_tick = -1
        self.jump_blocked = self.obstacle_hit.clone()
        self.training_iteration_offset = 0
        r = t.shared["randomization"]
        obs_history = (
            t.settings["evaluation"]["observation_delay_steps"] if cfg.evaluation else r["observation_delay_steps"][1]
        )
        act_history = t.settings["evaluation"]["action_delay_steps"] if cfg.evaluation else r["action_delay_steps"][1]
        self.obs_delay = DelayBuffer(obs_history, n, d)
        self.act_delay = DelayBuffer(act_history, n, d)
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
        self.disturbance_phase = t.stage["disturbance_phase"] if self.family == "p1" else None
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
            self.beam_top_z = torch.zeros(n, device=d)
            bounds = t.stage["tunnel"]["collision_bounds_m"]
            if set(bounds) != set(self.robot.body_names) or set(t.asset["collision_body_names"]) != set(bounds):
                raise ValueError("P3 tunnel bounds and collision_body_names must cover every USD robot body")
            self.tunnel_collision_bounds = torch.tensor([bounds[name] for name in self.robot.body_names], device=d)
            box = self.tunnel_collision_bounds
            if box.shape != (self.robot.num_bodies, 2, 3) or not (
                torch.isfinite(box).all() and (box[:, 1] > box[:, 0]).all()
            ):
                raise ValueError("P3 tunnel collision_bounds_m must contain finite, ordered link-local XYZ bounds")

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
        beam_start = p["beam_offset_from_entrance_m"]
        box = sim_utils.CuboidCfg(
            size=(p["beam_length_m"], p["beam_width_m"], p["beam_height_m"] - p["beam_bottom_m"]),
            collision_props=sim_utils.CollisionPropertiesCfg(),
            rigid_props=sim_utils.RigidBodyPropertiesCfg(kinematic_enabled=True, disable_gravity=True),
        )
        self.beam = RigidObject(
            RigidObjectCfg(
                prim_path="/World/envs/env_.*/TunnelBeam",
                spawn=box,
                init_state=RigidObjectCfg.InitialStateCfg(
                    pos=(beam_start + p["beam_length_m"] / 2, 0.0, (p["beam_height_m"] + p["beam_bottom_m"]) / 2)
                ),
            )
        )
        self.scene.rigid_objects["beam"] = self.beam

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
        maximum = torch.nan_to_num(actions.abs(), nan=float("inf"), posinf=float("inf")).amax()
        self.iteration_raw_action_max = torch.maximum(self.iteration_raw_action_max, maximum)
        if self.shu is not None:
            self.shu.second_action.copy_(self.previous_action)
            self.shu.event.begin_step()
        else:
            self.second_action.copy_(self.previous_action)
            self.prev_qd.copy_(self.robot.data.joint_vel[:, self.joints])
        self.previous_action.copy_(self.raw_action)
        self.bad_action = ~torch.isfinite(actions).all(-1)
        self.raw_action.copy_(torch.where(self.bad_action[:, None], 0.0, actions))
        self.contact_peaks.zero_()
        self.obstacle_hit.zero_()
        if self.jump is not None:
            self.jump_interval = self.jump.active.clone()
            self.jump.begin_step()
            self.jump_blocked.zero_()
            # _apply_action can see the previous interval's last sensor sample before stepping.
            self._jump_sample_tick = self._sim_step_counter
        elif self.shu is not None and not self.cfg.evaluation:
            self._push()

    def set_jump_button(
        self, button_down: torch.Tensor, *, target_height_m: float | None = None
    ) -> dict[str, torch.Tensor]:
        """Submit a same-device (N,) bool input level before observing the next action.

        The caller supplies press and release; there is no time/distance trigger.
        Compute actions from the returned observation, not the pre-button observation.
        """
        if self.jump is None:
            raise ValueError("jump button is available only on P3")
        if (
            button_down.shape != self.jump.active.shape
            or button_down.dtype != torch.bool
            or button_down.device != self.jump.active.device
        ):
            raise ValueError("jump button must be a same-device (N,) bool tensor")
        if self.training_jump_button is not None:
            raise ValueError("manual jump input cannot be mixed with the training button schedule")
        if target_height_m is not None:
            lower, upper = self.training.stage["height_range_m"]
            if not lower <= target_height_m <= upper:
                raise ValueError("jump target height is outside the configured rise range")
        self._operator_jump_height = target_height_m
        self.jump.request(button_down)
        return self._get_observations()

    def _prepare_stage_command(self) -> None:
        new_tick = self._stage_command_tick != self._sim_step_counter
        if self.jump is not None:
            if new_tick:
                self.jump.advance_command(self.step_dt)
            if new_tick and self.training_jump_button is not None:
                self.jump.request(self.training_jump_button.step(self.episode_length_buf * self.step_dt))
            requested = self.jump.requested.clone()
            if requested.any():
                t = self.training
                before = self._tunnel_geometry()[0] if t.task == "p3-tunnel" else None
                self.jump.trigger(self.robot.data.root_pos_w[:, 2], self._operator_jump_height, before_beam=before)
                fz = self.contact.data.net_forces_w[:, self.contact_wheels, 2]
                self.jump.had_support |= requested & (fz > t.shared["airborne"]["contact_force_n"]).any(-1)
        if not new_tick:
            return
        self._stage_command_tick = self._sim_step_counter
        if self.jump is not None:
            self.commands.step(self.step_dt, self.jump.command_m > 0)
        elif not self.commands_fixed:
            self.commands.step(self.step_dt, torch.zeros_like(self.airborne))

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
        if self.shu is not None:
            self.torque[self.shu.event.phase == RELEASE] = 0
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
        if self.shu is not None:
            self.shu.sample(tick)
        forces = torch.linalg.vector_norm(self.contact.data.net_forces_w_history, dim=-1).amax(1)
        self.contact_peaks = torch.maximum(self.contact_peaks, forces)
        if self.jump is None or tick <= self._jump_sample_tick:
            return
        self._jump_sample_tick = tick
        self._sample_jump()

    def _sample_jump(self) -> None:
        t = self.training
        data = self.robot.data
        force = self.contact.data.net_forces_w
        wheel_contact = force[:, self.contact_wheels, 2] > t.shared["airborne"]["contact_force_n"]
        ground_z = self.terrain.env_origins[:, 2:3]
        clearance = data.body_pos_w[:, self.wheels, 2] - ground_z - t.shared["wheel_radius_m"]
        roll, pitch, _ = euler_xyz_from_quat(data.root_quat_w)
        limit = t.stage["landing_tilt_rad"]
        stable = (wrap_to_pi(roll).abs() < limit) & (wrap_to_pi(pitch).abs() < limit)
        threshold = t.shared["termination"]["contact_force_n"]
        stable &= ~(force[:, self.contact_terminal].norm(dim=-1) > threshold).any(-1)
        valid = torch.ones_like(stable)
        over = blocked = None
        if t.task == "p3-tunnel":
            # Each filtered sensor covers one robot body and one beam per environment.
            for sensor in self.obstacle_contacts.values():
                filtered = sensor.data.force_matrix_w[:, 0]
                self.obstacle_hit |= (filtered.norm(dim=-1) > threshold).any(-1)
            _, over, blocked, self.tunnel_past = self._tunnel_geometry()
            self.jump_blocked |= blocked
            ground = clearance.abs() <= t.stage["tunnel"]["ground_tolerance_m"]
            valid = self.tunnel_past & (ground | ~wheel_contact).all(-1)
        self.jump.sample(
            self.physics_dt,
            data.root_pos_w[:, 2],
            data.root_lin_vel_w[:, 2],
            wheel_contact,
            stable,
            valid,
            self.obstacle_hit,
            wheel_clearance=clearance.amin(-1),
            takeoff_clearance_m=t.shared["airborne"]["wheel_clearance_m"],
            above_beam=over,
            blocked_at_beam=blocked,
        )

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
            ground = self.scanner.data.ray_hits_w[:, :, 2].median(-1).values
        base_height = data.root_pos_w[:, 2] - ground
        clearance = wheels_w[:, :, 2] - ground[:, None] - t.shared["wheel_radius_m"]
        force = self.contact_peaks[:, self.contact_wheels]
        contact = force > t.shared["airborne"]["contact_force_n"]
        height_target = self.commands.height[:, 0]
        linear_error = data.root_lin_vel_b[:, 0] * pitch.cos() - self.commands.value[:, 0]
        if t.task == "p3-tunnel":
            linear_error = data.root_lin_vel_w[:, 0] - self.commands.value[:, 0]
        angular_error = data.root_ang_vel_b[:, 2] - self.commands.value[:, 2]
        height_error = base_height - height_target
        leg_vector = wheel_b - wheel_b.new_tensor(t.shared["hip_pivot_positions_b_m"])
        return dict(
            velocity=data.root_lin_vel_b,
            velocity_w=data.root_lin_vel_w,
            angular_velocity=data.root_ang_vel_b,
            gravity=data.projected_gravity_b,
            roll=roll,
            pitch=pitch,
            yaw=yaw,
            base_height=base_height,
            ground=ground,
            wheel_position_w=wheels_w,
            wheel_position_b=wheel_b,
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
        )
        self.numerical_bad |= ~torch.isfinite(self.robot.data.root_pos_w).all(-1) | ~torch.isfinite(
            self.robot.data.root_quat_w
        ).all(-1)
        self._record_contacts(self._sim_step_counter)
        s = self._measure()
        t, dt = self.training, self.step_dt
        if self.shu is not None:
            timeout = self._sim_step_counter - self.shu.event.born >= round(
                t.settings["episode_length_s"] / self.physics_dt
            )
            if self.mixed_curriculum is not None:
                outside = self.shu.free_map.outside(self.robot.data.root_pos_w)
                timeout |= outside  # all mixed tasks share the outer atlas boundary
            terminated = self.shu.update(s, timeout)
            self.numerical_bad |= self.shu.event.numerical_failure
            self.iteration_numerical_terminations += self.numerical_bad.sum()
            if self.mixed_curriculum is not None:
                self.mixed_curriculum.step(
                    self.terrain,
                    self.previous_position,
                    self.robot.data.root_pos_w,
                    self.commands.value[:, 0] * s["yaw"].cos(),
                    terminated | timeout,
                    wheel_contact=self.contact.data.net_forces_w[:, self.contact_wheels, 2]
                    > t.shared["airborne"]["contact_force_n"],
                )
            s["terminated"] = terminated
            self.state = s
            return terminated, timeout & ~terminated
        self.iteration_numerical_terminations += self.numerical_bad.sum()
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
        term = t.shared["termination"]
        self.fall_counter, fell = leaky_termination(
            self.fall_counter, tilt_fail | body_hit, dt, term["duration_s"], term["decay_s"]
        )
        terminated = fell | self.bad_action | self.numerical_bad
        timeout_at = self.max_episode_length if self.jump is not None else self.max_episode_length - 1
        timeout = self.episode_length_buf >= timeout_at
        if self.jump is not None:
            if t.task == "p3-tunnel":
                terminated |= self.obstacle_hit | self.jump_blocked
            # The episode time limit interrupts an event; only its own deadline is a task failure.
            self.jump.finish_step(self.physics_dt, terminated | timeout)
            terminated |= self.jump.failed
        s["terminated"] = terminated
        self.state = s
        success = self.jump.landing_pulse if t.task == "p3-tunnel" else torch.zeros_like(terminated)
        return terminated | success, timeout & ~(terminated | success)

    def _get_rewards(self) -> torch.Tensor:
        t, s = self.training, self.state
        n = self.num_envs
        if self.shu is not None:
            terms = self.shu.rewards(s)
        else:
            one = torch.ones(n, device=self.device)
            s.update(
                tracking_mask=one,
                height_mask=one,
                vx_cmd=self.commands.value[:, 0],
                wz_cmd=self.commands.value[:, 2],
                ground_drive=torch.ones_like(self.airborne) if self.jump is None else ~self.jump_interval,
                height_rate=self.commands.height_rate,
                requested_speed=self.commands.value[:, :2].norm(dim=-1),
                airborne=self.airborne,
                contact_multiplier=torch.where(self.airborne, 25.0, 1.0),
                termination_multiplier=torch.where(self.airborne, 6.0, 1.0),
            )
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
            weights = t.settings["rewards"]
            if self.jump is not None:
                s["jump"] = self.jump
                flight = self.jump.flight
                s["height_mask"] = s["ground_drive"].float()
                s["tracking_mask"] = torch.where(flight, t.stage["flight_tracking_scale"], 1.0)
                s["termination_multiplier"] = one
                s["contact_multiplier"] = one
                unavailable = "jump_landing" if t.task == "p3-tunnel" else "tunnel_crossing"
                weights = {name: value for name, value in weights.items() if name != unavailable}
            terms = compute_rewards(
                s, t.settings["reward_parameters"], weights, self.step_dt, t.settings["reward_clip"]
            )
            s.update(
                joint_pos=self.robot.data.joint_pos[:, self.joints],
                joint_vel=self.robot.data.joint_vel[:, self.joints],
                previous_joint_vel=self.prev_qd,
                previous_previous_action=self.second_action,
            )
            costs = joint_costs(s, self.lower[self.legs], self.upper[self.legs], self.step_dt)
            for name, cost in costs.items():
                # Ground driving is agreed; takeoff-specific smoothing is not. Torque and limits always apply.
                enabled = one
                if self.jump is not None and name not in ("joint_torque", "leg_soft_limits"):
                    enabled = torch.where(s["ground_drive"], one, t.stage["jump_smooth_scale"])
                terms[name] = -cost.clamp_max(1) * enabled * self.step_dt
        if self.scanner is not None:
            progress, stuck_start, stuck_time, stuck = route_progress_and_stuck(
                self.mixed_curriculum.reward_active,
                self.robot.data.root_pos_w[:, 0],
                self.previous_position[:, 0],
                self.stuck_start[:, 0],
                self.stuck_time,
                self.stuck,
                dt=self.step_dt,
                window_s=t.stage["stuck_window_s"],
                distance_m=t.stage["stuck_distance_m"],
            )
            terms["progress"] = t.stage["progress_weight"] * progress
            self.stuck_start[:, 0] = stuck_start
            self.stuck_time.copy_(stuck_time)
            self.stuck.copy_(stuck)
            terms["stuck"] = t.stage["stuck_weight"] * self.step_dt * self.stuck
            terms["stair_impact"] = t.stage["impact_weight"] * self.step_dt * s["hip_torque"].square().amax(-1)
        self.previous_position.copy_(self.robot.data.root_pos_w)
        for name, value in terms.items():
            # SCUT wheelbipe25_v3/env.py:4007-4018: mask with where, never NaN * 0.
            terms[name] = torch.where(self.numerical_bad, 0.0, terms[name])
            if name not in self.reward_sums:
                self.reward_sums[name] = torch.zeros(n, device=self.device)
            self.reward_sums[name] += terms[name]
        # Preserve pre-reset measurements for evaluation; reset environments cannot contaminate metrics.
        self.extras["evaluation"] = {
            "errors": torch.stack((s["linear_error"], s["angular_error"], s["height_error"]), -1).detach().clone(),
            "failed": s["terminated"].detach().clone(),
            "position": self.robot.data.root_pos_w.detach().clone(),
        }
        if self.mixed_curriculum is not None:
            mix = self.mixed_curriculum
            self.extras["stairs"] = {
                "traverse": mix.traverse.clone(),
                "reverse_descent": mix.reverse_descent.clone(),
                "reverse_half_completed": (mix.reverse_descent & mix.reached_center).clone(),
                "full_crossed": mix.crossed.clone(),
            }
        if self.jump is not None:
            self.extras["jump"] = {
                "succeeded": self.jump.landing_pulse.clone(),
                "failed": (self.jump.failed | (self.jump.finished & s["terminated"])).clone(),
                "first_touch": self.jump.first_touch.clone(),
            }
        return torch.stack(list(terms.values())).sum(0) if terms else s["base_height"].new_zeros(n)

    def _get_observations(self) -> dict[str, torch.Tensor]:
        self._sample_sensors(self._sim_step_counter)
        if self.shu is None:
            self._prepare_stage_command()
        s = self._measure()
        t = self.training
        if self.shu is not None:
            self.shu.observe_commands(s["yaw"])
            s = self._measure()  # privileged next-observation errors follow the newly issued command
        sensor = self._sensors()

        def make_fields(values):
            return dict(
                command=self.commands.value,
                height=self.commands.height,
                angular_velocity=values[:, :3],
                gravity=values[:, 3:6],
                joint_position=values[:, 6:12],
                joint_velocity=values[:, 12:18],
                previous_action=self.raw_action,
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
        request = self.jump.command_m[:, None] if self.jump is not None else torch.zeros_like(self.commands.height)
        critic = torch.cat(
            (
                clean,
                request,
                component("base_linear_velocity", s["velocity"]),
                component("base_height", s["base_height"][:, None]),
                privileged,
                component("command_error", torch.stack((s["linear_error"], s["angular_error"], s["height_error"]), -1)),
            ),
            -1,
        )
        if self.scanner is not None:
            scan = self.robot.data.root_pos_w[:, 2:3] - self.scanner.data.ray_hits_w[:, :, 2]
            critic = torch.cat((critic, component("height_scan", scan)), -1)
        self.policy_history.update(actor, self.history_tick != self._sim_step_counter)
        self.history_tick = self._sim_step_counter
        return {
            "policy": torch.cat((actor, request), -1),
            "critic": critic,
            "history": self.policy_history.flat(),
            "estimator_target": s["velocity"].clone(),  # nonfinite labels are excluded by the estimator update
        }

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
        if self.reward_sums:
            self.extras["log"] = {
                f"Episode_Reward/{k}": v[env_ids].mean() / self.max_episode_length_s
                for k, v in self.reward_sums.items()
            }
            for value in self.reward_sums.values():
                value[env_ids] = 0
        if self.mixed_curriculum is not None:
            self.mixed_curriculum.reset(
                self.terrain,
                env_ids,
                (self.episode_length_buf > 0) & (self.reset_terminated | self.reset_time_outs),
                self.reset_terminated,
                evaluation=self.cfg.evaluation,
            )
        super()._reset_idx(env_ids)
        n = len(env_ids)
        self.spawn_check_mask[env_ids] = True
        root = self.robot.data.default_root_state[env_ids].clone()
        root[:, :3] += self.terrain.env_origins[env_ids]
        q, qd = self.robot.data.default_joint_pos[env_ids].clone(), self.robot.data.default_joint_vel[env_ids].clone()
        self.fall_counter[env_ids] = 0
        self.policy_history.reset(env_ids)
        if self.shu is not None:
            self.shu.reset(env_ids, root, q, qd)
        else:
            self.commands.reset(env_ids)
            self._stage_command_tick = -1
        if self.jump is not None:
            self.jump.reset(env_ids)
            if self.training_jump_button is not None:
                # Synthetic pulse state belongs to the episode, unlike an operator's held button.
                self.jump.button_down[env_ids] = False
                self.training_jump_button.reset(env_ids)
        if t.task == "p3-tunnel":
            self._reset_tunnel(env_ids)
            p = t.stage["tunnel"]
            approach = uniform(p["approach_distance_range_m"], (n,), self.device)
            root[:, 0] = self.terrain.env_origins[env_ids, 0] + p["beam_offset_from_entrance_m"] - approach
            root[:, 1] = self.terrain.env_origins[env_ids, 1]
            yaw = uniform(p["initial_yaw_range_rad"], (n,), self.device)
            root[:, 3:7] = quat_from_euler_xyz(torch.zeros_like(yaw), torch.zeros_like(yaw), yaw)
        self.robot.write_root_pose_to_sim(root[:, :7], env_ids)
        self.robot.write_root_velocity_to_sim(root[:, 7:], env_ids)
        self.robot.write_joint_state_to_sim(q, qd, env_ids=env_ids)
        self.initial_position[env_ids] = root[:, :3]
        self.previous_position[env_ids] = root[:, :3]
        self.stuck_start[env_ids] = root[:, :3]
        # Mixed P1 must issue fixed commands from the realized post-reset pose in observe_commands.
        if self.commands_fixed and self.mixed_curriculum is None:
            if self.jump is None:
                self.commands.value[env_ids] = self.fixed_command[0]
                self.commands.height[env_ids] = self.fixed_command[1]
            else:
                self.commands.target[env_ids] = self.fixed_command[0]
                self.commands.remaining[env_ids] = torch.inf
                self.commands.target_height[env_ids] = self.fixed_command[1]
                self.commands.height_remaining[env_ids] = torch.inf
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
            self.bad_action,
            self.torque,
            self.contact_peaks,
            self.action_ticks,
        ):
            value[env_ids] = 0
        self._randomize_controls(env_ids)
        self.obs_delay.reset(env_ids)
        self.act_delay.reset(env_ids)
        self.delayed_sensor[env_ids] = perturb_sensors(self._sensors(), self.zero_bias, self.imu_bias, self.legs)[
            env_ids
        ]

    def _reset_tunnel(self, ids: torch.Tensor) -> None:
        p = self.training.stage["tunnel"]
        self.beam_top_z[ids] = p["beam_height_m"]
        pose = self.beam.data.default_root_state[ids, :7].clone()
        pose[:, :3] = self.terrain.env_origins[ids]
        pose[:, 0] += p["beam_offset_from_entrance_m"] + p["beam_length_m"] / 2
        pose[:, 2] += (self.beam_top_z[ids] + p["beam_bottom_m"]) / 2
        self.beam.write_root_pose_to_sim(pose, ids)

    def _tunnel_geometry(self) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        p = self.training.stage["tunnel"]
        data = self.robot.data
        bounds = collision_bounds_w(data.body_link_pos_w, data.body_link_quat_w, self.tunnel_collision_bounds)
        beam_start = self.terrain.env_origins.clone()
        beam_start[:, 0] += p["beam_offset_from_entrance_m"]
        return tunnel_geometry(bounds, beam_start, beam_start[:, 2] + self.beam_top_z, p)

    def _randomize_controls(self, ids: torch.Tensor) -> None:
        t, n, d = self.training, len(ids), self.device
        r = t.shared["randomization"]
        self.kp[ids] = torch.tensor(t.policy.kp, device=d)
        self.kd[ids] = torch.tensor(t.policy.kd, device=d)
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
        if self.shu is not None:
            self.collision_timer[ids] = uniform(t.settings["disturbance"]["collision_interval_s"], (n,), d)
            self.push_timer[ids] = uniform(r["push_interval_s"], (n,), d)
        for buffer, bounds in (
            (self.obs_delay, r["observation_delay_steps"]),
            (self.act_delay, r["action_delay_steps"]),
        ):
            buffer.set_time_lag(torch.randint(bounds[0], bounds[1] + 1, (n,), device=d), ids)
