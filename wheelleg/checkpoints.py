from pathlib import Path

import torch

from .actor import build_actor
from .config import PolicyConfig


def load_actor(checkpoint: str | Path, policy: PolicyConfig) -> torch.nn.Module:
    """Strict actor-only extraction from an rsl_rl 3.1.2 checkpoint."""
    state = torch.load(checkpoint, map_location="cpu", weights_only=True)["model_state_dict"]
    actor = build_actor(policy)
    actor_state = {key.removeprefix("actor."): value for key, value in state.items() if key.startswith("actor.")}
    actor.load_state_dict(actor_state, strict=True)
    return actor.eval()


def initialize_actor(runner, checkpoint: str | Path) -> None:
    """Cross-stage transfer: actor only; critic/optimizer/iteration are fresh."""
    state = torch.load(checkpoint, map_location=runner.device, weights_only=True)["model_state_dict"]
    actor_state = {key.removeprefix("actor."): value for key, value in state.items() if key.startswith("actor.")}
    runner.alg.policy.actor.load_state_dict(actor_state, strict=True)


def require_target_runtime() -> None:
    from importlib.metadata import version

    if version("rsl-rl-lib") != "3.1.2":
        raise RuntimeError("Use Isaac Lab 2.3.2 with rsl-rl-lib==3.1.2; do not upgrade the cloud image blindly")
