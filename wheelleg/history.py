"""Optional history estimator (guide section 7.2); disabled unless history_estimator.frames > 0.

The estimator reads the last frames of the actor observation (exactly what the robot sees: delayed, noisy,
clipped) and predicts the body-frame base velocity and the two wheel contacts. The actor receives the
detached estimate after its 35 observation entries. Simulator truth is only a training label.
"""

import torch
import torch.nn.functional as F
from torch import nn

from .config import PolicyConfig
from .observation import OBS_DIM

# Body-frame base velocity, m/s (3); left/right wheel contact probability (2).
ESTIMATE_DIM = 5


def actor_input_dim(policy: PolicyConfig) -> int:
    return OBS_DIM + (ESTIMATE_DIM if policy.history_frames else 0)


class HistoryEstimator(nn.Module):
    """(..., frames * 35) oldest-first history -> (..., 5) velocity and contact logits."""

    def __init__(self, frames: int, hidden_dims: tuple[int, ...] | list[int]) -> None:
        super().__init__()
        layers, width = [], frames * OBS_DIM
        for size in hidden_dims:
            layers.extend((nn.Linear(width, size), nn.ELU()))
            width = size
        layers.append(nn.Linear(width, ESTIMATE_DIM))
        self.net = nn.Sequential(*layers)

    def forward(self, history: torch.Tensor) -> torch.Tensor:
        return self.net(history)

    def features(self, history: torch.Tensor) -> torch.Tensor:
        raw = self(history)
        return torch.cat((raw[..., :3], torch.sigmoid(raw[..., 3:])), -1)


def estimator_loss(
    raw: torch.Tensor, target: torch.Tensor, velocity_coef: float, contact_coef: float
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Velocity MSE plus contact BCE; target is (..., 5) with contacts as 0/1."""
    velocity = F.mse_loss(raw[..., :3], target[..., :3])
    contact = F.binary_cross_entropy_with_logits(raw[..., 3:], target[..., 3:])
    return velocity_coef * velocity + contact_coef * contact, velocity, contact


class DeployedPolicy(nn.Module):
    """Deterministic policy as exported: obs[...,35] (and obs_history[..., frames*35] when enabled)."""

    def __init__(self, actor: nn.Module, estimator: HistoryEstimator | None = None) -> None:
        super().__init__()
        self.actor = actor
        self.estimator = estimator

    def forward(self, obs: torch.Tensor, obs_history: torch.Tensor | None = None) -> torch.Tensor:
        if self.estimator is None:
            return self.actor(obs)
        return self.actor(torch.cat((obs, self.estimator.features(obs_history)), -1))


class HistoryBuffer:
    """Per-environment ring of actor observations, updated in place (safe across inference_mode).

    A reset environment is refilled with its first new frame, as in Fudan's encoder; firmware must do the same
    on every policy switch.
    """

    def __init__(self, num_envs: int, frames: int, width: int, device: str | torch.device) -> None:
        self.frames = torch.zeros(num_envs, frames, width, device=device)
        self.fresh = torch.ones(num_envs, dtype=torch.bool, device=device)

    def reset(self, ids: torch.Tensor) -> None:
        self.fresh[ids] = True

    def update(self, frame: torch.Tensor, new_step: bool) -> None:
        """Append on a new policy step; a repeated read within one step only refreshes the newest frame."""
        if new_step:
            self.frames.copy_(torch.roll(self.frames, -1, dims=1))
        self.frames[:, -1] = frame
        fresh = self.fresh.nonzero().flatten()
        self.frames[fresh] = frame[fresh, None].expand(-1, self.frames.shape[1], -1)
        self.fresh.zero_()

    def flat(self) -> torch.Tensor:
        return self.frames.flatten(1)


def expand_actor_input(actor_state: dict, input_dim: int) -> dict:
    """Zero columns for new actor inputs: the expanded actor reproduces the old one exactly at the start."""
    weight = actor_state["0.weight"]
    if weight.shape[1] > input_dim:
        raise ValueError(f"Cannot shrink the actor input from {weight.shape[1]} to {input_dim}")
    padded = weight.new_zeros(weight.shape[0], input_dim)
    padded[:, : weight.shape[1]] = weight
    return {**actor_state, "0.weight": padded}
