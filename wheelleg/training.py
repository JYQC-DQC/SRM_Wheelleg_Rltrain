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
        if self.task != "p1-stairs":
            shared.pop("spring_extension_height_m", None)
            shared.pop("stairs_passive_joint_limits_rad", None)
        if self.task in ("p1-flat", "p2-spin"):
            shared.pop("airborne")
            shared["termination"] = dict(shared["termination"])
            shared["termination"].pop("airborne_tilt_rad")
        if evaluation:
            shared["leg_reset"] = {"settle_s": shared["leg_reset"]["settle_s"]}  # 评测从默认零位出生
        if not evaluation:
            settings.pop("evaluation")
        if self.task in ("p1-flat", "p2-spin"):
            settings.pop("air_rewards")
        if TASKS[self.task].policy != "p1" or self.task == "p1-stairs" or evaluation:
            settings.pop("command_curriculum")
        if self.settings["transition_reset"]["probability"] == 0 or evaluation:
            settings.pop("transition_reset")
        if self.stage["disturbance_phase"] == 1 or evaluation:
            settings["disturbance"] = dict(settings["disturbance"])
            settings["disturbance"].pop("phase2_start_iteration")
        if TASKS[self.task].policy == "p2" or self.task in ("p3-tunnel", "p1-stairs"):
            settings["commands"] = dict(settings["commands"])
            for key in ("vx_range_m_s", "wz_range_rad_s", "dash_range_m_s"):
                settings["commands"].pop(key)
            if evaluation:
                settings["evaluation"] = dict(settings["evaluation"])
                for key in ("vx_values_m_s", "wz_values_rad_s", "combined_commands"):
                    settings["evaluation"].pop(key)
                if self.task in ("p3-tunnel", "p1-stairs"):
                    settings["evaluation"].pop("jump_velocity_m_s")
                if self.task == "p1-stairs":
                    settings["evaluation"].pop("height_m")
        stage = dict(self.stage)
        if self.task == "p1-stairs":
            for key in tuple(stage):
                if key.startswith("air_") and key != "air_reset_probability":
                    stage.pop(key)
        if self.task == "p3-tunnel":
            stage.pop("height_range_m")
        if self.task != "p3-tunnel":
            asset.pop("collision_body_names")
        return (
            missing_parameters(self.robot, self.policy)
            + null_fields(asset, "robot.asset")
            + null_fields(
                {
                    k: v
                    for k, v in shared.items()
                    if not (
                        self.asset.get("reference_preset") == "scut_v14_2"
                        and k in ("no_load_speed_rad_s", "saturation_torque_nm")
                    )
                },
                "robot.training",
            )
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
        if self.asset.get("reference_preset") == "scut_v14_2":
            module = Path(self.asset["reference_package"]) / "agent_world/assets/wheelbipe_V14_2.py"
            if not module.is_file():
                raise ValueError(f"Missing SCUT reference asset module: {module}")
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
    if cfg.asset.get("reference_preset") is not None:
        if cfg.asset["reference_preset"] != "scut_v14_2" or robot.variant != "reference_simulation_only":
            raise ValueError("Reference preset requires an explicitly simulation-only robot profile")
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
    # 旧的生成配置没有以下字段：在这里指明文件和字段，而不是在 Isaac 启动后报 KeyError。
    if "termination_contact_body_names" not in cfg.asset:
        raise ValueError(f"{cfg.robot_path}: missing asset.termination_contact_body_names")
    if "duration_s" not in cfg.shared["termination"]:
        raise ValueError(f"{cfg.robot_path}: missing training.termination.duration_s")
    value = cfg.shared["termination"]["duration_s"]
    if type(value) not in (float, int) or not isfinite(value) or value * cfg.robot.policy_hz < 1:
        raise ValueError("training.termination.duration_s must cover at least one policy step")
    for key in ("body_materials", "restitution"):
        if key not in cfg.shared["randomization"]:
            raise ValueError(f"{cfg.robot_path}: missing training.randomization.{key}")
    if "release_s" not in cfg.shared["termination"]:
        raise ValueError(f"{cfg.robot_path}: missing training.termination.release_s")
    value = cfg.shared["termination"]["release_s"]
    if type(value) not in (float, int) or not isfinite(value) or value <= 0:
        raise ValueError("training.termination.release_s must be finite and positive")
    if TASKS[cfg.task].policy == "p1":
        for key in ("relative_error", "height_error_threshold_m"):
            if key not in curriculum:
                raise ValueError(f"{cfg.policy_path}: missing training.command_curriculum.{key}")
        if "combined_wz_limit_rad_s" not in cfg.settings["commands"]:
            raise ValueError(f"{cfg.policy_path}: missing training.commands.combined_wz_limit_rad_s")
        if "height_wide_anneal" not in cfg.settings:
            raise ValueError(f"{cfg.policy_path}: missing training.height_wide_anneal")
        for key in ("final_weight", "start_iteration", "ramp_iterations"):
            if key not in cfg.settings["height_wide_anneal"]:
                raise ValueError(f"{cfg.policy_path}: missing training.height_wide_anneal.{key}")
        if cfg.settings["height_wide_anneal"]["ramp_iterations"] <= 0:
            raise ValueError("training.height_wide_anneal.ramp_iterations must be positive")
    parameters = cfg.settings["reward_parameters"]
    for key in ("pitch_velocity_amplitude", "pitch_velocity_sigma", "pitch_velocity_offset"):
        if key not in parameters:
            raise ValueError(f"{cfg.policy_path}: missing training.reward_parameters.{key}")
        value = parameters[key]
        if type(value) not in (float, int) or not isfinite(value) or value <= 0:
            raise ValueError(f"{cfg.policy_path}: training.reward_parameters.{key} must be finite and positive")
    if TASKS[cfg.task].policy in ("p1", "p2"):
        for key in ("height_gate_full_error_m", "height_gate_zero_error_m"):
            if key not in parameters:
                raise ValueError(f"{cfg.policy_path}: missing training.reward_parameters.{key}")
        if not 0 <= parameters["height_gate_full_error_m"] < parameters["height_gate_zero_error_m"]:
            raise ValueError("reward_parameters: expected 0 <= height_gate_full_error_m < height_gate_zero_error_m")
    if TASKS[cfg.task].policy == "p1":
        if "reward_overrides" not in cfg.stage:
            raise ValueError(f"{cfg.policy_path}: missing stages.{TASKS[cfg.task].stage}.reward_overrides")
        unknown = [name for name in cfg.stage["reward_overrides"] if name not in cfg.settings["rewards"]]
        if unknown:
            raise ValueError(f"stages.{TASKS[cfg.task].stage}.reward_overrides: not in training.rewards: {unknown}")
    if cfg.task == "p1-landing":
        if "landing_diagnostics" not in cfg.stage:
            raise ValueError(f"{cfg.policy_path}: missing stages.landing.landing_diagnostics")
        reward = cfg.stage["landing_reward"]
        for key in (
            "progress_budget",
            "success_bonus",
            "failure_cost",
            "contact_force_n",
            "support_force_n",
            "contact_timeout_s",
            "settle_support_s",
            "cushion_max_s",
            "window_s",
            "stable_s",
            "tilt_rad",
            "angular_xy_rad_s",
            "vertical_velocity_m_s",
            "height_error_m",
            "wheel_center_weight",
            "wheel_center_sigma",
            "wheel_speed_weight",
            "wheel_speed_sigma",
            "contact_multiplier",
            "guide_hard_speed_m_s",
            "guide_speed_cost",
            "leg_extension_weight",
            "leg_extension_target_m",
            "leg_extension_scale_m",
        ):
            if key not in reward:
                raise ValueError(f"{cfg.policy_path}: missing stages.landing.landing_reward.{key}")
            value = reward[key]
            if value is None and key == "leg_extension_target_m":
                continue  # robot geometry still unknown: reported by missing() and blocked by require_ready()
            if type(value) not in (int, float) or not isfinite(value) or value <= 0:
                raise ValueError(f"landing_reward.{key} must be finite and positive")
        if type(reward.get("guide_body_regex")) is not str:
            raise ValueError(
                f"{cfg.policy_path}: stages.landing.landing_reward.guide_body_regex must be a regex string"
            )
        if reward["contact_multiplier"] < 1:
            raise ValueError("landing_reward.contact_multiplier must not weaken the contact penalty")
        if "guide_brush_cost" in reward:
            raise ValueError("landing_reward.guide_brush_cost was removed: guide contacts cost guide_speed_cost each")
        # Per contact only: long guide support is charged by contact_multiplier and may exceed a failed landing.
        if reward["guide_speed_cost"] >= reward["failure_cost"]:
            raise ValueError("A single cushioned guide contact must cost less than a failed landing")
        reach = cfg.stage.get("air_leg_length_range_m")
        if (
            reward["leg_extension_target_m"] is not None
            and reach is not None
            and reward["leg_extension_target_m"] > reach[1]
        ):
            raise ValueError("landing_reward.leg_extension_target_m must be within air_leg_length_range_m")
        if reward["progress_budget"] + reward["success_bonus"] >= -cfg.settings["rewards"]["termination"]:
            raise ValueError("Total first-landing positive budget must stay below the termination cost")
        if (
            reward["stable_s"] >= reward["window_s"]
            or reward["cushion_max_s"] >= reward["window_s"]
            or reward["settle_support_s"] > reward["stable_s"]
            or reward["contact_timeout_s"] + reward["window_s"] >= cfg.settings["episode_length_s"]
        ):
            raise ValueError("Landing event deadlines must fit within an episode")
        if reward["support_force_n"] < reward["contact_force_n"]:
            raise ValueError("Landing support threshold must exceed first-contact threshold")
        for key in ("air_vx_command_probability", "air_vx_command_noise_m_s"):
            value = cfg.stage.get(key)
            if type(value) not in (int, float) or not isfinite(value) or value < 0:
                raise ValueError(f"stages.landing.{key} must be finite and nonnegative")
        if cfg.stage["air_vx_command_probability"] > 1:
            raise ValueError("stages.landing.air_vx_command_probability must be within [0, 1]")
        if "air_height_curriculum" not in cfg.stage:
            raise ValueError(f"{cfg.policy_path}: missing stages.landing.air_height_curriculum")
        height = cfg.stage["air_height_curriculum"]
        for key in ("levels_m", "min_events", "success_rate"):
            if key not in height:
                raise ValueError(f"{cfg.policy_path}: missing stages.landing.air_height_curriculum.{key}")
        low, high = cfg.stage["air_height_offset_m"]
        levels = list(height["levels_m"])
        if (
            not levels
            or any(type(v) not in (int, float) or not isfinite(v) for v in levels)
            or levels[0] <= low
            or any(b <= a for a, b in zip(levels, levels[1:]))
            or levels[-1] != high
        ):
            raise ValueError(
                "air_height_curriculum.levels_m must increase strictly from above air_height_offset_m[0] "
                "and end at air_height_offset_m[1]"
            )
        if type(height["min_events"]) is not int or height["min_events"] <= 0:
            raise ValueError("air_height_curriculum.min_events must be a positive integer")
        rate = height["success_rate"]
        if type(rate) not in (int, float) or not 0 < rate <= 1:
            raise ValueError("air_height_curriculum.success_rate must be within (0, 1]")
        if "command_curriculum_landing_gate" not in cfg.stage:
            raise ValueError(f"{cfg.policy_path}: missing stages.landing.command_curriculum_landing_gate")
        gate = cfg.stage["command_curriculum_landing_gate"]
        for key in ("min_events", "success_rate"):
            if key not in gate:
                raise ValueError(f"{cfg.policy_path}: missing stages.landing.command_curriculum_landing_gate.{key}")
        if type(gate["min_events"]) is not int or gate["min_events"] <= 0:
            raise ValueError("command_curriculum_landing_gate.min_events must be a positive integer")
        rate = gate["success_rate"]
        if type(rate) not in (int, float) or not 0 < rate <= 1:
            raise ValueError("command_curriculum_landing_gate.success_rate must be within (0, 1]")
        diagnostics = cfg.stage["landing_diagnostics"]
        for key in (
            "first_contact_force_n",
            "support_force_n",
            "first_contact_timeout_s",
            "observation_window_s",
            "stable_duration_s",
            "touchdown_difference_s",
            "tilt_rad",
            "angular_xy_rad_s",
            "vertical_velocity_m_s",
            "height_error_m",
        ):
            if key not in diagnostics:
                raise ValueError(f"{cfg.policy_path}: missing stages.landing.landing_diagnostics.{key}")
            value = diagnostics[key]
            if type(value) not in (int, float) or not isfinite(value) or value <= 0:
                raise ValueError(f"stages.landing.landing_diagnostics.{key}: expected finite positive value")
        if diagnostics["support_force_n"] < diagnostics["first_contact_force_n"]:
            raise ValueError("landing_diagnostics.support_force_n must be >= first_contact_force_n")
        if diagnostics["stable_duration_s"] >= diagnostics["observation_window_s"]:
            raise ValueError("landing_diagnostics observation window must exceed stable hold duration")
        deadline = diagnostics["first_contact_timeout_s"] + diagnostics["observation_window_s"]
        if deadline >= cfg.settings["episode_length_s"]:
            raise ValueError("landing diagnostics deadlines must fit within a full training episode")
        # The reward resolves at the first stable hold, the diagnostic at the window end; the bars must agree.
        for reward_key, diagnostic_key in (
            ("contact_force_n", "first_contact_force_n"),
            ("support_force_n", "support_force_n"),
            ("contact_timeout_s", "first_contact_timeout_s"),
            ("window_s", "observation_window_s"),
            ("stable_s", "stable_duration_s"),
            ("tilt_rad", "tilt_rad"),
            ("angular_xy_rad_s", "angular_xy_rad_s"),
            ("vertical_velocity_m_s", "vertical_velocity_m_s"),
            ("height_error_m", "height_error_m"),
        ):
            if reward[reward_key] != diagnostics[diagnostic_key]:
                raise ValueError(f"landing_reward.{reward_key} must equal landing_diagnostics.{diagnostic_key}")
    if cfg.task == "p2-spin":
        if "terrain" not in cfg.stage:
            raise ValueError(f"{cfg.policy_path}: missing stages.spin.terrain; regenerate the P2 configuration")
        terrain = cfg.stage["terrain"]
        required = (
            "tile_size_m",
            "rows",
            "columns",
            "difficulty_range",
            "flat_proportion",
            "rough_proportion",
            "slope_proportion",
            "slope_angle_range_rad",
            "rough_noise_range_m",
            "rough_noise_step_m",
            "rough_downsampled_scale_m",
            "heightfield_border_width_m",
        )
        for key in required:
            if key not in terrain:
                raise ValueError(f"{cfg.policy_path}: missing stages.spin.terrain.{key}")
        proportions = [terrain[k] for k in ("flat_proportion", "rough_proportion", "slope_proportion")]
        if any(not isfinite(v) or v <= 0 for v in proportions) or abs(sum(proportions) - 1) > 1e-6:
            raise ValueError("stages.spin.terrain proportions must be positive and sum to 1")
        for key in ("rows", "columns"):
            if type(terrain[key]) is not int or terrain[key] <= 0:
                raise ValueError(f"stages.spin.terrain.{key} must be a positive integer")
        # Curriculum terrain generation assigns whole columns to types.
        if any(abs(v * terrain["columns"] - round(v * terrain["columns"])) > 1e-6 for v in proportions):
            raise ValueError("stages.spin.terrain columns must represent each requested proportion exactly")
        for key in ("difficulty_range", "slope_angle_range_rad", "rough_noise_range_m", "tile_size_m"):
            value = terrain[key]
            if len(value) != 2 or any(not isfinite(v) for v in value):
                raise ValueError(f"stages.spin.terrain.{key} must contain two finite numbers")
            if key != "tile_size_m" and value[0] > value[1]:
                raise ValueError(f"stages.spin.terrain.{key} must be ordered")
        if not 0 <= terrain["difficulty_range"][0] <= terrain["difficulty_range"][1] <= 1:
            raise ValueError("stages.spin.terrain.difficulty_range must be in [0,1]")
        if min(terrain["tile_size_m"]) <= 0:
            raise ValueError("stages.spin.terrain.tile_size_m must be positive")
        for key in ("rough_noise_step_m", "rough_downsampled_scale_m", "heightfield_border_width_m"):
            if not isfinite(terrain[key]) or terrain[key] <= 0:
                raise ValueError(f"stages.spin.terrain.{key} must be finite and positive")
    if cfg.task == "p1-stairs":
        prefix = f"{cfg.policy_path}: stages.stairs"
        for key in ("course", "terrain"):
            if key not in cfg.stage:
                raise ValueError(f"{prefix}.{key} is required; regenerate stairs configuration")
        course, terrain = cfg.stage["course"], cfg.stage["terrain"]
        if "guide_body_regex" not in course or type(course["guide_body_regex"]) is not str:
            raise ValueError(f"{prefix}.course.guide_body_regex: required body-name regular expression")
        required = (
            "episode_length_s",
            "initial_speed_fraction",
            "minimum_speed_fraction",
            "speed_increment",
            "speed_window_episodes",
            "speed_promote_rate",
            "speed_demote_rate",
            "tracking_sigma",
            "tracking_promote",
            "tracking_demote",
            "minimum_episode_s",
            "tracking_warmup_s",
            "reverse_probability",
            "yaw_jitter_rad",
            "heading_kp",
            "yaw_deadzone_rad_s",
            "heading_probability",
            "traversal_hold_s",
            "traversal_tilt_rad",
            "traversal_angular_rad_s",
            "traversal_height_error_m",
            "small_turn_probability",
            "small_turn_range_rad_s",
            "segment_duration_s",
            "height_duration_s",
            "edge_clearance_m",
            "finish_hold_s",
            "finish_tilt_rad",
            "finish_angular_rad_s",
            "finish_speed_m_s",
            "scan_resolution_m",
            "scan_half_length_m",
            "scan_half_width_m",
            "scan_lane_half_width_m",
            "scan_min_rays",
            "edge_height_m",
            "edge_gradient_excess_m",
            "detection_distance_m",
            "trigger_distance_m",
            "detection_hold_s",
            "contact_force_n",
            "guide_contact_scale",
            "min_flight_s",
            "min_drop_m",
            "impact_free_speed_m_s",
            "impact_speed_scale_m_s",
            "impact_clip",
            "cushion_s",
            "impact_weight",
            "air_wheel_speed_weight",
            "air_wheel_speed_sigma",
        )
        for key in required:
            if key not in course:
                raise ValueError(f"{prefix}.course.{key} is required")
            value = course[key]
            if key in ("small_turn_range_rad_s", "segment_duration_s", "height_duration_s"):
                if value is None:
                    continue  # Unknown SRM values are reported by require_ready().
                if (
                    len(value) != 2
                    or any(type(v) not in (int, float) or not isfinite(v) for v in value)
                    or not 0 < value[0] <= value[1]
                ):
                    raise ValueError(f"{prefix}.course.{key}: expected positive ordered pair")
            else:
                if type(value) not in (int, float) or not isfinite(value):
                    raise ValueError(f"{prefix}.course.{key}: expected finite number")
                if key == "impact_weight":
                    invalid = value >= 0
                elif key in ("reverse_probability", "yaw_jitter_rad", "speed_demote_rate", "tracking_demote"):
                    invalid = value < 0
                else:
                    invalid = value <= 0
                if invalid:
                    raise ValueError(f"{prefix}.course.{key}: invalid sign or zero")
        if (
            not 0 < course["minimum_speed_fraction"] < 1
            or not course["minimum_speed_fraction"] <= course["initial_speed_fraction"] <= 1
        ):
            raise ValueError(f"{prefix}.course: invalid speed fractions")
        for a, b in (("speed_demote_rate", "speed_promote_rate"), ("tracking_demote", "tracking_promote")):
            if not 0 <= course[a] < course[b] <= 1:
                raise ValueError(f"{prefix}.course: expected 0 <= {a} < {b} <= 1")
        if not 0 <= course["reverse_probability"] <= 1:
            raise ValueError(f"{prefix}.course.reverse_probability must be in [0,1]")
        if not 0 < course["guide_contact_scale"] <= 1:
            raise ValueError(f"{prefix}.course.guide_contact_scale must be in (0,1]")
        for key in ("heading_probability", "small_turn_probability"):
            if not 0 < course[key] < 1:
                raise ValueError(f"{prefix}.course.{key} must be in (0,1)")
        if "motion_segment_probabilities" not in course or len(course["motion_segment_probabilities"]) != 4:
            raise ValueError(f"{prefix}.course.motion_segment_probabilities requires stand/straight/turn/combined")
        probabilities = course["motion_segment_probabilities"]
        if any(not isfinite(x) or x <= 0 for x in probabilities) or abs(sum(probabilities) - 1) > 1e-6:
            raise ValueError(f"{prefix}.course.motion_segment_probabilities must be positive and sum to 1")
        if "spring_extension_height_m" not in cfg.shared:
            raise ValueError(f"{cfg.robot_path}: training.spring_extension_height_m is required")
        ceiling = cfg.shared["spring_extension_height_m"]
        if ceiling is not None and (type(ceiling) not in (int, float) or not isfinite(ceiling) or ceiling <= 0):
            raise ValueError(f"{cfg.robot_path}: training.spring_extension_height_m must be positive or null")
        for key in ("step_height_margin_m", "step_height_hold_s"):
            if (
                key not in cfg.stage
                or type(cfg.stage[key]) not in (int, float)
                or not isfinite(cfg.stage[key])
                or cfg.stage[key] <= 0
            ):
                raise ValueError(f"{prefix}.{key}: expected a positive finite value")
        if ceiling is not None and cfg.stage["step_height_margin_m"] >= ceiling:
            raise ValueError(f"{prefix}.step_height_margin_m must be below the spring height limit")
        if ceiling is not None:
            ceiling -= cfg.stage["step_height_margin_m"]
        if "step_height_clearance_range_m" not in cfg.stage:
            raise ValueError(f"{prefix}.step_height_clearance_range_m is required")
        clearance = cfg.stage["step_height_clearance_range_m"]
        if clearance is not None and (
            type(clearance) is not tuple
            or len(clearance) != 2
            or any(type(x) not in (int, float) or not isfinite(x) for x in clearance)
            or not 0 < clearance[0] < clearance[1]
            or (ceiling is not None and clearance[1] > ceiling)
        ):
            raise ValueError(
                f"{prefix}.step_height_clearance_range_m: positive ordered pair below height ceiling required"
            )
        if "stairs_passive_joint_limits_rad" not in cfg.shared:
            raise ValueError(f"{cfg.robot_path}: training.stairs_passive_joint_limits_rad is required")
        limits = cfg.shared["stairs_passive_joint_limits_rad"]
        if type(limits) is not MappingProxyType:
            raise ValueError(f"{cfg.robot_path}: training.stairs_passive_joint_limits_rad must be a mapping")
        if limits and (
            cfg.robot.variant != "reference_simulation_only" or cfg.asset.get("reference_preset") != "scut_v14_2"
        ):
            raise ValueError("Passive limit widening is authorized only for SCUT reference simulation")
        allowed = {f"{side}_{part}_joint" for side in ("left", "right") for part in ("front2", "front4", "rear2")}
        for name, pair in limits.items():
            if (
                name not in allowed
                or len(pair) != 2
                or any(type(x) not in (int, float) or not isfinite(x) for x in pair)
                or not pair[0] <= 0 < pair[1]
            ):
                raise ValueError(f"{cfg.robot_path}: training.stairs_passive_joint_limits_rad.{name}: invalid limits")
        if "motion_reward_overrides" not in cfg.stage:
            raise ValueError(f"{prefix}.motion_reward_overrides is required")
        for name, weight in cfg.stage["motion_reward_overrides"].items():
            if name not in cfg.settings["rewards"] or not isfinite(weight) or weight >= 0:
                raise ValueError(f"{prefix}.motion_reward_overrides.{name}: expected existing negative penalty")
        if "terrain_reward_overrides" not in cfg.stage:
            raise ValueError(f"{prefix}.terrain_reward_overrides is required")
        terrain_weights = cfg.stage["terrain_reward_overrides"]
        if set(terrain_weights) != {"grid", "slope", "rough"}:
            raise ValueError(f"{prefix}.terrain_reward_overrides requires grid, slope and rough")
        for kind, overrides in terrain_weights.items():
            if set(overrides) != set(cfg.stage["motion_reward_overrides"]):
                raise ValueError(f"{prefix}.terrain_reward_overrides.{kind}: must cover all motion penalties")
            for name, weight in overrides.items():
                if not isfinite(weight) or weight >= 0:
                    raise ValueError(f"{prefix}.terrain_reward_overrides.{kind}.{name}: negative penalty required")
        for key in ("speed_window_episodes", "scan_min_rays"):
            if type(course[key]) is not int:
                raise ValueError(f"{prefix}.course.{key} must be an integer")
        for key in ("rows", "columns"):
            if type(terrain[key]) is not int or terrain[key] <= 0:
                raise ValueError(f"{prefix}.terrain.{key} must be a positive integer")
        for key in (
            "profiles",
            "spawn_x_m",
            "entry_x_m",
            "exit_x_m",
            "finish_x_m",
            "ground_thickness_m",
            "surface_resolution_m",
            "surface_x_range_m",
            "seed",
            "grid",
        ):
            if key not in terrain:
                raise ValueError(f"{prefix}.terrain.{key} is required")
        if (
            not 0
            < terrain["spawn_x_m"]
            < terrain["entry_x_m"]
            < terrain["exit_x_m"]
            < terrain["finish_x_m"]
            < terrain["tile_size_m"][0]
        ):
            raise ValueError(f"{prefix}.terrain: require spawn < entry < exit < finish inside tile")
        for key in ("ground_thickness_m", "surface_resolution_m"):
            if not isfinite(terrain[key]) or terrain[key] <= 0:
                raise ValueError(f"{prefix}.terrain.{key} must be finite and positive")
        if type(terrain["seed"]) is not int or terrain["seed"] < 0:
            raise ValueError(f"{prefix}.terrain.seed must be a nonnegative integer")
        proportions = [v["proportion"] for v in terrain["profiles"].values()]
        if (
            any(
                not isfinite(v) or v <= 0 or abs(v * terrain["columns"] - round(v * terrain["columns"])) > 1e-6
                for v in proportions
            )
            or abs(sum(proportions) - 1) > 1e-6
        ):
            raise ValueError(f"{prefix}.terrain.profiles: positive proportions must sum to 1 and occupy whole columns")
        for name, profile in terrain["profiles"].items():
            for key in (
                "command_mode",
                "start_speed_range_m_s",
                "height_range_m",
                "yaw_range_rad_s",
                "heading_yaw_limit_rad_s",
            ):
                if key not in profile:
                    raise ValueError(f"{prefix}.terrain.profiles.{name}.{key} is required")
            if profile["command_mode"] not in ("motion", "traverse") or (profile["command_mode"] == "motion") != (
                profile["kind"] == "flat"
            ):
                raise ValueError(f"{prefix}.terrain.profiles.{name}: motion replay requires flat terrain")
            if profile["kind"] not in ("up", "down", "mixed", "flat", "grid", "slope", "rough"):
                raise ValueError(f"{prefix}.terrain.profiles.{name}: unknown kind")
            if profile["step_count"] not in (0, 1, 2):
                raise ValueError(f"{prefix}.terrain.profiles.{name}: unsupported step_count")
            bounds = profile["speed_range_m_s"]
            if bounds is not None and (len(bounds) != 2 or not 0 <= bounds[0] < bounds[1]):
                raise ValueError(f"{prefix}.terrain.profiles.{name}: invalid speed range")
            for key in ("start_speed_range_m_s", "height_range_m", "yaw_range_rad_s"):
                pair = profile[key]
                if pair is not None and (
                    len(pair) != 2
                    or any(type(v) not in (int, float) or not isfinite(v) for v in pair)
                    or pair[0] >= pair[1]
                ):
                    raise ValueError(f"{prefix}.terrain.profiles.{name}.{key}: expected finite ordered pair")
            start = profile["start_speed_range_m_s"]
            height = profile["height_range_m"]
            yaw = profile["yaw_range_rad_s"]
            if start is not None and (start[0] < 0 or (profile["command_mode"] == "traverse" and start[0] == 0)):
                raise ValueError(f"{prefix}.terrain.profiles.{name}: traversal minimum speed must be positive")
            if start is not None and bounds is not None and any(a > b for a, b in zip(start, bounds, strict=True)):
                raise ValueError(f"{prefix}.terrain.profiles.{name}: starting speeds exceed final speeds")
            if height is not None and (
                height[0] <= 0
                or (
                    ceiling is not None and (height[0] >= ceiling if profile["kind"] == "flat" else ceiling < height[1])
                )
            ):
                raise ValueError(f"{prefix}.terrain.profiles.{name}: height must be positive and below assist ceiling")
            if yaw is None or not yaw[0] <= 0 <= yaw[1] or max(abs(v) for v in yaw) <= course["yaw_deadzone_rad_s"]:
                raise ValueError(f"{prefix}.terrain.profiles.{name}: turning range must exceed yaw deadzone")
            if (
                not isfinite(profile["heading_yaw_limit_rad_s"])
                or profile["heading_yaw_limit_rad_s"] <= course["yaw_deadzone_rad_s"]
            ):
                raise ValueError(f"{prefix}.terrain.profiles.{name}: invalid heading correction limit")
        for key in ("width_range_m", "height_range_m", "spacing_range_m"):
            bounds = terrain["grid"][key]
            if len(bounds) != 2 or not 0 < bounds[0] <= bounds[1]:
                raise ValueError(f"{prefix}.terrain.grid.{key}: invalid positive range")
        sx, sy = terrain["tile_size_m"]
        if not 0 < course["trigger_distance_m"] <= course["detection_distance_m"] < course["scan_half_length_m"]:
            raise ValueError(f"{prefix}.course: trigger <= detection < scan half length is required")
        for key in ("scan_half_length_m", "scan_half_width_m"):
            cells = 2 * course[key] / course["scan_resolution_m"]
            if abs(cells - round(cells)) > 1e-6:
                raise ValueError(f"{prefix}.course.{key}: scan extent must be divisible by resolution")
        if not sy / 2 - terrain["boundary_margin_m"] < terrain["grid"]["half_span_m"] < sy / 2:
            raise ValueError(f"{prefix}.terrain.grid.half_span_m must cover the usable region and stay inside tile")
        surface = terrain["surface_x_range_m"]
        if len(surface) != 2 or any(type(v) not in (int, float) or not isfinite(v) for v in surface):
            raise ValueError(f"{prefix}.terrain.surface_x_range_m requires two finite coordinates")
        if not terrain["spawn_x_m"] < surface[0] < surface[1] < terrain["finish_x_m"]:
            raise ValueError(f"{prefix}.terrain.surface_x_range_m must leave clear spawn and finish pads")
        if "spawn_xy_jitter_m" not in cfg.stage or set(cfg.stage["spawn_xy_jitter_m"]) != {"flat", "grid", "rough"}:
            raise ValueError(f"{prefix}.spawn_xy_jitter_m requires flat, grid and rough")
        if "spawn_footprint_margin_m" not in cfg.stage:
            raise ValueError(f"{prefix}.spawn_footprint_margin_m is required")
        footprint = cfg.stage["spawn_footprint_margin_m"]
        if footprint is not None and (type(footprint) not in (int, float) or not isfinite(footprint) or footprint <= 0):
            raise ValueError(f"{prefix}.spawn_footprint_margin_m must be positive")
        for kind, jitter in cfg.stage["spawn_xy_jitter_m"].items():
            if set(jitter) != {"x", "y"}:
                raise ValueError(f"{prefix}.spawn_xy_jitter_m.{kind} requires x and y")
            for axis, pair in jitter.items():
                if (
                    len(pair) != 2
                    or any(type(v) not in (int, float) or not isfinite(v) for v in pair)
                    or pair[0] > pair[1]
                ):
                    raise ValueError(f"{prefix}.spawn_xy_jitter_m.{kind}.{axis}: finite ordered pair required")
            x0, x1 = jitter["x"]
            y0, y1 = jitter["y"]
            origin = sx / 2 if kind == "flat" else terrain["spawn_x_m"]
            xmin = terrain["boundary_margin_m"] if kind == "flat" else course["edge_clearance_m"]
            xmax = sx - terrain["boundary_margin_m"] if kind == "flat" else surface[0] - terrain["surface_resolution_m"]
            if footprint is not None and (origin + x0 - footprint <= xmin or origin + x1 + footprint >= xmax):
                raise ValueError(f"{prefix}.spawn_xy_jitter_m.{kind}.x must keep the robot inside its clear spawn pad")
            if footprint is not None and min(sy / 2 + y0, sy / 2 - y1) <= footprint + terrain["boundary_margin_m"]:
                raise ValueError(f"{prefix}.spawn_xy_jitter_m.{kind}.y is too close to the tile boundary")
        if terrain["grid"]["width_range_m"][1] >= terrain["grid"]["spacing_range_m"][0]:
            raise ValueError(f"{prefix}.terrain.grid: bars must be narrower than their separation")
        grid_span = sum((terrain["grid"]["spacing_range_m"][1], terrain["grid"]["width_range_m"][1]))
        if grid_span >= terrain["exit_x_m"] - terrain["entry_x_m"]:
            raise ValueError(f"{prefix}.terrain.grid: bars must fit between entry and exit")
        if course["edge_clearance_m"] * 2 >= sx - terrain["finish_x_m"]:
            raise ValueError(f"{prefix}.terrain: leave a braking margin after finish")
        width = terrain["step_width_m"]
        if width is not None:
            for name, profile in terrain["profiles"].items():
                count = profile["step_count"]
                if profile["kind"] in ("up", "down", "mixed") and count == 0:
                    raise ValueError(f"{prefix}.terrain.profiles.{name}: stairs require at least one step")
                if width <= 0 or 2 * max(count - 1, 0) * width >= terrain["exit_x_m"] - terrain["entry_x_m"]:
                    raise ValueError(f"{prefix}.terrain.step_width_m: steps overlap or exceed obstacle region")
        for name, profile in terrain["profiles"].items():
            bounds = profile["start_speed_range_m_s"]
            if bounds is not None and profile["command_mode"] == "traverse":
                required_time = (terrain["finish_x_m"] - terrain["spawn_x_m"]) / bounds[0]
                required_time += course["finish_hold_s"] + cfg.shared["leg_reset"]["settle_s"]
                if course["episode_length_s"] <= required_time:
                    raise ValueError(f"{prefix}.course.episode_length_s too short for {name} at minimum speed")
        if cfg.stage["air_reset_probability"] != 0 or cfg.settings["transition_reset"]["probability"] != 0:
            raise ValueError(f"{prefix}: traversal starts on a support pad; random air/library resets must be disabled")
    if "terrain" in cfg.stage:
        for key in (
            "rough_proportion",
            "rough_noise_range_m",
            "rough_noise_step_m",
            "rough_downsampled_scale_m",
            "heightfield_border_width_m",
            "border_width_m",
            "boundary_margin_m",
        ):
            if key not in cfg.stage["terrain"]:
                raise ValueError(f"{cfg.policy_path}: missing stages.{TASKS[cfg.task].stage}.terrain.{key}")
        terrain = cfg.stage["terrain"]
        for key in ("border_width_m", "boundary_margin_m"):
            if type(terrain[key]) not in (int, float) or not isfinite(terrain[key]) or terrain[key] < 0:
                raise ValueError(f"stages.{TASKS[cfg.task].stage}.terrain.{key} must be finite and nonnegative")
        half = min(terrain["rows"] * terrain["tile_size_m"][0], terrain["columns"] * terrain["tile_size_m"][1]) / 2
        if terrain["boundary_margin_m"] >= half:
            raise ValueError("terrain.boundary_margin_m must be smaller than half the tile grid")
    stage_keys = []
    if TASKS[cfg.task].policy == "p1" and cfg.stage["air_reset_probability"] > 0:
        stage_keys += [
            ("air_tilt_rad", 2),
            ("air_vy_range_m_s", 2),
            ("air_angular_velocity_rad_s", 3),
            ("air_leg_length_range_m", 2),
            ("air_leg_angle_range_rad", 2),
            ("air_command_limit_s", None),
            ("air_command_vx_limit_m_s", None),
            ("air_command_wz_limit_rad_s", None),
        ]
    if cfg.task == "p1-recovery":
        stage_keys += [
            ("recovery_root_height_m", None),
            ("recovery_forward_probability", None),
            ("recovery_leg_length_m", 2),
            ("recovery_leg_height_m", 2),
            ("recovery_forward_leg_height_m", 2),
        ]
    for key, size in stage_keys:
        if key not in cfg.stage:
            raise ValueError(f"{cfg.policy_path}: missing stages.{TASKS[cfg.task].stage}.{key}")
        if size is not None and cfg.stage[key] is not None and len(cfg.stage[key]) != size:
            raise ValueError(f"stages.{TASKS[cfg.task].stage}.{key}: expected {size} entries")
    if cfg.task == "p1-recovery" and cfg.stage["recovery_leg_length_m"] is not None:
        # 腿摆角 = ±arccos(轮心低于髋轴的距离 / 腿长)：距离的绝对值不能超过最短腿长。
        shortest = cfg.stage["recovery_leg_length_m"][0]
        for key in ("recovery_leg_height_m", "recovery_forward_leg_height_m"):
            if cfg.stage[key] is not None and max(abs(v) for v in cfg.stage[key]) > shortest:
                raise ValueError(f"stages.recovery.{key}: magnitude must not exceed the shortest recovery leg length")
    if "leg_reset" not in cfg.shared:
        raise ValueError(f"{cfg.robot_path}: missing training.leg_reset")
    leg_reset = cfg.shared["leg_reset"]
    for key, size in (
        ("joint_names", 12),
        ("link_lengths_m", 3),
        ("angle_offsets_rad", 6),
        ("length_range_m", 2),
        ("angle_range_rad", 2),
        ("root_tilt_rad", None),
        ("min_root_height_m", None),
        ("settle_s", None),
    ):
        if key not in leg_reset:
            raise ValueError(f"{cfg.robot_path}: missing training.leg_reset.{key}")
        if size is not None and leg_reset[key] is not None and len(leg_reset[key]) != size:
            raise ValueError(f"training.leg_reset.{key}: expected {size} entries")
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
    if cfg.policy.history_frames:
        if "history_estimator" not in cfg.settings:
            raise ValueError(f"{cfg.policy_path}: history_estimator.frames > 0 requires training.history_estimator")
        for key in ("learning_rate", "velocity_loss_coef", "contact_loss_coef"):
            value = cfg.settings["history_estimator"][key]
            if type(value) not in (int, float) or not isfinite(value) or value <= 0:
                raise ValueError(f"training.history_estimator.{key} must be finite and positive")
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
    config = {
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
    if cfg.policy.history_frames:
        estimator = cfg.settings["history_estimator"]
        config["policy"].update(
            class_name="HistoryActorCritic",
            history_frames=cfg.policy.history_frames,
            estimator_hidden_dims=list(cfg.policy.estimator_hidden_dims),
        )
        config["algorithm"].update(
            class_name="HistoryPPO",
            estimator_learning_rate=estimator["learning_rate"],
            velocity_loss_coef=estimator["velocity_loss_coef"],
            contact_loss_coef=estimator["contact_loss_coef"],
        )
    return config
