"""One vectorized term per log channel. Guide sections 6.1, 6.5, 6.6."""

import torch

from .shu_rewards import motion_bonus, motion_height_factor


def track_lin_vel(s, p):
    return motion_bonus(s["vx_cmd"], s["linear_error"], p["vx_tol_max"], p["vx_tol_knee"]) * s["motion_bonus_mask"]


def lin_vel_error(s, p):
    return -torch.expm1(-s["linear_error"].square() / p["vx_error_sigma"]) * s["tracking_mask"] * (s["vx_cmd"] != 0)


def track_ang_vel(s, p):
    return motion_bonus(s["wz_cmd"], s["angular_error"], p["wz_tol_max"], p["wz_tol_knee"]) * s["motion_bonus_mask"]


def ang_vel_error(s, p):
    return -torch.expm1(-s["angular_error"].square() / p["wz_error_sigma"]) * s["tracking_mask"]


def track_height(s, p):
    return torch.exp(-s["height_error"].square() / p["height_sigma"]) * s["height_mask"]


def height_error(s, p):
    return (10 * s["height_error"]).square() * s["height_mask"]


def flat_roll(s, p):
    return torch.exp(-s["gravity"][:, 1].square() / p["roll_sigma"])


def flat_pitch(s, p):
    return torch.exp(-s["gravity"][:, 0].square() / p["pitch_sigma"])


def roll_penalty(s, p):
    return ((2 * torch.exp(-s["velocity"][:, 0].square() / 3) + 2) * s["gravity"][:, 1]).square()


def pitch_penalty(s, p):
    return ((2 * torch.exp(-s["velocity"][:, 0].square() / 3) + 2) * s["gravity"][:, 0]).square()


def vertical_velocity(s, p):
    return (s["velocity_w"][:, 2] - s["height_rate"]).square() * s["ground_drive"]


def orientation(s, p):
    return 100 * s["gravity"][:, :2].square().sum(-1) * s["ground_drive"]


def angular_xy(s, p):
    return s["angular_velocity"][:, :2].square().sum(-1)


def no_fork(s, p):
    dx = (s["wheel_position_b"][:, 0, 0] - s["wheel_position_b"][:, 1, 0]).abs()
    return (dx > p["fork_deadzone_m"]).float()


def no_fork_square(s, p):
    dx = (s["wheel_position_b"][:, 0, 0] - s["wheel_position_b"][:, 1, 0]).abs()
    return (p["fork_square_scale"] * dx).square() * s["ground_drive"]


def leg_symmetry(s, p):
    return (s["leg_angle"][:, 0] - s["leg_angle"][:, 1]).square() + p["leg_length_symmetry_scale"] * (
        s["leg_length"][:, 0] - s["leg_length"][:, 1]
    ).square()


def undesired_contact(s, p):
    return (s["undesired_force"] > p["contact_force_n"]).any(-1).float()


def stand_still(s, p):
    yaw = s["yaw"]
    vx, vy = s["velocity_w"][:, :2].unbind(-1)
    slip = (vx * yaw.cos() + vy * yaw.sin()).abs() + (vy * yaw.cos() - vx * yaw.sin()).abs()
    return slip * (s["requested_speed"] == 0) * s["ground_drive"]


def joint_torque(s, p):
    return s["torque"].square().sum(-1)


def wheel_power(s, p):
    return (s["wheel_torque"] * s["wheel_velocity"]).abs().sum(-1)


def action_rate(s, p):
    return (s["action"] - s["previous_action"]).square().sum(-1)


def termination(s, p):
    return s["terminated"].float() * s["termination_multiplier"]


def spin_velocity(s, p):
    return torch.exp(-s["translation_error"].square().sum(-1) / p["spin_velocity_sigma"])


def spin_speed(s, p):
    return torch.exp(-s["speed_error"].square() / p["spin_velocity_sigma"])


def spin_heading(s, p):
    return torch.exp(-s["heading_error"].square() / p["spin_heading_sigma"]) * (s["requested_speed"] > 0)


def spin_velocity_error(s, p):
    return s["translation_error"].square().sum(-1)


def spin_speed_error(s, p):
    return s["speed_error"].square()


def jump_landing(s, p):
    return s["jump"].landing_pulse.float()


def tunnel_crossing(s, p):
    return s["jump"].landing_pulse.float()


TERMS = {
    f.__name__: f
    for f in (
        track_lin_vel,
        lin_vel_error,
        track_ang_vel,
        ang_vel_error,
        track_height,
        height_error,
        flat_roll,
        flat_pitch,
        roll_penalty,
        pitch_penalty,
        vertical_velocity,
        orientation,
        angular_xy,
        no_fork,
        no_fork_square,
        undesired_contact,
        stand_still,
        joint_torque,
        wheel_power,
        action_rate,
        termination,
        spin_velocity,
        spin_speed,
        spin_heading,
        spin_velocity_error,
        spin_speed_error,
        leg_symmetry,
        jump_landing,
        tunnel_crossing,
    )
}


EVENT_TERMS = frozenset(("termination", "jump_landing", "tunnel_crossing"))


def compute_rewards(state: dict, parameters: dict, weights: dict, dt: float, clip: float) -> dict[str, torch.Tensor]:
    unresolved = [name for name, weight in weights.items() if weight is None]
    if unresolved:
        raise ValueError(f"Reward weights must be configured (explicit zero disables): {', '.join(unresolved)}")
    # Event weights are total payouts: neither dt nor the continuous-term clip applies.
    if "tracking_mask" in state:
        gate = motion_height_factor(state["height_error"], parameters["height_gate_shape"])
        state["motion_bonus_mask"] = state["tracking_mask"] * torch.where(state["ground_drive"], gate, 1.0)
    return {
        name: TERMS[name](state, parameters) * weight
        if name in EVENT_TERMS
        else (TERMS[name](state, parameters) * weight).clamp(-2 if name == "undesired_contact" else -clip, clip) * dt
        for name, weight in weights.items()
        if weight != 0
    }
