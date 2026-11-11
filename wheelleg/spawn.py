from math import isfinite
from collections.abc import Sequence


def scut_spawn_height(base_position: Sequence[float], wheel_positions: Sequence[Sequence[float]],
                      wheel_radius_m: float, clearance_m: float) -> float:
    """USD zero-pose world coordinates, meters; validation reference is the grounded height."""
    if len(base_position) != 3 or len(wheel_positions) != 2 or any(len(w) != 3 for w in wheel_positions):
        raise ValueError("Expected base xyz and exactly two wheel xyz coordinates")
    values = [*base_position, *wheel_positions[0], *wheel_positions[1], wheel_radius_m, clearance_m]
    if not all(isfinite(v) for v in values) or wheel_radius_m <= 0 or clearance_m < 0:
        raise ValueError("Spawn coordinates must be finite; radius positive and clearance nonnegative")
    heights = [base_position[2]-wheel[2]+wheel_radius_m for wheel in wheel_positions]
    if abs(heights[0]-heights[1]) > 0.001:
        raise ValueError(f"SCUT wheel grounded heights differ by >1 mm: {heights} m")
    # supermimic_wheelbipe/tools/mujoco_check.py:58: zero-joint FK ~0.185 m.
    if any(abs(height-0.185) > 0.01 for height in heights):
        raise ValueError(f"SCUT grounded heights differ from 0.185 m by >1 cm: {heights} m")
    return sum(heights)/2+clearance_m
