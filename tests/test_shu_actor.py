from pathlib import Path

import pytest

from wheelleg.config import load_policy

torch = pytest.importorskip("torch")

from wheelleg.actor import DeployedPolicy  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("family", ("p1", "p2", "p3"))
def test_deployed_policy_size_and_roundtrip(family):
    policy = load_policy(ROOT / f"config/policies/{family}/policy_meta.yaml")
    assert policy.obs_version == 3 and policy.hidden_dims == (128, 64, 32)
    module = DeployedPolicy(policy).eval()
    assert sum(p.numel() for p in module.parameters()) == 46_505
    obs = torch.randn(8, 35)
    history = torch.cat((torch.randn(8, 140), obs), dim=-1)
    expected = module(obs, history)
    assert expected.shape == (8, 6)
    assert module.encoder(history).shape == (8, 3)
    assert torch.isfinite(expected).all()
    replica = DeployedPolicy(policy).eval()
    replica.load_state_dict(module.state_dict())
    torch.testing.assert_close(replica(obs, history), expected, rtol=0, atol=0)
    assert not torch.equal(expected, module(obs, torch.cat((torch.zeros(8, 140), obs), -1)))
