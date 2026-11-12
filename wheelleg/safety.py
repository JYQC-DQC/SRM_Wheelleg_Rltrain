import torch


def numerical_failure(
    joint_velocity: torch.Tensor, linear_velocity: torch.Tensor, angular_velocity: torch.Tensor, thresholds: dict
) -> torch.Tensor:
    """SCUT wheelbipe25_v3/env.py:4918-4947; evaluate unmodified physical state."""
    bad = torch.zeros(joint_velocity.shape[0], dtype=torch.bool, device=joint_velocity.device)
    for values, key in (
        (joint_velocity, "joint_velocity_abs_max"),
        (linear_velocity, "base_linear_velocity_abs_max"),
        (angular_velocity, "base_angular_velocity_abs_max"),
    ):
        bad |= (~torch.isfinite(values) | (values.abs() > thresholds[key])).any(-1)
    return bad


def nonfinite_pose(
    root_position: torch.Tensor, root_quaternion: torch.Tensor, joint_position: torch.Tensor
) -> torch.Tensor:
    """Poses feed height, attitude and wheel-geometry rewards; finite velocities do not imply a finite pose."""
    return ~(
        torch.isfinite(root_position).all(-1)
        & torch.isfinite(root_quaternion).all(-1)
        & torch.isfinite(joint_position).all(-1)
    )


def airborne_enabled(task: str) -> bool:
    return task not in ("p1-flat", "p2-spin")
