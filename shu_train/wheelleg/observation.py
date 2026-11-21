import numpy as np

from .config import PolicyConfig, RobotConfig

# 唯一布局定义；生成的 C 偏移从这里读取。角速度/重力在机体系，命令 vx 为机体前向。
OBS_FIELDS = (
    ("command", 3),
    ("height", 1),
    ("angular_velocity", 3),
    ("gravity", 3),
    ("joint_position", 4),
    ("joint_velocity", 6),
    ("previous_action", 6),
)
OBS_DIM = sum(size for _, size in OBS_FIELDS)
POLICY_OBS_DIM = OBS_DIM + 1  # packed current frame plus actor-only jump_request_m


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
) -> np.ndarray:
    """输入已按合同归一到 SI；支持 (..., width) 批量；不加训练噪声。"""
    if joint_position.shape != (*command.shape[:-1], 6):
        raise ValueError("joint_position: expected six drive channels")
    arrays = (
        command,
        height,
        angular_velocity,
        gravity,
        joint_position[..., list(robot.leg_indices)],
        joint_velocity,
        previous_action,
    )
    batch_shape = command.shape[:-1]
    for (name, size), values in zip(OBS_FIELDS, arrays, strict=True):
        if values.shape != (*batch_shape, size):
            raise ValueError(f"{name}: expected values of shape {(*batch_shape, size)}")
    if any(robot.q_default_rad[i] is None for i in robot.leg_indices):
        raise ValueError("robot.q_default_rad: leg zero/default calibration is incomplete")
    indices = list(robot.leg_indices)
    relative_q = joint_position[..., indices] - np.asarray([robot.q_default_rad[i] for i in indices])
    raw = (command, height, angular_velocity, gravity, relative_q, joint_velocity, previous_action)
    scales = (
        np.asarray(policy.command_scale),
        policy.height_scale,
        policy.angular_velocity_scale,
        policy.gravity_scale,
        policy.joint_position_scale,
        policy.joint_velocity_scale,
        1.0,
    )
    clips = dict(robot.observation_clip)
    parts = [
        np.nan_to_num(np.clip(value, *clips[name]) * scale, nan=0.0, posinf=0.0, neginf=0.0)
        for (name, _), value, scale in zip(OBS_FIELDS, raw, scales, strict=True)
    ]
    return np.concatenate(parts, axis=-1).astype(np.float32)
