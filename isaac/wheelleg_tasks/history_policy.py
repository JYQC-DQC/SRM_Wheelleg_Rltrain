"""rsl_rl 3.1.2 integration of the optional history estimator (wheelleg/history.py).

The rollout storage keeps every observation group returned by the environment, so the history and the
estimator target ride along with PPO's own data. PPO never back-propagates into the estimator: the actor
sees a detached estimate, and the estimator is fitted separately after each PPO update on the same batch.
"""

import torch
from rsl_rl.algorithms import PPO
from rsl_rl.modules import ActorCritic
from rsl_rl.networks import MLP
from tensordict import TensorDict
from torch import nn

from wheelleg.history import ESTIMATE_DIM, HistoryEstimator, estimator_loss


class HistoryActorCritic(ActorCritic):
    def __init__(
        self,
        obs: TensorDict,
        obs_groups: dict[str, list[str]],
        num_actions: int,
        history_frames: int,
        estimator_hidden_dims: list[int],
        **kwargs,
    ) -> None:
        super().__init__(obs, obs_groups, num_actions, **kwargs)
        if self.actor_obs_normalization or self.state_dependent_std:
            raise ValueError("The history policy supports neither actor normalization nor state-dependent std")
        inputs = sum(obs[group].shape[-1] for group in obs_groups["policy"]) + ESTIMATE_DIM
        self.actor = MLP(inputs, num_actions, kwargs["actor_hidden_dims"], kwargs["activation"])
        self.estimator = HistoryEstimator(history_frames, estimator_hidden_dims)

    def get_actor_obs(self, obs: TensorDict) -> torch.Tensor:
        return torch.cat((super().get_actor_obs(obs), self.estimator.features(obs["history"]).detach()), -1)


class HistoryPPO(PPO):
    def __init__(
        self,
        policy: HistoryActorCritic,
        estimator_learning_rate: float,
        velocity_loss_coef: float,
        contact_loss_coef: float,
        **kwargs,
    ) -> None:
        super().__init__(policy, **kwargs)
        if self.is_multi_gpu:
            raise NotImplementedError("The history estimator update is single-GPU only")
        self.estimator_optimizer = torch.optim.Adam(policy.estimator.parameters(), lr=estimator_learning_rate)
        self.velocity_loss_coef = velocity_loss_coef
        self.contact_loss_coef = contact_loss_coef

    def update(self) -> dict[str, float]:
        # PPO.update clears the storage, so keep this rollout's estimator data first.
        observations = self.storage.observations.flatten(0, 1)
        history = observations["history"].clone()
        target = observations["estimator_target"].clone()
        loss_dict = super().update()
        estimator = self.policy.estimator
        count = history.shape[0]
        size = count // self.num_mini_batches
        sums = torch.zeros(2, device=history.device)
        for _ in range(self.num_learning_epochs):
            order = torch.randperm(count, device=history.device)
            for i in range(self.num_mini_batches):
                index = order[i * size : (i + 1) * size]
                loss, velocity, contact = estimator_loss(
                    estimator(history[index]), target[index], self.velocity_loss_coef, self.contact_loss_coef
                )
                self.estimator_optimizer.zero_grad()
                loss.backward()
                nn.utils.clip_grad_norm_(estimator.parameters(), self.max_grad_norm)
                self.estimator_optimizer.step()
                sums += torch.stack((velocity.detach(), contact.detach()))
        sums /= self.num_learning_epochs * self.num_mini_batches
        loss_dict["estimator_velocity"] = sums[0].item()
        loss_dict["estimator_contact"] = sums[1].item()
        return loss_dict
