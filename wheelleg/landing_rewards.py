"""Bounded first-landing rewards; diagnostics remain an independent observer."""

import torch


class LandingRewards:
    def __init__(self, count: int, wheels: list[int], body_count: int, settings: dict, device: str):
        self.p = settings
        self.wheels = wheels
        self.nonwheel = torch.ones(body_count, dtype=torch.bool, device=device)
        self.nonwheel[wheels] = False
        self.active = torch.zeros(count, dtype=torch.bool, device=device)
        self.bad = self.active.clone()
        self.support = self.active.clone()
        self.born = torch.zeros(count, dtype=torch.long, device=device)
        self.last_tick = torch.full_like(self.born, -1)
        self.touch = torch.full((count,), -1.0, device=device)
        self.held = torch.zeros(count, device=device)
        self.best = self.held.clone()
        self.effort_paid = self.held.clone()
        self.progress = self.held.clone()
        self.outcome = self.held.clone()

    def reset(self, ids: torch.Tensor, air: torch.Tensor, tick: int) -> None:
        # Only exogenous air-reset births open an event. Hops and contact chatter cannot reopen it.
        self.active[ids] = air
        self.born[ids] = tick
        self.last_tick[ids] = tick
        self.touch[ids] = -1
        for value in (self.bad, self.support, self.held, self.best, self.effort_paid, self.progress, self.outcome):
            value[ids] = 0

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
        self.bad |= use & (~finite | contact[:, self.nonwheel].any(-1))
        both = (forces[:, self.wheels] > self.p["support_force_n"]).all(-1)
        self.support &= ~use | (finite & both & ~contact[:, self.nonwheel].any(-1))

    def flight(self) -> torch.Tensor:
        return self.active & (self.touch < 0) & ~self.bad

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
        tilt = torch.stack((state["roll"], state["pitch"]), -1).abs().amax(-1)
        omega = state["angular_velocity"][:, :2].abs().amax(-1)
        vz = state["velocity_w"][:, 2].abs()
        height = state["height_error"].abs()
        values = torch.stack((tilt, omega, vz, height), -1)
        finite = torch.isfinite(values).all(-1)
        self.bad |= self.active & (~finite | numerical)
        done = terminated | timeout | numerical
        contacted = self.touch >= 0
        eligible = self.active & contacted & self.support & ~self.bad & ~done & finite
        scales = values.new_tensor(
            [self.p[k] for k in ("tilt_rad", "angular_xy_rad_s", "vertical_velocity_m_s", "height_error_m")]
        )
        # Squared, normalized, bounded quality; never multiply an unchecked NaN by a mask.
        quality = torch.exp(-0.25 * (torch.nan_to_num(values / scales, nan=1e6).clamp(-1e6, 1e6)).square().sum(-1))
        quality = torch.where(eligible, quality, 0.0)
        higher = torch.maximum(self.best, quality)
        self.progress.copy_((higher - self.best) * self.p["progress_budget"])
        self.best.copy_(higher)
        stable = eligible & (values <= scales).all(-1)
        self.held = torch.where(stable, self.held + dt, 0.0)
        expired = contacted & (age - self.touch >= self.p["window_s"])
        missing = ~contacted & (age >= self.p["contact_timeout_s"])
        finish = self.active & (done | expired | missing)
        good = finish & expired & ~done & ~self.bad & (self.held >= self.p["stable_s"])
        self.outcome[finish] = -self.p["failure_cost"]
        # An early exogenous time limit (randomized initial episode age) is not a landing failure.
        self.outcome[finish & timeout & ~terminated & ~numerical] = 0.0
        self.outcome[good] = self.p["success_bonus"]
        self.active[finish] = False

    def terms(self, torque: torch.Tensor, limits: torch.Tensor, dt: float) -> dict[str, torch.Tensor]:
        cost = self.p["flight_effort_rate"] * (torque / limits).square().mean(-1).clamp(0, 1) * dt
        cost = torch.where(self.flight(), cost, 0.0)
        cost = torch.minimum(cost, (self.p["flight_effort_budget"] - self.effort_paid).clamp_min(0))
        self.effort_paid += cost
        return {"landing_progress": self.progress, "landing_outcome": self.outcome, "landing_flight_effort": -cost}
