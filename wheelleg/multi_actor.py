"""Named actor bundles. Routing never changes the fixed seven-slot mode contract."""

import hashlib
from copy import deepcopy
from pathlib import Path

import torch
import yaml
from torch import nn

from .checkpoints import load_policy_module
from .config import load_policy, load_robot
from .observation import MODE_CONTRACT_REVISION


def resume_contract_matches(
    saved: dict | None,
    current: dict,
    handoff_vertical_speed: float | None = None,
    handoff_duration: float | None = None,
    air_motion_update: bool = False,
    crouch_guidance_update: bool = False,
) -> bool:
    if saved is None:
        return False
    if (
        handoff_vertical_speed is None
        and handoff_duration is None
        and not air_motion_update
        and not crouch_guidance_update
    ):
        return saved == current
    if "actor_bundle" not in saved or "actor_bundle" not in current:
        return False
    migrated = deepcopy(saved)
    if crouch_guidance_update:
        if "jump_event_stage" not in migrated or "jump_event_stage" not in current:
            return False
        previous = migrated["jump_event_stage"].get("clearance_jump", {})
        stage = current["jump_event_stage"].get("clearance_jump", {})
        if "crouch_guidance" not in stage:
            return False
        previous["crouch_guidance"] = deepcopy(stage["crouch_guidance"])
    if air_motion_update:
        if "jump_event_stage" not in migrated or "jump_event_stage" not in current:
            return False
        previous, stage = migrated["jump_event_stage"], current["jump_event_stage"]
        previous["clearance_jump"]["air_smoothness"] = deepcopy(stage["clearance_jump"]["air_smoothness"])
        previous["clearance_jump"]["reward_overrides"]["jump_air_leg_smoothness"] = stage["clearance_jump"][
            "reward_overrides"
        ]["jump_air_leg_smoothness"]
        for key in ("tuck_extension_tolerance_m", "tuck_extension_cost_per_m"):
            previous["body_wheel_jump"]["air_leg_guard"][key] = stage["body_wheel_jump"]["air_leg_guard"][key]
    for key, value in (("vertical_speed_m_s", handoff_vertical_speed), ("duration_s", handoff_duration)):
        if value is not None:
            if current["actor_bundle"]["handoff"][key] != value:
                return False
            migrated["actor_bundle"]["handoff"][key] = value
    if handoff_duration == 0:
        migrated["actor_bundle"]["handoff"]["failure_cost"] = 0.0
    return migrated == current


def read_bundle(path: Path, specialist_checkpoint: Path | None = None) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data.get("version") != 1 or data.get("mode_contract_revision") != MODE_CONTRACT_REVISION:
        raise ValueError("Actor bundle version or mode contract does not match")
    actors = data.get("actors", {})
    if not actors or data.get("default_actor") not in actors or data.get("trainable_actor") not in actors:
        raise ValueError("Bundle must name default_actor and trainable_actor in actors")
    if data["default_actor"] == data["trainable_actor"]:
        raise ValueError("Base actor and trainable specialist must be separate")
    for name, spec in actors.items():
        if not name.isidentifier():
            raise ValueError("Actor names must be identifiers")
        if name == data["trainable_actor"] and specialist_checkpoint is not None:
            spec["checkpoint"] = str(specialist_checkpoint.resolve())
            spec["policy"] = str((specialist_checkpoint.parent / "params/policy_meta.yaml").resolve())
            spec["robot"] = str((specialist_checkpoint.parent / "params/robot.yaml").resolve())
        for key in ("checkpoint", "policy", "robot"):
            spec[key] = str((path.parent / spec[key]).resolve())
            if not Path(spec[key]).is_file():
                raise ValueError(f"Missing {name} {key}: {spec[key]}")
        digest = hashlib.sha256(Path(spec["checkpoint"]).read_bytes()).hexdigest()
        replacing = name == data["trainable_actor"] and specialist_checkpoint is not None
        if spec.get("sha256") and not replacing and spec["sha256"] != digest:
            raise ValueError(f"Actor checkpoint changed: {name}")
        spec["sha256"] = digest
    handoff = data["handoff"]
    if not 0 <= float(handoff["duration_s"]) < float("inf"):
        raise ValueError("Invalid handoff duration_s")
    for key in ("tilt_rad", "vertical_speed_m_s", "angular_xy_rad_s", "vx_error_m_s", "yaw_error_rad_s"):
        if not 0 < float(handoff[key]) < float("inf"):
            raise ValueError(f"Invalid handoff {key}")
    if not -float("inf") < float(handoff["failure_cost"]) <= 0:
        raise ValueError("Handoff failure_cost must be finite and nonpositive")
    return data


class BundlePolicy(nn.Module):
    """Deterministic Landing/Jump routing for evaluation; bank supports additional explicit actor IDs."""

    def __init__(self, bank):
        super().__init__()
        self.bank = bank

    def forward(self, observation, history=None):
        ids = torch.where(actor_mask(observation), self.bank.specialist, self.bank.default)
        return self.bank(observation, ids)


class NumpyBundlePolicy:
    def __init__(self, checkpoint: Path, bundle_path: Path, handoff_vertical_speed: float | None = None):
        bundle = read_bundle(bundle_path, checkpoint)
        if handoff_vertical_speed is not None:
            bundle["handoff"]["vertical_speed_m_s"] = handoff_vertical_speed
        self.bank = ActorBank(bundle, "cpu")
        self.policy = BundlePolicy(self.bank)
        self.iteration = torch.load(checkpoint, map_location="cpu", weights_only=True).get("iter")

    def __call__(self, observation):
        with torch.inference_mode():
            return self.policy(torch.as_tensor(observation, dtype=torch.float32).unsqueeze(0))[0].numpy()


class ActorBank(nn.Module):
    """Any number of named deterministic actors; an optional specialist is supplied by PPO."""

    def __init__(self, bundle: dict, device: str, *, training: bool = False):
        super().__init__()
        self.bundle = bundle
        self.actors = nn.ModuleDict()
        self.names = tuple(bundle["actors"])
        self.default = self.names.index(bundle["default_actor"])
        self.specialist = self.names.index(bundle["trainable_actor"])
        reference = None
        for name, spec in bundle["actors"].items():
            policy, robot = load_policy(spec["policy"]), load_robot(spec["robot"])
            if policy.history_frames or policy.obs_version != 2:
                raise ValueError("Actor bundles currently require single-frame obs_v2")
            contract = (
                robot.joint_order,
                robot.q_default_rad,
                robot.control_hz,
                robot.policy_hz,
                robot.observation_clip,
                policy.command_scale,
                policy.height_scale,
                policy.angular_velocity_scale,
                policy.gravity_scale,
                policy.joint_position_scale,
                policy.joint_velocity_scale,
                policy.action_scales,
                policy.action_clip,
                policy.kp,
                policy.kd,
                policy.torque_limit_nm,
            )
            if reference is not None and reference != contract:
                raise ValueError("Actors must share sensor, action and physical-controller contracts")
            reference = contract
            if training and name == bundle["trainable_actor"]:
                continue
            module = load_policy_module(spec["checkpoint"], policy).to(device).eval()
            module.requires_grad_(False)
            self.actors[name] = module

    def forward(self, observation: torch.Tensor, actor_ids: torch.Tensor) -> torch.Tensor:
        if actor_ids.shape != observation.shape[:-1] or not bool(
            ((actor_ids >= 0) & (actor_ids < len(self.names))).all()
        ):
            raise ValueError("Invalid actor selection")
        actions = observation.new_empty((*actor_ids.shape, 6))
        for index, name in enumerate(self.names):
            selected = actor_ids == index
            if selected.any():
                if name not in self.actors:
                    raise ValueError("Trainable actor actions must come from PPO")
                actions[selected] = self.actors[name](observation[selected])
        return actions


def actor_mask(observation: torch.Tensor) -> torch.Tensor:
    """Jump owns the full event, including its landing recovery."""
    return observation[..., 32] > 0.5  # mode starts at 28, jump is slot 4.


def masked_mean(values: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
    return torch.where(mask.bool(), values, 0).sum() / mask.sum().clamp_min(1)
