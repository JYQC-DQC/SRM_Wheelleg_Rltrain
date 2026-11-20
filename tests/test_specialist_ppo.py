"""Run on the pinned rsl_rl image; no Isaac simulator is needed."""

import pytest
import torch
from torch import nn

pytest.importorskip("rsl_rl")
pytest.importorskip("tensordict")
from rsl_rl.modules import ActorCritic
from tensordict import TensorDict

from isaac.wheelleg_tasks.specialist_ppo import SpecialistPPO


class FrozenBase(nn.Module):
    default = 0

    def forward(self, observation, actor_ids):
        return observation.new_full((len(actor_ids), 6), 0.125)


def run_update(mask):
    obs = TensorDict(
        {
            "policy": torch.randn(4, 35),
            "critic": torch.randn(4, 12),
            "actor_train_mask": torch.full((4, 1), float(mask)),
        },
        batch_size=[4],
    )
    policy = ActorCritic(
        obs, {"policy": ["policy"], "critic": ["critic"]}, 6, actor_hidden_dims=[16], critic_hidden_dims=[16]
    )
    alg = SpecialistPPO(policy, FrozenBase(), num_learning_epochs=2, num_mini_batches=2, schedule="fixed")
    alg.init_storage("rl", 4, 4, obs, [6])
    initial = {name: value.clone() for name, value in policy.actor.state_dict().items()}
    std = policy.std.clone()
    with torch.inference_mode():
        for _ in range(4):
            actions = alg.act(obs)
            if not mask:
                torch.testing.assert_close(actions, torch.full_like(actions, 0.125))
            alg.process_env_step(obs, torch.randn(4), torch.zeros(4, dtype=torch.bool), {})
        alg.compute_returns(obs)
    metrics = alg.update()
    assert all(torch.isfinite(torch.tensor(value)) for value in metrics.values())
    return alg, policy, initial, std


def test_frozen_only_batches_cannot_update_jump_actor_or_noise():
    _, policy, initial, std = run_update(False)
    assert all(torch.equal(value, initial[name]) for name, value in policy.actor.state_dict().items())
    torch.testing.assert_close(policy.std, std, rtol=0, atol=0)


def test_jump_batches_update_the_specialist():
    _, policy, initial, _ = run_update(True)
    assert any(not torch.equal(value, initial[name]) for name, value in policy.actor.state_dict().items())


def test_frozen_batches_preserve_actor_after_adam_has_momentum():
    alg, policy, _, _ = run_update(True)
    initial = {name: value.clone() for name, value in policy.actor.state_dict().items()}
    std = policy.std.clone()
    obs = TensorDict(
        {"policy": torch.randn(4, 35), "critic": torch.randn(4, 12), "actor_train_mask": torch.zeros(4, 1)},
        batch_size=[4],
    )
    with torch.inference_mode():
        for _ in range(4):
            alg.act(obs)
            alg.process_env_step(obs, torch.randn(4), torch.zeros(4, dtype=torch.bool), {})
        alg.compute_returns(obs)
    alg.update()
    assert all(torch.equal(value, initial[name]) for name, value in policy.actor.state_dict().items())
    torch.testing.assert_close(policy.std, std, rtol=0, atol=0)


def test_landing_handoff_cost_reaches_prior_jump_transition():
    alg, policy, _, _ = run_update(True)
    with torch.no_grad():
        for parameter in policy.critic.parameters():
            parameter.zero_()
    obs = TensorDict(
        {"policy": torch.randn(4, 35), "critic": torch.randn(4, 12), "actor_train_mask": torch.ones(4, 1)},
        batch_size=[4],
    )
    with torch.inference_mode():
        for tick in range(4):
            obs["actor_train_mask"].fill_(float(tick == 0))
            alg.act(obs.clone())
            alg.process_env_step(obs, torch.full((4,), -4.0 if tick == 3 else 0.0), torch.full((4,), tick == 3), {})
        alg.compute_returns(obs)
    assert bool((alg.storage.returns[0] < 0).all())
