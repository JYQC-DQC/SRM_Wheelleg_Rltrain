import re
from dataclasses import dataclass
from math import ceil, isfinite
from pathlib import Path
from types import MappingProxyType

import yaml

from .config import PolicyConfig, RobotConfig, load_policy, load_robot, missing_parameters
from .tasks import TASKS


def command_rate(commands, key):
    """'step' bypasses the command ramp, not actuator or physical limits. None stays uncalibrated."""
    v = commands[key]
    if v == "step":
        return float("inf")
    if type(v) not in (float, int) or not isfinite(v) or v <= 0:
        raise ValueError(f"commands.{key}: expected a finite positive rate or 'step'")
    return v


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


# Only configuration inputs: per-step velocity/height estimates and hard joint limits
# are supplied to the reward function by the environment, not copied into policy YAML.
_SHU_REWARDS = (
    "vx_tol_max",
    "vx_tol_knee",
    "wz_tol_max",
    "wz_tol_knee",
    "vx_error_sigma",
    "wz_error_sigma",
    "height_wide_weight",
    "height_gate_shape",
)
_SHU_COMMANDS = (
    "vx_range_m_s",
    "wz_range_rad_s",
    "height_range_m",
    "dash_speed_abs_m_s",
    "segment_duration_s",
    "height_duration_s",
    "linear_slew_m_s2",
    "angular_slew_rad_s2",
    "segment_probabilities",
    "combined_wz_limit_rad_s",
    "heading_kp",
    "heading_max_wz",
)
_SHU_CONTACT = ("contact_force_n", "wheel_contact_force_n", "support_force_n", "release_s")
_SHU_CONTACT_BODIES = ("guide_body_names", "leg_body_names")
_P1_MASS_LEGS = "mass_randomized_leg_body_names"
_P1_MASS_FIELDS = ("base_mass_scale", "limb_mass_scale", "inertia_scale", "com_offset_m")
_P1_MATERIAL_GROUPS = ("base", "guide")
_P1_MATERIAL_FIELDS = ("static_friction", "dynamic_friction", "restitution")
_RESET_MODE = "planar_rear_knee_coaxial_v1"
_RESET_SIGNS = {"canonical_to_asset_sign": 14, "knee_rotation_sign": 2, "extension_sign": 2}
_RESET_PAIRS = ("fixed_pin_xz_m", "knee_pivot_xz_m", "moving_pin_knee0_xz_m", "slider_safe_range_m")
_RESET_KEYS = (
    "mode",
    *_RESET_SIGNS,
    *_RESET_PAIRS,
    "canonical_zero_in_asset_rad",
    "zero_pin_distance_m",
    "auxiliary_joint_names",
    "hinge_zero_xz_rad",
    "hinge_asset_sign",
)
_SHU_SPAWN = (
    "ik_branch",
    "link_lengths_m",
    "angle_offsets_rad",
    "min_root_height_m",
    "ordinary_length_m",
    "ordinary_angle_rad",
    "ordinary_tilt_rad",
    "air_length_m",
    "recovery_length_m",
    "recovery_forward_leg_height_m",
    "recovery_rear_leg_height_m",
    "recovery_root_height_m",
    "wheel_angle_rad",
    "wheel_speed_rad_s",
    "leg_speed_rad_s",
)
_SHU_STAGE = {
    "p1-flat": ("recovery_probability", "min_segments", "initial_fraction", "error_floor", "relative_error"),
    "p1-landing": ("height_edges_m", "air_wheel_height_bias_m", "air_wheel_height_max_m"),
    "p2-spin": ("spin_rates_rad_s", "spin_probabilities", "center_drift_tolerance_m"),
    "p3-jump": (
        "height_range_m",
        "event_duration_s",
        "landing_stable_s",
        "landing_tilt_rad",
        "flight_tracking_scale",
        "jump_smooth_scale",
    ),
    "p3-tunnel": (
        "jump_smooth_scale",
        "height_range_m",
        "event_duration_s",
        "landing_stable_s",
        "landing_tilt_rad",
        "flight_tracking_scale",
    ),
}


def _required(section, keys):
    # An omitted calibrated key must block just like an explicit null; never substitute a value.
    return {key: section.get(key) for key in keys}


def _asset_name_fields(task):
    # The contact sensor has its own ordering; these are literal USD names, never regex selectors.
    fields = {
        "wheel_body_names": 2,
        "base_body_name": 1,
        "undesired_contact_body_names": None,
        "termination_contact_body_names": None,
        "active_joint_names": 6,
        "spring_joint_names": 2,
    }
    if TASKS[task].policy == "p1":
        fields.update(dict.fromkeys(_SHU_CONTACT_BODIES))
        fields["shu_leg_reset_joint_names"] = 12
        fields[_P1_MASS_LEGS] = None
    if task in ("p1-landing", "p3-tunnel"):
        fields["collision_body_names"] = None
    return fields


def _validate_asset_names(cfg):
    for key, size in _asset_name_fields(cfg.task).items():
        names = cfg.asset.get(key)
        if names is None:
            continue
        if key == "base_body_name":
            names = (names,)
        if not isinstance(names, tuple) or not names or (size is not None and len(names) != size):
            raise ValueError(f"robot.asset.{key}: invalid number of asset names")
        known = [name for name in names if name is not None]
        if any(
            type(name) is not str or not name or name.strip() != name or re.search(r"[.\\^$*+?{}\[\]|()/]", name)
            for name in known
        ) or len(set(known)) != len(known):
            raise ValueError(f"robot.asset.{key}: expected distinct literal USD names, not patterns")
    if TASKS[cfg.task].policy == "p1":
        base = cfg.asset.get("base_body_name")
        wheels = set(cfg.asset.get("wheel_body_names") or ()) - {None}
        guides = set(cfg.asset.get("guide_body_names") or ()) - {None}
        legs = set(cfg.asset.get(_P1_MASS_LEGS) or ()) - {None}
        if base in wheels or base in guides or wheels & guides:
            raise ValueError("robot.asset: P1 base_body_name, wheel_body_names and guide_body_names must be disjoint")
        if legs & (wheels | guides | {base}):
            raise ValueError(f"robot.asset.{_P1_MASS_LEGS}: exclude the base, main wheels and guide wheels")
    if cfg.task == "p3-tunnel":
        names = cfg.asset.get("collision_body_names")
        boxes = (cfg.stage.get("tunnel") or {}).get("collision_bounds_m")
        if boxes is not None and not isinstance(boxes, MappingProxyType):
            raise ValueError("tunnel.collision_bounds_m must map exact body names to bounds")
        if boxes is not None and names and None not in names and set(boxes) - set(names):
            raise ValueError("tunnel.collision_bounds_m contains unknown robot.asset.collision_body_names")


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
    flat_recovery_probability: float | None = None  # mixed replay reads policy.stages.flat

    def __deepcopy__(self, memo):
        # Isaac configclass deep-copies attributes; this complete tree is immutable.
        return self

    def missing(self, *, evaluation: bool = False, simulate_jump_button: bool = False) -> list[str]:
        asset = dict(self.asset)
        settings = dict(self.settings)
        shared = dict(self.shared)
        stage = dict(self.stage)
        family = TASKS[self.task].policy
        if self.task == "p1-landing":
            shared.setdefault("shu_air_collision", None)
        else:
            shared.pop("shu_air_collision", None)
        settings.pop("transition_reset", None)  # Inert legacy metadata only; active resets are rejected at load.
        settings.pop("command_curriculum", None)
        if family == "p1":
            for obsolete in ("air_rewards", "reward_parameters", "rewards", "reward_clip"):
                settings.pop(obsolete, None)
            settings["commands"] = _required(self.settings.get("commands") or {}, _SHU_COMMANDS)
            settings["shu_rewards"] = _required(self.settings.get("shu_rewards") or {}, _SHU_REWARDS)
            shared["wheel_rim_sign"] = self.shared.get("wheel_rim_sign")
            asset.update(_required(self.asset, _SHU_CONTACT_BODIES))
            shared["termination"] = _required(
                self.shared["termination"], ("tilt_rad", "contact_force_n", "duration_s", "decay_s")
            )
            shared["shu_contact"] = _required(
                self.shared.get("shu_contact") or {},
                _SHU_CONTACT,
            )
            shared.update(_required(self.shared, ("hip_pivot_positions_b_m", "wheel_radius_m", "spawn_clearance_m")))
            shared["shu_reset_map"] = _required(self.shared.get("shu_reset_map") or {}, _RESET_KEYS)
            shared["shu_spawn"] = _required(self.shared.get("shu_spawn") or {}, _SHU_SPAWN)
        else:
            shared.pop("shu_spawn", None)
            shared.pop("shu_reset_map", None)
            asset.pop("shu_leg_reset_joint_names", None)
            shared.pop("shu_contact", None)
            shared.pop("wheel_rim_sign", None)
            for key in ("guide_body_names", "leg_body_names"):
                asset.pop(key, None)
            asset.setdefault("termination_contact_body_names", None)
        asset.update(_required(self.asset, _asset_name_fields(self.task)))
        randomization = dict(shared["randomization"])
        if family == "p1" and not evaluation:
            randomization.update(_required(randomization, (*_P1_MASS_FIELDS, *_P1_MATERIAL_FIELDS[:2])))
            materials = randomization.get("p1_materials") or {}
            randomization["p1_materials"] = {
                group: _required(materials.get(group) or {}, _P1_MATERIAL_FIELDS) for group in _P1_MATERIAL_GROUPS
            }
        else:
            randomization.pop("p1_materials", None)
            asset.pop(_P1_MASS_LEGS, None)
        shared["randomization"] = randomization
        if self.task == "p2-spin":
            stage.pop("hardware_spin_limit_rad_s", None)  # Deployment sign-off, not a simulation limit.
        stage.update(_required(self.stage, _SHU_STAGE.get(self.task, ())))
        if family == "p1" or self.task == "p2-spin":
            shared["airborne"] = _required(self.shared.get("airborne") or {}, ("contact_force_n",))
            shared["termination"] = dict(shared["termination"])
            shared["termination"].pop("airborne_tilt_rad", None)
        if self.task == "p2-spin":
            settings.pop("air_rewards", None)
        if evaluation:
            evaluation_settings = dict(settings.get("evaluation") or {})
            for key in ("observation_delay_steps", "action_delay_steps"):
                if family == "p1" and key == "observation_delay_steps":
                    evaluation_settings.pop(key, None)
                else:
                    value = evaluation_settings.setdefault(key, None)
                    if value is not None and (type(value) is not int or value < 0):
                        raise ValueError(f"evaluation.{key}: expected a nonnegative integer or null")
            settings["evaluation"] = evaluation_settings
        else:
            settings.pop("evaluation", None)
        if self.stage.get("disturbance_phase") == 1 or evaluation:
            if settings.get("disturbance") is not None:
                settings["disturbance"] = dict(settings["disturbance"])
                settings["disturbance"].pop("phase2_start_iteration", None)
        if family in ("p2", "p3"):
            if settings.get("commands") is not None:
                settings["commands"] = dict(settings["commands"])
                unused = ("wz_range_rad_s", "dash_range_m_s", "segment_probabilities")
                if self.task != "p3-jump":
                    unused += ("vx_range_m_s",)
                for key in unused:
                    settings["commands"].pop(key, None)
            if evaluation:
                settings["evaluation"] = dict(settings["evaluation"])
                for key in ("vx_values_m_s", "wz_values_rad_s", "combined_commands"):
                    settings["evaluation"].pop(key, None)
        if family in ("p2", "p3"):
            settings.pop("disturbance", None)
            stage.pop("disturbance_phase", None)
        if family == "p3":
            settings.pop("air_rewards", None)
            button_keys = ("press_time_range_s", "no_press_probability", "moving_probability")
            if simulate_jump_button and not evaluation:
                stage.update(_required(self.stage, button_keys))
            else:
                for key in button_keys:
                    stage.pop(key, None)
            if evaluation:
                settings["evaluation"].update(
                    _required(
                        settings["evaluation"],
                        (
                            "duration_s",
                            "episodes_per_case",
                            "seed",
                            "height_m",
                        ),
                    )
                )
            unused_outcome = "tunnel_crossing" if self.task == "p3-jump" else "jump_landing"
            settings["rewards"] = dict(settings["rewards"])
            settings["rewards"].pop(unused_outcome, None)
        if self.task == "p3-tunnel":
            tunnel = _required(
                stage.get("tunnel") or {},
                (
                    "beam_offset_from_entrance_m",
                    "beam_length_m",
                    "beam_width_m",
                    "beam_height_m",
                    "beam_bottom_m",
                    "lane_width_m",
                    "vx_range_m_s",
                    "approach_distance_range_m",
                    "initial_yaw_range_rad",
                    "clearance_margin_m",
                    "landing_margin_m",
                    "ground_tolerance_m",
                    "collision_bounds_m",
                ),
            )
            boxes = tunnel.get("collision_bounds_m")
            names = asset["collision_body_names"]
            if boxes is not None and names:
                boxes = {**boxes, **_required(boxes, (name for name in names if name is not None))}
            tunnel["collision_bounds_m"] = boxes
            stage["tunnel"] = tunnel
        elif self.task != "p1-landing":
            asset.pop("collision_body_names", None)
        asset.setdefault("usd_path", None)
        return (
            missing_parameters(self.robot, self.policy)
            + null_fields(asset, "robot.asset")
            + null_fields(shared, "robot.training")
            + null_fields(settings, "policy.training")
            + null_fields(stage, f"policy.stages.{TASKS[self.task].stage}")
            + (
                null_fields(self.flat_recovery_probability, "policy.stages.flat.recovery_probability")
                if self.task == "p1-stairs"
                else []
            )
        )

    def require_ready(self, *, evaluation: bool = False, simulate_jump_button: bool = False) -> None:
        missing = self.missing(evaluation=evaluation, simulate_jump_button=simulate_jump_button)
        if missing:
            raise ValueError("Training is not ready; fill measured/verified values:\n- " + "\n- ".join(missing))
        if TASKS[self.task].policy == "p3":
            if evaluation:
                _validate_p3_rollout(self)
            elif simulate_jump_button:
                _validate_p3_button_schedule(self)
        usd = Path(self.asset["usd_path"])
        if not usd.is_file():
            raise ValueError(f"robot.asset.usd_path: file does not exist: {usd}")
        if TASKS[self.task].policy == "p1":
            # Reuse the reset implementation's geometric/closure checks before launching Isaac.
            from .shu_spawn import SpawnConfig

            common = ("hip_pivot_positions_b_m", "wheel_radius_m", "spawn_clearance_m")
            SpawnConfig(**self.shared["shu_spawn"], **{key: self.shared[key] for key in common})
        if self.task == "p1-landing":
            from .shu_air_clearance import validate_air_collision

            colliders = self.asset["collision_body_names"]
            required_bodies = {
                self.asset["base_body_name"],
                *self.asset["wheel_body_names"],
                *self.asset["guide_body_names"],
                *self.asset["leg_body_names"],
                *self.asset["undesired_contact_body_names"],
                *self.asset["termination_contact_body_names"],
            }
            omitted = required_bodies - set(colliders)
            if omitted:
                raise ValueError(f"robot.asset.collision_body_names: omitted contact bodies {sorted(omitted)}")
            validate_air_collision(self.shared["shu_air_collision"], self.asset["base_body_name"], colliders)
        if (
            not evaluation
            and TASKS[self.task].policy == "p1"
            and self.stage.get("disturbance_phase") == 2
            and not self.settings["disturbance"]["baseline_evaluation_passed"]
        ):
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
            flat_recovery_probability=(
                (p["stages"].get("flat") or {}).get("recovery_probability") if task == "p1-stairs" else None
            ),
        )
    except KeyError as error:
        raise ValueError(f"Training configuration missing field {error.args[0]}") from error
    if (robot.control_hz, robot.policy_hz) != (500, 100):
        raise ValueError("Training contract requires 500 Hz physics/PD and 100 Hz policy")
    if cfg.settings["ppo"]["gamma"] != 0.995 or cfg.settings["rollout_steps"] != 48:
        raise ValueError("PPO timing contract requires gamma=0.995 and rollout_steps=48")
    legacy = cfg.settings.get("transition_reset")
    if legacy is not None and legacy.get("probability") != 0:
        raise ValueError("transition_reset is retired; remove the legacy state-library configuration")
    _validate_asset_names(cfg)
    _validate_training(cfg)
    if TASKS[task].policy == "p1":
        _validate_reset_map(cfg)
    _validate_shu(cfg)
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
    if TASKS[cfg.task].policy == "p1":
        _validate_p1_randomization(cfg)
        controls = cfg.settings.get("control_randomization") or {}
        for key in ("gain_scale", "output_scale"):
            path = f"policy.training.control_randomization.{key}"
            bounds = _values(controls.get(key), path, 2)
            if len(bounds) != 2 or not 0 < bounds[0] <= bounds[1]:
                raise ValueError(f"{path}: expected an ordered positive scale range")
        delay = controls.get("action_delay_steps")
        if (
            not isinstance(delay, tuple)
            or len(delay) != 2
            or any(type(step) is not int for step in delay)
            or not 0 <= delay[0] <= delay[1]
        ):
            raise ValueError(
                "policy.training.control_randomization.action_delay_steps: expected two ordered step counts"
            )
        duration = cfg.shared["randomization"]["external_wrench_duration_s"]
        if type(duration) not in (float, int) or not isfinite(duration) or duration <= 0:
            raise ValueError("external_wrench_duration_s must be finite and positive")
        if duration < cfg.shared["randomization"]["push_interval_s"][1]:
            raise ValueError("external_wrench_duration_s must be >= the upper bound of push_interval_s")
        collision_duration = cfg.settings["disturbance"]["collision_duration_s"]
        if type(collision_duration) not in (float, int) or not isfinite(collision_duration) or collision_duration <= 0:
            raise ValueError("collision_duration_s must be finite and positive")
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
    family = TASKS[cfg.task].policy
    commands = cfg.settings.get("commands") or {}
    for axis in ("linear_slew_m_s2", "angular_slew_rad_s2"):
        if commands.get(axis) is not None:
            command_rate(commands, axis)
    if family == "p1":
        probabilities = commands.get("segment_probabilities")
        if probabilities is not None:
            weights = _values(probabilities, "commands.segment_probabilities", 6)
            if any(x < 0 for x in weights) or (len(weights) == 6 and abs(sum(weights) - 1) > 1e-6):
                raise ValueError("Segment probabilities must be nonnegative and sum to one")
        for key in ("combined_wz_limit_rad_s", "heading_kp", "heading_max_wz"):
            value = commands.get(key)
            if value is not None and (type(value) not in (float, int) or not isfinite(value) or value <= 0):
                raise ValueError(f"commands.{key}: expected a finite positive value")
    else:
        weights = cfg.settings["rewards"]
        if weights.get("leg_symmetry") and (weights.get("no_fork") or weights.get("no_fork_square")):
            raise ValueError("leg_symmetry and no_fork must not be enabled together")
    ranges = ("height_range_m", "segment_duration_s", "height_duration_s")
    if family == "p1":
        ranges += ("vx_range_m_s", "wz_range_rad_s", "dash_speed_abs_m_s")
    elif cfg.task == "p3-jump":
        ranges += ("vx_range_m_s",)
    for key in ranges:
        if commands.get(key) is not None:
            bounds = _values(commands[key], f"commands.{key}", 2)
            if len(bounds) == 2 and bounds[0] > bounds[1]:
                raise ValueError(f"commands.{key}: expected [lower, upper]")
            if key == "dash_speed_abs_m_s" and any(v <= 0 for v in bounds):
                raise ValueError(f"commands.{key}: expected positive magnitudes")
    if cfg.task == "p2-spin":
        rates, weights = cfg.stage.get("spin_rates_rad_s"), cfg.stage.get("spin_probabilities")
        for key, seq in (("spin_rates_rad_s", rates), ("spin_probabilities", weights)):
            if seq is None:
                continue
            if not isinstance(seq, tuple) or not seq:
                raise ValueError(f"spin.{key}: expected a nonempty vector")
            known = _values(seq, key, len(seq))
            if key == "spin_rates_rad_s" and any(abs(x) > 18 for x in known):
                raise ValueError("spin_rates_rad_s exceeds the simulation limit of 18 rad/s")
            if key == "spin_probabilities" and (
                any(x < 0 for x in known) or (len(known) == len(seq) and abs(sum(known) - 1) > 1e-6)
            ):
                raise ValueError("spin_probabilities must be nonnegative and sum to one")
        if rates is not None and weights is not None and len(rates) != len(weights):
            raise ValueError("spin_probabilities must match spin_rates_rad_s")
    if family == "p3":
        stage = cfg.stage
        heights = stage.get("height_range_m")
        if heights is not None:
            known = _values(heights, "height_range_m", 2)
            if any(x <= 0 for x in known) or (len(known) == 2 and known[1] < known[0]):
                raise ValueError("Jump height range must be positive and ordered")
        for key in ("event_duration_s", "landing_stable_s", "landing_tilt_rad"):
            value = stage.get(key)
            if value is not None and (type(value) not in (float, int) or not isfinite(value) or value <= 0):
                raise ValueError(f"P3 {key}: expected a finite positive value")
        for key in ("flight_tracking_scale", "jump_smooth_scale"):
            scale = stage.get(key)
            if scale is not None and (type(scale) not in (float, int) or not 0 <= scale <= 1):
                raise ValueError(f"P3 {key}: expected a fraction in [0,1]")
        window = stage.get("press_time_range_s")
        if window is not None:
            known = _values(window, "press_time_range_s", 2)
            if any(x < 0 for x in known) or (len(known) == 2 and known[0] > known[1]):
                raise ValueError("press_time_range_s: expected nonnegative ordered bounds")
        for key in ("no_press_probability", "moving_probability"):
            value = stage.get(key)
            if value is not None and (type(value) not in (float, int) or not 0 <= value <= 1):
                raise ValueError(f"{key}: expected a fraction in [0,1]")
        tunnel = stage.get("tunnel") or {}
        for key in ("beam_length_m", "beam_width_m", "beam_height_m", "lane_width_m"):
            value = tunnel.get(key)
            if value is not None and (type(value) not in (float, int) or not isfinite(value) or value <= 0):
                raise ValueError(f"P3 tunnel.{key}: expected a finite positive value")
        for key in ("beam_bottom_m", "clearance_margin_m", "landing_margin_m", "ground_tolerance_m"):
            value = tunnel.get(key)
            if value is not None and (type(value) not in (float, int) or not isfinite(value) or value < 0):
                raise ValueError(f"P3 tunnel.{key}: expected a finite nonnegative value")
        bottom, top = tunnel.get("beam_bottom_m"), tunnel.get("beam_height_m")
        if bottom is not None and top is not None and bottom >= top:
            raise ValueError("P3 tunnel.beam_bottom_m must be below beam_height_m")
        offset = tunnel.get("beam_offset_from_entrance_m")
        if offset is not None and (type(offset) not in (int, float) or not isfinite(offset)):
            raise ValueError("P3 tunnel.beam_offset_from_entrance_m: expected a finite offset")
        for key in ("vx_range_m_s", "approach_distance_range_m", "initial_yaw_range_rad"):
            if tunnel.get(key) is not None:
                known = _values(tunnel[key], f"tunnel.{key}", 2)
                if len(known) == 2 and known[0] > known[1]:
                    raise ValueError(f"P3 tunnel.{key}: expected an ordered range")
    if family != "p1":
        return
    phase = cfg.stage["disturbance_phase"]
    if type(phase) is not int or phase not in (1, 2):
        raise ValueError("disturbance_phase must be 1 or 2")
    schedule = cfg.settings["disturbance"]
    if not 2000 <= schedule["ramp_iterations"] <= 4000:
        raise ValueError("Guide v2.1 requires a 2000-4000 iteration disturbance ramp")
    if not 1.0 <= schedule["final_push_velocity_m_s"] <= 1.5:
        raise ValueError("Guide v2.1 final velocity push must be in [1.0,1.5] m/s")


def _validate_p3_button_schedule(cfg: TrainingConfig) -> None:
    bounds = cfg.stage["press_time_range_s"]
    _values(bounds, "press_time_range_s", 2)
    lo, hi = bounds
    if lo < 0 or hi < lo:
        raise ValueError("press_time_range_s: expected a nonnegative ordered interval")
    probability = cfg.stage["no_press_probability"]
    moving = cfg.stage["moving_probability"]
    if type(probability) not in (float, int) or not 0 <= probability < 1:
        raise ValueError("no_press_probability must be in [0,1) for P3 training to receive button presses")
    if type(moving) not in (float, int) or not 0 <= moving <= 1:
        raise ValueError("moving_probability must be in [0,1]")
    if cfg.task == "p3-tunnel" and moving == 0:
        raise ValueError("p3-tunnel training requires a nonzero moving_probability")
    hz = cfg.robot.policy_hz
    if ceil(hi * hz) >= ceil(cfg.settings["episode_length_s"] * hz):
        raise ValueError("latest press must leave at least one actionable policy interval")


def _validate_p3_rollout(cfg: TrainingConfig) -> None:
    p = cfg.settings["evaluation"]
    if type(p["seed"]) is not int or p["seed"] < 0:
        raise ValueError("evaluation.seed must be a nonnegative integer")
    if type(p["episodes_per_case"]) is not int or p["episodes_per_case"] <= 0:
        raise ValueError("evaluation.episodes_per_case must be a positive integer")
    for key in ("duration_s", "height_m"):
        value = p[key]
        if type(value) not in (int, float) or not isfinite(value) or value <= 0:
            raise ValueError(f"evaluation.{key} must be finite and positive")
    if round(p["duration_s"] * cfg.robot.policy_hz) < 1:
        raise ValueError("evaluation.duration_s must cover at least one policy interval")


def _values(value, key, length):
    if not isinstance(value, tuple) or len(value) != length:
        raise ValueError(f"{key}: expected {length} entries")
    for x in value:
        if x is not None and (type(x) not in (float, int) or not isfinite(x)):
            raise ValueError(f"{key}: expected finite numbers or null")
    return [x for x in value if x is not None]


def _validate_p1_randomization(cfg: TrainingConfig) -> None:
    randomization = cfg.shared["randomization"]
    prefix = "robot.training.randomization"
    for key in _P1_MASS_FIELDS:
        if randomization.get(key) is None:
            continue
        path = f"{prefix}.{key}"
        if key == "com_offset_m":
            if any(v < 0 for v in _values(randomization[key], path, 3)):
                raise ValueError(f"{path}: expected nonnegative XYZ offset magnitudes")
        else:
            vals = _values(randomization[key], path, 2)
            if any(v <= 0 for v in vals) or (len(vals) == 2 and vals[0] > vals[1]):
                raise ValueError(f"{path}: expected an ordered positive scale range")
    materials = randomization.get("p1_materials")
    if materials is not None and (
        not isinstance(materials, MappingProxyType) or set(materials) - set(_P1_MATERIAL_GROUPS)
    ):
        raise ValueError(f"{prefix}.p1_materials: expected a mapping of base and guide materials")
    groups = [(prefix, randomization)]
    groups.extend((f"{prefix}.p1_materials.{group}", (materials or {}).get(group)) for group in _P1_MATERIAL_GROUPS)
    for path, group in groups:
        if group is None:
            continue
        if not isinstance(group, MappingProxyType):
            raise ValueError(f"{path}: expected a material mapping")
        fields = _P1_MATERIAL_FIELDS[:2] if path == prefix else _P1_MATERIAL_FIELDS
        for key in fields:
            if group.get(key) is None:
                continue
            vals = _values(group[key], f"{path}.{key}", 2)
            if any(v < 0 or (key == "restitution" and v > 1) for v in vals) or (len(vals) == 2 and vals[0] > vals[1]):
                raise ValueError(f"{path}.{key}: expected an ordered nonnegative range, restitution at most 1")
        static, dynamic = group.get("static_friction"), group.get("dynamic_friction")
        if static and dynamic and static[0] is not None and dynamic[0] is not None and dynamic[0] > static[0]:
            raise ValueError(f"{path}.dynamic_friction: its lower bound must not exceed the static lower bound")


def _validate_reset_map(cfg):
    branch = (cfg.shared.get("shu_spawn") or {}).get("ik_branch")
    if branch is not None and branch != "symmetric_five_bar_v1":
        raise ValueError("shu_spawn.ik_branch: expected symmetric_five_bar_v1")
    raw = cfg.shared.get("shu_reset_map")
    if raw is None:
        return
    if not isinstance(raw, MappingProxyType):
        raise ValueError("shu_reset_map: expected a mapping")
    m = _required(raw, _RESET_KEYS)
    if m["mode"] is not None and m["mode"] != _RESET_MODE:
        raise ValueError(f"shu_reset_map.mode: expected {_RESET_MODE}")
    for key, size in {**_RESET_SIGNS, "canonical_zero_in_asset_rad": 14, "zero_pin_distance_m": 2}.items():
        if m[key] is not None:
            known = _values(m[key], key, size)
            if key in _RESET_SIGNS and any(x not in (-1, 1) for x in known):
                raise ValueError(f"shu_reset_map.{key}: expected calibrated signs (+1/-1)")
    for key in _RESET_PAIRS:
        rows = m[key]
        if rows is None:
            continue
        if not isinstance(rows, tuple) or len(rows) != 2:
            raise ValueError(f"shu_reset_map.{key}: expected L/R pairs")
        for row in rows:
            if row is not None:
                vals = _values(row, key, 2)
                if key == "slider_safe_range_m" and len(vals) == 2 and vals[0] >= vals[1]:
                    raise ValueError("shu_reset_map.slider_safe_range_m: expected lower < upper")
    names = m["auxiliary_joint_names"]
    if names is not None:
        if not isinstance(names, tuple) or len(names) not in (0, 2):
            raise ValueError("shu_reset_map.auxiliary_joint_names: expected [] or two exact L/R names")
        known = [x for x in names if x is not None]
        if any(not isinstance(x, str) or not x.isidentifier() for x in known) or len(set(known)) != len(known):
            raise ValueError("shu_reset_map.auxiliary_joint_names: expected distinct literal names")
    for key in ("hinge_zero_xz_rad", "hinge_asset_sign"):
        values = m[key]
        if values is None:
            continue
        if not isinstance(values, tuple) or len(values) not in (0, 2):
            raise ValueError(f"shu_reset_map.{key}: expected [] or two L/R values")
        known = _values(values, key, len(names) if names is not None else len(values))
        if key == "hinge_asset_sign" and any(x not in (-1, 1) for x in known):
            raise ValueError("shu_reset_map.hinge_asset_sign: expected calibrated signs (+1/-1)")
    if not null_fields(m, "shu_reset_map"):
        # A fully populated map must pass the same geometric checks as the actual reset adapter.
        from .shu_spawn import CalibratedResetModel

        CalibratedResetModel(**raw)


def _validate_shu(cfg: TrainingConfig) -> None:
    family = TASKS[cfg.task].policy
    if family == "p1":
        signs = cfg.shared.get("wheel_rim_sign")
        if signs is not None and any(x not in (-1, 1) for x in _values(signs, "wheel_rim_sign", 2)):
            raise ValueError("wheel_rim_sign: expected two calibrated signs (+1/-1)")
        rewards = cfg.settings.get("shu_rewards") or {}
        for key in _SHU_REWARDS:
            x = rewards.get(key)
            if x is not None and (
                type(x) not in (int, float) or not isfinite(x) or x < 0 or (key != "height_wide_weight" and x == 0)
            ):
                raise ValueError(f"shu_rewards.{key}: invalid coefficient")
    if family == "p1":
        for section, keys in (
            ("shu_contact", _SHU_CONTACT),
            ("termination", ("tilt_rad", "contact_force_n", "duration_s", "decay_s")),
        ):
            for key in keys:
                x = (cfg.shared.get(section) or {}).get(key)
                if x is not None and (type(x) not in (int, float) or not isfinite(x) or x <= 0):
                    raise ValueError(f"robot.training.{section}.{key}: expected a finite positive value")
    if cfg.task == "p1-stairs":
        route = cfg.stage["terrain"]["route"]
        for key in ("up_height_range_m", "down_height_range_m"):
            bounds = _values(route.get(key), key, 2)
            if any(x <= 0 for x in bounds) or (len(bounds) == 2 and bounds[0] > bounds[1]):
                raise ValueError(f"{key}: expected positive ordered heights")
    if cfg.task in ("p1-flat", "p1-stairs"):
        prob = cfg.stage.get("recovery_probability") if cfg.task == "p1-flat" else cfg.flat_recovery_probability
        if prob is not None and (type(prob) not in (float, int) or not 0 <= prob <= 1):
            raise ValueError("flat.recovery_probability must be in [0,1]")
    if cfg.task == "p1-flat":
        for key in ("error_floor", "relative_error"):
            value = cfg.stage.get(key)
            if value is not None and any(x < 0 for x in _values(value, key, 3)):
                raise ValueError(f"flat.{key}: expected nonnegative errors")
        for key in ("min_segments", "initial_fraction"):
            value = cfg.stage.get(key)
            if value is None:
                continue
            values = _values(value, key, 6) if isinstance(value, tuple) else [value]
            for x in values:
                if key == "min_segments" and (type(x) is not int or x <= 0):
                    raise ValueError("flat.min_segments must be positive integers")
                if key == "initial_fraction" and (type(x) not in (float, int) or not 0 < x <= 1):
                    raise ValueError("flat.initial_fraction must be in (0,1]")
    if cfg.task == "p1-landing":
        for key in ("air_wheel_height_bias_m", "air_wheel_height_max_m"):
            value = cfg.stage.get(key)
            if value is not None and (type(value) not in (int, float) or not isfinite(value) or value <= 0):
                raise ValueError(f"landing.{key}: expected finite positive metres or null")
    if cfg.task == "p1-landing" and cfg.stage.get("height_edges_m") is not None:
        edges = _values(cfg.stage["height_edges_m"], "height_edges_m", 5)
        if any(x < 0 for x in edges) or any(a >= b for a, b in zip(edges, edges[1:])):
            raise ValueError("landing.height_edges_m must be nonnegative and strictly increasing")


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
