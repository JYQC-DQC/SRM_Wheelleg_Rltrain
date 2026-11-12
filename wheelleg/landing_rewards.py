"""Bounded first-landing rewards; diagnostics remain an independent observer.

One event per air-reset episode: flight -> cushion -> settled -> resolved. The event resolves exactly once,
as soon as its outcome is known, so success and failure are paid when the deciding motion happens.
The command hold outlives an early success and ends with the diagnostic window (first contact + window_s).
"""

import torch

FEATURES = 9  # critic-only event state, see features()


class LandingRewards:
    def __init__(self, count: int, wheels: list[int], body_count: int, settings: dict, device: str):
        self.p = settings
        self.wheels = wheels
        self.nonwheel = torch.ones(body_count, dtype=torch.bool, device=device)
        self.nonwheel[wheels] = False
        self.active = torch.zeros(count, dtype=torch.bool, device=device)
        self.hold = self.active.clone()
        self.bad = self.active.clone()
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
        ):
            value[ids] = 0
        self._add("births", air.sum())

    def begin_step(self) -> None:
        # Support must remain present throughout every physical sample of the policy interval.
        self.support.fill_(True)

    def sample(self, tick: int, physics_dt: float, forces: torch.Tensor) -> None:
        use = self.active & (tick > self.last_tick)
        self.last_tick[use] = tick
        finite = torch.isfinite(forces).all(-1)
        contact = forces > self.p["contact_force_n"]
        first = use & finite & (self.touch < 0) & contact.any(-1)
        self.touch[first] = ((tick - self.born) * physics_dt)[first]
        self.invalid |= use & ~finite
        self.bad |= use & finite & contact[:, self.nonwheel].any(-1)
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
        supported = self.active & contacted & self.support & ~self.bad & ~self.invalid & ~done
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
        failed = self.active & ~success & (done | self.bad | self.invalid | expired | missing)
        # An early exogenous time limit (randomized initial episode age) is not a landing failure.
        neutral = failed & timeout & ~terminated & ~numerical & ~self.bad & ~self.invalid
        failed &= ~neutral
        self.outcome[failed] = -self.p["failure_cost"]
        self.outcome[success] = self.p["success_bonus"]
        # Mutually exclusive causes, in priority order.
        causes = {
            "invalid": failed & self.invalid,
            "collision": failed & ~self.invalid & self.bad,
            "terminated": failed & ~self.invalid & ~self.bad & terminated,
            "no_contact": failed & ~self.invalid & ~self.bad & ~terminated & missing,
        }
        causes["unstable"] = failed & ~torch.stack(list(causes.values())).any(0)
        self._add("success", success.sum())
        self._add("neutral_timeout", neutral.sum())
        for name, mask in causes.items():
            self._add(f"failure/{name}", mask.sum())
        self._add("success_time_s/sum", torch.where(success, self.since_touch, 0.0).sum())
        self.active[success | failed | neutral] = False
        # Same end as the diagnostic window: a failed event (e.g. a collision) keeps the commands frozen so the
        # diagnostic recovery that follows is not mixed with responses to new commands.
        self.hold &= ~(done | expired | missing)

    def terms(self, state: dict, wheel_radius: float, dt: float) -> dict[str, torch.Tensor]:
        # Both flight terms are nonpositive, so they add nothing for staying airborne. The attitude rewards and the
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
        return {
            "landing_progress": self.progress,
            "landing_outcome": self.outcome,
            "landing_wheel_center": torch.where(flight, -self.p["wheel_center_weight"] * dt * (1 - center), 0.0),
            "landing_wheel_speed": torch.where(flight, -self.p["wheel_speed_weight"] * dt * (1 - speed), 0.0),
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
        result = {f"LandingReward/{k}": v for k, v in values.items() if not k.endswith("/sum")}
        result["LandingReward/pending"] = float(self.active.sum().item())
        failures = sum(v for k, v in values.items() if k.startswith("failure/"))
        resolved = values.get("success", 0.0) + failures
        if resolved:
            # First 0.5 s stable hold reached; says nothing about staying stable afterwards. Exogenous timeouts
            # are excluded from the denominator: they say nothing about the landing.
            result["LandingReward/first_recovery_rate"] = values["success"] / resolved
        if values.get("success"):
            result["LandingReward/success_time_s/mean"] = values["success_time_s/sum"] / values["success"]
        return result
