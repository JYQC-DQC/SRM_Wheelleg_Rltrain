"""Frozen-base specialist training, with a critic for the combined controller."""

import torch

from wheelleg.jump_outcomes import HANDOFF_COST_TIMING, JumpOutcomeTracker, handoff_cost_due
from wheelleg.multi_actor import ActorBank, actor_mask

from .env import WheelLegEnv


class MultiActorEnv(WheelLegEnv):
    handoff_failure_cost_timing = HANDOFF_COST_TIMING
    handoff_reasons = (
        "tilt",
        "vertical_speed",
        "angular_xy",
        "vx_error",
        "yaw_error",
        "contact_loss",
        "termination",
        "timeout",
    )

    def __init__(self, cfg, bundle, **kwargs):
        cfg.state_space += 2  # Critic-only handoff time and accumulated failure; actor stays at 35 inputs.
        super().__init__(cfg, **kwargs)
        if self.training.task != "p3-jump":
            raise ValueError("Specialist training currently supports p3-jump")
        self.actor_bundle = bundle
        # Base is frozen; optional post-handoff acceptance is controlled by duration_s.
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
        self.handoff_cost_pulse = torch.zeros_like(self.handoff_bad)
        self.iteration_handoff_cost_stats = torch.zeros(3, device=self.device)
        self.iteration_handoff_counts = torch.zeros(2, dtype=torch.long, device=self.device)
        self.outcome_tracker = JumpOutcomeTracker(n, self.device)
        self.outcome_checks = torch.ones((n, 3), dtype=torch.bool, device=self.device)
        self.iteration_handoff_stability_failures = torch.zeros((), dtype=torch.long, device=self.device)
        self.handoff_reason_flags = torch.zeros((n, len(self.handoff_reasons)), dtype=torch.bool, device=self.device)
        self.iteration_handoff_reasons = torch.zeros(
            (2, len(self.handoff_reasons)), dtype=torch.long, device=self.device
        )

    def _get_observations(self):
        # Publish accepted requests before the actor is selected, so the first push is owned by Jump.
        if hasattr(self, "actor_bundle"):
            self._advance_jump_request()
        result = super()._get_observations()
        if hasattr(self, "actor_bundle"):
            state = torch.stack(
                (
                    self.handoff_left / max(self.actor_bundle["handoff"]["duration_s"], self.step_dt),
                    self.handoff_bad.float(),
                ),
                dim=-1,
            )
            result["critic"] = torch.cat((result["critic"], state), dim=-1)
        result["actor_train_mask"] = actor_mask(result["policy"]).float().unsqueeze(-1)
        return result

    def _record_jump_curriculum(self, ids, success, iteration):
        if not hasattr(self, "actor_bundle"):
            return super()._record_jump_curriculum(ids, success, iteration)
        # The base calls this before the handoff verdict exists. All final grading is done below.

    def _record_final_outcome(self, ids, event_failed, handoff_failed, iteration):
        ids, success = self.outcome_tracker.record(
            ids,
            self.commands.target[ids, 0] > 0,
            self.outcome_checks[ids],
            event_failed,
            handoff_failed,
        )
        if len(ids) and not self.cfg.evaluation:
            super()._record_jump_curriculum(ids, success, iteration)

    def _get_dones(self):
        watching = self.handoff_left > 0
        was_bad = self.handoff_bad.clone()
        previous_grade = self.handoff_grade.clone()
        terminated, timeout = super()._get_dones()
        self.handoff_pulse.zero_()
        self.handoff_failed.zero_()
        cfg, state = self.actor_bundle["handoff"], self.state
        if cfg["duration_s"] == 0:
            return self._finish_without_handoff_observation(terminated, timeout)
        reasons = torch.stack(
            (
                (state["roll"].abs() >= cfg["tilt_rad"]) | (state["pitch"].abs() >= cfg["tilt_rad"]),
                state["velocity_w"][:, 2].abs() >= cfg["vertical_speed_m_s"],
                state["angular_velocity"][:, :2].abs().amax(-1) >= cfg["angular_xy_rad_s"],
                state["linear_error"].abs() >= cfg["vx_error_m_s"],
                state["angular_error"].abs() >= cfg["yaw_error_rad_s"],
                ~state["wheel_contact"].all(-1),
                terminated,
                timeout,
            ),
            dim=-1,
        )
        self.handoff_reason_flags |= watching[:, None] & reasons
        self.handoff_bad |= watching & reasons.any(-1)
        self.handoff_left = (self.handoff_left - self.step_dt).clamp_min(0)
        finished = watching & ((self.handoff_left <= 0) | terminated | timeout)
        self.handoff_pulse.copy_(finished)
        stability_failed = self.handoff_bad | terminated | timeout
        self.handoff_failed.copy_(finished & (stability_failed | ~self.handoff_grade))
        self.iteration_handoff_counts += torch.stack((finished.sum(), self.handoff_failed.sum()))
        self.iteration_handoff_stability_failures += (finished & stability_failed).sum()
        ids = finished.nonzero().flatten()
        self.iteration_handoff_reasons.index_add_(
            0,
            (self.commands.target[ids, 0] > 0).long(),
            self.handoff_reason_flags[ids].long(),
        )
        if len(ids):
            iteration = (
                self.training_iteration_offset + self.common_step_counter / self.training.settings["rollout_steps"]
            )
            self._record_final_outcome(ids, torch.zeros_like(ids, dtype=torch.bool), stability_failed[ids], iteration)
        started = self.jump.landing_pulse & ~terminated
        heading_ok = self._jump_direction_ok() if self.promotion_checks is not None else torch.ones_like(started)
        checks = torch.stack((self.jump.target_reached, self.jump_vx_qualified, heading_ok), dim=-1)
        grade = checks.all(-1)
        self.handoff_cost_pulse.copy_(
            handoff_cost_due(watching, was_bad, previous_grade, stability_failed, started, grade)
        )
        self.outcome_checks[started] = checks[started]
        self.handoff_grade[started] = grade[started]
        self.handoff_left[started] = cfg["duration_s"]
        self.handoff_bad[started] = False
        self.handoff_reason_flags[started] = False
        self.handoff_left[finished] = 0
        aborted = self.jump.finished & ~started & ~watching & (self.jump.elapsed > 0)
        ids = aborted.nonzero().flatten()
        if len(ids):
            iteration = (
                self.training_iteration_offset + self.common_step_counter / self.training.settings["rollout_steps"]
            )
            self._record_final_outcome(
                ids, torch.ones_like(ids, dtype=torch.bool), torch.zeros_like(ids, dtype=torch.bool), iteration
            )
        terminated |= finished
        timeout &= ~terminated
        return terminated, timeout

    def _finish_without_handoff_observation(self, terminated, timeout):
        # A completed settle is a true terminal, not a timeout bootstrapped into a new episode.
        completed = self.jump.landing_pulse & ~terminated & ~timeout
        heading_ok = self._jump_direction_ok() if self.promotion_checks is not None else torch.ones_like(completed)
        self.outcome_checks[completed] = torch.stack(
            (self.jump.target_reached, self.jump_vx_qualified, heading_ok), dim=-1
        )[completed]
        self.handoff_pulse.copy_(completed)
        self.handoff_failed.copy_(completed & ~self.outcome_checks.all(-1))
        # No post-handoff observation or its failure cost. Original jump rewards remain unchanged.
        self.handoff_cost_pulse.zero_()
        self.iteration_handoff_counts += torch.stack((completed.sum(), self.handoff_failed.sum()))
        aborted = (self.jump.finished & (self.jump.elapsed > 0) | terminated | timeout) & ~completed
        ids = (completed | aborted).nonzero().flatten()
        iteration = self.training_iteration_offset + self.common_step_counter / self.training.settings["rollout_steps"]
        self._record_final_outcome(ids, aborted[ids], torch.zeros_like(aborted[ids]), iteration)
        self.handoff_left.zero_()
        self.handoff_bad.zero_()
        terminated |= completed
        timeout &= ~terminated
        return terminated, timeout

    def _get_rewards(self):
        rewards = super()._get_rewards()
        cost = self.handoff_cost_pulse.float() * self.actor_bundle["handoff"]["failure_cost"]
        rewards += cost
        self.iteration_handoff_cost_stats += torch.stack(
            (
                self.handoff_cost_pulse.sum().float(),
                cost.sum(),
                (self.handoff_left * self.handoff_cost_pulse).sum(),
            )
        )
        self.extras["evaluation"]["handoff_complete"] = self.handoff_pulse.clone()
        self.extras["evaluation"]["handoff_failed"] = self.handoff_failed.clone()
        self.extras["evaluation"]["handoff_cost_paid"] = self.handoff_cost_pulse.clone()
        return rewards

    def _reset_idx(self, ids):
        if hasattr(self, "handoff_left"):
            self.handoff_left[ids] = 0
            self.handoff_bad[ids] = False
            self.handoff_grade[ids] = False
            self.outcome_tracker.reset(ids)
            self.outcome_checks[ids] = True
            self.handoff_reason_flags[ids] = False
        super()._reset_idx(ids)
