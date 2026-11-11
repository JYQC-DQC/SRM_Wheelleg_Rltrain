"""Batched observation and actuator math shared by the training tasks."""

import torch

from .config import PolicyConfig, RobotConfig
from .observation import OBS_FIELDS


def clipped_component(values: torch.Tensor, bounds: tuple[float, float], scale: float = 1.0) -> torch.Tensor:
    return torch.nan_to_num(values.clamp(*bounds) * scale, nan=0.0, posinf=0.0, neginf=0.0)


def observation_tensor(
    robot: RobotConfig, policy: PolicyConfig, fields: dict[str, torch.Tensor], noise: torch.Tensor | None = None
) -> torch.Tensor:
    q = torch.zeros_like(fields["joint_position"])
    indices = list(robot.leg_indices)
    default = q.new_tensor([robot.q_default_rad[i] for i in indices])
    q[:, indices] = fields["joint_position"][:, indices] - default
    values = {**fields, "joint_position": q}
    scales = dict(
        command=q.new_tensor(policy.command_scale),
        height=policy.height_scale,
        angular_velocity=policy.angular_velocity_scale,
        gravity=policy.gravity_scale,
        joint_position=policy.joint_position_scale,
        joint_velocity=policy.joint_velocity_scale,
        previous_action=1.0,
        mode=1.0,
    )
    clips = dict(robot.observation_clip)
    parts = []
    offset = 0
    for name, width in OBS_FIELDS:
        raw = values[name]
        if noise is not None:
            # noise is expressed in scaled observation units; apply it before the physical clip.
            raw = raw + noise[:, offset : offset + width] / scales[name]
        parts.append(clipped_component(raw, clips[name], scales[name]))
        offset += width
    return torch.cat(parts, dim=-1)


def observation_noise(robot: RobotConfig, policy: PolicyConfig, settings: dict, device: str) -> torch.Tensor:
    widths = dict(OBS_FIELDS)
    noise = {name: torch.zeros(width, device=device) for name, width in OBS_FIELDS}
    noise["angular_velocity"][:] = settings["angular_velocity"] * policy.angular_velocity_scale
    noise["gravity"][:] = settings["gravity"] * policy.gravity_scale
    noise["joint_position"][:] = settings["joint_position"] * policy.joint_position_scale
    noise["joint_velocity"][list(robot.leg_indices)] = settings["leg_velocity"] * policy.joint_velocity_scale
    noise["joint_velocity"][list(robot.wheel_indices)] = settings["wheel_velocity"] * policy.joint_velocity_scale
    return torch.cat([noise[name] for name in widths])


def action_targets(
    actions: torch.Tensor,
    default_q: torch.Tensor,
    scale: torch.Tensor,
    clip: float | None,
    legs: list[int],
    wheels: list[int],
    lower: torch.Tensor,
    upper: torch.Tensor,
    wheel_limit: float,
) -> tuple[torch.Tensor, torch.Tensor]:
    scaled = (actions if clip is None else actions.clamp(-clip, clip)) * scale
    q = default_q.expand_as(actions).clone()
    q[:, legs] = (default_q[legs] + scaled[:, legs]).clamp(lower[legs], upper[legs])
    qd = torch.zeros_like(actions)
    qd[:, wheels] = scaled[:, wheels].clamp(-wheel_limit, wheel_limit)
    return q, qd


def motor_torque(
    q: torch.Tensor,
    qd: torch.Tensor,
    q_target: torch.Tensor,
    qd_target: torch.Tensor,
    kp: torch.Tensor,
    kd: torch.Tensor,
    limit: torch.Tensor,
    saturation: torch.Tensor,
    no_load_speed: torch.Tensor,
    output_scale: torch.Tensor,
    wheels: list[int],
) -> torch.Tensor:
    """Signed DC envelope; opposing/braking torque remains available at high speed."""
    position_error = q_target - q
    position_error[:, wheels] = 0
    effort = kp * position_error + kd * (qd_target - qd)
    top = torch.minimum(saturation * (1 - qd / no_load_speed), limit).clamp_min(0)
    bottom = torch.maximum(saturation * (-1 - qd / no_load_speed), -limit).clamp_max(0)
    return torch.maximum(torch.minimum(effort, top), bottom) * output_scale


def spring_force(q: torch.Tensor, qd: torch.Tensor, params: dict, bias: torch.Tensor, stroke: float) -> torch.Tensor:
    direction = q.new_tensor(params["direction"])
    compression = (direction * (q - q.new_tensor(params["reference_q_m"]))).clamp(0, stroke)
    elastic = q.new_tensor(params["f0_n"]) + q.new_tensor(params["stiffness_n_m"]) * compression + bias
    force = -direction * elastic - q.new_tensor(params["damping_n_s_m"]) * qd
    force -= q.new_tensor(params["hysteresis_n"]) * torch.sign(qd)
    limit = q.new_tensor(params["force_limit_n"])
    return force.clamp(-limit, limit)


def slew(current: torch.Tensor, target: torch.Tensor, rate: torch.Tensor | float, dt: float) -> torch.Tensor:
    return current + (target - current).clamp(-rate * dt, rate * dt)


def rotate_xy(vector: torch.Tensor, angle: torch.Tensor) -> torch.Tensor:
    c, s = angle.cos(), angle.sin()
    return torch.stack((c * vector[:, 0] - s * vector[:, 1], s * vector[:, 0] + c * vector[:, 1]), dim=-1)


def smooth_height(start: torch.Tensor, target: torch.Tensor, elapsed: torch.Tensor, duration: float) -> torch.Tensor:
    t = (elapsed / duration).clamp(0, 1)
    return start + (target - start) * t.square() * (3 - 2 * t)


def reference_pd_torque(
    q: torch.Tensor,
    qd: torch.Tensor,
    q_ref: torch.Tensor,
    qd_ref: torch.Tensor,
    kp: torch.Tensor,
    kd: torch.Tensor,
    limit: torch.Tensor,
    output_scale: torch.Tensor,
    wheels: list[int],
) -> torch.Tensor:
    """SCUT ideal-PD reference envelope, not an identified DC motor model."""
    error = q_ref - q
    error[:, wheels] = 0
    return (kp * error + kd * (qd_ref - qd)).clamp(-limit, limit) * output_scale
