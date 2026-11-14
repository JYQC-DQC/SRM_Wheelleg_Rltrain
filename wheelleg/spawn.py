from collections.abc import Sequence
from math import acos, cos, hypot, isfinite, pi, sin


def spring_extension_height(
    links: Sequence[float],
    offsets: Sequence[float],
    rear_hip_z_m: float,
    rear_knee_m: Sequence[float],
    spring_pivot_m: Sequence[float],
    rear_pin_m: Sequence[float],
    wheel_m: Sequence[float],
    max_pin_distance_m: float,
    wheel_radius_m: float,
) -> tuple[float, float]:
    """Level body, vertical virtual leg; x/z points in rear1/rear2 zero-pose frames.

    The spring end pins constrain the rear-knee angle. This is a kinematic
    command ceiling, not a global reachable-height or obstacle-clearance proof.
    Returns root height and virtual leg length at the spring extension limit (m).
    IK follows SCUT wheelbipe25_v3/env.py:5604-5631.
    """
    l0, l1, l2 = links

    def geometry(length):
        half = acos((l0**2 * length**2 + l2**2 * (l0**2 - l1**2)) / (2 * l2 * l0**2 * length))
        knee = acos((l0**2 + l1**2 - l0**2 * length**2 / l2**2) / (2 * l0 * l1)) - offsets[5]
        hip = pi / 2 + half - offsets[1]
        c, s = cos(knee), sin(knee)
        px = rear_knee_m[0] + c * rear_pin_m[0] + s * rear_pin_m[2] - spring_pivot_m[0]
        pz = rear_knee_m[2] - s * rear_pin_m[0] + c * rear_pin_m[2] - spring_pivot_m[2]
        wx = rear_knee_m[0] + c * wheel_m[0] + s * wheel_m[2]
        wz = rear_knee_m[2] - s * wheel_m[0] + c * wheel_m[2]
        return hypot(px, pz), wheel_radius_m - rear_hip_z_m + sin(hip) * wx - cos(hip) * wz

    # Triangle limits, with epsilon solely to avoid acos roundoff at the singular endpoints.
    low = l2 * abs(l0 - l1) / l0 + 1e-8
    high = l2 * (l0 + l1) / l0 - 1e-8
    if not geometry(low)[0] < max_pin_distance_m < geometry(high)[0]:
        raise ValueError("Spring maximum pin distance does not bound this five-bar extension branch")
    for _ in range(60):  # Offline bisection; never called in the simulation rollout.
        mid = (low + high) / 2
        if geometry(mid)[0] < max_pin_distance_m:
            low = mid
        else:
            high = mid
    height = geometry(low)[1]
    if not isfinite(height) or height <= 0:
        raise ValueError(f"Invalid spring-limited standing height: {height} m")
    return height, low


def scut_spawn_height(
    base_position: Sequence[float],
    wheel_positions: Sequence[Sequence[float]],
    wheel_radius_m: float,
    clearance_m: float,
) -> float:
    """USD zero-pose world coordinates, meters; validation reference is the grounded height."""
    if len(base_position) != 3 or len(wheel_positions) != 2 or any(len(w) != 3 for w in wheel_positions):
        raise ValueError("Expected base xyz and exactly two wheel xyz coordinates")
    values = [*base_position, *wheel_positions[0], *wheel_positions[1], wheel_radius_m, clearance_m]
    if not all(isfinite(v) for v in values) or wheel_radius_m <= 0 or clearance_m < 0:
        raise ValueError("Spawn coordinates must be finite; radius positive and clearance nonnegative")
    heights = [base_position[2] - wheel[2] + wheel_radius_m for wheel in wheel_positions]
    if abs(heights[0] - heights[1]) > 0.001:
        raise ValueError(f"SCUT wheel grounded heights differ by >1 mm: {heights} m")
    # supermimic_wheelbipe/tools/mujoco_check.py:58: zero-joint FK ~0.185 m.
    if any(abs(height - 0.185) > 0.01 for height in heights):
        raise ValueError(f"SCUT grounded heights differ from 0.185 m by >1 cm: {heights} m")
    return sum(heights) / 2 + clearance_m
