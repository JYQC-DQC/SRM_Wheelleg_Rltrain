from dataclasses import replace
from pathlib import Path

import pytest

from shu_train.wheelleg.config import load_policy, load_robot
from shu_train.wheelleg.observation import build_observation

torch = pytest.importorskip("torch")

from shu_train.wheelleg.actor import DeployedPolicy, actor_input  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("family", ("p1", "p2", "p3"))
def test_deployed_policy_size_and_roundtrip(family):
    policy = load_policy(ROOT / f"config/policies/{family}/policy_meta.yaml")
    assert policy.obs_version == 4 and policy.hidden_dims == (128, 64, 32)
    module = DeployedPolicy(policy).eval()
    assert sum(p.numel() for p in module.parameters()) == 39_721
    obs = torch.randn(8, 27)
    history = torch.cat((torch.randn(8, 104), obs[:, :26]), dim=-1)
    expected = module(obs, history)
    assert expected.shape == (8, 6)
    assert module.encoder(history).shape == (8, 3)
    assert torch.isfinite(expected).all()
    replica = DeployedPolicy(policy).eval()
    replica.load_state_dict(module.state_dict())
    torch.testing.assert_close(replica(obs, history), expected, rtol=0, atol=0)
    assert not torch.equal(expected, module(obs, torch.cat((torch.zeros(8, 104), obs[:, :26]), -1)))


def test_deployable_frame_matches_training_and_request_is_actor_only():
    from shu_train.wheelleg.tensor_ops import observation_tensor

    policy = load_policy(ROOT / "config/policies/p1/policy_meta.yaml")
    robot = replace(load_robot(ROOT / "config/robot.yaml"), q_default_rad=(1.0,) * 6)
    fields = {
        name: torch.randn(2, width)
        for name, width in (
            ("command", 3),
            ("height", 1),
            ("angular_velocity", 3),
            ("gravity", 3),
            ("joint_position", 6),
            ("joint_velocity", 6),
            ("previous_action", 6),
        )
    }
    fields["command"][:, 1] = 0
    fields["joint_position"][:, [2, 5]] = float("nan")  # wheel revolution counters are not inputs
    base = observation_tensor(robot, policy, fields)
    other = build_observation(robot, policy, **{name: value.numpy() for name, value in fields.items()})
    torch.testing.assert_close(torch.from_numpy(other), base)
    torch.testing.assert_close(base[:, 10:14], fields["joint_position"][:, [0, 1, 3, 4]] - 1)
    assert not base[:, 1].any()
    request = torch.tensor([[0.0], [0.25]])
    velocity = torch.randn(2, 3)
    packed = torch.cat((base, request), -1)
    torch.testing.assert_close(actor_input(packed, velocity), torch.cat((base, velocity, request), -1))
