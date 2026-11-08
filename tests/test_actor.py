from pathlib import Path

import pytest

torch = pytest.importorskip("torch")

from wheelleg.actor import build_actor  # noqa: E402
from wheelleg.config import load_policy  # noqa: E402


def test_actor_shape_size_and_roundtrip():
    path = Path(__file__).resolve().parents[1] / "config/policies/p1/policy_meta.yaml"
    policy = load_policy(path)
    torch.manual_seed(7)
    actor = build_actor(policy).eval()
    assert sum(p.numel() for p in actor.parameters()) == 50758
    inputs = torch.randn(32, 35)
    output = actor(inputs)
    assert output.shape == (32, 6)
    assert torch.isfinite(output).all()
    copy = build_actor(policy).eval()
    copy.load_state_dict(actor.state_dict())
    torch.testing.assert_close(copy(inputs), output, rtol=0.0, atol=0.0)
    output.square().mean().backward()
    assert all(p.grad is not None and torch.isfinite(p.grad).all() for p in actor.parameters())
