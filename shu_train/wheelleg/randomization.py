import torch


def rotate_imu(vector: torch.Tensor, roll: torch.Tensor, pitch: torch.Tensor) -> torch.Tensor:
    """R_y(pitch) R_x(roll), identical fixed mounting error for gyro and gravity."""
    x, y, z = vector.unbind(-1)
    y1 = roll.cos() * y - roll.sin() * z
    z1 = roll.sin() * y + roll.cos() * z
    return torch.stack((pitch.cos() * x + pitch.sin() * z1, y1, -pitch.sin() * x + pitch.cos() * z1), -1)


def perturb_sensors(
    sensor: torch.Tensor, zero_bias: torch.Tensor, imu_angles: torch.Tensor, legs: list[int]
) -> torch.Tensor:
    result = sensor.clone()
    result[:, :3] = rotate_imu(sensor[:, :3], imu_angles[:, 0], imu_angles[:, 1])
    result[:, 3:6] = rotate_imu(sensor[:, 3:6], imu_angles[:, 0], imu_angles[:, 1])
    result[:, [6 + i for i in legs]] += zero_bias
    return result


def disturbance_progress(iteration: float, phase: int, ramp_iterations: int) -> float:
    return min(max(iteration / ramp_iterations, 0.0), 1.0) if phase == 2 else 0.0


def impulse_velocity(velocity: torch.Tensor, delta: torch.Tensor) -> torch.Tensor:
    result = velocity.clone()
    result[:, :2] += delta
    return result
