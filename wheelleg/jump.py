import torch

from .commands import uniform

FEATURES = 16
TUNNEL_FEATURES = 5


def jump_height_error(actual: torch.Tensor, target: torch.Tensor, settings: dict) -> torch.Tensor:
    """A narrow undershoot band and a wider, bounded overshoot band."""
    low = (target - settings["height_tolerance_m"] - actual).clamp_min(0)
    high = (actual - target - settings.get("height_overshoot_tolerance_m", 0.03)).clamp_min(0)
    return low + high


class JumpEvent:
    """Contact-driven phases; apex/landing pulses can only occur once per event."""

    def __init__(self, settings: dict, count: int, device: str):
        self.settings, self.device = settings, device
        self.active = torch.zeros(count, dtype=torch.bool, device=device)
        self.remaining = torch.zeros(count, dtype=torch.long, device=device)
        self.elapsed = torch.zeros(count, device=device)
        self.next_trigger = torch.zeros_like(self.elapsed)
        self.height = torch.zeros_like(self.elapsed)
        self.start_z = torch.zeros_like(self.elapsed)
        self.apex_z = torch.zeros_like(self.elapsed)
        self.height_progress = torch.zeros_like(self.elapsed)
        self.air_time = torch.zeros_like(self.elapsed)
        self.stable_time = torch.zeros_like(self.elapsed)
        self.touchdown_time = torch.full((count, 2), -1.0, device=device)
        self.took_off = self.active.clone()
        self.landed = self.active.clone()
        self.apex_paid = self.active.clone()
        self.landing_paid = self.active.clone()
        self.invalid = self.active.clone()
        self.apex_pulse = self.active.clone()
        self.landing_pulse = self.active.clone()
        self.touchdown_pulse = self.active.clone()
        self.finished = self.active.clone()
        self.first_touch = self.active.clone()
        self.takeoff_time = torch.zeros_like(self.elapsed)
        self.takeoff_peak_vz = torch.zeros_like(self.elapsed)
        self.quality_sum = torch.zeros(count, 2, device=device)
        self.quality_time = torch.zeros_like(self.elapsed)
        self.quality_active = self.active.clone()
        self.failure_pulse = self.active.clone()
        self.failure_paid = self.active.clone()
        self.quality_paid = self.active.clone()

    def reset(self, ids: torch.Tensor) -> None:
        for value in (
            self.active,
            self.took_off,
            self.landed,
            self.apex_paid,
            self.landing_paid,
            self.invalid,
            self.apex_pulse,
            self.landing_pulse,
            self.touchdown_pulse,
            self.finished,
            self.first_touch,
            self.quality_active,
            self.failure_pulse,
            self.failure_paid,
            self.quality_paid,
        ):
            value[ids] = False
        for value in (
            self.elapsed,
            self.height,
            self.air_time,
            self.stable_time,
            self.start_z,
            self.apex_z,
            self.height_progress,
            self.takeoff_time,
            self.takeoff_peak_vz,
            self.quality_sum,
            self.quality_time,
        ):
            value[ids] = 0
        self.touchdown_time[ids] = -1
        self.remaining[ids] = torch.multinomial(
            self.elapsed.new_tensor(self.settings["jump_count_probabilities"]), len(ids), replacement=True
        )
        self.next_trigger[ids] = uniform(self.settings["first_trigger_range_s"], (len(ids),), self.device)

    def trigger(
        self,
        age: torch.Tensor,
        z: torch.Tensor,
        allowed: torch.Tensor,
        target_height: torch.Tensor | None = None,
        *,
        require_trigger_time: bool = True,
    ) -> None:
        start = ~self.active & (self.remaining > 0) & allowed
        if require_trigger_time:
            start &= age >= self.next_trigger
        ids = start.nonzero().flatten()
        if not len(ids):
            return
        self.active[ids] = True
        self.remaining[ids] -= 1
        for value in (
            self.took_off,
            self.landed,
            self.apex_paid,
            self.landing_paid,
            self.invalid,
            self.failure_paid,
            self.quality_active,
            self.quality_paid,
        ):
            value[ids] = False
        self.first_touch[ids] = False
        self.elapsed[ids] = 0
        self.air_time[ids] = 0
        self.stable_time[ids] = 0
        self.takeoff_time[ids] = 0
        self.takeoff_peak_vz[ids] = 0
        self.quality_sum[ids] = 0
        self.quality_time[ids] = 0
        self.touchdown_time[ids] = -1
        self.height[ids] = (
            uniform(self.settings["height_range_m"], (len(ids),), self.device)
            if target_height is None
            else target_height[ids]
        )
        self.start_z[ids] = z[ids]
        self.apex_z[ids] = z[ids]

    def update(
        self,
        dt: float,
        age: torch.Tensor,
        z: torch.Tensor,
        vz: torch.Tensor,
        contact: torch.Tensor,
        stable: torch.Tensor,
        valid_landing: torch.Tensor,
        obstacle_contact: torch.Tensor,
        wheel_clearance: torch.Tensor | None = None,
        failed: torch.Tensor | None = None,
        require_height: torch.Tensor | None = None,
    ) -> None:
        self.apex_pulse.zero_()
        self.landing_pulse.zero_()
        self.touchdown_pulse.zero_()
        self.finished.zero_()
        self.failure_pulse.zero_()
        self.elapsed += dt * self.active
        no_contact = ~contact.any(-1)
        can_takeoff = self.active & ~self.landed & (self.elapsed >= self.settings["crouch_duration_s"])
        clearance = torch.zeros_like(z) if wheel_clearance is None else wheel_clearance.amin(-1)
        candidate = can_takeoff & no_contact & (clearance >= self.settings.get("takeoff_clearance_m", 0.02))
        self.takeoff_time = torch.where(candidate, self.takeoff_time + dt, 0.0)
        self.takeoff_peak_vz = torch.where(candidate, torch.maximum(self.takeoff_peak_vz, vz), 0.0)
        self.apex_z = torch.where(~self.took_off & ~candidate, self.start_z, self.apex_z)
        confirmed = candidate & (self.takeoff_time >= self.settings.get("takeoff_confirmation_s", 0.03) - dt * 0.5)
        confirmed &= self.takeoff_peak_vz >= self.settings.get("takeoff_upward_velocity_m_s", 0.1)
        # The running apex is monotone within an attempt. Do not cash any of it in until takeoff is confirmed.
        old_apex = torch.where(self.took_off, self.apex_z, self.start_z)
        self.took_off |= confirmed
        flight = self.active & self.took_off & ~self.landed
        self.air_time += dt * flight * no_contact
        self.apex_z = torch.where(candidate | flight, torch.maximum(self.apex_z, z), self.apex_z)
        self.invalid |= self.active & obstacle_contact
        if failed is not None:
            self.invalid |= self.active & failed
        self.apex_pulse = flight & no_contact & (vz <= 0) & ~self.apex_paid & ~self.invalid
        self.apex_paid |= self.apex_pulse
        self.quality_active.copy_(flight & candidate & ~self.invalid)
        goal = self.height.clamp_min(torch.finfo(self.height.dtype).eps)
        previous = ((old_apex - self.start_z) / goal).clamp(0, 1)
        current = ((self.apex_z - self.start_z) / goal).clamp(0, 1)
        self.height_progress.copy_(torch.where(self.quality_active, (current - previous).clamp_min(0), 0.0))
        # Invalid first touchdown cannot become success by driving off the roof later.
        height_ok = jump_height_error(self.apex_z - self.start_z, self.height, self.settings) <= 1e-6
        if require_height is not None:
            height_ok |= ~require_height
        new_touch = flight & contact.any(-1) & ~self.first_touch
        self.invalid |= new_touch & (~valid_landing | ~height_ok)
        self.first_touch |= new_touch
        first_touch = flight[:, None] & contact & (self.touchdown_time < 0)
        self.touchdown_time = torch.where(first_touch, self.elapsed[:, None], self.touchdown_time)
        self.touchdown_pulse = flight & contact.all(-1)
        self.landed |= self.touchdown_pulse
        landing_ok = self.active & self.landed & contact.all(-1) & stable & valid_landing & ~self.invalid & height_ok
        self.stable_time = torch.where(landing_ok, self.stable_time + dt, 0)
        self.landing_pulse = landing_ok & (self.stable_time >= self.settings["landing_stable_s"] - dt / 2)
        self.landing_pulse &= ~self.landing_paid
        self.landing_paid |= self.landing_pulse
        # Keep the event alive through the required post-landing validation window.
        expired = self.elapsed >= self.settings["event_duration_s"] + self.settings["landing_stable_s"]
        self.failure_pulse = self.active & (expired | self.invalid) & ~self.landing_pulse & ~self.failure_paid
        self.failure_paid |= self.failure_pulse
        finished = self.active & (self.failure_pulse | self.landing_pulse)
        self.finished = finished
        ids = finished.nonzero().flatten()
        self.next_trigger[ids] = age[ids] + uniform(self.settings["between_events_s"], (len(ids),), self.device)
        self.active[ids] = False

    def fail_pending(self, ended: torch.Tensor) -> None:
        """An episode that ends before its requested takeoff is still a failed attempt."""
        pending = ended & (self.remaining > 0) & ~self.landing_paid & ~self.failure_paid
        self.failure_pulse |= pending
        self.failure_paid |= pending
        self.finished |= pending
        self.remaining[pending] = 0

    def sample_air_quality(
        self, torque: torch.Tensor, wheel_x: torch.Tensor, parameters: dict, dt: float
    ) -> torch.Tensor:
        quality = torch.stack(
            (
                torch.exp(-torque.square().sum(-1) / parameters["wheel_torque_sigma"]),
                torch.exp(-wheel_x.square().sum(-1) / parameters["wheel_center_sigma"]),
            ),
            -1,
        )
        quality = torch.nan_to_num(quality, nan=0.0, posinf=0.0, neginf=0.0).clamp(0, 1)
        self.quality_sum += quality * self.quality_active[:, None] * dt
        self.quality_time += self.quality_active * dt
        average = self.quality_sum / self.quality_time.clamp_min(dt)[:, None]
        pay = self.landing_pulse & ~self.quality_paid & (self.quality_time > 0)
        self.quality_paid |= self.landing_pulse
        return average.clamp(0, 1) * pay[:, None]

    def features(self) -> torch.Tensor:
        window = self.settings["event_duration_s"] + self.settings["landing_stable_s"]
        quality = self.quality_sum / self.quality_time.clamp_min(1e-6)[:, None]
        return torch.nan_to_num(
            torch.cat(
                (
                    (self.elapsed / window)[:, None],
                    (self.takeoff_time / self.settings.get("takeoff_confirmation_s", 0.03))[:, None],
                    (self.takeoff_peak_vz / self.settings.get("takeoff_upward_velocity_m_s", 0.1))[:, None],
                    self.took_off[:, None],
                    self.landed[:, None],
                    self.invalid[:, None],
                    ((self.apex_z - self.start_z) / self.height.clamp_min(0.01))[:, None],
                    (self.stable_time / self.settings["landing_stable_s"])[:, None],
                    (self.air_time / window)[:, None],
                    self.apex_paid[:, None],
                    self.landing_paid[:, None],
                    self.failure_paid[:, None],
                    quality,
                    (self.quality_time / window)[:, None],
                    (self.remaining / 2)[:, None],
                ),
                -1,
            )
        ).clamp(-1, 1)

    @property
    def phase(self) -> torch.Tensor:
        return (self.elapsed / self.settings["event_duration_s"]).clamp(0, 1)

    def references(self, vz: torch.Tensor, wheel_clearance: torch.Tensor, gravity: float) -> dict[str, torch.Tensor]:
        flight = self.active & self.took_off & ~self.landed
        # Ballistic time remaining, evaluated only for the descending phase.
        time_to_ground = (vz + torch.sqrt(vz.square() + 2 * gravity * wheel_clearance.clamp_min(0))) / gravity
        prepare = flight & (vz < 0) & (time_to_ground < self.settings["landing_prepare_time_s"])
        return {
            "crouch": self.active & ~self.took_off & (self.elapsed < self.settings["crouch_duration_s"]),
            "push": self.active & ~self.took_off & (self.elapsed >= self.settings["crouch_duration_s"]),
            "flight": flight,
            "prepare": prepare,
            "tuck": flight & ~prepare,
            "takeoff_velocity": torch.sqrt(2 * gravity * self.height),
        }


class TunnelTraversal:
    """Latch corridor and airborne-clearance checks through both obstacle faces."""

    def __init__(self, count: int, device: str):
        self.approached = torch.zeros(count, dtype=torch.bool, device=device)
        self.entered = torch.zeros_like(self.approached)
        self.cleared = torch.zeros_like(self.approached)
        self.invalid = torch.zeros_like(self.approached)
        self.progress_max = torch.zeros(count, device=device)

    def reset(self, ids: torch.Tensor) -> None:
        self.progress_max[ids] = 0
        for value in (self.approached, self.entered, self.cleared, self.invalid):
            value[ids] = False

    def progress(self, distance: torch.Tensor, limit: torch.Tensor, enabled: torch.Tensor) -> torch.Tensor:
        """Pay only newly reached forward distance; reversing cannot replenish it."""
        reached = torch.minimum(distance.clamp_min(0), limit)
        increment = (reached - self.progress_max).clamp_min(0) * enabled
        self.progress_max = torch.where(enabled, torch.maximum(self.progress_max, reached), self.progress_max)
        return increment

    def update(
        self,
        wheels: torch.Tensor,
        wheel_radius: float,
        bodies: torch.Tensor,
        start: torch.Tensor,
        end: torch.Tensor,
        top: torch.Tensor,
        center_y: torch.Tensor,
        half_width: float,
        margin: float,
        clearance: float,
        flight: torch.Tensor,
        enabled: torch.Tensor,
    ) -> None:
        front = torch.maximum((wheels[:, :, 0] + wheel_radius).amax(-1), bodies[:, :, 0].amax(-1))
        rear = torch.minimum((wheels[:, :, 0] - wheel_radius).amin(-1), bodies[:, :, 0].amin(-1))
        lateral = torch.maximum(
            (wheels[:, :, 1] - center_y[:, None]).abs().amax(-1) + wheel_radius,
            (bodies[:, :, 1] - center_y[:, None]).abs().amax(-1),
        )
        self.approached |= enabled & (front < start)
        reached = enabled & (front >= start)
        self.invalid |= enabled & (lateral > half_width - margin)
        self.invalid |= reached & ~self.approached
        overlap = reached & (rear <= end) & ~self.cleared
        high = (wheels[:, :, 2] - wheel_radius).amin(-1) >= top + clearance
        high &= bodies[:, :, 2].amin(-1) >= top + clearance
        self.invalid |= overlap & (~flight | ~high)
        self.entered |= reached & self.approached & ~self.invalid
        self.cleared |= enabled & self.entered & (rear > end + margin) & ~self.invalid

    def features(self) -> torch.Tensor:
        return torch.stack((self.approached, self.entered, self.cleared, self.invalid, self.progress_max), -1).float()


def tunnel_landing(
    wheel_position: torch.Tensor,
    wheel_radius: float,
    body_position: torch.Tensor,
    beam_end_x: torch.Tensor,
    ground_z: torch.Tensor,
    margin: float,
    ground_tolerance: float,
    center_y: torch.Tensor | None = None,
    half_width: float | None = None,
    contact: torch.Tensor | None = None,
) -> torch.Tensor:
    wheels_beyond = (wheel_position[:, :, 0] - wheel_radius > beam_end_x[:, None] + margin).all(-1)
    body_beyond = (body_position[:, :, 0] > beam_end_x[:, None] + margin).all(-1)
    near_ground = (wheel_position[:, :, 2] - wheel_radius - ground_z[:, None]).abs() < ground_tolerance
    if contact is not None:
        near_ground |= ~contact
    on_ground = near_ground.all(-1)
    valid = wheels_beyond & body_beyond & on_ground
    if center_y is not None:
        lateral = torch.maximum(
            (wheel_position[:, :, 1] - center_y[:, None]).abs().amax(-1) + wheel_radius,
            (body_position[:, :, 1] - center_y[:, None]).abs().amax(-1),
        )
        valid &= lateral <= half_width - margin
    return valid
