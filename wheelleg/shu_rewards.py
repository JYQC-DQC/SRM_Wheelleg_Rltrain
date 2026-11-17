"""Stateless, batched SHU P1 continuous rewards. Events are scored by the caller."""

from collections.abc import Mapping
from math import pi

import torch

DRIVE, AIR, CATCH, RISE, RELEASE = range(5)
_LEGS = (0, 1, 3, 4)  # LF, LR, LW, RF, RR, RW (docs/INTERFACE.md)


def shu_reward_terms(
    state: Mapping[str, torch.Tensor],
    phase: torch.Tensor,
    parameters: Mapping[str, float | torch.Tensor],
    dt: float,
) -> dict[str, torch.Tensor]:
    """Return weighted, individually clipped (where applicable), per-step terms of shape (N,).

    ``phase`` is (N,) int: DRIVE=0, AIR=1 (before any first touch), CATCH=2 (through
    rebounds, until driving is handed back), RISE=3 (after drive takeover), RELEASE=4.
    Use the landing module's reward_phase for the interval just sampled: a first-touch
    interval is CATCH, even though the action at its start was computed in AIR.
    Supply finite same-device inputs for the whole batch; use zeros for unused inputs.
    Rewards do not validate physics: check the raw state for immediate faults independently,
    including during RELEASE when every continuous payoff is zero.
    ``dt`` is the positive policy-step interval in seconds. Sum the returned values and
    add event payments separately; do not apply dt, weights or aggregate clipping again.

    State (all tensors; scalar-per-env fields are (N,), not (N,1)):
        velocity_w, angular_velocity, gravity: (N,3), true world root linear velocity
            [m/s], body angular velocity [rad/s], and body unit gravity projection.
        yaw, heading_ref: current world yaw and latched straight heading [rad]. The caller
            latches at straight entry or driving handoff; no latch in pure rotation.
        vx_cmd, wz_cmd: signed issued translation and turn commands. On a heading segment,
            supply heading_wz_cmd (N,) from the actual post-limit issued yaw command.
            If omitted, reconstruct the legacy raw-command heading target from yaw/ref.
        vx_active, wz_active, heading_active: bool masks from command-segment semantics,
            not command magnitudes. ``wz_active`` denotes a requested turn, not correction;
            ``heading_active`` enables heading correction on a straight segment only.
        height_error, height_target_rate: actual root height above ground minus issued
            target [m], and issued target derivative [m/s] (used only while driving).
        wheel_x_b, wheel_heading_x: (N,2) wheel-center offsets from root [m], projected onto
            body X (fork) and yaw-only heading X (air centering), respectively.
        wheel_rim_speed: (N,2) signed rolling speeds [m/s], positive for forward ground
            motion, computed by the adapter from joint speed, calibrated radius and sign.
        fork_threshold_enabled: bool, fixed per episode. True for standalone flat and
            ordinary births; false for landing air/preset births, including after handoff.
        leg_or_guide_contact, other_undesired_contact: bool, any effective contact during
            this policy step in each penalty group (main wheels excluded from both).
        joint_pos, joint_vel, previous_joint_vel, torque, action, previous_action,
            previous_previous_action: (N,6), all in INTERFACE order. Angles are actual
            asset coordinates; torque is applied drive effort [Nm]; actions are policy
            outputs before actuator mapping. Caller updates history every policy step.

    Parameters (no hardware or undecided tuning defaults):
        leg_lower_rad, leg_upper_rad: (4,) tensors, actual hard angle limits in LF/LR/RF/RR order.
        height_fraction: scalar or (N,) tensor, flat height curriculum fraction; landing inherits it.
        height_wide_weight: initial wide-kernel weight >= 0; height_gate_shape: positive exponent shape.
        vx_tol_max, vx_tol_knee, wz_tol_max, wz_tol_knee: positive active tracking tolerance
            parameters in the axis units, for tol(|cmd|) = max * |cmd| / (knee + |cmd|).
        vx_error_sigma, wz_error_sigma: positive broad error-kernel denominators (axis units squared).
            Broad error cost is exp(-error**2/sigma)-1. Heading/zero yaw error uses
            that same wz penalty, without a yaw positive reward.
        lateral_velocity_scale: scale in 1/(m/s) before squaring straight-line lateral slip.
        heading_kp, heading_max_wz: gain [1/s] and positive limit [rad/s]; required only
            when heading_wz_cmd is omitted, not used to re-limit an issued correction.
    """
    drive, air, catch, rise = (phase == value for value in (DRIVE, AIR, CATCH, RISE))
    drop = air | catch
    controlled = drive | drop | rise
    on_ground_terms = drive | catch | rise  # CATCH does not revert to AIR on a bounce.
    p = parameters
    s = state

    vx_active, wz_active = s["vx_active"], s["wz_active"]
    straight = vx_active & ~wz_active
    use_heading = straight & s["heading_active"]
    yaw, ref = s["yaw"], s["heading_ref"]
    if "heading_wz_cmd" in s:
        heading_wz = s["heading_wz_cmd"]
    else:
        yaw_error = torch.remainder(ref - yaw + pi, 2 * pi) - pi
        heading_wz = (p["heading_kp"] * yaw_error).clamp(-p["heading_max_wz"], p["heading_max_wz"])
    yaw_target = torch.where(wz_active, s["wz_cmd"], torch.where(use_heading, heading_wz, 0.0))

    vx_w, vy_w, vz_w = s["velocity_w"].unbind(-1)
    cy, sy = yaw.cos(), yaw.sin()
    forward = vx_w * cy + vy_w * sy
    side_yaw = torch.where(use_heading, ref, yaw)
    lateral = vy_w * side_yaw.cos() - vx_w * side_yaw.sin()
    # L1 depends on axes: use current yaw axes, not world XYZ or full tilted body axes.
    horizontal_l1 = forward.abs() + (vy_w * cy - vx_w * sy).abs()
    vx_error = forward - s["vx_cmd"]
    wx, wy, wz = s["angular_velocity"].unbind(-1)
    wz_error = wz - torch.where(rise, 0.0, yaw_target)
    one = torch.ones_like(vz_w)
    steady_scale = torch.where(rise, 0.5, one)

    h_error = s["height_error"]
    # Clamp the annealing fraction before multiplying by the initial weight.
    fraction = torch.as_tensor(p["height_fraction"], device=h_error.device, dtype=h_error.dtype)
    wide_weight = p["height_wide_weight"] * ((0.8 - fraction) / 0.2).clamp(0.0, 1.0)
    height = (torch.exp(-h_error.square() / 0.001) + wide_weight * torch.exp(-h_error.square() / 0.025)) / (
        1.0 + wide_weight
    )
    h_abs = h_error.abs()
    u = ((h_abs - 0.03) / 0.05).clamp(0.0, 1.0)
    # Same normalized exponential as (exp(-k*u**2)-exp(-k))/(1-exp(-k)), without cancellation for small k.
    k = torch.as_tensor(p["height_gate_shape"], device=h_error.device, dtype=h_error.dtype)
    u_sq = u.square()
    height_gate = torch.exp(-k * u_sq) * torch.expm1(-k * (1 - u_sq)) / torch.expm1(-k)
    height_gate = torch.where(h_abs >= 0.08, 0.0, height_gate)

    def tracking(axis: str, target: torch.Tensor, error: torch.Tensor) -> torch.Tensor:
        speed = target.abs()
        # Exact zero can occur during an active segment (slew/reversal). Pay no bonus;
        # do not change the segment masks or suppress the separate error penalty.
        # Divide by |cmd| first so tiny nonzero commands have no fixed tolerance floor.
        relative_error = error / torch.where(speed > 0, speed, 1.0)
        scaled_error = relative_error * ((p[f"{axis}_tol_knee"] + speed) / p[f"{axis}_tol_max"])
        return torch.where(speed > 0, torch.exp(-scaled_error.square()) * height_gate, 0.0)

    gx, gy = s["gravity"][:, :2].unbind(-1)
    tilt = -100.0 * (torch.where(air, 0.0, gx.square()) + gy.square())
    # Only driving follows the height target derivative; AIR/CATCH penalize raw world vz.
    vz_error = vz_w - torch.where(drive, s["height_target_rate"], 0.0)
    dx = s["wheel_x_b"][:, 0] - s["wheel_x_b"][:, 1]
    leg_contact, other_contact = s["leg_or_guide_contact"], s["other_undesired_contact"]
    contact_rate = torch.where(
        other_contact | (leg_contact & ~rise), -2.0, torch.where(leg_contact, -1.0, torch.zeros_like(vz_w))
    )

    q = s["joint_pos"][:, _LEGS]
    lo, hi = p["leg_lower_rad"], p["leg_upper_rad"]
    margin = 0.015 * (hi - lo)
    excess = ((lo + margin - q).clamp_min(0.0) + (q - (hi - margin)).clamp_min(0.0)).sum(-1)
    qd = s["joint_vel"]
    qdd = (qd - s["previous_joint_vel"]) / dt
    da = s["action"] - s["previous_action"]
    dda_leg = da[:, _LEGS] - (s["previous_action"] - s["previous_previous_action"])[:, _LEGS]
    smooth_scale = torch.where(drop, 0.4, one)

    def paid(rate: torch.Tensor, enabled: torch.Tensor, lower: float = -1.0, upper: float = 1.0) -> torch.Tensor:
        return torch.where(enabled, rate.clamp(lower, upper) * dt, 0.0)

    center_error_sq = s["wheel_heading_x"].square()
    rim_error_sq = (s["wheel_rim_speed"] - forward[:, None]).square()
    return {
        "track_lin_vel": paid(tracking("vx", s["vx_cmd"], vx_error), drive & vx_active),
        "lin_vel_error": paid(torch.expm1(-vx_error.square() / p["vx_error_sigma"]), drive & vx_active),
        "track_ang_vel": paid(tracking("wz", s["wz_cmd"], wz_error), drive & wz_active),
        "ang_vel_error": paid(torch.expm1(-wz_error.square() / p["wz_error_sigma"]), drive | rise) * steady_scale,
        "lateral_velocity": paid(-(p["lateral_velocity_scale"] * lateral).square(), drive & straight),
        "stand_still": paid(-horizontal_l1, (drive & ~vx_active) | rise) * steady_scale,
        "track_height": paid(height, drive),
        "vertical_velocity": paid(-vz_error.square(), drive | drop),
        "angular_xy": paid(-0.20 * (wx.square() + wy.square()), controlled),
        "orientation": paid(tilt, controlled) * torch.where(rise, 0.6, one),
        "no_fork_square": paid(-(5.0 * dx).square(), on_ground_terms),
        "no_fork": paid(-(dx.abs() > 0.05).to(dx.dtype), drive & s["fork_threshold_enabled"]),
        "undesired_contact": paid(contact_rate, on_ground_terms, -2.0, 0.0),
        "leg_joint_vel": paid(-5e-5 * smooth_scale * qd[:, _LEGS].square().sum(-1), controlled),
        "joint_acc": paid(-2.5e-7 * smooth_scale * qdd.square().sum(-1), controlled),
        "action_rate": paid(-0.01 * smooth_scale * da.square().sum(-1), controlled),
        "action_smoothness_leg": paid(-0.05 * smooth_scale * dda_leg.square().sum(-1), controlled),
        "joint_torque": paid(-1e-4 * s["torque"].square().sum(-1), controlled),
        "leg_soft_limits": paid(-excess, controlled),
        "air_wheel_center": paid(4.0 * torch.expm1(-center_error_sq / 0.02).mean(-1), air, -4.0, 0.0),
        "air_wheel_speed": paid(6.0 * torch.expm1(-rim_error_sq.mean(-1) / 1.0), air, -6.0, 0.0),
    }
