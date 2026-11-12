import torch
from rsl_rl.runners import OnPolicyRunner

from wheelleg.training import mutable


class WheelLegRunner(OnPolicyRunner):
    """Persist task curriculum state alongside upstream PPO state."""

    def observation_contract(self) -> dict:
        cfg = self.env.unwrapped.training
        contract = {
            "revision": 1,
            "clip": mutable(cfg.shared["observation_clip"]),
            "critic_torque_scale": cfg.shared["critic_torque_scale"],
        }
        if cfg.policy.history_frames:  # absent when disabled, so existing checkpoints keep resuming
            contract["history_frames"] = cfg.policy.history_frames
        return contract

    def _construct_algorithm(self, obs):
        if self.policy_cfg["class_name"] != "HistoryActorCritic":
            return super()._construct_algorithm(obs)
        # Upstream resolves class names with eval() inside rsl_rl; build the history classes here instead.
        from isaac.wheelleg_tasks.history_policy import HistoryActorCritic, HistoryPPO

        policy_cfg = {key: value for key, value in self.policy_cfg.items() if key != "class_name"}
        alg_cfg = {key: value for key, value in self.alg_cfg.items() if key != "class_name"}
        policy = HistoryActorCritic(obs, self.cfg["obs_groups"], self.env.num_actions, **policy_cfg).to(self.device)
        alg = HistoryPPO(policy, device=self.device, **alg_cfg, multi_gpu_cfg=self.multi_gpu_cfg)
        alg.init_storage("rl", self.env.num_envs, self.num_steps_per_env, obs, [self.env.num_actions])
        return alg

    def log(self, locs: dict, width: int = 80, pad: int = 35) -> None:
        super().log(locs, width, pad)
        env = self.env.unwrapped
        iteration = locs["it"]
        self.writer.add_scalar("Safety/raw_action_abs_max", env.iteration_raw_action_max.item(), iteration)
        self.writer.add_scalar("Safety/numerical_terminations", env.iteration_numerical_terminations.item(), iteration)
        # 指令范围课程进度（0-1）；不写出来就看不出课程是否卡住。
        self.writer.add_scalar("Curriculum/command_fraction", env.commands.command_fraction, iteration)
        # The rollout runs under torch.inference_mode(); its tensors cannot be zeroed in place here.
        env.iteration_raw_action_max = torch.zeros((), device=env.device)
        env.iteration_numerical_terminations = torch.zeros((), dtype=torch.long, device=env.device)

    def save(self, path: str, infos: dict | None = None) -> None:
        extra = {} if infos is None else dict(infos)
        env = self.env.unwrapped
        extra["observation_contract"] = self.observation_contract()
        extra["command_fraction"] = env.commands.command_fraction
        if env.command_curriculum is not None:
            extra["command_curriculum"] = env.command_curriculum.state_dict()
        if env.jump_curriculum is not None:
            extra["jump_curriculum"] = env.jump_curriculum.state_dict()
        if hasattr(self.alg, "estimator_optimizer"):
            extra["estimator_optimizer"] = self.alg.estimator_optimizer.state_dict()
        super().save(path, extra)

    def load(self, path: str, load_optimizer: bool = True, map_location=None) -> dict:
        checkpoint = torch.load(path, map_location="cpu", weights_only=True)
        infos = checkpoint["infos"]
        if not infos or infos.get("observation_contract") != self.observation_contract():
            raise ValueError(
                "Critic observation contract changed: use --initialize-from for actor only; --resume is forbidden"
            )
        infos = super().load(path, load_optimizer=load_optimizer, map_location=map_location)
        env = self.env.unwrapped
        env.commands.command_fraction = infos["command_fraction"]
        if env.command_curriculum is not None:
            env.command_curriculum.load_state_dict(infos["command_curriculum"])
        if env.jump_curriculum is not None:
            env.jump_curriculum.load_state_dict(infos["jump_curriculum"])
        if load_optimizer and hasattr(self.alg, "estimator_optimizer"):
            self.alg.estimator_optimizer.load_state_dict(infos["estimator_optimizer"])
        return infos
