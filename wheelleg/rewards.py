"""One vectorized term per log channel. Guide sections 6.1, 6.5, 6.6."""

import torch


def track_lin_vel(s, p):
    return torch.exp(-s["linear_error"].square() / p["linear_sigma"]) * s["tracking_mask"] * s["height_gate"]


def lin_vel_error(s, p):
    return (0.25 * s["linear_error"]).square() * s["tracking_mask"] * s["height_gate"]


def track_ang_vel(s, p):
    return torch.exp(-s["angular_error"].square() / p["angular_sigma"]) * s["tracking_mask"] * s["height_gate"]


def ang_vel_error(s, p):
    return (0.5 * s["angular_error"]).square() * s["tracking_mask"] * s["height_gate"]


def track_height(s, p):
    return torch.exp(-s["height_error"].square() / p["height_sigma"]) * s["height_mask"]


def track_height_wide(s, p):
    # 改自 SCUT wheelbipe25_v3/env.py:3831 (track_height_exp，V14 的 height_sigma=0.025)：
    # 紧核在误差 7 cm 处只有 0.007，没有梯度；宽核让腿折叠的姿态也能感到“再高一点更好”。
    return torch.exp(-s["height_error"].square() / p["height_wide_sigma"]) * s["height_mask"]


def height_error(s, p):
    # ground_mask: 腾空时不罚，SCUT V14/env_cfg.py:1560 (track_height_square → 0)。
    return (10 * s["height_error"]).square() * s["height_mask"] * s["ground_mask"]


def flat_roll(s, p):
    return torch.exp(-s["gravity"][:, 1].square() / p["roll_sigma"])


def flat_pitch(s, p):
    return torch.exp(-s["gravity"][:, 0].square() / p["pitch_sigma"])


def roll_penalty(s, p):
    return ((2 * torch.exp(-s["heading_velocity"][:, 0].square() / 3) + 2) * s["gravity"][:, 1]).square()


def pitch_penalty(s, p):
    # ground_mask: 腾空时不罚，SCUT V14/env_cfg.py:1551 (flat_orientation_y_v → 0)。
    # 保留原来的指数衰减形式；P1 系数 1/4/3 使 3 m/s 时平方后的强度约为零速的 60%。
    factor = (
        p["pitch_velocity_amplitude"] * torch.exp(-s["heading_velocity"][:, 0].square() / p["pitch_velocity_sigma"])
        + p["pitch_velocity_offset"]
    )
    return (factor * s["gravity"][:, 0]).square() * s["ground_mask"]


def vertical_velocity(s, p):
    # World vz relative to the height-reference rate: commanded height changes are free, bobbing is not.
    # The body-frame vz used before (SCUT V14 lin_vel_z) also charged forward speed whenever the body leaned.
    return (s["velocity_w"][:, 2] - s["height_target_rate"]).square() * s["height_mask"]


def angular_xy(s, p):
    return s["angular_velocity"][:, :2].square().sum(-1)


def no_fork(s, p):
    dx = (s["wheel_position_b"][:, 0, 0] - s["wheel_position_b"][:, 1, 0]).abs()
    return (dx > p["fork_deadzone_m"]).float()


def no_fork_square(s, p):
    dx = (s["wheel_position_b"][:, 0, 0] - s["wheel_position_b"][:, 1, 0]).abs()
    return (p["fork_square_scale"] * (dx - p["fork_deadzone_m"]).clamp_min(0)).square()


def leg_symmetry(s, p):
    return (s["leg_angle"][:, 0] - s["leg_angle"][:, 1]).square() + p["leg_length_symmetry_scale"] * (
        s["leg_length"][:, 0] - s["leg_length"][:, 1]
    ).square()


def undesired_contact(s, p):
    # 改自 SCUT wheelbipe25_v3/env.py:3929-3935: 二值项，名单变长后不随触地刚体数放大。
    return (s["undesired_force"] > p["contact_force_n"]).any(-1).float() * s["contact_multiplier"]


def stand_still(s, p):
    # 改自 SCUT wheelbipe25_v3/env.py:3748-3751 (stand_still_lin_vel): 绝对值，慢速溜车也有梯度。
    # Heading-frame horizontal velocity, so vertical motion of a pitched body does not count as drifting.
    return s["heading_velocity"].abs().sum(-1) * (s["requested_speed"] < p["stand_deadzone"])


def joint_torque(s, p):
    return s["torque"].square().sum(-1)


def wheel_power(s, p):
    return (s["wheel_torque"] * s["wheel_velocity"]).abs().sum(-1)


def action_rate(s, p):
    return (s["action"] - s["previous_action"]).square().sum(-1)


# 以下四项改自 SCUT wheelbipe25_v3/env.py:3515-3561，权重见 V14/env_cfg.py:869-883。
def leg_joint_vel(s, p):
    return s["hip_velocity"].square().sum(-1)  # (N,), (rad/s)^2


def leg_joint_acc(s, p):
    # 改自 SCUT wheelbipe25_v3/env.py:3508 (V14 权重 -5e-7)；本项目按策略步差分，SCUT 读取 joint_acc。
    return s["hip_acceleration"].square().sum(-1)  # (N,), (rad/s^2)^2


def wheel_vel(s, p):
    return s["wheel_velocity"].square().sum(-1)  # (N,), (rad/s)^2


def action_smoothness_leg(s, p):
    return s["leg_action_second_difference"].square().sum(-1)


def action_smoothness_wheel(s, p):
    return s["wheel_action_second_difference"].square().sum(-1)


def termination(s, p):
    return s["terminated"].float() * s["termination_multiplier"]


# 三个小陀螺正奖励乘高度门控：趴低自旋或平移不得分，与 P1 的跟踪奖励一致。
def spin_velocity(s, p):
    return torch.exp(-s["translation_error"].square().sum(-1) / p["spin_velocity_sigma"]) * s["height_gate"]


def spin_speed(s, p):
    return torch.exp(-s["speed_error"].square() / p["spin_velocity_sigma"]) * s["height_gate"]


def spin_heading(s, p):
    return (
        torch.exp(-s["heading_error"].square() / p["spin_heading_sigma"])
        * (s["requested_speed"] > p["stand_deadzone"])
        * s["height_gate"]
    )


def spin_heading_error(s, p):
    # 改自 SCUT wheelbipe_V14/env.py:1049 (gimbal_spin_heading_error_square)，门控与 spin_heading 相同。
    return (p["spin_heading_square_scale"] * s["heading_error"]).square() * (s["requested_speed"] > p["stand_deadzone"])


def spin_velocity_error(s, p):
    return s["translation_error"].square().sum(-1)


def spin_speed_error(s, p):
    return s["speed_error"].square()


def jump_apex(s, p):
    error = (s["jump"].height - (s["jump"].apex_z - s["jump"].start_z)).clamp_min(0)
    return torch.exp(-error.square() / s["jump"].settings["apex_sigma"]) * s["jump"].apex_pulse


def jump_landing(s, p):
    return s["jump"].landing_pulse.float()


def jump_flight(s, p):
    return s["jump_ref"]["flight"].float()


def jump_crouch(s, p):
    error = (s["leg_length"] - s["jump"].settings["crouch_leg_length_m"]).abs().sum(-1)
    return torch.exp(-4 * error) * s["jump_ref"]["crouch"] * s["guidance_scale"]


def jump_takeoff(s, p):
    target = s["jump_ref"]["takeoff_velocity"]
    ratio = s["velocity_w"][:, 2] / target.clamp_min(torch.finfo(target.dtype).eps)
    return ratio.clamp(0, 1) * s["jump_ref"]["push"] * s["guidance_scale"]


def jump_push_symmetry(s, p):
    force = s["wheel_force"].clamp_min(0)
    return (1 - (force[:, 0] - force[:, 1]).abs() / force.sum(-1).clamp_min(1)) * s["jump_ref"]["push"]


def jump_tuck(s, p):
    error = (s["leg_length"] - s["jump"].settings["tuck_leg_length_m"]).abs().sum(-1)
    return torch.exp(-4 * error) * s["jump_ref"]["tuck"] * s["guidance_scale"]


def jump_prepare(s, p):
    error = (s["leg_length"] - s["jump"].settings["landing_leg_length_m"]).abs().sum(-1)
    return torch.exp(-4 * error) * s["jump_ref"]["prepare"] * s["guidance_scale"]


def jump_impact(s, p):
    return (s["hip_torque"].square().amax(-1) + s["hip_velocity"].square().sum(-1)) * s["jump"].touchdown_pulse


def jump_asymmetric_landing(s, p):
    times = s["jump"].touchdown_time
    return ((times[:, 0] - times[:, 1]).abs() > s["jump"].settings["max_touchdown_difference_s"]).float() * s[
        "jump"
    ].touchdown_pulse


def uncommanded_flight(s, p):
    return (s["airborne"] & ~s["jump"].active & ~s["jump"].landing_pulse).float()


TERMS = {
    f.__name__: f
    for f in (
        track_lin_vel,
        lin_vel_error,
        track_ang_vel,
        ang_vel_error,
        track_height,
        track_height_wide,
        height_error,
        flat_roll,
        flat_pitch,
        roll_penalty,
        pitch_penalty,
        vertical_velocity,
        angular_xy,
        no_fork,
        no_fork_square,
        undesired_contact,
        stand_still,
        joint_torque,
        wheel_power,
        action_rate,
        leg_joint_vel,
        leg_joint_acc,
        wheel_vel,
        action_smoothness_leg,
        action_smoothness_wheel,
        termination,
        spin_velocity,
        spin_speed,
        spin_heading,
        spin_heading_error,
        spin_velocity_error,
        spin_speed_error,
        leg_symmetry,
        jump_apex,
        jump_landing,
        jump_flight,
        jump_crouch,
        jump_takeoff,
        jump_push_symmetry,
        jump_tuck,
        jump_prepare,
        jump_impact,
        jump_asymmetric_landing,
        uncommanded_flight,
    )
}


EVENT_TERMS = frozenset(
    (
        "termination",
        "jump_apex",
        "jump_landing",
        "jump_impact",
        "jump_asymmetric_landing",
        "tunnel_crossing",
        "stair_impact",
        # Paid by wheelleg/landing_rewards.py as per-event totals.
        "landing_progress",
        "landing_outcome",
        "landing_guide_contact",
    )
)


def compute_rewards(state: dict, parameters: dict, weights: dict, dt: float, clip: float) -> dict[str, torch.Tensor]:
    # Event weights are total payouts: neither dt nor the continuous-term clip applies.
    return {
        name: TERMS[name](state, parameters) * weight
        if name in EVENT_TERMS
        else (TERMS[name](state, parameters) * weight * dt).clamp(-clip, clip)
        for name, weight in weights.items()
        if weight != 0
    }
