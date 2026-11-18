import torch
from torch import nn

from .config import PolicyConfig
from .history import ENCODER_HIDDEN_DIMS, HISTORY_DIM, VELOCITY_DIM, history_contract
from .observation import OBS_DIM, POLICY_OBS_DIM


def _elu_mlp(input_dim: int, hidden_dims: tuple[int, ...], output_dim: int) -> nn.Sequential:
    layers = []
    for width in hidden_dims:
        layers.extend((nn.Linear(input_dim, width), nn.ELU()))
        input_dim = width
    layers.append(nn.Linear(input_dim, output_dim))
    return nn.Sequential(*layers)


def actor_input(obs: torch.Tensor, velocity: torch.Tensor) -> torch.Tensor:
    return torch.cat((obs[..., :OBS_DIM], velocity, obs[..., OBS_DIM:]), dim=-1)


def build_actor(policy: PolicyConfig) -> nn.Sequential:
    """Action mean from [current obs, estimated body vx/vy/vz, jump_request_m], before clipping."""
    return _elu_mlp(POLICY_OBS_DIM + VELOCITY_DIM, policy.hidden_dims, len(policy.action_scales))


def build_encoder() -> nn.Sequential:
    return _elu_mlp(HISTORY_DIM, ENCODER_HIDDEN_DIMS, VELOCITY_DIM)


def policy_contract(policy: PolicyConfig) -> dict:
    """Checkpoint and deployment signature; obs_version itself describes the per-frame layout."""
    return {
        "obs_version": policy.obs_version,
        "actor_hidden_dims": list(policy.hidden_dims),
        "activation": policy.activation,
        "observation_scales": {
            "command": list(policy.command_scale),
            "height": policy.height_scale,
            "angular_velocity": policy.angular_velocity_scale,
            "gravity": policy.gravity_scale,
            "joint_position": policy.joint_position_scale,
            "joint_velocity": policy.joint_velocity_scale,
        },
        "action_scales": list(policy.action_scales),
        "action_clip": policy.action_clip,
        "velocity_encoder": history_contract(),
    }


class DeployedPolicy(nn.Module):
    """Deterministic two-input inference: obs[...,27], obs_history[...,130] -> actions[...,6]."""

    def __init__(self, policy: PolicyConfig) -> None:
        super().__init__()
        self.actor = build_actor(policy)
        self.encoder = build_encoder()

    def forward(self, obs: torch.Tensor, obs_history: torch.Tensor) -> torch.Tensor:
        return self.actor(actor_input(obs, self.encoder(obs_history)))
