from math import isfinite

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


def leaky_termination(
    counter: torch.Tensor, condition: torch.Tensor, dt: float, duration_s: float, decay_s: float
) -> tuple[torch.Tensor, torch.Tensor]:
    """Return (updated counter, sustained termination mask), without modifying the inputs.

    ``counter`` is a float32/float64 tensor of elapsed policy-step equivalents, one
    per env; initialize/reset it to zero. ``condition`` is a same-shape/device bool
    tensor for ordinary physical risk only. A bad interval adds 1; a clean interval
    subtracts ``duration_s / decay_s``, so a full counter drains in ``decay_s``.
    Keep ``dt`` fixed for a counter's lifetime; all three times are positive host scalars.
    The caller handles release/reset masks and ORs immediate faults separately, never
    feeding numerical anomalies, hard impacts or external timeouts into ``condition``.
    """
    if not all(isfinite(value) and value > 0 for value in (dt, duration_s, decay_s)):
        raise ValueError("dt, duration_s and decay_s must be finite and positive")
    limit = duration_s / dt
    leak = duration_s / decay_s
    updated = torch.where(condition, counter + 1.0, counter - leak).clamp(0.0, limit)
    # Fractional leakage can leave a value just below the boundary by rounding error.
    tolerance = min(0.5, 4.0 * torch.finfo(counter.dtype).eps * limit)
    reached = condition & (updated >= limit - tolerance)
    return torch.where(reached, limit, updated), reached


def airborne_enabled(task: str) -> bool:
    return task not in ("p1-flat", "p2-spin")
