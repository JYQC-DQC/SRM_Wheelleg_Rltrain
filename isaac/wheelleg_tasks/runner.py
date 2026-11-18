import torch
import torch.nn.functional as F
from rsl_rl.algorithms import PPO
from rsl_rl.modules import ActorCritic
from rsl_rl.runners import OnPolicyRunner
from tensordict import TensorDict
from torch import nn

from wheelleg.actor import actor_input, build_actor, build_encoder, policy_contract
from wheelleg.config import PolicyConfig
from wheelleg.history import HISTORY_DIM, VELOCITY_DIM
from wheelleg.observation import POLICY_OBS_DIM
from wheelleg.training import mutable


class VelocityActorCritic(ActorCritic):
    def __init__(self, obs, obs_groups, num_actions, *, policy: PolicyConfig, **kwargs):
        super().__init__(obs, obs_groups, num_actions, **kwargs)
        self.actor = build_actor(policy)
        self.encoder = build_encoder()

    def get_actor_obs(self, obs: TensorDict) -> torch.Tensor:
        with torch.no_grad():
            velocity = self.encoder(obs["history"])
        return actor_input(obs["policy"], velocity)


class VelocityPPO(PPO):
    min_lr = 1e-5
    max_lr = 1e-3
    lr_factor = 1.2

    def __init__(self, policy: VelocityActorCritic, **kwargs) -> None:
        super().__init__(policy, **kwargs)
        encoder_parameters = set(policy.encoder.parameters())
        group = self.optimizer.param_groups[0]
        group["params"] = [p for p in group["params"] if p not in encoder_parameters]
        # Fudan plane: separate Adam at 1e-3 (not affected by PPO's adaptive KL schedule).
        self.encoder_optimizer = torch.optim.Adam(policy.encoder.parameters(), lr=1e-3)

    def set_ppo_lr(self, lr: float) -> None:
        self.learning_rate = min(self.max_lr, max(self.min_lr, lr)) if self.schedule == "adaptive" else lr
        for group in self.optimizer.param_groups:
            group["lr"] = self.learning_rate

    def adapt_lr(self, kl: float) -> None:
        if kl > 2 * self.desired_kl:
            self.set_ppo_lr(self.learning_rate / self.lr_factor)
        elif 0 < kl < self.desired_kl / 2:
            self.set_ppo_lr(self.learning_rate * self.lr_factor)

    def _update_ppo(self) -> dict[str, float]:
        # rsl_rl 3.1.2 has no scheduler callback; keep its feed-forward PPO equations here.
        if self.rnd or self.symmetry or self.is_multi_gpu or self.policy.is_recurrent:
            raise ValueError("SHU PPO supports single-device feed-forward updates without RND or symmetry")
        totals = dict(value_function=0.0, surrogate=0.0, entropy=0.0)
        batches = self.storage.mini_batch_generator(self.num_mini_batches, self.num_learning_epochs)
        for obs, actions, old_value, advantage, returns, old_logp, old_mu, old_std, _, _ in batches:
            if self.normalize_advantage_per_mini_batch:
                advantage = (advantage - advantage.mean()) / (advantage.std() + 1e-8)
            self.policy.act(obs)
            logp = self.policy.get_actions_log_prob(actions)
            value = self.policy.evaluate(obs)
            entropy = self.policy.entropy.mean()
            if self.schedule == "adaptive" and self.desired_kl is not None:
                with torch.no_grad():
                    mu, std = self.policy.action_mean, self.policy.action_std
                    kl = (
                        (std / old_std + 1e-5).log()
                        + (old_std.square() + (old_mu - mu).square()) / (2 * std.square())
                        - 0.5
                    )
                    self.adapt_lr(kl.sum(-1).mean().item())
            ratio = (logp - old_logp.squeeze(-1)).exp()
            clipped = ratio.clamp(1 - self.clip_param, 1 + self.clip_param)
            adv = advantage.squeeze(-1)
            surrogate = torch.maximum(-adv * ratio, -adv * clipped).mean()
            value_error = (value - returns).square()
            if self.use_clipped_value_loss:
                value_clipped = old_value + (value - old_value).clamp(-self.clip_param, self.clip_param)
                value_error = torch.maximum(value_error, (value_clipped - returns).square())
            value_loss = value_error.mean()
            loss = surrogate + self.value_loss_coef * value_loss - self.entropy_coef * entropy
            self.optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(self.policy.parameters(), self.max_grad_norm)
            self.optimizer.step()
            for key, metric in zip(totals, (value_loss, surrogate, entropy), strict=True):
                totals[key] += metric.item()
        self.storage.clear()
        return {key: value / (self.num_learning_epochs * self.num_mini_batches) for key, value in totals.items()}

    def act(self, obs: TensorDict) -> torch.Tensor:
        # rsl_rl 3.1.2 writes transition.observations only after env.step(). Snapshot before
        # advancing the env, since history and simulator truth can be views of mutable buffers.
        return super().act(obs.clone())

    def update(self) -> dict[str, float]:
        storage = self.storage
        history = storage.observations["history"].flatten(0, 1)
        target = storage.observations["estimator_target"].flatten(0, 1)
        # PPO uses the behavior encoder throughout its epochs. In 3.1.2 update() only
        # rewinds storage.step; it does not overwrite observations before this update finishes.
        losses = self._update_ppo()
        valid = torch.isfinite(target).all(dim=-1).nonzero().flatten()
        count = len(valid)
        encoder = self.policy.encoder
        squared_error = target.new_zeros(())
        if count:
            for _ in range(self.num_learning_epochs):
                order = valid[torch.randperm(count, device=target.device)]
                for indices in order.tensor_split(min(count, self.num_mini_batches)):
                    loss = F.mse_loss(encoder(history[indices]), target[indices])
                    self.encoder_optimizer.zero_grad(set_to_none=True)
                    loss.backward()
                    nn.utils.clip_grad_norm_(encoder.parameters(), 0.1)
                    self.encoder_optimizer.step()
                    squared_error += loss.detach() * len(indices)
            self.encoder_optimizer.zero_grad(set_to_none=True)
        losses["encoder_velocity_mse"] = squared_error.item() / max(1, count * self.num_learning_epochs)
        return losses


class WheelLegRunner(OnPolicyRunner):
    """Persist task curriculum and velocity encoder state alongside PPO state."""

    def _construct_algorithm(self, obs: TensorDict) -> PPO:
        if self.is_distributed:
            raise ValueError("Velocity encoder training requires one device")
        if self.cfg["obs_groups"] != {"policy": ["policy"], "critic": ["critic"]}:
            raise ValueError("Velocity policy requires separate policy and critic observation groups")
        for key, width in (("policy", POLICY_OBS_DIM), ("history", HISTORY_DIM), ("estimator_target", VELOCITY_DIM)):
            if key not in obs or obs[key].shape != (self.env.num_envs, width):
                raise ValueError(f"env observation '{key}' must have shape (num_envs, {width})")
        self.critic_dim = obs["critic"].shape[-1]
        policy_cfg = {k: v for k, v in self.policy_cfg.items() if k != "class_name"}
        if policy_cfg["actor_obs_normalization"] or policy_cfg.get("state_dependent_std"):
            raise ValueError("The exported velocity policy requires unnormalized inputs and state-independent std")
        net = VelocityActorCritic(
            obs, self.cfg["obs_groups"], self.env.num_actions, policy=self.env.unwrapped.training.policy, **policy_cfg
        ).to(self.device)
        alg_cfg = {k: v for k, v in self.alg_cfg.items() if k != "class_name"}
        alg = VelocityPPO(net, device=self.device, **alg_cfg)
        alg.init_storage("rl", self.env.num_envs, self.num_steps_per_env, obs, [self.env.num_actions])
        return alg

    def observation_contract(self) -> dict:
        cfg = self.env.unwrapped.training
        return {
            "revision": 2,
            "task": cfg.task,
            "policy": policy_contract(cfg.policy),
            "critic_dim": self.critic_dim,
            "clip": mutable(cfg.shared["observation_clip"]),
            "critic_torque_scale": cfg.shared["critic_torque_scale"],
        }

    def log(self, locs: dict, width: int = 80, pad: int = 35) -> None:
        super().log(locs, width, pad)
        env = self.env.unwrapped
        iteration = locs["it"]
        if env.shu is not None:
            for key, scalar in env.shu.log.take().items():
                self.writer.add_scalar(key, scalar, iteration)
            if env.shu.drop is not None:
                self.writer.add_scalar("Curriculum/drop_band", env.shu.drop.level + 1, iteration)
                self.writer.add_scalar("Curriculum/latest_band_sample_count", env.shu.drop.events, iteration)
            if env.shu.flat is not None:
                for kind, fraction in enumerate(env.shu.flat.fraction.tolist()):
                    self.writer.add_scalar(f"Curriculum/flat_bucket_{kind}", fraction, iteration)
        self.writer.add_scalar("Safety/raw_action_abs_max", env.iteration_raw_action_max.item(), iteration)
        self.writer.add_scalar("Safety/numerical_terminations", env.iteration_numerical_terminations.item(), iteration)
        # The rollout runs under torch.inference_mode(); its tensors cannot be zeroed in place here.
        env.iteration_raw_action_max = torch.zeros((), device=env.device)
        env.iteration_numerical_terminations = torch.zeros((), dtype=torch.long, device=env.device)

    def save(self, path: str, infos: dict | None = None) -> None:
        extra = {} if infos is None else dict(infos)
        env = self.env.unwrapped
        extra["observation_contract"] = self.observation_contract()
        extra["encoder_optimizer_state_dict"] = self.alg.encoder_optimizer.state_dict()
        if env.shu is not None:
            extra["shu_curriculum"] = env.shu.curriculum_state_dict()
        else:
            extra["command_fraction"] = env.commands.command_fraction
            if env.command_curriculum is not None:
                extra["command_curriculum"] = env.command_curriculum.state_dict()
        if env.jump_curriculum is not None:
            extra["jump_curriculum"] = env.jump_curriculum.state_dict()
        if env.mixed_curriculum is not None:
            extra["mixed_curriculum"] = env.mixed_curriculum.state_dict()
        super().save(path, extra)

    def load(self, path: str, load_optimizer: bool = True, map_location=None) -> dict:
        checkpoint = torch.load(path, map_location=map_location or "cpu", weights_only=True)
        infos = checkpoint["infos"]
        if not infos or infos.get("observation_contract") != self.observation_contract():
            raise ValueError("--resume requires the same task and Actor/encoder/critic observation contract")
        self.alg.policy.load_state_dict(checkpoint["model_state_dict"])
        if load_optimizer:
            self.alg.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
            self.alg.encoder_optimizer.load_state_dict(infos["encoder_optimizer_state_dict"])
            self.alg.set_ppo_lr(self.alg.optimizer.param_groups[0]["lr"])
        self.current_learning_iteration = checkpoint["iter"]
        env = self.env.unwrapped
        if env.shu is not None:
            env.shu.load_curriculum_state_dict(infos["shu_curriculum"])
        else:
            env.commands.command_fraction = infos["command_fraction"]
            if env.command_curriculum is not None:
                env.command_curriculum.load_state_dict(infos["command_curriculum"])
        if env.jump_curriculum is not None:
            env.jump_curriculum.load_state_dict(infos["jump_curriculum"])
        if env.mixed_curriculum is not None:
            env.mixed_curriculum.load_state_dict(infos["mixed_curriculum"])
        return infos
