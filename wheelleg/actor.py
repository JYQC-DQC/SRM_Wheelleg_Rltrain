from torch import nn

from .config import PolicyConfig
from .observation import OBS_DIM


def build_actor(policy: PolicyConfig) -> nn.Sequential:
    """Deterministic actor mean: (..., 35) -> (..., 6), raw actions before clipping."""
    layers = []
    input_dim = OBS_DIM
    for width in policy.hidden_dims:
        layers.extend((nn.Linear(input_dim, width), nn.ELU()))
        input_dim = width
    layers.append(nn.Linear(input_dim, 6))
    return nn.Sequential(*layers)
