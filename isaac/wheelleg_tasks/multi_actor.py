"""Frozen-base specialist training, with a critic for the combined controller."""

import torch

from wheelleg.multi_actor import ActorBank, actor_mask

from .env import WheelLegEnv


class MultiActorEnv(WheelLegEnv):
    def __init__(self, cfg, bundle, **kwargs):
        cfg.state_space += 2  # Critic-only handoff time and accumulated failure; actor stays at 35 inputs.
        super().__init__(cfg, **kwargs)
        if self.training.task != "p3-jump":
            raise ValueError("Specialist training currently supports p3-jump")
        self.actor_bundle = bundle
        # Frozen base performance is checked at handoff; no non-jump cohorts are needed for promotion.
        self.ground_promotion = None
        self.actor_bank = ActorBank(bundle, str(self.device), training=True)
        from wheelleg.config import load_policy

        specialist = bundle["actors"][bundle["trainable_actor"]]
        if load_policy(specialist["policy"]) != self.training.policy:
            raise ValueError("Training policy must match the specialist bundle policy")
        n = self.num_envs
        self.handoff_left = torch.zeros(n, device=self.device)
        self.handoff_bad = torch.zeros(n, dtype=torch.bool, device=self.device)
        self.handoff_grade = torch.zeros_like(self.handoff_bad)
        self.handoff_pulse = torch.zeros_like(self.handoff_bad)
        self.handoff_failed = torch.zeros_like(self.handoff_bad)
        self.iteration_handoff_counts = torch.zeros(2, dtype=torch.long, device=self.device)

    def _get_observations(self):
        # Publish accepted requests before the actor is selected, so the first push is owned by Jump.
        if hasattr(self, "actor_bundle"):
            self._advance_jump_request()
        result = super()._get_observations()
        if hasattr(self, "actor_bundle"):
            state = torch.stack(
                (self.handoff_left / self.actor_bundle["handoff"]["duration_s"], self.handoff_bad.float()), dim=-1
            )
            result["critic"] = torch.cat((result["critic"], state), dim=-1)
        result["actor_train_mask"] = actor_mask(result["policy"]).float().unsqueeze(-1)
        return result

    def _record_jump_curriculum(self, ids, success, iteration):
        if not hasattr(self, "actor_bundle"):
            return super()._record_jump_curriculum(ids, success, iteration)
        passed = ids[success]
        self.handoff_grade[passed] = True
        failed = ids[~success]
        if len(failed):
            super()._record_jump_curriculum(failed, torch.zeros_like(failed, dtype=torch.bool), iteration)

    def _get_dones(self):
        watching = self.handoff_left > 0
        terminated, timeout = super()._get_dones()
        self.handoff_pulse.zero_()
        self.handoff_failed.zero_()
        cfg, state = self.actor_bundle["handoff"], self.state
        bad = (state["roll"].abs() >= cfg["tilt_rad"]) | (state["pitch"].abs() >= cfg["tilt_rad"])
        bad |= state["velocity_w"][:, 2].abs() >= cfg["vertical_speed_m_s"]
        bad |= state["angular_velocity"][:, :2].abs().amax(-1) >= cfg["angular_xy_rad_s"]
        bad |= state["linear_error"].abs() >= cfg["vx_error_m_s"]
        bad |= state["angular_error"].abs() >= cfg["yaw_error_rad_s"]
        bad |= ~state["wheel_contact"].all(-1)
        self.handoff_bad |= watching & bad
        self.handoff_left = (self.handoff_left - self.step_dt).clamp_min(0)
        finished = watching & ((self.handoff_left <= 0) | terminated | timeout)
        self.handoff_pulse.copy_(finished)
        self.handoff_failed.copy_(finished & (self.handoff_bad | ~self.handoff_grade | terminated | timeout))
        self.iteration_handoff_counts += torch.stack((finished.sum(), self.handoff_failed.sum()))
        ids = finished.nonzero().flatten()
        if len(ids) and not self.cfg.evaluation:
            iteration = (
                self.training_iteration_offset + self.common_step_counter / self.training.settings["rollout_steps"]
            )
            super()._record_jump_curriculum(ids, self.handoff_grade[ids] & ~self.handoff_failed[ids], iteration)
        started = self.jump.landing_pulse & ~terminated
        grade = self.jump.target_reached & self.jump_vx_qualified
        if self.promotion_checks is not None:
            grade &= self._jump_direction_ok()
        self.handoff_grade[started] = grade[started]
        self.handoff_left[started] = cfg["duration_s"]
        self.handoff_bad[started] = False
        self.handoff_left[finished] = 0
        terminated |= finished
        timeout &= ~terminated
        return terminated, timeout

    def _get_rewards(self):
        rewards = super()._get_rewards()
        cost = self.handoff_failed.float() * self.actor_bundle["handoff"]["failure_cost"]
        rewards += cost
        self.extras["evaluation"]["handoff_complete"] = self.handoff_pulse.clone()
        self.extras["evaluation"]["handoff_failed"] = self.handoff_failed.clone()
        return rewards

    def _reset_idx(self, ids):
        if hasattr(self, "handoff_left"):
            self.handoff_left[ids] = 0
            self.handoff_bad[ids] = False
            self.handoff_grade[ids] = False
        super()._reset_idx(ids)
