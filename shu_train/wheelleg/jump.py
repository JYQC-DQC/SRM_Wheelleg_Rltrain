import torch

from .commands import uniform


class TrainingJumpButton:
    """An optional scripted operator: one time-based press pulse per episode, never obstacle-based."""

    def __init__(self, settings: dict, count: int, device: str):
        self.bounds = settings["press_time_range_s"]
        self.no_press_probability = settings["no_press_probability"]
        self.due_s = torch.zeros(count, device=device)
        self.pending = torch.zeros(count, dtype=torch.bool, device=device)

    def reset(self, ids: torch.Tensor) -> None:
        self.due_s[ids] = uniform(self.bounds, (len(ids),), self.due_s.device)
        self.pending[ids] = torch.rand(len(ids), device=self.due_s.device) >= self.no_press_probability

    def step(self, episode_age_s: torch.Tensor) -> torch.Tensor:
        pulse = self.pending & (episode_age_s >= self.due_s)
        self.pending &= ~pulse
        return pulse


class JumpEvent:
    """One jump per rising button edge; no retrigger or queue while busy."""

    def __init__(self, settings: dict, count: int, device: str):
        self.settings, self.device = settings, device
        self.active = torch.zeros(count, dtype=torch.bool, device=device)
        self.elapsed = torch.zeros(count, device=device)
        self.height = torch.zeros_like(self.elapsed)
        self.command_remaining = torch.zeros_like(self.elapsed)
        self.command_m = torch.zeros_like(self.elapsed)
        self.start_z = torch.zeros_like(self.elapsed)
        self.apex_z = torch.zeros_like(self.elapsed)
        self.peak_wheel_clearance = torch.zeros_like(self.elapsed)
        self.air_time = torch.zeros_like(self.elapsed)
        self.stable_time = torch.zeros_like(self.elapsed)
        self.touchdown_time = torch.full((count, 2), -1.0, device=device)
        self.took_off = self.active.clone()
        self.landed = self.active.clone()
        self.landing_paid = self.active.clone()
        self.invalid = self.active.clone()
        self.landing_pulse = self.active.clone()
        self.touchdown_pulse = self.active.clone()
        self.finished = self.active.clone()
        self.failed = self.active.clone()
        self._deadline = self.active.clone()
        self.first_touch = self.active.clone()
        self.had_support = self.active.clone()
        self.crossed_over_beam = self.active.clone()
        self.button_down = self.active.clone()
        self.requested = self.active.clone()

    def reset(self, ids: torch.Tensor) -> None:
        for value in (
            self.active,
            self.took_off,
            self.landed,
            self.landing_paid,
            self.invalid,
            self.landing_pulse,
            self.touchdown_pulse,
            self.finished,
            self.failed,
            self._deadline,
            self.first_touch,
            self.had_support,
            self.crossed_over_beam,
            self.requested,
        ):
            value[ids] = False
        for value in (
            self.elapsed,
            self.height,
            self.air_time,
            self.stable_time,
            self.command_remaining,
            self.command_m,
            self.start_z,
            self.apex_z,
            self.peak_wheel_clearance,
        ):
            value[ids] = 0
        self.touchdown_time[ids] = -1

    def advance_command(self, dt: float) -> None:
        # Operator latch, never shortened by a simulated landing or failure. Half a tick handles float roundoff.
        self.command_remaining.sub_(dt).clamp_min_(0)
        self.command_remaining.masked_fill_(self.command_remaining < dt / 2, 0)
        self.command_m.masked_fill_(self.command_remaining == 0, 0)

    def request(self, button_down: torch.Tensor) -> None:
        """Supply the batched button level each policy tick, including the release."""
        self.requested |= button_down & ~self.button_down & (self.command_remaining == 0)
        self.button_down.copy_(button_down)

    def trigger(
        self,
        z: torch.Tensor,
        target_height: torch.Tensor | float | None = None,
        *,
        before_beam: torch.Tensor | None = None,
    ) -> None:
        start = self.requested.clone()
        self.requested.zero_()
        ids = start.nonzero().flatten()
        if not len(ids):
            return
        self.active[ids] = True
        for value in (self.took_off, self.landed, self.landing_paid, self.invalid, self._deadline):
            value[ids] = False
        self.first_touch[ids] = False
        self.had_support[ids] = False
        self.crossed_over_beam[ids] = False
        if before_beam is not None:
            # This invalidates success, not the operator's request to jump.
            self.invalid[ids] = ~before_beam[ids]
        self.elapsed[ids] = 0
        self.air_time[ids] = 0
        self.stable_time[ids] = 0
        self.touchdown_time[ids] = -1
        if target_height is None:
            self.height[ids] = uniform(self.settings["height_range_m"], (len(ids),), self.device)
        else:
            self.height[ids] = target_height[ids] if torch.is_tensor(target_height) else target_height
        self.command_m[ids] = self.height[ids]
        self.command_remaining[ids] = self.settings["event_duration_s"] + self.settings["landing_stable_s"]
        self.start_z[ids] = z[ids]
        self.apex_z[ids] = z[ids]
        self.peak_wheel_clearance[ids] = 0

    def begin_step(self) -> None:
        self.landing_pulse.zero_()
        self.touchdown_pulse.zero_()
        self.finished.zero_()
        self.failed.zero_()

    def sample(
        self,
        dt: float,
        z: torch.Tensor,
        vz: torch.Tensor,
        contact: torch.Tensor,
        stable: torch.Tensor,
        valid_landing: torch.Tensor,
        obstacle_contact: torch.Tensor,
        *,
        wheel_clearance: torch.Tensor,
        takeoff_clearance_m: float,
        above_beam: torch.Tensor | None = None,
        blocked_at_beam: torch.Tensor | None = None,
    ) -> None:
        """Advance evidence from one fresh physics sample; never pay rewards here."""
        use = self.active & ~self.invalid & ~self._deadline
        self.elapsed += dt * use
        no_contact = ~contact.any(-1)
        self.had_support |= use & ~no_contact
        lifting = no_contact & (vz > 0) & (wheel_clearance > takeoff_clearance_m)
        self.took_off |= use & self.had_support & lifting
        flight = use & self.took_off & ~self.first_touch
        self.air_time += dt * flight * no_contact
        self.apex_z = torch.where(flight, torch.maximum(self.apex_z, z), self.apex_z)
        self.peak_wheel_clearance = torch.where(
            flight & no_contact, torch.maximum(self.peak_wheel_clearance, wheel_clearance), self.peak_wheel_clearance
        )
        self.invalid |= self.active & obstacle_contact
        if above_beam is not None:
            self.crossed_over_beam |= flight & no_contact & above_beam
            self.invalid |= self.active & blocked_at_beam
            valid_landing = valid_landing & self.crossed_over_beam
        # Check the geometry of the touching wheel(s) at the original sample, not later in the policy step.
        new_touch = flight & ~no_contact
        self.invalid |= new_touch & ~valid_landing
        self.first_touch |= new_touch
        first_wheel_touch = (use & self.took_off)[:, None] & contact & (self.touchdown_time < 0)
        self.touchdown_time = torch.where(first_wheel_touch, self.elapsed[:, None], self.touchdown_time)
        self.touchdown_pulse |= use & self.took_off & ~self.landed & contact.all(-1)
        self.landed |= self.touchdown_pulse
        landing_ok = use & self.landed & contact.all(-1) & stable & valid_landing & ~self.invalid
        self.stable_time = torch.where(landing_ok, self.stable_time + dt, 0.0)
        # A small tolerance covers accumulation; unlike peak forces, these samples cannot span a contact gap.
        ready = self.stable_time >= self.settings["landing_stable_s"] - dt / 2
        duration = self.settings["event_duration_s"]
        late_touchdown = ~self.landed & (self.elapsed >= duration - dt / 2)
        expired = (self.elapsed >= duration + self.settings["landing_stable_s"] - dt / 2) & ~ready
        self._deadline |= use & (late_touchdown | expired)

    def finish_step(self, dt: float, interrupted: torch.Tensor) -> None:
        """Publish at most one outcome after the final physics sample and external safety checks."""
        ready = (self.stable_time > 0) & (self.stable_time >= self.settings["landing_stable_s"] - dt / 2)
        eligible = self.active & ~interrupted
        self.failed.copy_(eligible & (self.invalid | self._deadline))
        self.landing_pulse.copy_(eligible & ready & ~self.failed & ~self.landing_paid)
        self.landing_paid |= self.landing_pulse
        self.finished.copy_(self.active & (interrupted | self.failed | self.landing_pulse))
        self.active &= ~self.finished

    def update(
        self,
        dt: float,
        z: torch.Tensor,
        vz: torch.Tensor,
        contact: torch.Tensor,
        stable: torch.Tensor,
        valid_landing: torch.Tensor,
        obstacle_contact: torch.Tensor,
        *,
        wheel_clearance: torch.Tensor,
        takeoff_clearance_m: float,
        above_beam: torch.Tensor | None = None,
        blocked_at_beam: torch.Tensor | None = None,
    ) -> None:
        """Single-sample convenience API; the env uses begin_step/sample/finish_step."""
        self.begin_step()
        self.sample(
            dt,
            z,
            vz,
            contact,
            stable,
            valid_landing,
            obstacle_contact,
            wheel_clearance=wheel_clearance,
            takeoff_clearance_m=takeoff_clearance_m,
            above_beam=above_beam,
            blocked_at_beam=blocked_at_beam,
        )
        self.finish_step(dt, torch.zeros_like(self.active))

    @property
    def flight(self) -> torch.Tensor:
        return self.active & self.took_off & ~self.first_touch


def collision_bounds_w(
    body_position: torch.Tensor, body_quat: torch.Tensor, local_bounds: torch.Tensor
) -> tuple[torch.Tensor, torch.Tensor]:
    """Conservative world AABBs of body-frame collision envelopes; quaternions are wxyz."""
    lo, hi = local_bounds.unbind(-2)
    center, half = (lo + hi) / 2, (hi - lo) / 2
    w, x, y, z = body_quat.unbind(-1)
    matrix = torch.stack(
        (
            1 - 2 * (y * y + z * z),
            2 * (x * y - w * z),
            2 * (x * z + w * y),
            2 * (x * y + w * z),
            1 - 2 * (x * x + z * z),
            2 * (y * z - w * x),
            2 * (x * z - w * y),
            2 * (y * z + w * x),
            1 - 2 * (x * x + y * y),
        ),
        dim=-1,
    ).unflatten(-1, (3, 3))
    center_w = body_position + (matrix @ center.unsqueeze(-1)).squeeze(-1)
    half_w = (matrix.abs() @ half.unsqueeze(-1)).squeeze(-1)
    return center_w - half_w, center_w + half_w


def tunnel_geometry(
    bounds_w: tuple[torch.Tensor, torch.Tensor],
    start_w: torch.Tensor,
    top_z_w: torch.Tensor,
    settings: dict,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    """Return before, over, under/intersecting, and wholly past the beam (along world +X)."""
    lo, hi = bounds_w
    start = start_w[:, 0:1]
    end = start + settings["beam_length_m"]
    side = settings["lane_width_m"] / 2
    within_lane = ((lo[..., 1] >= start_w[:, 1:2] - side) & (hi[..., 1] <= start_w[:, 1:2] + side)).all(-1)
    overlaps = (hi[..., 0] >= start) & (lo[..., 0] <= end)
    low = overlaps & (lo[..., 2] <= top_z_w[:, None] + settings["clearance_margin_m"])
    before = (hi[..., 0] < start).all(-1)
    over = overlaps.any(-1) & ~low.any(-1) & within_lane
    past = (lo[..., 0] > end + settings["landing_margin_m"]).all(-1) & within_lane
    blocked = low.any(-1) | (overlaps.any(-1) & ~within_lane)
    return before, over, blocked, past
