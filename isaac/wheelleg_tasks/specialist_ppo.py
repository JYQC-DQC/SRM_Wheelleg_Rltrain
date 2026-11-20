"""PPO for one trainable actor within a fixed multi-actor controller."""

import torch
from rsl_rl.algorithms import PPO

from wheelleg.multi_actor import masked_mean


class SpecialistPPO(PPO):
    """Actor gradients only from specialist actions; critic models both frozen and learned phases."""

    def __init__(self, policy, bank, **kwargs):
        super().__init__(policy, **kwargs)
        if self.rnd or self.symmetry or self.is_multi_gpu or policy.is_recurrent:
            raise ValueError("Specialist PPO requires feedforward, single-GPU PPO without RND/symmetry")
        self.bank = bank
        self.specialist_actions = torch.zeros((), device=self.device)
        self.total_actions = 0

    def act(self, obs):
        actions = super().act(obs)
        frozen = ~obs["actor_train_mask"].squeeze(-1).bool()
        self.specialist_actions += (~frozen).sum()
        self.total_actions += frozen.numel()
        if frozen.any():
            ids = torch.full((int(frozen.sum()),), self.bank.default, device=actions.device, dtype=torch.long)
            actions[frozen] = self.bank(obs["policy"][frozen], ids)
        return actions

    def compute_returns(self, obs):
        values = self.policy.evaluate(obs).detach()
        # Keep frozen transitions in the value trace so handoff outcomes reach preceding Jump actions.
        self.storage.compute_returns(values, self.gamma, self.lam, normalize_advantage=False)
        mask = self.storage.observations["actor_train_mask"].bool()
        selected = self.storage.advantages[mask]
        if selected.numel():
            normalized = (self.storage.advantages - selected.mean()) / (selected.std(unbiased=False) + 1e-8)
            self.storage.advantages.copy_(torch.where(mask, normalized, 0))

    def update(self):
        sums = dict(value_function=0.0, surrogate=0.0, entropy=0.0)
        updates = 0
        for (
            obs,
            actions,
            old_values,
            advantages,
            returns,
            old_logp,
            old_mu,
            old_std,
            _,
            _,
        ) in self.storage.mini_batch_generator(self.num_mini_batches, self.num_learning_epochs):
            mask = obs["actor_train_mask"].squeeze(-1)
            self.policy.act(obs)
            logp = self.policy.get_actions_log_prob(actions)
            values = self.policy.evaluate(obs)
            entropy = masked_mean(self.policy.entropy, mask)
            if mask.any() and self.schedule == "adaptive" and self.desired_kl is not None:
                with torch.no_grad():
                    std = self.policy.action_std
                    kl = (
                        torch.log(std / old_std + 1e-5)
                        + (old_std.square() + (old_mu - self.policy.action_mean).square()) / (2 * std.square())
                        - 0.5
                    ).sum(-1)
                    divergence = masked_mean(kl, mask).item()
                    if divergence > 2 * self.desired_kl:
                        self.learning_rate = max(1e-5, self.learning_rate / 1.5)
                    elif 0 < divergence < self.desired_kl / 2:
                        self.learning_rate = min(1e-2, self.learning_rate * 1.5)
                    for group in self.optimizer.param_groups:
                        group["lr"] = self.learning_rate
            log_ratio = torch.where(mask.bool(), logp - old_logp.squeeze(-1), 0)
            ratio = log_ratio.exp()
            advantage = advantages.squeeze(-1)
            surrogate = masked_mean(
                torch.maximum(-advantage * ratio, -advantage * ratio.clamp(1 - self.clip_param, 1 + self.clip_param)),
                mask,
            )
            error = (values - returns).square()
            if self.use_clipped_value_loss:
                clipped = old_values + (values - old_values).clamp(-self.clip_param, self.clip_param)
                error = torch.maximum(error, (clipped - returns).square())
            value_loss = error.mean()
            loss = surrogate + self.value_loss_coef * value_loss - self.entropy_coef * entropy
            self.optimizer.zero_grad()
            loss.backward()
            # Empty specialist batches must not move actor/std through Adam's momentum.
            if not mask.any():
                for parameter in self.policy.actor.parameters():
                    parameter.grad = None
                self.policy.std.grad = None
            torch.nn.utils.clip_grad_norm_(self.policy.parameters(), self.max_grad_norm)
            self.optimizer.step()
            for key, value in (("value_function", value_loss), ("surrogate", surrogate), ("entropy", entropy)):
                sums[key] += value.item()
            updates += 1
        self.storage.clear()
        return {key: value / max(updates, 1) for key, value in sums.items()}
