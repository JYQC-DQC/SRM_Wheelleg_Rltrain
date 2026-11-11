from dataclasses import dataclass
from math import isfinite
from pathlib import Path

import yaml

# Shared actor/critic raw-quantity limits; SCUT wheelbipe_V14/cfg_utils.py:75-124.
OBSERVATION_CLIP_FIELDS = (
    "command",
    "height",
    "angular_velocity",
    "gravity",
    "joint_position",
    "joint_velocity",
    "previous_action",
    "mode",
    "base_linear_velocity",
    "base_height",
    "torque",
    "wheel_linear_velocity",
    "kp",
    "kd",
    "delay_steps",
    "mass_ratio",
    "wheel_contact",
    "material",
    "spring_force",
    "voltage_scale",
    "power_scale",
    "command_error",
    "height_scan",
)


@dataclass(frozen=True)
class RobotConfig:
    name: str
    variant: str
    control_hz: int
    policy_hz: int
    wheel_reduction_ratio: float
    spring_nominal_force_n: float
    spring_stroke_m: float
    joint_order: tuple[str, ...]
    leg_indices: tuple[int, ...]
    wheel_indices: tuple[int, ...]
    q_default_rad: tuple[float | None, ...]
    q_zero_offset_rad: tuple[float | None, ...]
    motor_direction: tuple[int | None, ...]
    can_bus: tuple[int, ...]
    pending_measurements: tuple[str, ...]
    observation_clip: tuple[tuple[str, tuple[float, float]], ...]

    @property
    def decimation(self) -> int:
        return self.control_hz // self.policy_hz


@dataclass(frozen=True)
class PolicyConfig:
    name: str
    obs_version: int
    hidden_dims: tuple[int, ...]
    activation: str
    command_scale: tuple[float, ...]
    height_scale: float
    angular_velocity_scale: float
    gravity_scale: float
    joint_position_scale: float
    joint_velocity_scale: float
    action_scales: tuple[float, ...]
    action_clip: float | None
    kp: tuple[float | None, ...]
    kd: tuple[float | None, ...]
    torque_limit_nm: tuple[float | None, ...]


def _positive(value: object, field: str) -> None:
    if type(value) not in (int, float) or not isfinite(value) or value <= 0:
        raise ValueError(f"{field}: expected a finite positive number")


def _vector(value: list, length: int, field: str, *, allow_missing: bool = False) -> tuple:
    if type(value) is not list or len(value) != length:
        raise ValueError(f"{field}: expected {length} entries")
    for i, item in enumerate(value):
        if item is None and allow_missing:
            continue
        if type(item) not in (int, float) or not isfinite(item):
            raise ValueError(f"{field}[{i}]: expected a finite number")
    return tuple(value)


def load_robot(path: str | Path) -> RobotConfig:
    path = Path(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if type(data) is not dict:
        raise ValueError(f"{path}: expected a YAML mapping")
    try:
        for key in ("control_hz", "policy_hz"):
            if type(data[key]) is not int or data[key] <= 0:
                raise ValueError(f"{path}:{key}: expected a positive integer")
        if data["control_hz"] % data["policy_hz"]:
            raise ValueError(f"{path}: control_hz must be divisible by policy_hz")
        for key in ("wheel_reduction_ratio", "spring_nominal_force_n", "spring_stroke_m"):
            _positive(data[key], f"{path}:{key}")
        names = data["joint_order"]
        if len(names) != 6 or any(type(name) is not str for name in names) or len(set(names)) != 6:
            raise ValueError(f"{path}: joint_order must contain six unique names")
        legs, wheels = data["leg_indices"], data["wheel_indices"]
        if len(legs) != 4 or len(wheels) != 2 or sorted(legs + wheels) != list(range(6)):
            raise ValueError(f"{path}: leg_indices/wheel_indices must partition six joints")
        if any(type(i) is not int for i in legs + wheels):
            raise ValueError(f"{path}: joint indices must be integers")
        vectors = {
            key: _vector(data[key], 6, f"{path}:{key}", allow_missing=True)
            for key in ("q_default_rad", "q_zero_offset_rad", "motor_direction")
        }
        if any(x is not None and x not in (-1, 1) for x in vectors["motor_direction"]):
            raise ValueError(f"{path}: motor_direction must contain -1, 1 or null")
        buses = _vector(data["can_bus"], 6, f"{path}:can_bus")
        if any(type(x) is not int or x not in (1, 2, 3) for x in buses):
            raise ValueError(f"{path}: can_bus must contain integer bus indices 1..3")
        pending = tuple(key for key, value in data["pending_measurements"].items() if value is None)
        clips = []
        for key in OBSERVATION_CLIP_FIELDS:
            field = f"training.observation_clip.{key}"
            if key not in data["training"]["observation_clip"]:
                raise ValueError(f"{path}: missing required field {field}")
            bounds = _vector(data["training"]["observation_clip"][key], 2, f"{path}:{field}")
            if bounds[0] >= bounds[1]:
                raise ValueError(f"{path}:{field}: expected lower < upper")
            clips.append((key, bounds))
        return RobotConfig(
            name=data["name"],
            variant=data["variant"],
            control_hz=data["control_hz"],
            policy_hz=data["policy_hz"],
            wheel_reduction_ratio=data["wheel_reduction_ratio"],
            spring_nominal_force_n=data["spring_nominal_force_n"],
            spring_stroke_m=data["spring_stroke_m"],
            joint_order=tuple(names),
            leg_indices=tuple(legs),
            wheel_indices=tuple(wheels),
            can_bus=buses,
            pending_measurements=pending,
            observation_clip=tuple(clips),
            **vectors,
        )
    except KeyError as error:
        raise ValueError(f"{path}: missing required field {error.args[0]}") from error


def load_policy(path: str | Path) -> PolicyConfig:
    path = Path(path)
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if type(data) is not dict:
        raise ValueError(f"{path}: expected a YAML mapping")
    try:
        if data["obs_version"] != 2:
            raise ValueError(f"{path}: this implementation supports obs_version 2 only")
        dims = data["hidden_dims"]
        if not dims or any(type(n) is not int or n <= 0 for n in dims):
            raise ValueError(f"{path}: hidden_dims must contain positive integers")
        if data["activation"] != "elu":
            raise ValueError(f"{path}: expected elu activation")
        scales = data["observation_scales"]
        command = _vector(scales["command"], 3, f"{path}:observation_scales.command")
        for value in command:
            _positive(value, f"{path}:observation_scales.command")
        scalar_names = ("height", "angular_velocity", "gravity", "joint_position", "joint_velocity")
        for key in scalar_names:
            _positive(scales[key], f"{path}:observation_scales.{key}")
        action = _vector(data["action_scales"], 6, f"{path}:action_scales")
        for value in action:
            _positive(value, f"{path}:action_scales")
        if data["action_clip"] is not None:
            _positive(data["action_clip"], f"{path}:action_clip")
        vectors = {
            key: _vector(data[key], 6, f"{path}:{key}", allow_missing=True) for key in ("kp", "kd", "torque_limit_nm")
        }
        for key, values in vectors.items():
            if any(x is not None and (x < 0 or (key == "torque_limit_nm" and x == 0)) for x in values):
                raise ValueError(f"{path}:{key}: invalid gain or torque limit")
        return PolicyConfig(
            name=data["name"],
            obs_version=data["obs_version"],
            hidden_dims=tuple(dims),
            activation=data["activation"],
            command_scale=command,
            action_scales=action,
            action_clip=data["action_clip"],
            **{f"{key}_scale": scales[key] for key in scalar_names},
            **vectors,
        )
    except KeyError as error:
        raise ValueError(f"{path}: missing required field {error.args[0]}") from error


def missing_parameters(robot: RobotConfig, policy: PolicyConfig) -> list[str]:
    missing = list(robot.pending_measurements)
    for key in ("q_default_rad", "q_zero_offset_rad", "motor_direction"):
        missing.extend(f"robot.{key}[{i}]" for i, x in enumerate(getattr(robot, key)) if x is None)
    for key in ("kp", "kd", "torque_limit_nm"):
        missing.extend(f"policy.{key}[{i}]" for i, x in enumerate(getattr(policy, key)) if x is None)
    # Guide v2.1: null intentionally disables clipping of the raw policy output.
    return missing
