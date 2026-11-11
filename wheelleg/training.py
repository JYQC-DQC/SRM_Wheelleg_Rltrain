from dataclasses import dataclass
from math import isfinite
from pathlib import Path
from types import MappingProxyType

import yaml

from .config import PolicyConfig, RobotConfig, load_policy, load_robot, missing_parameters
from .tasks import TASKS


def _freeze(value):
    if type(value) is dict:
        return MappingProxyType({k: _freeze(v) for k, v in value.items()})
    if type(value) is list:
        return tuple(_freeze(v) for v in value)
    return value


def mutable(value):
    """Convert the immutable config snapshot for Isaac/rsl_rl serialization."""
    if type(value) is MappingProxyType:
        return {k: mutable(v) for k, v in value.items()}
    if type(value) is tuple:
        return [mutable(v) for v in value]
    return value


def null_fields(value, prefix: str) -> list[str]:
    if value is None:
        return [prefix]
    if type(value) in (dict, MappingProxyType):
        return [p for k, v in value.items() for p in null_fields(v, f"{prefix}.{k}")]
    if type(value) in (list, tuple):
        return [p for i, v in enumerate(value) for p in null_fields(v, f"{prefix}[{i}]")]
    return []


@dataclass(frozen=True)
class TrainingConfig:
    task: str
    robot: RobotConfig
    policy: PolicyConfig
    robot_path: Path
    policy_path: Path
    asset: MappingProxyType
    shared: MappingProxyType
    settings: MappingProxyType
    stage: MappingProxyType

    def __deepcopy__(self, memo):
        # Isaac configclass deep-copies attributes; this complete tree is immutable.
        return self

    def missing(self, *, evaluation: bool = False) -> list[str]:
        asset = dict(self.asset)
        settings = dict(self.settings)
        shared = dict(self.shared)
        if self.task in ("p1-flat", "p2-spin"):
            shared.pop("airborne")
            shared["termination"] = dict(shared["termination"])
            shared["termination"].pop("airborne_tilt_rad")
        if not evaluation:
            settings.pop("evaluation")
        if self.task in ("p1-flat", "p2-spin"):
            settings.pop("air_rewards")
        if TASKS[self.task].policy != "p1" or evaluation:
            settings.pop("command_curriculum")
        if self.settings["transition_reset"]["probability"] == 0 or evaluation:
            settings.pop("transition_reset")
        if self.stage["disturbance_phase"] == 1 or evaluation:
            settings["disturbance"] = dict(settings["disturbance"])
            settings["disturbance"].pop("phase2_start_iteration")
        if TASKS[self.task].policy == "p2" or self.task == "p3-tunnel":
            settings["commands"] = dict(settings["commands"])
            for key in ("vx_range_m_s", "wz_range_rad_s", "dash_range_m_s"):
                settings["commands"].pop(key)
            if evaluation:
                settings["evaluation"] = dict(settings["evaluation"])
                for key in ("vx_values_m_s", "wz_values_rad_s", "combined_commands"):
                    settings["evaluation"].pop(key)
                if self.task == "p3-tunnel":
                    settings["evaluation"].pop("jump_velocity_m_s")
        stage = dict(self.stage)
        if self.task == "p3-tunnel":
            stage.pop("height_range_m")
        if self.task != "p3-tunnel":
            asset.pop("collision_body_names")
        return (
            missing_parameters(self.robot, self.policy)
            + null_fields(asset, "robot.asset")
            + null_fields(shared, "robot.training")
            + null_fields(settings, "policy.training")
            + null_fields(stage, f"policy.stages.{TASKS[self.task].stage}")
        )

    def require_ready(self, *, evaluation: bool = False) -> None:
        missing = self.missing(evaluation=evaluation)
        if missing:
            raise ValueError("Training is not ready; fill measured/verified values:\n- " + "\n- ".join(missing))
        usd = Path(self.asset["usd_path"])
        if not usd.is_file():
            raise ValueError(f"robot.asset.usd_path: file does not exist: {usd}")
        if self.task == "p1-recovery" and not Path(self.stage["handover_states_npz"]).is_file():
            raise ValueError("handover_states_npz must name a real recovery handover state library")
        transition = self.settings["transition_reset"]
        if transition["probability"] > 0 and not Path(transition["states_npz"]).is_file():
            raise ValueError("transition_reset.states_npz must name a real rollout state library")
        disturbance = self.settings["disturbance"]
        if not evaluation and self.stage["disturbance_phase"] == 2 and not disturbance["baseline_evaluation_passed"]:
            raise ValueError(
                "Stage-2 disturbances require a passing P1 baseline evaluation; record it in the policy YAML"
            )


def load_training(task: str, robot_path: str | Path, policy_path: str | Path) -> TrainingConfig:
    if task not in TASKS:
        raise ValueError(f"Unknown task {task}; choose from {', '.join(TASKS)}")
    robot_path, policy_path = Path(robot_path).resolve(), Path(policy_path).resolve()
    robot, policy = load_robot(robot_path), load_policy(policy_path)
    r = yaml.safe_load(robot_path.read_text(encoding="utf-8"))
    p = yaml.safe_load(policy_path.read_text(encoding="utf-8"))
    try:
        if p["policy_family"] != TASKS[task].policy:
            raise ValueError(f"{policy_path}: policy_family does not match {task}")
        cfg = TrainingConfig(
            task,
            robot,
            policy,
            robot_path,
            policy_path,
            _freeze(r["asset"]),
            _freeze(r["training"]),
            _freeze(p["training"]),
            _freeze(p["stages"][TASKS[task].stage]),
        )
    except KeyError as error:
        raise ValueError(f"Training configuration missing field {error.args[0]}") from error
    if (robot.control_hz, robot.policy_hz) != (500, 100):
        raise ValueError("Training contract requires 500 Hz physics/PD and 100 Hz policy")
    if cfg.settings["ppo"]["gamma"] != 0.995 or cfg.settings["rollout_steps"] != 48:
        raise ValueError("PPO timing contract requires gamma=0.995 and rollout_steps=48")
    _validate_training(cfg)
    return cfg


def _validate_training(cfg: TrainingConfig) -> None:
    for key in ("critic_torque_scale", "spawn_clearance_m", "spawn_clearance_max_m"):
        if key not in cfg.shared:
            raise ValueError(f"{cfg.robot_path}: missing training.{key}")
        value = cfg.shared[key]
        if type(value) not in (float, int) or not isfinite(value) or value <= 0:
            raise ValueError(f"training.{key} must be finite and positive")
    if "numerical_safety" not in cfg.shared:
        raise ValueError(f"{cfg.robot_path}: missing training.numerical_safety")
    for key in ("joint_velocity_abs_max", "base_linear_velocity_abs_max", "base_angular_velocity_abs_max"):
        if key not in cfg.shared["numerical_safety"]:
            raise ValueError(f"{cfg.robot_path}: missing training.numerical_safety.{key}")
        value = cfg.shared["numerical_safety"][key]
        if type(value) not in (float, int) or not isfinite(value) or value <= 0:
            raise ValueError(f"training.numerical_safety.{key} must be finite and positive")
    curriculum = cfg.settings["command_curriculum"]
    if "min_completed_episodes" not in curriculum:
        raise ValueError(f"{cfg.policy_path}: missing training.command_curriculum.min_completed_episodes")
    if type(curriculum["min_completed_episodes"]) is not int or curriculum["min_completed_episodes"] <= 0:
        raise ValueError("command_curriculum.min_completed_episodes must be a positive integer")
    if curriculum["min_completed_episodes"] < cfg.settings["num_envs"]:
        raise ValueError("command_curriculum.min_completed_episodes must be >= training.num_envs")
    for key in ("observation_delay_steps", "action_delay_steps"):
        if key not in cfg.settings["evaluation"]:
            raise ValueError(f"{cfg.policy_path}: missing training.evaluation.{key}")
        value = cfg.settings["evaluation"][key]
        if value is not None and (type(value) is not int or value < 0):
            raise ValueError(f"evaluation.{key}: expected a nonnegative integer or null pending measurement")
    duration = cfg.shared["randomization"]["external_wrench_duration_s"]
    if type(duration) not in (float, int) or not isfinite(duration) or duration <= 0:
        raise ValueError("external_wrench_duration_s must be finite and positive")
    if duration < cfg.shared["randomization"]["push_interval_s"][1]:
        raise ValueError("external_wrench_duration_s must be >= the upper bound of push_interval_s")
    collision_duration = cfg.settings["disturbance"]["collision_duration_s"]
    if type(collision_duration) not in (float, int) or not isfinite(collision_duration) or collision_duration <= 0:
        raise ValueError("collision_duration_s must be finite and positive")
    weights = cfg.settings["rewards"]
    if weights["leg_symmetry"] != 0 and (weights["no_fork"] != 0 or weights["no_fork_square"] != 0):
        raise ValueError("Guide v2.1: leg_symmetry and no_fork must not be enabled together")
    if cfg.policy.action_clip is not None:
        raise ValueError("Guide v2.1 requires action_clip: null; only converted targets are clipped")
    for key in (
        "joint_lower_rad",
        "joint_upper_rad",
        "joint_armature",
        "joint_viscous_friction",
        "joint_coulomb_friction",
        "joint_dynamic_friction",
        "no_load_speed_rad_s",
        "saturation_torque_nm",
    ):
        values = cfg.shared[key]
        if len(values) != 6:
            raise ValueError(f"robot.training.{key}: expected 6 logical joint channels")
        for value in values:
            if value is not None and (type(value) not in (float, int) or not isfinite(value)):
                raise ValueError(f"robot.training.{key}: expected finite numbers or null")
    for i in cfg.robot.leg_indices:
        lo, hi = cfg.shared["joint_lower_rad"][i], cfg.shared["joint_upper_rad"][i]
        if lo is not None and hi is not None and lo + 2 * cfg.shared["joint_target_margin_rad"] >= hi:
            raise ValueError(f"robot.training joint limits[{i}]: empty target range after safety margin")
    probabilities = cfg.settings["commands"]["segment_probabilities"]
    if any(x < 0 for x in probabilities) or abs(sum(probabilities) - 1) > 1e-6:
        raise ValueError("Segment probabilities must be nonnegative and sum to one")
    for key in ("vx_range_m_s", "wz_range_rad_s", "height_range_m", "segment_duration_s", "height_duration_s"):
        bounds = cfg.settings["commands"][key]
        if bounds is not None and (len(bounds) != 2 or bounds[0] > bounds[1]):
            raise ValueError(f"commands.{key}: expected [lower, upper]")
    if TASKS[cfg.task].policy == "p3":
        probabilities = cfg.stage["jump_count_probabilities"]
        if len(probabilities) != 3 or any(x < 0 for x in probabilities) or abs(sum(probabilities) - 1) > 1e-6:
            raise ValueError("Jump count probabilities must cover 0/1/2 events and sum to one")
        heights = cfg.stage["height_range_m"]
        feasible = cfg.stage["feasible_height_m"]
        if heights is not None and (heights[0] <= 0 or heights[1] < heights[0]):
            raise ValueError("Jump height range must be positive and ordered")
        if cfg.task != "p3-tunnel" and heights is not None and feasible is not None and heights[1] > feasible:
            raise ValueError("Jump target exceeds measured feasible_height_m")
        if cfg.task == "p3-tunnel":
            p = cfg.stage["tunnel"]
            vx = p["vx_range_m_s"]
            if vx is not None and (len(vx) != 2 or vx[0] <= 0 or vx[1] < vx[0]):
                raise ValueError("tunnel.vx_range_m_s must be a positive, ordered forward-speed range")
            required_height = max(p["beam_height_m"], max(p["height_curriculum_m"]) + p["height_jitter_m"][1])
            if feasible is not None and required_height + p["clearance_margin_m"] > feasible:
                raise ValueError("Tunnel beam plus clearance margin exceeds feasible_height_m")
    if cfg.stage["disturbance_phase"] not in (1, 2):
        raise ValueError("disturbance_phase must be 1 or 2")
    schedule = cfg.settings["disturbance"]
    if not 0 <= cfg.settings["transition_reset"]["probability"] <= 1:
        raise ValueError("transition_reset.probability must lie in [0,1]")
    if not 2000 <= schedule["ramp_iterations"] <= 4000:
        raise ValueError("Guide v2.1 requires a 2000-4000 iteration disturbance ramp")
    if not 1.0 <= schedule["final_push_velocity_m_s"] <= 1.5:
        raise ValueError("Guide v2.1 final velocity push must be in [1.0,1.5] m/s")
    if cfg.task == "p2-spin" and cfg.stage["reference_frame"] != "fixed_world_yaw":
        raise ValueError("Current chassis-only P2 uses fixed_world_yaw; gimbal dynamics require a new asset contract")


def runner_config(cfg: TrainingConfig) -> dict:
    return {
        "seed": cfg.settings["seed"],
        "num_steps_per_env": cfg.settings["rollout_steps"],
        "save_interval": cfg.settings["save_interval"],
        "obs_groups": {"policy": ["policy"], "critic": ["critic"]},
        "logger": "tensorboard",
        "policy": {
            "class_name": "ActorCritic",
            "actor_hidden_dims": list(cfg.policy.hidden_dims),
            "critic_hidden_dims": list(cfg.policy.hidden_dims),
            "activation": cfg.policy.activation,
            "init_noise_std": cfg.settings["init_noise_std"],
            "actor_obs_normalization": False,
            "critic_obs_normalization": False,
        },
        "algorithm": {"class_name": "PPO", **mutable(cfg.settings["ppo"])},
    }
