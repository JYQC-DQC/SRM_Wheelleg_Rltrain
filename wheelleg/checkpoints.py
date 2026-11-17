from collections.abc import Mapping
from pathlib import Path

import torch

from .actor import DeployedPolicy, policy_contract
from .config import PolicyConfig


def _inference_state(checkpoint: Path, data: dict, policy: PolicyConfig) -> dict:
    contract = (data.get("infos") or {}).get("observation_contract", {})
    if contract.get("policy") != policy_contract(policy):
        raise ValueError(f"{checkpoint}: incompatible Actor/velocity encoder contract (requires five frames and xyz)")
    # Match the deployment module exactly; strict loading rejects incomplete or differently shaped heads.
    return {key: value for key, value in data["model_state_dict"].items() if key.startswith(("actor.", "encoder."))}


def load_actor(checkpoint: str | Path, policy: PolicyConfig, *, source_task: str | None = None) -> DeployedPolicy:
    """Extract the complete deterministic inference module, not the bare action head."""
    checkpoint = Path(checkpoint)
    data = torch.load(checkpoint, map_location="cpu", weights_only=True)
    deployed = DeployedPolicy(policy)
    deployed.load_state_dict(_inference_state(checkpoint, data, policy), strict=True)
    if source_task is not None and (data["infos"]["observation_contract"].get("task") != source_task):
        raise ValueError(f"{checkpoint}: expected a {source_task} checkpoint")
    return deployed.eval()


def initialize_actor(runner, checkpoint: str | Path) -> None:
    """Transfer the Actor and encoder only; critic, std, optimizers and stage state remain fresh."""
    checkpoint = Path(checkpoint)
    cfg = runner.env.unwrapped.training
    data = torch.load(checkpoint, map_location="cpu", weights_only=True)
    state = _inference_state(checkpoint, data, cfg.policy)
    target = runner.alg.policy
    for name, module in (("actor", target.actor), ("encoder", target.encoder)):
        prefix = name + "."
        module.load_state_dict(
            {key.removeprefix(prefix): value for key, value in state.items() if key.startswith(prefix)}, strict=True
        )


def load_landing_transfer(checkpoint: str | Path, policy: PolicyConfig, *, source_task: str, commands: Mapping) -> dict:
    """Require a full flat command curriculum before creating a landing environment."""
    from .shu_curriculum import N_KINDS
    from .training import mutable

    checkpoint = Path(checkpoint)
    data = torch.load(checkpoint, map_location="cpu", weights_only=True)
    # Validate the actual tensors as well as metadata before construction of the landing env.
    deployed = DeployedPolicy(policy)
    deployed.load_state_dict(_inference_state(checkpoint, data, policy), strict=True)
    infos = data["infos"]
    if infos["observation_contract"].get("task") != source_task:
        raise ValueError(f"{checkpoint}: landing requires a {source_task} checkpoint")
    proof = infos.get("shu_curriculum", {}).get("flat_transfer") or {}
    if not (
        proof.get("stage") == "p1-flat"
        and proof.get("all_full") is True
        and proof.get("fractions") == [1.0] * N_KINDS
        and proof.get("commands") == mutable(commands)
    ):
        raise ValueError(f"{checkpoint}: landing requires all flat command buckets at full range and matching commands")
    return proof


def require_target_runtime() -> None:
    from importlib.metadata import version

    if version("rsl-rl-lib") != "3.1.2":
        raise RuntimeError("Use Isaac Lab 2.3.2 with rsl-rl-lib==3.1.2; do not upgrade the cloud image blindly")
