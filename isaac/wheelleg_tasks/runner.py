import torch
from rsl_rl.runners import OnPolicyRunner

from wheelleg.landing_rewards import FEATURES as LANDING_FEATURES
from wheelleg.stairs import FEATURES as STAIR_FEATURES
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
        if cfg.task == "p1-landing":  # critic gains the landing event state
            contract["landing_event_features"] = LANDING_FEATURES
        if cfg.task == "p1-stairs":
            contract["stair_course_revision"] = 4
            contract["stair_course_features"] = STAIR_FEATURES
            contract["stair_scan"] = [
                cfg.stage["course"][k] for k in ("scan_half_length_m", "scan_half_width_m", "scan_resolution_m")
            ]
            contract["stair_terrain"] = mutable(cfg.stage["terrain"])
            contract["stair_course"] = mutable(cfg.stage["course"])
            contract["stair_passive_joint_limits_rad"] = mutable(cfg.shared["stairs_passive_joint_limits_rad"])
            contract["stair_assist"] = [
                cfg.shared["spring_extension_height_m"],
                cfg.stage["step_height_margin_m"],
                cfg.stage["step_height_hold_s"],
                mutable(cfg.stage["step_height_clearance_range_m"]),
            ]
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
        if env.stair_course is None:
            self.writer.add_scalar("Curriculum/command_fraction", env.commands.command_fraction, iteration)
        if env.stair_course is not None:
            for k, name in enumerate(env.stair_course.names):
                if env.training.stage["terrain"]["profiles"][name]["command_mode"] != "motion":
                    selected = env.stair_course.group == k
                    if not selected.any():
                        continue
                    self.writer.add_scalar(
                        f"Stairs/{name}/speed_fraction",
                        env.stair_course.episode_speed_fraction[selected].mean().item(),
                        iteration,
                    )
                    for row in range(env.training.stage["terrain"]["rows"]):
                        self.writer.add_scalar(
                            f"Stairs/{name}/row{row}/speed_fraction",
                            env.stair_course.speed_fraction[k, row].item(),
                            iteration,
                        )
                        self.writer.add_scalar(
                            f"Stairs/{name}/row{row}/pass_rate",
                            env.stair_course.latest_pass[k, row].item(),
                            iteration,
                        )
        if env.command_curriculum is not None and env.command_curriculum.last_landing_rate is not None:
            rate = env.command_curriculum.last_landing_rate
            self.writer.add_scalar("Curriculum/command_landing_gate_rate", rate, iteration)
        if env.air_height_curriculum is not None:
            curriculum = env.air_height_curriculum
            self.writer.add_scalar("Curriculum/air_height_max_m", curriculum.upper, iteration)
            if curriculum.last_rate is not None:
                self.writer.add_scalar("Curriculum/air_height_band_success_rate", curriculum.last_rate, iteration)
        if env.first_landing is not None:
            self.writer.add_scalar("Landing/height_wide_weight", env.reward_weights["track_height_wide"], iteration)
            for name, value in env.first_landing.take_log().items():
                self.writer.add_scalar(name, value, iteration)
        if env.landing_reward is not None:
            for name, value in env.landing_reward.take_log().items():
                self.writer.add_scalar(name, value, iteration)
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
        if env.air_height_curriculum is not None:
            extra["air_height_curriculum"] = env.air_height_curriculum.state_dict()
        if env.stair_course is not None:
            extra["stair_course"] = {
                k: getattr(env.stair_course, k).cpu() for k in ("speed_fraction", "completed", "passed", "latest_pass")
            }
            extra["stair_terrain_levels"] = env.stair_course.training_level.cpu()
        if hasattr(self.alg, "estimator_optimizer"):
            extra["estimator_optimizer"] = self.alg.estimator_optimizer.state_dict()
        super().save(path, extra)

    def load(
        self, path: str, load_optimizer: bool = True, map_location=None, restart_command_curriculum: bool = False
    ) -> dict:
        """restart_command_curriculum: the caller restarts the command curriculum, so its saved state is not needed,
        and a landing air-height curriculum missing from an older checkpoint starts at its first level."""
        checkpoint = torch.load(path, map_location="cpu", weights_only=True)
        infos = checkpoint["infos"]
        if not infos or infos.get("observation_contract") != self.observation_contract():
            raise ValueError(
                "Critic observation contract changed: use --initialize-from for actor only; --resume is forbidden"
            )
        env = self.env.unwrapped
        if not restart_command_curriculum:
            if env.air_height_curriculum is not None and "air_height_curriculum" not in infos:
                raise ValueError("Checkpoint has no landing air-height curriculum state: use --initialize-from")
            gate = env.command_curriculum
            if (
                gate is not None
                and gate.landing_gate is not None
                and "landing_events" not in infos["command_curriculum"]
            ):
                raise ValueError("Checkpoint has no landing-gated command curriculum state: use --initialize-from")
        if env.stair_course is not None:
            if restart_command_curriculum:
                raise ValueError("Stairs uses per-terrain speed windows; --command-fraction is not applicable")
            if infos["stair_terrain_levels"].shape != env.terrain.terrain_levels.shape:
                raise ValueError("Stairs resume requires the same number of environments")
        infos = super().load(path, load_optimizer=load_optimizer, map_location=map_location)
        if not restart_command_curriculum:
            env.commands.command_fraction = infos["command_fraction"]
            if env.command_curriculum is not None:
                env.command_curriculum.load_state_dict(infos["command_curriculum"])
        if env.jump_curriculum is not None:
            env.jump_curriculum.load_state_dict(infos["jump_curriculum"])
        if env.air_height_curriculum is not None and "air_height_curriculum" in infos:
            if not env.air_height_curriculum.load_state_dict(infos["air_height_curriculum"]):
                # Saved gate counts belong to an older band definition (or counted every height).
                env.command_curriculum.discard_landing()
        if load_optimizer and hasattr(self.alg, "estimator_optimizer"):
            self.alg.estimator_optimizer.load_state_dict(infos["estimator_optimizer"])
        if env.stair_course is not None:
            for k in ("speed_fraction", "completed", "passed", "latest_pass"):
                getattr(env.stair_course, k).copy_(infos["stair_course"][k].to(env.device))
            saved = infos["stair_terrain_levels"].to(env.device)
            env.stair_course.training_level.copy_(saved)
            env.terrain.terrain_levels.copy_(saved)
            env.terrain.env_origins.copy_(env.terrain.terrain_origins[saved, env.terrain.terrain_types])
            # Reset restores physics at the new origins; it must not grade the discarded pre-load episode.
            env.stair_course.age.zero_()
            env.stair_course.success.zero_()
            env.stair_course.traversed.zero_()
            env.reset()
        return infos
