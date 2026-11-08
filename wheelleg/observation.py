import numpy as np

from .config import PolicyConfig, RobotConfig

# 唯一布局定义；生成的 C 偏移从这里读取。角速度/重力在机体系，命令 vx 为机体前向。
OBS_FIELDS = (
    ("command", 3),
    ("height", 1),
    ("angular_velocity", 3),
    ("gravity", 3),
    ("joint_position", 6),
    ("joint_velocity", 6),
    ("previous_action", 6),
    ("mode", 7),
)
OBS_DIM = sum(size for _, size in OBS_FIELDS)


def build_observation(
    robot: RobotConfig,
    policy: PolicyConfig,
    *,
    command: np.ndarray,
    height: np.ndarray,
    angular_velocity: np.ndarray,
    gravity: np.ndarray,
    joint_position: np.ndarray,
    joint_velocity: np.ndarray,
    previous_action: np.ndarray,
    mode: np.ndarray,
) -> np.ndarray:
    """输入已按合同归一到 SI；支持 (..., width) 批量；不加训练噪声。"""
    arrays = (command, height, angular_velocity, gravity, joint_position, joint_velocity, previous_action, mode)
    batch_shape = command.shape[:-1]
    for (name, size), values in zip(OBS_FIELDS, arrays, strict=True):
        if values.shape != (*batch_shape, size) or not np.isfinite(values).all():
            raise ValueError(f"{name}: expected finite values of shape {(*batch_shape, size)}")
    if any(robot.q_default_rad[i] is None for i in robot.leg_indices):
        raise ValueError("robot.q_default_rad: leg zero/default calibration is incomplete")
    relative_q = np.zeros(joint_position.shape, dtype=np.float32)
    for i in robot.leg_indices:  # 四个固定通道，不是逐环境循环
        relative_q[..., i] = joint_position[..., i] - robot.q_default_rad[i]
    return np.concatenate(
        (
            command * np.asarray(policy.command_scale),
            height * policy.height_scale,
            angular_velocity * policy.angular_velocity_scale,
            gravity * policy.gravity_scale,
            relative_q * policy.joint_position_scale,
            joint_velocity * policy.joint_velocity_scale,
            previous_action,
            mode,
        ),
        axis=-1,
    ).astype(np.float32)
