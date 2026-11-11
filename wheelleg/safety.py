import torch


def numerical_failure(joint_velocity: torch.Tensor, linear_velocity: torch.Tensor,
                      angular_velocity: torch.Tensor, thresholds: dict) -> torch.Tensor:
    """SCUT wheelbipe25_v3/env.py:4918-4947; evaluate unmodified physical state."""
    bad = torch.zeros(joint_velocity.shape[0], dtype=torch.bool, device=joint_velocity.device)
    for values, key in ((joint_velocity, "joint_velocity_abs_max"),
                        (linear_velocity, "base_linear_velocity_abs_max"),
                        (angular_velocity, "base_angular_velocity_abs_max")):
        bad |= (~torch.isfinite(values) | (values.abs() > thresholds[key])).any(-1)
    return bad


def airborne_enabled(task: str) -> bool:
    return task not in ("p1-flat", "p2-spin")
