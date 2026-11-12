"""Bounded first-landing rewards; diagnostics remain an independent observer.

One event per air-reset episode: flight -> cushion -> settled -> resolved. The event resolves exactly once,
as soon as its outcome is known, so success and failure are paid when the deciding motion happens.
The command hold outlives an early success and ends with the diagnostic window (first contact + window_s).

Guide wheels are graded, not binary, at every environment sample with a new guide contact while the event is open:
the impact speed is the touching guide body's own downward speed one physics sample (2 ms) before the contact,
so body pitch counts too. At guide_hard_speed_m_s or faster (little cushioning), or with no sample before the
contact, or with a non-finite guide speed, the event fails; slower contacts cost guide_speed_cost x speed /
threshold each. No per-event history decides a payout, so the critic needs no extra feature. Long guide support
is charged separately by the window contact multiplier.
"""

import torch

FEATURES = 9  # critic-only event state, see features()


class LandingRewards:
    def __init__(self, count: int, wheels: list[int], guides: list[int], body_count: int, settings: dict, device: str):
        self.p = settings
        self.wheels = wheels
        self.nonwheel = torch.ones(body_count, dtype=torch.bool, device=device)
        self.nonwheel[wheels] = False
        self.guide = torch.zeros(body_count, dtype=torch.bool, device=device)
        self.guide[guides] = True
        self.hard = self.nonwheel & ~self.guide
        self.guide_count = len(guides)
        self.active = torch.zeros(count, dtype=torch.bool, device=device)
        self.hold = self.active.clone()
        self.bad = self.active.clone()  # hard non-wheel collision
        self.guide_bad = self.active.clone()  # guide impact with little cushioning
        self.guide_touched = self.active.clone()  # logging only: strict success excludes any guide contact
        # Guide contact and downward speed at the previous physics sample, (N, guides), for rising-edge grading.
        self.guide_previous = torch.zeros(count, len(guides), dtype=torch.bool, device=device)
        self.guide_previous_down = torch.zeros(count, len(guides), device=device)
        self.guide_previous_valid = self.active.clone()  # False until one physics sample after reset
        self.invalid = self.active.clone()
        self.support = self.active.clone()
        self.settled = self.active.clone()
        self.born = torch.zeros(count, dtype=torch.long, device=device)
        self.last_tick = torch.full_like(self.born, -1)
        self.touch = torch.full((count,), -1.0, device=device)
        self.supported = torch.zeros(count, device=device)
        self.held = self.supported.clone()
        self.best = self.supported.clone()
        self.since_touch = self.supported.clone()
        self.age = self.supported.clone()
        self.progress = self.supported.clone()
        self.outcome = self.supported.clone()
        self.guide_cost = self.supported.clone()  # accumulated over the physics samples of one policy step
        self.resolved = self.active.clone()
        self.succeeded = self.active.clone()
        self.stats = {}

    def _add(self, name: str, value: torch.Tensor) -> None:
        self.stats[name] = self.stats[name] + value.detach() if name in self.stats else value.detach().clone()

    def reset(self, ids: torch.Tensor, air: torch.Tensor, tick: int) -> None:
        # Only exogenous air-reset births open an event. Hops and contact chatter cannot reopen it.
        self.active[ids] = air
        self.hold[ids] = air
        self.born[ids] = tick
        self.last_tick[ids] = tick
        self.touch[ids] = -1
        for value in (
            self.bad,
            self.guide_bad,
            self.guide_touched,
            self.guide_previous,
            self.guide_previous_down,
            self.guide_previous_valid,
            self.invalid,
            self.support,
            self.settled,
            self.supported,
            self.held,
            self.best,
            self.since_touch,
            self.age,
            self.progress,
            self.outcome,
            self.guide_cost,
        ):
            value[ids] = 0
        self._add("births", air.sum())

    def begin_step(self) -> None:
        # Support must remain present throughout every physical sample of the policy interval.
        self.support.fill_(True)
        self.guide_cost.zero_()

    def sample(self, tick: int, physics_dt: float, forces: torch.Tensor, guide_down: torch.Tensor) -> None:
        """forces (N, bodies) contact force magnitudes; guide_down (N, guides) downward speed of each guide body."""
        use = self.active & (tick > self.last_tick)
        self.last_tick[use] = tick
        finite = torch.isfinite(forces).all(-1)
        contact = forces > self.p["contact_force_n"]
        first = use & finite & (self.touch < 0) & contact.any(-1)
        self.touch[first] = ((tick - self.born) * physics_dt)[first]
        self.invalid |= use & ~finite
        self.bad |= use & finite & contact[:, self.hard].any(-1)
        if self.guide_count:
            # A non-finite guide speed is no evidence of a cushioned contact: the event becomes invalid instead.
            speed_ok = torch.isfinite(guide_down).all(-1)
            self.invalid |= use & ~speed_ok
            guide = contact[:, self.guide] & (use & finite & speed_ok)[:, None]
            onset = guide & ~self.guide_previous
            # Pre-contact speed: the sample before the contact, not after the impact has already slowed the body.
            speed = torch.where(onset, self.guide_previous_down, 0.0).amax(-1)
            touched = onset.any(-1)
            # No sample before it (contact at the first physics step after reset): unknown speed counts as hard.
            unknown = touched & ~self.guide_previous_valid
            severe = touched & ((speed >= self.p["guide_hard_speed_m_s"]) | unknown)
            self.guide_bad |= severe
            light = touched & ~severe
            cost = self.p["guide_speed_cost"] * speed / self.p["guide_hard_speed_m_s"]
            self.guide_cost -= torch.where(light, cost, 0.0)
            self.guide_touched |= touched
            # Counted per environment sample with a new guide contact, not per guide body: guides that start
            # touching in the same 2 ms sample are graded and charged once, at the fastest of them.
            self._add("guide_contacts", touched.sum())
            self._add("guide_contact_without_prior_sample", unknown.sum())
            self._add("guide_impact_speed_m_s/sum", torch.where(touched & ~unknown, speed, 0.0).sum())
            self._add("guide_impact_speed_m_s/count", (touched & ~unknown).sum())
            down = torch.nan_to_num(guide_down, nan=0.0, posinf=0.0, neginf=0.0).clamp_min(0)
            stored = use & speed_ok
            self.guide_previous = torch.where(stored[:, None], guide, self.guide_previous)
            self.guide_previous_down = torch.where(stored[:, None], down, self.guide_previous_down)
            self.guide_previous_valid |= stored
        both = (forces[:, self.wheels] > self.p["support_force_n"]).all(-1)
        self.support &= ~use | (finite & both & ~contact[:, self.nonwheel].any(-1))

    def flight(self) -> torch.Tensor:
        return self.active & (self.touch < 0)

    def cushion(self) -> torch.Tensor:
        # One-shot transition after the first touch; its deadline runs from first contact, so bounces cannot extend it.
        return self.active & (self.touch >= 0) & ~self.settled

    def update(
        self,
        tick: int,
        physics_dt: float,
        dt: float,
        state: dict,
        terminated: torch.Tensor,
        timeout: torch.Tensor,
        numerical: torch.Tensor,
    ) -> None:
        self.progress.zero_()
        self.outcome.zero_()
        age = (tick - self.born) * physics_dt
        self.age = torch.where(self.hold, age, 0.0)
        collided = self.bad | self.guide_bad
        tilt = torch.stack((state["roll"], state["pitch"]), -1).abs().amax(-1)
        omega = state["angular_velocity"][:, :2].abs().amax(-1)
        vz = state["velocity_w"][:, 2].abs()
        height = state["height_error"].abs()
        values = torch.stack((tilt, omega, vz, height), -1)
        finite = torch.isfinite(values).all(-1)
        self.invalid |= self.active & (~finite | numerical)
        done = terminated | timeout | numerical
        contacted = self.touch >= 0
        self.since_touch = torch.where(self.hold & contacted, age - self.touch, 0.0)
        supported = self.active & contacted & self.support & ~collided & ~self.invalid & ~done
        self.supported = torch.where(supported, self.supported + dt, 0.0)
        # Durations accumulate float32 steps; half a step of tolerance keeps the hold exactly N steps long.
        tolerance = 0.5 * dt
        self.settled |= (
            self.active
            & contacted
            & (
                (self.supported >= self.p["settle_support_s"] - tolerance)
                | (self.since_touch >= self.p["cushion_max_s"])
            )
        )
        scales = values.new_tensor(
            [self.p[k] for k in ("tilt_rad", "angular_xy_rad_s", "vertical_velocity_m_s", "height_error_m")]
        )
        # Squared, normalized, bounded quality; never multiply an unchecked NaN by a mask.
        quality = torch.exp(-0.25 * (torch.nan_to_num(values / scales, nan=1e6).clamp(-1e6, 1e6)).square().sum(-1))
        quality = torch.where(supported, quality, 0.0)
        higher = torch.maximum(self.best, quality)
        self.progress.copy_((higher - self.best) * self.p["progress_budget"])
        self.best.copy_(higher)
        stable = supported & (values <= scales).all(-1)
        self.held = torch.where(stable, self.held + dt, 0.0)
        success = stable & (self.held >= self.p["stable_s"] - tolerance)
        expired = contacted & (self.since_touch >= self.p["window_s"])
        missing = ~contacted & (age >= self.p["contact_timeout_s"])
        failed = self.active & ~success & (done | collided | self.invalid | expired | missing)
        # An early exogenous time limit (randomized initial episode age) is not a landing failure.
        neutral = failed & timeout & ~terminated & ~numerical & ~collided & ~self.invalid
        failed &= ~neutral
        self.outcome[failed] = -self.p["failure_cost"]
        self.outcome[success] = self.p["success_bonus"]
        # Mutually exclusive causes, in priority order.
        causes = {
            "invalid": failed & self.invalid,
            "collision": failed & ~self.invalid & self.bad,
            "guide_impact": failed & ~self.invalid & ~self.bad & self.guide_bad,
            "terminated": failed & ~self.invalid & ~collided & terminated,
            "no_contact": failed & ~self.invalid & ~collided & ~terminated & missing,
        }
        causes["unstable"] = failed & ~torch.stack(list(causes.values())).any(0)
        self._add("success", success.sum())
        # Strict reference: success without any guide contact, comparable with the rule before guide grading.
        self._add("success_no_guide", (success & ~self.guide_touched).sum())
        self._add("neutral_timeout", neutral.sum())
        for name, mask in causes.items():
            self._add(f"failure/{name}", mask.sum())
        self._add("success_time_s/sum", torch.where(success, self.since_touch, 0.0).sum())
        self.active[success | failed | neutral] = False
        # Read by the air-height curriculum: events resolved this step, exogenous timeouts excluded.
        self.resolved = success | failed
        self.succeeded = success
        # Same end as the diagnostic window: a failed event (e.g. a collision) keeps the commands frozen so the
        # diagnostic recovery that follows is not mixed with responses to new commands.
        self.hold &= ~(done | expired | missing)

    def terms(self, state: dict, wheel_radius: float, dt: float) -> dict[str, torch.Tensor]:
        # All flight terms are nonpositive, so they add nothing for staying airborne. The attitude rewards and the
        # relaxed ground terms still apply in flight; watch Landing/first_contact_s for a drift toward later touchdowns.
        flight = self.flight()
        center = torch.exp(-state["wheel_heading_x"].square() / self.p["wheel_center_sigma"]).mean(-1)
        # Approximate no-slip target: the heading-frame body speed, ignoring leg swing, body rotation and wheel heading.
        # The actor sees only the command, which matches it for most births; a command target would teach braking
        # on mismatched ones.
        yaw = state["yaw"]
        forward = state["velocity_w"][:, 0] * yaw.cos() + state["velocity_w"][:, 1] * yaw.sin()
        speed_error = state["wheel_velocity"] * wheel_radius - forward[:, None]
        speed = torch.exp(-speed_error.square().mean(-1) / self.p["wheel_speed_sigma"])
        # Legs extended before touchdown leave cushioning stroke; only a shortfall below the target costs.
        shortfall = (self.p["leg_extension_target_m"] - state["leg_length"]).clamp_min(0).mean(-1)
        extension = (shortfall / self.p["leg_extension_scale_m"]).clamp(max=1.0)
        return {
            "landing_progress": self.progress,
            "landing_outcome": self.outcome,
            "landing_guide_contact": self.guide_cost,
            "landing_wheel_center": torch.where(flight, -self.p["wheel_center_weight"] * dt * (1 - center), 0.0),
            "landing_wheel_speed": torch.where(flight, -self.p["wheel_speed_weight"] * dt * (1 - speed), 0.0),
            "landing_leg_extension": torch.where(flight, -self.p["leg_extension_weight"] * dt * extension, 0.0),
        }

    def features(self) -> torch.Tensor:
        """Event state the critic needs to predict the payouts; (N, FEATURES), each in [0, 1]."""
        active, flight, cushion = self.active.float(), self.flight().float(), self.cushion().float()
        return torch.stack(
            (
                active,
                flight,
                cushion,
                (self.since_touch / self.p["window_s"]).clamp(0, 1),
                (self.held / self.p["stable_s"]).clamp(0, 1) * active,
                self.best * active,
                (self.age / self.p["contact_timeout_s"]).clamp(0, 1) * flight,  # no-contact deadline
                (self.supported / self.p["settle_support_s"]).clamp(0, 1) * cushion,  # cushion exit
                self.hold.float(),  # commands stay frozen
            ),
            -1,
        )

    def take_log(self) -> dict[str, float]:
        values = {key: float(value.item()) for key, value in self.stats.items()}
        self.stats = {}
        result = {f"LandingReward/{k}": v for k, v in values.items() if not k.endswith(("/sum", "/count"))}
        result["LandingReward/pending"] = float(self.active.sum().item())
        failures = sum(v for k, v in values.items() if k.startswith("failure/"))
        resolved = values.get("success", 0.0) + failures
        if resolved:
            # First 0.5 s stable hold reached; says nothing about staying stable afterwards. Exogenous timeouts
            # are excluded from the denominator: they say nothing about the landing.
            result["LandingReward/first_recovery_rate"] = values["success"] / resolved
            result["LandingReward/first_recovery_no_guide_rate"] = values["success_no_guide"] / resolved
        if values.get("success"):
            result["LandingReward/success_time_s/mean"] = values["success_time_s/sum"] / values["success"]
        if values.get("guide_impact_speed_m_s/count"):
            # Downward speed of the touching guide body 2 ms before each new guide contact sample.
            result["LandingReward/guide_impact_speed_m_s/mean"] = (
                values["guide_impact_speed_m_s/sum"] / values["guide_impact_speed_m_s/count"]
            )
        return result
