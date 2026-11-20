"""MuJoCo sim2sim for the wheel-leg PPO policy, mirroring the Isaac training loop (isaac/wheelleg_tasks/env.py).

Timing matches training: physics + leg/wheel PD + gas spring at control_hz (500 Hz), policy at policy_hz (100 Hz).
Sensor and action delays are counted in physics ticks exactly like Isaac's DelayBuffer: the observation sees the
IMU/joint state from `obs_delay` ticks ago, the PD sees the policy action from `act_delay` ticks ago (zero for the
first ticks after a reset). Defaults come from policy_meta.yaml training.evaluation (5 and 4 ticks).

    # full report (stand / straight / turn / combined / landing cases), JSON + Markdown in results/
    python sim2sim.py --run checkpoints/landing_r5b2ffae_cmd40
    # record selected cases to mp4
    python sim2sim.py --run checkpoints/landing_r5b2ffae_cmd40 --cases straight_5 drop_0.32_vx_1.0 --video

Interactive viewer with air spawns and keyboard driving: play.py.
"""

import argparse
import json
import math
import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import mujoco
import numpy as np
import torch
import yaml

from wheelleg.observation import OBS_FIELDS

HERE = Path(__file__).resolve().parent


class RunConfig:
    """robot.yaml + policy_meta.yaml snapshot saved by the training run (params/)."""

    def __init__(self, run: Path):
        self.robot = yaml.safe_load((run / "params" / "robot.yaml").read_text(encoding="utf-8"))
        self.policy = yaml.safe_load((run / "params" / "policy_meta.yaml").read_text(encoding="utf-8"))
        run_info = run / "params" / "run.json"
        self.run = json.loads(run_info.read_text(encoding="utf-8")) if run_info.exists() else {}
        r, p = self.robot, self.policy
        self.shared = r["training"]
        if p["obs_version"] != 2 or (p.get("history_estimator") or {}).get("frames", 0):
            raise ValueError("Only the single-frame obs_version 2 actor is supported")
        if p.get("policy_family") not in ("p1", "p3"):
            raise ValueError("Only p1 and p3 single-frame actors are supported")
        self.control_hz, self.policy_hz = r["control_hz"], r["policy_hz"]
        self.decimation = self.control_hz // self.policy_hz
        self.active_joints = r["asset"]["active_joint_names"]
        self.spring_joints = r["asset"]["spring_joint_names"]
        self.wheel_bodies = r["asset"]["wheel_body_names"]
        self.legs, self.wheels = r["leg_indices"], r["wheel_indices"]
        self.default_q = np.array(r["q_default_rad"], dtype=np.float64)
        self.action_scale = np.array(p["action_scales"])
        self.action_clip = p["action_clip"]
        self.kp, self.kd = np.array(p["kp"], dtype=float), np.array(p["kd"], dtype=float)
        self.torque_limit = np.array(p["torque_limit_nm"], dtype=float)
        self.target_lower = np.array(self.shared["joint_lower_rad"]) + self.shared["joint_target_margin_rad"]
        self.target_upper = np.array(self.shared["joint_upper_rad"]) - self.shared["joint_target_margin_rad"]
        self.wheel_speed_limit = self.shared["wheel_speed_limit_rad_s"]
        self.spring = self.shared["spring"]
        self.spring_stroke = r["spring_stroke_m"]
        self.clip = self.shared["observation_clip"]
        s = p["observation_scales"]
        self.scales = dict(
            command=np.array(s["command"]),
            height=s["height"],
            angular_velocity=s["angular_velocity"],
            gravity=s["gravity"],
            joint_position=s["joint_position"],
            joint_velocity=s["joint_velocity"],
            previous_action=1.0,
            mode=1.0,
        )
        self.training = p["training"]
        self.evaluation = self.training["evaluation"]
        self.commands = self.training["commands"]
        self.landing = p["stages"].get("landing", {}).get("landing_reward")
        self.termination = self.shared["termination"]
        self.airborne = self.shared["airborne"]
        self.leg_reset = self.shared["leg_reset"]


class NumpyActor:
    """Deterministic actor mean (rsl_rl 'actor.*' weights), ELU MLP evaluated in float32 numpy."""

    def __init__(self, checkpoint: Path, hidden_dims: list[int]):
        state = torch.load(checkpoint, map_location="cpu", weights_only=True)
        self.iteration = state.get("iter")
        weights = state["model_state_dict"]
        self.layers = []
        for i in range(len(hidden_dims) + 1):
            w = weights[f"actor.{2 * i}.weight"].numpy().astype(np.float32)
            b = weights[f"actor.{2 * i}.bias"].numpy().astype(np.float32)
            self.layers.append((w, b))
        if self.layers[0][0].shape[1] != sum(n for _, n in OBS_FIELDS) or self.layers[-1][0].shape[0] != 6:
            raise ValueError("Checkpoint actor shape does not match the 35 -> 6 contract")

    def __call__(self, obs: np.ndarray) -> np.ndarray:
        x = obs.astype(np.float32)
        for i, (w, b) in enumerate(self.layers):
            x = w @ x + b
            if i < len(self.layers) - 1:
                x = np.where(x > 0, x, np.expm1(np.minimum(x, 0)))
        return x.astype(np.float64)


class DelayLine:
    """Fixed lag in physics ticks; push() returns the value pushed `lag` ticks earlier (or the fill value)."""

    def __init__(self, lag: int):
        self.lag = lag
        self.buffer = deque(maxlen=lag + 1)

    def reset(self, fill: np.ndarray) -> None:
        self.buffer.clear()
        self.buffer.extend([fill.copy()] * (self.lag + 1))

    def push(self, value: np.ndarray) -> np.ndarray:
        self.buffer.append(value.copy())
        return self.buffer[0]


def five_bar_joint_angles(length: float, angle: float, links, offsets) -> list[float]:
    """Same closed-chain IK as wheelleg.tensor_ops.five_bar_joint_angles; order front1, rear1, front2..4, rear2."""
    l0, l1, l2 = links
    half = math.acos((l0**2 * length**2 + l2**2 * (l0**2 - l1**2)) / (2 * l2 * l0**2 * length))
    knee = math.acos((l0**2 + l1**2 - l0**2 * length**2 / l2**2) / (2 * l0 * l1))
    closing = 2 * math.pi - 2 * half - 2 * knee
    return [
        angle + math.pi / 2 - half - offsets[0],
        angle + math.pi / 2 + half - offsets[1],
        offsets[2] - knee,
        offsets[3] - closing,
        offsets[4] - knee,
        knee - offsets[5],
    ]


def euler_xyz(quat_wxyz: np.ndarray) -> tuple[float, float, float]:
    w, x, y, z = quat_wxyz
    roll = math.atan2(2 * (w * x + y * z), 1 - 2 * (x * x + y * y))
    pitch = math.asin(max(-1.0, min(1.0, 2 * (w * y - z * x))))
    yaw = math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))
    return roll, pitch, yaw


def quat_from_euler(roll: float, pitch: float, yaw: float) -> np.ndarray:
    cr, sr = math.cos(roll / 2), math.sin(roll / 2)
    cp, sp = math.cos(pitch / 2), math.sin(pitch / 2)
    cy, sy = math.cos(yaw / 2), math.sin(yaw / 2)
    return np.array(
        [
            cr * cp * cy + sr * sp * sy,
            sr * cp * cy - cr * sp * sy,
            cr * sp * cy + sr * cp * sy,
            cr * cp * sy - sr * sp * cy,
        ]
    )


@dataclass
class Spawn:
    height_offset_m: float = 0.0  # added to the ground-birth root height (air birth when > 0)
    vx_m_s: float = 0.0  # initial forward speed in the heading frame
    leg_length_m: float | None = None  # None keeps the zero (folded) joint pose used by Isaac evaluation
    leg_angle_rad: float = 0.0
    roll_rad: float = 0.0
    pitch_rad: float = 0.0
    yaw_rad: float = 0.0
    x_m: float = 0.0
    y_m: float = 0.0
    vy_m_s: float = 0.0  # initial lateral speed in the heading frame
    rate_b: tuple[float, float, float] = (0.0, 0.0, 0.0)  # initial body-frame angular velocity, rad/s


class WheelLegSim:
    def __init__(
        self,
        cfg: RunConfig,
        actor: NumpyActor,
        model_path: Path,
        obs_delay: int,
        act_delay: int,
        noise: bool,
        wheel_friction: float | None = None,
    ):
        self.cfg, self.actor = cfg, actor
        self.model = mujoco.MjModel.from_xml_path(str(model_path))
        self.data = mujoco.MjData(self.model)
        if wheel_friction is not None:
            for i in range(self.model.ngeom):
                if self.model.geom(i).name.endswith("wheel_link_collision"):
                    self.model.geom_friction[i, 0] = wheel_friction
        expected_dt = 1.0 / cfg.control_hz
        if abs(self.model.opt.timestep - expected_dt) > 1e-12:
            raise ValueError(f"MJCF timestep {self.model.opt.timestep} != 1/control_hz {expected_dt}")
        m = self.model
        joint = lambda name: m.joint(name).id  # noqa: E731
        self.q_adr = np.array([m.jnt_qposadr[joint(n)] for n in cfg.active_joints])
        self.v_adr = np.array([m.jnt_dofadr[joint(n)] for n in cfg.active_joints])
        self.spring_q = np.array([m.jnt_qposadr[joint(n)] for n in cfg.spring_joints])
        self.spring_v = np.array([m.jnt_dofadr[joint(n)] for n in cfg.spring_joints])
        actuators = [m.actuator(i) for i in range(m.nu)]
        joint_of = {m.joint(a.trnid[0]).name: a.id for a in actuators}
        self.ctrl_active = np.array([joint_of[n] for n in cfg.active_joints])
        self.ctrl_spring = np.array([joint_of[n] for n in cfg.spring_joints])
        self.base = m.body(cfg.robot["asset"]["base_body_name"]).id
        self.wheel_ids = np.array([m.body(n).id for n in cfg.wheel_bodies])
        self.chain_free = np.array(
            [m.jnt_dofadr[j] for j in range(m.njnt) if m.joint(j).name.split("_", 1)[1].startswith("spring")]
        )
        self.chain_free_q = np.array(
            [m.jnt_qposadr[j] for j in range(m.njnt) if m.joint(j).name.split("_", 1)[1].startswith("spring")]
        )
        self.robot_body = np.zeros(m.nbody, dtype=bool)
        self.robot_body[self.base :] = True
        self.ground = m.geom("ground").id
        self.obs_line, self.act_line = DelayLine(obs_delay), DelayLine(act_delay)
        self.noise = self._noise_vector() if noise else None
        self.rng = np.random.default_rng(0)
        self.reset(Spawn())

    # ----- state -----
    def _noise_vector(self) -> np.ndarray:
        c, n = self.cfg, self.cfg.shared["observation_noise"]
        parts = {name: np.zeros(width) for name, width in OBS_FIELDS}
        parts["angular_velocity"][:] = n["angular_velocity"] * c.scales["angular_velocity"]
        parts["gravity"][:] = n["gravity"] * c.scales["gravity"]
        parts["joint_position"][:] = n["joint_position"] * c.scales["joint_position"]
        parts["joint_velocity"][c.legs] = n["leg_velocity"] * c.scales["joint_velocity"]
        parts["joint_velocity"][c.wheels] = n["wheel_velocity"] * c.scales["joint_velocity"]
        return np.concatenate([parts[name] for name, _ in OBS_FIELDS])

    def sensors(self) -> np.ndarray:
        d = self.data
        rot = d.xmat[self.base].reshape(3, 3)
        angular_b = d.qvel[3:6].copy()  # free joint angular velocity is already in the body frame
        gravity_b = rot.T @ np.array([0.0, 0.0, -1.0])
        return np.concatenate((angular_b, gravity_b, d.qpos[self.q_adr], d.qvel[self.v_adr]))

    def _close_spring_chain(self) -> None:
        """Solve spring1/spring2 so the gas-spring connect constraints hold after an IK leg reset."""
        m, d = self.model, self.data
        for _ in range(30):
            mujoco.mj_forward(m, d)
            rows = d.efc_type == mujoco.mjtConstraint.mjCNSTR_EQUALITY
            residual = d.efc_pos[rows]
            if np.abs(residual).max(initial=0) < 1e-7:
                break
            jac = d.efc_J.reshape(d.nefc, m.nv)[rows][:, self.chain_free]
            d.qpos[self.chain_free_q] += np.linalg.lstsq(jac, -residual, rcond=None)[0]

    def reset(self, spawn: Spawn) -> None:
        c, m, d = self.cfg, self.model, self.data
        mujoco.mj_resetData(m, d)
        d.qpos[:3] = [spawn.x_m, spawn.y_m, 0.0]
        d.qpos[3:7] = quat_from_euler(spawn.roll_rad, spawn.pitch_rad, spawn.yaw_rad)
        if spawn.leg_length_m is None:
            root_height = c.robot["asset"]["initial_root_position_m"][2]
        else:
            r = c.leg_reset
            values = five_bar_joint_angles(spawn.leg_length_m, spawn.leg_angle_rad, r["link_lengths_m"], r["angle_offsets_rad"])
            for name, value in zip(r["joint_names"], [v for v in values for _ in (0, 1)]):
                d.qpos[m.jnt_qposadr[m.joint(name).id]] = value
            self._close_spring_chain()
            mujoco.mj_forward(m, d)
            wheel_z = d.xpos[self.wheel_ids, 2].min()
            root_height = max(
                c.shared["wheel_radius_m"] + c.shared["spawn_clearance_m"] - wheel_z, r["min_root_height_m"]
            )
        d.qpos[2] = root_height + spawn.height_offset_m
        # Linear velocity in the yaw-only heading frame, as in the Isaac air reset.
        cy, sy = math.cos(spawn.yaw_rad), math.sin(spawn.yaw_rad)
        d.qvel[0:2] = [cy * spawn.vx_m_s - sy * spawn.vy_m_s, sy * spawn.vx_m_s + cy * spawn.vy_m_s]
        d.qvel[3:6] = spawn.rate_b
        mujoco.mj_forward(m, d)
        self.raw_action = np.zeros(6)
        self.torque = np.zeros(6)
        self.obs_line.reset(self.sensors())
        self.act_line.reset(np.zeros(6))
        self.delayed_sensor = self.sensors()
        self.time = 0.0
        self.termination_steps = 0.0
        self.air_enter = self.air_exit = self.air_elapsed = 0.0
        self.is_airborne = False

    # ----- policy I/O -----
    def observation(self, command: np.ndarray, height: float) -> np.ndarray:
        c, s = self.cfg, self.delayed_sensor
        q = np.zeros(6)
        q[c.legs] = s[6:12][c.legs] - c.default_q[c.legs]
        mode = self.observation_mode()
        raw = dict(
            command=command,
            height=np.array([height]),
            angular_velocity=s[0:3],
            gravity=s[3:6],
            joint_position=q,
            joint_velocity=s[12:18],
            previous_action=self.raw_action,
            mode=mode,
        )
        parts, offset = [], 0
        for name, width in OBS_FIELDS:
            value = raw[name]
            if self.noise is not None:
                value = value + (2 * self.rng.random(width) - 1) * self.noise[offset : offset + width] / c.scales[name]
            part = np.clip(value, *c.clip[name]) * c.scales[name]
            parts.append(np.nan_to_num(part, nan=0.0, posinf=0.0, neginf=0.0))
            offset += width
        return np.concatenate(parts)

    def observation_mode(self) -> np.ndarray:
        mode = np.zeros(7)
        mode[0] = 1.0
        return mode

    def _targets(self, action: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        c = self.cfg
        a = action if c.action_clip is None else np.clip(action, -c.action_clip, c.action_clip)
        scaled = a * c.action_scale
        q_ref, qd_ref = c.default_q.copy(), np.zeros(6)
        q_ref[c.legs] = np.clip(c.default_q[c.legs] + scaled[c.legs], c.target_lower[c.legs], c.target_upper[c.legs])
        qd_ref[c.wheels] = np.clip(scaled[c.wheels], -c.wheel_speed_limit, c.wheel_speed_limit)
        return q_ref, qd_ref

    def _spring_force(self) -> np.ndarray:
        p, d = self.cfg.spring, self.data
        q, qd = d.qpos[self.spring_q], d.qvel[self.spring_v]
        direction = np.array(p["direction"], dtype=float)
        compression = np.clip(direction * (q - np.array(p["reference_q_m"])), 0, self.cfg.spring_stroke)
        elastic = np.array(p["f0_n"]) + np.array(p["stiffness_n_m"]) * compression
        force = -direction * elastic - np.array(p["damping_n_s_m"]) * qd - np.array(p["hysteresis_n"]) * np.sign(qd)
        limit = np.array(p["force_limit_n"])
        return np.clip(force, -limit, limit)

    def _contact_forces(self) -> np.ndarray:
        """Net contact force magnitude per body, N (robot-ground only; robot self-collision is disabled)."""
        m, d = self.model, self.data
        net = np.zeros((m.nbody, 3))
        wrench = np.zeros(6)
        for i in range(d.ncon):
            contact = d.contact[i]
            mujoco.mj_contactForce(m, d, i, wrench)
            force_w = contact.frame.reshape(3, 3).T @ wrench[:3]
            b1, b2 = m.geom_bodyid[contact.geom1], m.geom_bodyid[contact.geom2]
            net[b1] -= force_w
            net[b2] += force_w
        return np.linalg.norm(net, axis=1)

    def step(self, command: np.ndarray, height: float) -> dict:
        """One policy step (decimation physics ticks). Returns measurements for metrics."""
        c, m, d = self.cfg, self.model, self.data
        obs = self.observation(command, height)
        t0 = time.perf_counter()
        action = self.actor(obs)
        inference_s = time.perf_counter() - t0
        bad_action = not np.isfinite(action).all()
        self.raw_action = np.zeros(6) if bad_action else action
        peaks = np.zeros(m.nbody)
        saturated = np.zeros(6)
        for _ in range(c.decimation):
            q_ref, qd_ref = self._targets(self.act_line.push(self.raw_action))
            q, qd = d.qpos[self.q_adr], d.qvel[self.v_adr]
            error = q_ref - q
            error[c.wheels] = 0
            effort = c.kp * error + c.kd * (qd_ref - qd)
            self.torque = np.clip(effort, -c.torque_limit, c.torque_limit)
            if bad_action:
                self.torque[:] = 0
            saturated += np.abs(effort) >= c.torque_limit
            d.ctrl[self.ctrl_active] = self.torque
            d.ctrl[self.ctrl_spring] = self._spring_force()
            mujoco.mj_step(m, d)
            self.delayed_sensor = self.obs_line.push(self.sensors())
            peaks = np.maximum(peaks, self._contact_forces())
        self.time += c.decimation * m.opt.timestep
        return self._measure(command, height, peaks, saturated / c.decimation, inference_s, bad_action)

    def _measure(self, command, height, peaks, saturated, inference_s, bad_action) -> dict:
        c, d = self.cfg, self.data
        dt = 1.0 / c.policy_hz
        roll, pitch, yaw = euler_xyz(d.qpos[3:7])
        vel_w = d.qvel[0:3]
        heading_vx = math.cos(yaw) * vel_w[0] + math.sin(yaw) * vel_w[1]
        deadzone = c.training["reward_parameters"]["stand_deadzone"]
        tracked = np.where(np.abs(command) < deadzone, 0.0, command)
        base_height = d.qpos[2]
        wheel_force = peaks[self.wheel_ids]
        wheel_contact = wheel_force > c.airborne["contact_force_n"]
        nonwheel = peaks.copy()
        nonwheel[self.wheel_ids] = 0
        nonwheel[: self.base] = 0
        body_hit = bool((nonwheel > c.termination["contact_force_n"]).any())
        clearance = d.xpos[self.wheel_ids, 2] - c.shared["wheel_radius_m"]
        # Airborne state machine and accumulated termination counter, as in env._get_dones.
        a = c.airborne
        candidate = not wheel_contact.any() and clearance.min() > a["wheel_clearance_m"] and base_height > a["base_height_m"]
        self.air_enter = self.air_enter + dt if candidate else 0.0
        self.air_exit = self.air_exit + dt if wheel_contact.any() else 0.0
        self.is_airborne |= self.air_enter >= a["enter_duration_s"]
        self.air_elapsed = self.air_elapsed + dt if self.is_airborne else 0.0
        self.is_airborne &= self.air_exit < a["exit_duration_s"] and self.air_elapsed < a["max_duration_s"]
        tilt_limit = c.termination["airborne_tilt_rad"] if self.is_airborne else c.termination["tilt_rad"]
        tilt_fail = abs(roll) > tilt_limit or abs(pitch) > tilt_limit
        physical = (tilt_fail or body_hit) and self.time >= c.leg_reset["settle_s"]
        leak = c.termination["duration_s"] / c.termination["release_s"]
        self.termination_steps = self.termination_steps + 1 if physical else max(self.termination_steps - leak, 0.0)
        numerical = not (np.isfinite(d.qpos).all() and np.isfinite(d.qvel).all())
        safety = c.shared["numerical_safety"]
        numerical |= np.abs(d.qvel[self.v_adr]).max() > safety["joint_velocity_abs_max"]
        numerical |= np.abs(d.qvel[0:3]).max() > safety["base_linear_velocity_abs_max"]
        numerical |= np.abs(d.qvel[3:6]).max() > safety["base_angular_velocity_abs_max"]
        terminated = (
            self.termination_steps >= round(c.termination["duration_s"] * c.policy_hz) or bad_action or numerical
        )
        return dict(
            time=self.time,
            command=command.copy(),
            height_command=height,
            heading_vx=heading_vx,
            wz=d.qvel[5],
            angular_xy=float(np.abs(d.qvel[3:5]).max()),
            vz=vel_w[2],
            base_height=base_height,
            position=d.qpos[0:3].copy(),
            roll=roll,
            pitch=pitch,
            errors=np.array([heading_vx - tracked[0], d.qvel[5] - tracked[2], base_height - height]),
            wheel_force=wheel_force,
            wheel_contact=wheel_contact,
            nonwheel_contact=body_hit,
            airborne=self.is_airborne,
            terminated=bool(terminated),
            torque=self.torque.copy(),
            saturated=saturated,
            action=self.raw_action.copy(),
            spring_q=d.qpos[self.spring_q].copy(),
            inference_s=inference_s,
        )


# ----- evaluation cases -----
@dataclass
class Case:
    name: str
    command: tuple[float, float, float]
    height: float
    spawn: Spawn
    landing: bool = False


def build_cases(cfg: RunConfig, heights: list[float] | None) -> list[Case]:
    e = cfg.evaluation
    h = e["height_m"]
    cases = [Case(f"straight_{i}", (vx, 0.0, 0.0), h, Spawn()) for i, vx in enumerate(e["vx_values_m_s"])]
    cases += [Case(f"turn_{i}", (0.0, 0.0, wz), h, Spawn()) for i, wz in enumerate(e["wz_values_rad_s"])]
    cases += [Case(f"combined_{i}", tuple(cmd), h, Spawn()) for i, cmd in enumerate(e["combined_commands"])]
    cases.append(Case("stand", (0.0, 0.0, 0.0), h, Spawn()))
    for height in heights or cfg.commands["height_range_m"]:
        cases.append(Case(f"stand_h{height:.2f}", (0.0, 0.0, 0.0), height, Spawn()))
    # Landing: Isaac evaluation-style air births (zero joint pose + height offset) and training-style births with
    # an extended leg; the forward command equals the birth speed (driving off a ledge).
    landing = cfg.policy["stages"].get("landing")
    if landing:
        low, high = landing["air_height_offset_m"]
        for offset in np.linspace(low, high, 4):
            for vx in (0.0, 1.0):
                cases.append(
                    Case(f"drop_{offset:.2f}_vx_{vx:.1f}", (vx, 0.0, 0.0), h, Spawn(float(offset), vx), landing=True)
                )
                cases.append(
                    Case(
                        f"drop_leg_{offset:.2f}_vx_{vx:.1f}",
                        (vx, 0.0, 0.0),
                        h,
                        Spawn(float(offset), vx, leg_length_m=0.25),
                        landing=True,
                    )
                )
    return cases


def landing_metrics(cfg: RunConfig, trace: list[dict]) -> dict:
    """First-landing recovery with the training landing_reward thresholds (support, tilt, rates, height)."""
    p = cfg.landing
    dt = 1.0 / cfg.policy_hz
    touch = next((i for i, s in enumerate(trace) if (s["wheel_force"] > p["contact_force_n"]).any() or s["nonwheel_contact"]), None)
    if touch is None:
        return dict(first_contact_s=None, landing_success=False, landing_failure="no_contact")
    held, collision = 0.0, False
    for s in trace[touch : touch + int(p["window_s"] / dt)]:
        collision |= s["nonwheel_contact"]
        if collision or s["terminated"]:
            break
        supported = (s["wheel_force"] > p["support_force_n"]).all()
        stable = supported and max(abs(s["roll"]), abs(s["pitch"])) <= p["tilt_rad"]
        stable &= s["angular_xy"] <= p["angular_xy_rad_s"] and abs(s["vz"]) <= p["vertical_velocity_m_s"]
        stable &= abs(s["errors"][2]) <= p["height_error_m"]
        held = held + dt if stable else 0.0
        if held >= p["stable_s"] - 1e-6:
            return dict(
                first_contact_s=round(trace[touch]["time"], 3),
                landing_success=True,
                landing_recovery_s=round(s["time"] - trace[touch]["time"], 3),
                peak_wheel_force_n=round(float(max(x["wheel_force"].max() for x in trace[touch : touch + 50])), 1),
            )
    reason = "collision" if collision else "terminated" if any(s["terminated"] for s in trace) else "unstable"
    return dict(first_contact_s=round(trace[touch]["time"], 3), landing_success=False, landing_failure=reason)


def run_case(sim: WheelLegSim, case: Case, duration: float, settling: float, frames=None, renderer=None, camera=None) -> dict:
    cfg = sim.cfg
    sim.reset(case.spawn)
    command = np.array(case.command, dtype=float)
    trace = []
    failed_at = None
    frame_every = max(1, round(cfg.policy_hz / 50))
    start = time.perf_counter()
    for step in range(int(round(duration * cfg.policy_hz))):
        s = sim.step(command, case.height)
        trace.append(s)
        if frames is not None and step % frame_every == 0:
            camera.lookat[:] = sim.data.qpos[0:3]
            renderer.update_scene(sim.data, camera)
            frames.append(renderer.render())
        if s["terminated"]:
            failed_at = s["time"]
            break
    wall = time.perf_counter() - start
    valid = [s for s in trace if s["time"] >= settling]
    errors = np.abs(np.array([s["errors"] for s in valid])) if valid else np.full((1, 3), np.nan)
    tilt = np.array([max(abs(s["roll"]), abs(s["pitch"])) for s in valid]) if valid else np.array([np.nan])
    start_xy = trace[0]["position"][:2]
    result = dict(
        case=case.name,
        command=list(case.command),
        height_command=case.height,
        failed=failed_at is not None,
        failed_at_s=failed_at,
        simulated_s=round(trace[-1]["time"], 3),
        mean_abs_velocity_error=float(errors[:, 0].mean()),
        mean_abs_yaw_rate_error=float(errors[:, 1].mean()),
        mean_abs_height_error=float(errors[:, 2].mean()),
        mean_vx=float(np.mean([s["heading_vx"] for s in valid])) if valid else None,
        mean_wz=float(np.mean([s["wz"] for s in valid])) if valid else None,
        mean_base_height=float(np.mean([s["base_height"] for s in valid])) if valid else None,
        tilt_p95_rad=float(np.percentile(tilt, 95)),
        tilt_max_rad=float(tilt.max()),
        nonwheel_contact_fraction=float(np.mean([s["nonwheel_contact"] for s in valid])) if valid else None,
        displacement_m=float(np.linalg.norm(trace[-1]["position"][:2] - start_xy)),
        leg_torque_saturation=float(np.mean([s["saturated"][cfg.legs].mean() for s in trace])),
        wheel_torque_saturation=float(np.mean([s["saturated"][cfg.wheels].mean() for s in trace])),
        max_abs_raw_action=float(max(np.abs(s["action"]).max() for s in trace)),
        realtime_factor=round(trace[-1]["time"] / wall, 2),
    )
    if case.landing:
        result.update(landing_metrics(cfg, trace))
    result["_trace"] = trace
    return result


def write_report(out: Path, header: dict, results: list[dict], save_traces: bool) -> None:
    out.mkdir(parents=True, exist_ok=True)
    clean = [{k: v for k, v in r.items() if k != "_trace"} for r in results]
    (out / "report.json").write_text(json.dumps(dict(header, cases=clean), indent=2), encoding="utf-8")
    fmt = lambda v, n=3: "-" if v is None else f"{v:.{n}f}" if isinstance(v, float) else str(v)  # noqa: E731
    lines = [
        f"# sim2sim {header['checkpoint']}",
        "",
        "\n".join(f"- {k}: {v}" for k, v in header.items() if k != "checkpoint"),
        "",
        "| case | cmd (vx, wz) | h | failed | \\|e_v\\| | \\|e_w\\| | \\|e_h\\| | mean vx | mean wz | tilt p95 | non-wheel contact | landing |",
        "|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for r in clean:
        landing = ""
        if "landing_success" in r:
            landing = (
                f"ok {r['landing_recovery_s']} s" if r["landing_success"] else f"FAIL {r.get('landing_failure')}"
            )
        failed = f"FAIL@{r['failed_at_s']:.2f}s" if r["failed"] else "no"
        lines.append(
            f"| {r['case']} | {r['command'][0]:+.1f}, {r['command'][2]:+.1f} | {r['height_command']:.2f} | {failed} | "
            f"{fmt(r['mean_abs_velocity_error'])} | {fmt(r['mean_abs_yaw_rate_error'])} | "
            f"{fmt(r['mean_abs_height_error'])} | {fmt(r['mean_vx'], 2)} | {fmt(r['mean_wz'], 2)} | "
            f"{fmt(r['tilt_p95_rad'])} | {fmt(r['nonwheel_contact_fraction'], 2)} | {landing} |"
        )
    (out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if save_traces:
        keys = ("time", "heading_vx", "wz", "base_height", "roll", "pitch", "torque", "action", "wheel_force", "spring_q")
        for r in results:
            np.savez(out / f"trace_{r['case']}.npz", **{k: np.array([s[k] for s in r["_trace"]]) for k in keys})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", type=Path, required=True, help="folder with model_*.pt and params/")
    parser.add_argument("--checkpoint", type=Path, help="default: highest model_*.pt in --run")
    parser.add_argument("--model", type=Path, default=HERE / "assets" / "scut_v14_2_flat.xml")
    parser.add_argument("--obs-delay", type=int, help="physics ticks; default training.evaluation")
    parser.add_argument("--act-delay", type=int, help="physics ticks; default training.evaluation")
    parser.add_argument("--noise", action="store_true", help="add the training observation noise")
    parser.add_argument("--wheel-friction", type=float, help="override the MJCF wheel friction (training 0.4-1.2)")
    parser.add_argument("--duration", type=float, help="seconds per case; default training.evaluation")
    parser.add_argument("--cases", nargs="*", help="run only these case names")
    parser.add_argument("--video", action="store_true", help="write an mp4 per case")
    parser.add_argument("--traces", action="store_true", help="save per-case npz traces")
    parser.add_argument("--output", type=Path, help="default results/<run>_<checkpoint>_<time>")
    args = parser.parse_args()

    cfg = RunConfig(args.run)
    checkpoint = args.checkpoint or max(args.run.glob("model_*.pt"), key=lambda p: int(p.stem.split("_")[1]))
    actor = NumpyActor(checkpoint, cfg.policy["hidden_dims"])
    obs_delay = cfg.evaluation["observation_delay_steps"] if args.obs_delay is None else args.obs_delay
    act_delay = cfg.evaluation["action_delay_steps"] if args.act_delay is None else args.act_delay
    sim = WheelLegSim(cfg, actor, args.model, obs_delay, act_delay, args.noise, args.wheel_friction)
    print(
        f"checkpoint {checkpoint} (iter {actor.iteration}), task {cfg.run.get('task')}; physics {cfg.control_hz} Hz, "
        f"policy {cfg.policy_hz} Hz (decimation {cfg.decimation}); delays obs {obs_delay} / act {act_delay} ticks"
    )
    cases = build_cases(cfg, None)
    if args.cases:
        unknown = set(args.cases) - {c.name for c in cases}
        if unknown:
            parser.error(f"unknown cases {sorted(unknown)}; available: {[c.name for c in cases]}")
        cases = [c for c in cases if c.name in args.cases]
    duration = args.duration or cfg.evaluation["duration_s"]
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = args.output or HERE / "results" / f"{args.run.name}_{checkpoint.stem}_{stamp}"
    renderer = camera = None
    if args.video:
        import imageio

        renderer = mujoco.Renderer(sim.model, height=720, width=1280)
        camera = mujoco.MjvCamera()
        camera.distance, camera.elevation, camera.azimuth = 2.2, -15, 135
        out.mkdir(parents=True, exist_ok=True)
    results = []
    for case in cases:
        frames = [] if args.video else None
        r = run_case(sim, case, duration, cfg.evaluation["settling_s"], frames, renderer, camera)
        if frames:
            imageio.mimwrite(out / f"{case.name}.mp4", frames, fps=50, quality=7)
        results.append(r)
        status = f"FAIL@{r['failed_at_s']:.2f}s" if r["failed"] else "ok"
        extra = ""
        if case.landing:
            extra = f" landing={'ok' if r['landing_success'] else r.get('landing_failure')}"
        print(
            f"{case.name:24s} {status:10s} |e_v|={r['mean_abs_velocity_error']:.3f} |e_w|={r['mean_abs_yaw_rate_error']:.3f} "
            f"|e_h|={r['mean_abs_height_error']:.3f} tilt95={r['tilt_p95_rad']:.3f}{extra}  rt x{r['realtime_factor']}"
        )
    header = dict(
        checkpoint=str(checkpoint),
        iteration=actor.iteration,
        task=cfg.run.get("task"),
        git_commit=cfg.run.get("git_commit"),
        mjcf=str(args.model),
        mujoco=mujoco.__version__,
        physics_hz=cfg.control_hz,
        policy_hz=cfg.policy_hz,
        observation_delay_ticks=obs_delay,
        action_delay_ticks=act_delay,
        observation_noise=args.noise,
        wheel_friction=float(sim.model.geom_friction[sim.model.geom("left_wheel_link_collision").id, 0]),
        duration_s=duration,
        settling_s=cfg.evaluation["settling_s"],
    )
    write_report(out, header, results, args.traces)
    failures = sum(r["failed"] for r in results)
    print(f"\n{len(results) - failures}/{len(results)} cases without termination; report: {out / 'report.md'}")


if __name__ == "__main__":
    main()
