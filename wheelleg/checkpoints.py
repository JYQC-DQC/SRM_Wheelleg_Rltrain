from pathlib import Path

import torch

from .actor import build_actor
from .config import PolicyConfig
from .history import DeployedPolicy, HistoryEstimator, expand_actor_input
from .observation import OBS_DIM


def _prefixed(state: dict, prefix: str) -> dict:
    return {key.removeprefix(prefix): value for key, value in state.items() if key.startswith(prefix)}


def load_actor(checkpoint: str | Path, policy: PolicyConfig) -> torch.nn.Module:
    """Strict actor-only extraction from an rsl_rl 3.1.2 checkpoint."""
    state = torch.load(checkpoint, map_location="cpu", weights_only=True)["model_state_dict"]
    actor = build_actor(policy)
    actor.load_state_dict(_prefixed(state, "actor."), strict=True)
    return actor.eval()


def load_policy_module(checkpoint: str | Path, policy: PolicyConfig) -> DeployedPolicy:
    """Actor plus, for obs_version 3, the history estimator; call as module(obs, obs_history)."""
    estimator = None
    if policy.history_frames:
        state = torch.load(checkpoint, map_location="cpu", weights_only=True)["model_state_dict"]
        estimator = HistoryEstimator(policy.history_frames, policy.estimator_hidden_dims)
        estimator.load_state_dict(_prefixed(state, "estimator."), strict=True)
    return DeployedPolicy(load_actor(checkpoint, policy), estimator).eval()


def initialize_actor(runner, checkpoint: str | Path) -> None:
    """Cross-stage transfer: actor only; critic/optimizer/iteration are fresh.

    A single-frame (35-input) actor moved into a history policy gets zero weights for the estimate inputs, so it
    starts with exactly the old behaviour. A source estimator is reused when present; otherwise it starts fresh.
    """
    state = torch.load(checkpoint, map_location=runner.device, weights_only=True)["model_state_dict"]
    policy = runner.alg.policy
    actor_state = _prefixed(state, "actor.")
    target_inputs = policy.actor.state_dict()["0.weight"].shape[1]
    if actor_state["0.weight"].shape[1] == OBS_DIM and target_inputs > OBS_DIM and hasattr(policy, "estimator"):
        actor_state = expand_actor_input(actor_state, target_inputs)
    policy.actor.load_state_dict(actor_state, strict=True)
    estimator_state = _prefixed(state, "estimator.")
    if estimator_state and hasattr(policy, "estimator"):
        policy.estimator.load_state_dict(estimator_state, strict=True)


def require_target_runtime() -> None:
    from importlib.metadata import version

    if version("rsl-rl-lib") != "3.1.2":
        raise RuntimeError("Use Isaac Lab 2.3.2 with rsl-rl-lib==3.1.2; do not upgrade the cloud image blindly")
