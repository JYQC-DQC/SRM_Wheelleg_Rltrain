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
        if values.shape != (*batch_shape, size):
            raise ValueError(f"{name}: expected values of shape {(*batch_shape, size)}")
    if any(robot.q_default_rad[i] is None for i in robot.leg_indices):
        raise ValueError("robot.q_default_rad: leg zero/default calibration is incomplete")
    relative_q = np.zeros(joint_position.shape, dtype=np.float32)
    for i in robot.leg_indices:  # 四个固定通道，不是逐环境循环
        relative_q[..., i] = joint_position[..., i] - robot.q_default_rad[i]
    raw = (command, height, angular_velocity, gravity, relative_q, joint_velocity, previous_action, mode)
    scales = (
        np.asarray(policy.command_scale),
        policy.height_scale,
        policy.angular_velocity_scale,
        policy.gravity_scale,
        policy.joint_position_scale,
        policy.joint_velocity_scale,
        1.0,
        1.0,
    )
    clips = dict(robot.observation_clip)
    parts = [
        np.nan_to_num(np.clip(value, *clips[name]) * scale, nan=0.0, posinf=0.0, neginf=0.0)
        for (name, _), value, scale in zip(OBS_FIELDS, raw, scales, strict=True)
    ]
    return np.concatenate(parts, axis=-1).astype(np.float32)
