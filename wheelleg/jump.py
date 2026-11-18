import torch

from .air_retraction import AirRetractionTracker
from .commands import uniform

FEATURES = 16
TUNNEL_FEATURES = 5


def jump_height_overshoot(actual: torch.Tensor, target: torch.Tensor, settings: dict) -> torch.Tensor:
    return (actual - (target + settings.get("height_overshoot_tolerance_m", 0.03))).clamp_min(0)


def jump_height_error(actual: torch.Tensor, target: torch.Tensor, settings: dict) -> torch.Tensor:
    """Capacity targets charge undershoot only; precision targets still charge both sides."""
    low = ((target - settings["height_tolerance_m"]) - actual).clamp_min(0)
    return low if settings.get("height_is_minimum", False) else low + jump_height_overshoot(actual, target, settings)


def landing_rates_ok(vz: torch.Tensor, roll_pitch_rate: torch.Tensor, settings: dict) -> torch.Tensor:
    return (vz.abs() < settings["stable_vz_m_s"]) & (
        roll_pitch_rate.abs().amax(-1) < settings["stable_roll_pitch_rate_rad_s"]
    )


class JumpEvent:
    """Contact-driven phases; apex/landing pulses can only occur once per event."""

    def __init__(self, settings: dict, count: int, device: str):
        self.settings, self.device = settings, device
        self.landing_settle_timeout_s = settings.get("landing_settle_timeout_s")
        self.clearance_training = settings.get("clearance_jump")
        self.body_wheel = settings.get("body_wheel_jump")
        self.active = torch.zeros(count, dtype=torch.bool, device=device)
        self.remaining = torch.zeros(count, dtype=torch.long, device=device)
        self.elapsed = torch.zeros(count, device=device)
        self.next_trigger = torch.zeros_like(self.elapsed)
        self.height = torch.zeros_like(self.elapsed)
        self.start_z = torch.zeros_like(self.elapsed)
        self.apex_z = torch.zeros_like(self.elapsed)
        self.peak_wheel_clearance = torch.zeros_like(self.elapsed)
        self.start_body_clearance = torch.zeros_like(self.elapsed)
        self.peak_joint_clearance = torch.zeros_like(self.elapsed)
        self.peak_body_at_apex = torch.zeros_like(self.elapsed)
        self.peak_wheel_at_apex = torch.zeros_like(self.elapsed)
        self.peak_leg_angle_rad = torch.zeros_like(self.elapsed)
        self.apex_pose_quality = torch.zeros_like(self.elapsed)
        self.band_width = (self.body_wheel or {}).get("apex_band_m")
        if self.band_width is not None:
            # Five rolling height bins, not a time buffer: even long flights have bounded storage.
            self.band_frames = self.elapsed.new_zeros((count, 5, 4))  # joint height, body, wheel, worst leg angle
            self.band_rows = torch.arange(count, device=device)
            self.band_scored_height = torch.zeros_like(self.elapsed)
        self.preparing = self.active.clone()
        self.delay_extension = self.clearance_training is not None and "prepare_drop_fraction" in self.clearance_training
        if self.delay_extension:
            self.flight_start_z = torch.zeros_like(self.elapsed)
            self.flight_peak_z = torch.zeros_like(self.elapsed)
        self.height_progress = torch.zeros_like(self.elapsed)
        self.air_guard = (self.body_wheel or {}).get("air_leg_guard")
        if self.air_guard is not None:
            self.retraction = AirRetractionTracker(count, self.air_guard["retract_tolerance_m"], device,
                                                  base_threshold_m=self.air_guard.get("retract_base_threshold_m"))
            multipliers = self.air_guard.get("retract_multipliers")
            self.retract_multipliers = None if multipliers is None else self.elapsed.new_tensor(multipliers)
            if self.retract_multipliers is not None and self.retract_multipliers.shape != (3,):
                raise ValueError(
                    "retract_multipliers must specify three values for the first, second, and later excursions"
                )
            # An old configuration with neither key keeps the unweighted length-only cost.
            default_fourth_cost = 0.5 if multipliers is not None else 0.0
            self.retract_fourth_cost = self.air_guard.get("retract_fourth_cost", default_fourth_cost)
            self.deepest_intrusion = torch.zeros_like(self.elapsed)
            self.air_fold_cost = torch.zeros_like(self.elapsed)
            self.air_retract_cost = torch.zeros_like(self.elapsed)
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
        self.last_air_vz = torch.zeros_like(self.elapsed)
        self.first_touch_speed_pulse = torch.zeros_like(self.elapsed)
        self.takeoff_time = torch.zeros_like(self.elapsed)
        self.takeoff_latency_s = torch.zeros_like(self.elapsed)
        self.takeoff_peak_vz = torch.zeros_like(self.elapsed)
        self.quality_sum = torch.zeros(count, 2, device=device)
        self.quality_time = torch.zeros_like(self.elapsed)
        self.quality_active = self.active.clone()
        self.failure_pulse = self.active.clone()
        self.failure_paid = self.active.clone()
        self.quality_paid = self.active.clone()

    def reset(self, ids: torch.Tensor) -> None:
        if self.air_guard is not None:
            self.deepest_intrusion[ids] = 0
            self.air_fold_cost[ids] = 0
            self.air_retract_cost[ids] = 0
            self.retraction.reset(ids)
        if self.band_width is not None:
            self.band_frames[ids] = 0
            self.band_scored_height[ids] = 0
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
            self.preparing,
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
            self.peak_wheel_clearance,
            self.start_body_clearance,
            self.peak_joint_clearance,
            self.peak_body_at_apex,
            self.peak_wheel_at_apex,
            self.peak_leg_angle_rad,
            self.apex_pose_quality,
            self.last_air_vz,
            self.first_touch_speed_pulse,
            self.height_progress,
            self.takeoff_time,
            self.takeoff_latency_s,
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
        body_clearance_m: torch.Tensor | None = None,
    ) -> None:
        start = ~self.active & (self.remaining > 0) & allowed
        if require_trigger_time:
            start &= age >= self.next_trigger
        ids = start.nonzero().flatten()
        if not len(ids):
            return
        if self.air_guard is not None:
            self.deepest_intrusion[ids] = 0
            self.retraction.reset(ids)
        if self.band_width is not None:
            self.band_frames[ids] = 0
            self.band_scored_height[ids] = 0
        if self.body_wheel is not None:
            if body_clearance_m is None:
                raise ValueError("body_wheel_jump requires chassis-bottom clearance at the press")
            self.start_body_clearance[ids] = body_clearance_m[ids]
            self.peak_joint_clearance[ids] = 0
            self.peak_body_at_apex[ids] = 0
            self.peak_wheel_at_apex[ids] = 0
            self.peak_leg_angle_rad[ids] = 0
            self.apex_pose_quality[ids] = 0
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
        self.preparing[ids] = False
        self.peak_wheel_clearance[ids] = 0
        self.last_air_vz[ids] = 0
        self.first_touch_speed_pulse[ids] = 0
        self.elapsed[ids] = 0
        self.air_time[ids] = 0
        self.stable_time[ids] = 0
        self.takeoff_time[ids] = 0
        self.takeoff_latency_s[ids] = 0
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
        body_clearance_m: torch.Tensor | None = None,
        leg_angle_rad: torch.Tensor | None = None,
        leg_length_m: torch.Tensor | None = None,
    ) -> None:
        self.apex_pulse.zero_()
        self.landing_pulse.zero_()
        self.touchdown_pulse.zero_()
        self.finished.zero_()
        self.failure_pulse.zero_()
        self.elapsed += dt * self.active
        no_contact = ~contact.any(-1)
        can_takeoff = self.active & ~self.landed
        if self.clearance_training is None:
            can_takeoff &= self.elapsed >= self.settings["crouch_duration_s"]
        clearance = torch.zeros_like(z) if wheel_clearance is None else wheel_clearance.amin(-1)
        candidate = can_takeoff & no_contact & (clearance >= self.settings.get("takeoff_clearance_m", 0.02))
        self.takeoff_time = torch.where(candidate, self.takeoff_time + dt, 0.0)
        self.takeoff_peak_vz = torch.where(candidate, torch.maximum(self.takeoff_peak_vz, vz), 0.0)
        self.apex_z = torch.where(~self.took_off & ~candidate, self.start_z, self.apex_z)
        confirmed = candidate & (self.takeoff_time >= self.settings.get("takeoff_confirmation_s", 0.03) - dt * 0.5)
        confirmed &= self.takeoff_peak_vz >= self.settings.get("takeoff_upward_velocity_m_s", 0.1)
        # The running apex is monotone within an attempt. Do not cash any of it in until takeoff is confirmed.
        old_height = torch.where(self.took_off, self.progress_height, 0.0)
        if self.clearance_training is not None:
            self.takeoff_latency_s.copy_(torch.where(confirmed & ~self.took_off, self.elapsed, self.takeoff_latency_s))
        new_flight = confirmed & ~self.took_off
        self.took_off |= confirmed
        flight = self.active & self.took_off & ~self.landed
        self.air_time += dt * flight * no_contact
        apex_sample = candidate | flight
        airborne = flight & no_contact & ~self.first_touch
        score_frame = airborne
        if self.air_guard is not None:
            if leg_length_m is None:
                raise ValueError("air_leg_guard requires both sagittal leg lengths")
            guard = self.air_guard
            squared = "entry_length_m" in guard
            boundary = guard["entry_length_m"] if squared else guard["sim_floor_m"] + guard["margin_m"]
            margin = guard["depth_scale_m"] if squared else guard["margin_m"]
            intrusion_m = (boundary - leg_length_m.amin(-1)).clamp_min(0)
            depth = torch.where(airborne, intrusion_m / margin, 0.0)
            # Unsafe frames cannot buy progress, apex quality, or a passing height.
            score_frame = airborne & (depth == 0)
            # Remain monotone beyond the nominal stop without making a bad jump vastly worse than no jump.
            inside = depth.clamp_max(1)
            severity = (inside.square() if squared else inside) + (1 - torch.exp(-(depth - 1).clamp_min(0))) / 6
            first_entry = (depth > 0) & (self.deepest_intrusion == 0)
            extra = (severity - self.deepest_intrusion).clamp_min(0)
            self.deepest_intrusion = torch.maximum(self.deepest_intrusion, severity)
            self.air_fold_cost = guard.get("entry_cost", 0.0) * first_entry + guard["depth_cost"] * extra + guard["hold_cost_per_s"] * severity * dt
        if self.clearance_training is not None:
            self.peak_wheel_clearance.copy_(
                torch.where(airborne, torch.maximum(self.peak_wheel_clearance, clearance), self.peak_wheel_clearance)
            )
            if self.body_wheel is not None:
                if wheel_clearance is None or body_clearance_m is None or leg_angle_rad is None:
                    raise ValueError("body_wheel_jump requires wheel and chassis clearance and both leg angles")
                self._record_joint_peak(score_frame, clearance, body_clearance_m, leg_angle_rad)
            apex_sample &= no_contact & ~self.first_touch
            prepare = airborne & (vz <= -self.clearance_training["tuck_end_vz_m_s"])
            if self.delay_extension:
                # Initialize on each liftoff, including second jumps. Wheel motion must not set the apex.
                self.flight_start_z = torch.where(new_flight, z, self.flight_start_z)
                peak = torch.where(new_flight, z, torch.maximum(self.flight_peak_z, z))
                self.flight_peak_z = torch.where(airborne, peak, self.flight_peak_z)
                rise = self.flight_peak_z - self.flight_start_z
                drop = rise * self.clearance_training["prepare_drop_fraction"]
                if "prepare_drop_min_m" in self.clearance_training:
                    drop = drop.clamp_min(self.clearance_training["prepare_drop_min_m"])
                else:  # Reproduce existing snapshots with a capped drop.
                    drop = drop.clamp(*self.clearance_training["prepare_drop_range_m"])
                prepare &= self.flight_peak_z - z >= drop - 1e-6
            self.preparing |= prepare
            if self.air_guard is not None:
                retract = self.retraction.update(leg_length_m, airborne & self.preparing)
                if self.retract_multipliers is not None:
                    tier = self.retraction.excursion_count.clamp(1, 3) - 1
                    retract = retract * self.retract_multipliers[tier]
                self.air_retract_cost = self.air_guard["retract_cost_per_m"] * retract.mean(-1)
                if self.retraction.base_threshold_m is not None:
                    self.air_retract_cost += self.air_guard["retract_base_cost"] * self.retraction.base_crossing.to(retract.dtype).mean(-1)
                if self.retract_fourth_cost:
                    fourth = self.retraction.fourth_excursion.to(retract.dtype)
                    self.air_retract_cost += self.retract_fourth_cost * fourth.mean(-1)
        self.apex_z = torch.where(apex_sample, torch.maximum(self.apex_z, z), self.apex_z)
        self.invalid |= self.active & obstacle_contact
        if failed is not None:
            self.invalid |= self.active & failed
        self.apex_pulse = flight & no_contact & (vz <= 0) & ~self.apex_paid & ~self.invalid
        self.apex_paid |= self.apex_pulse
        self.quality_active.copy_(flight & candidate & ~self.invalid)
        goal = self.height.clamp_min(torch.finfo(self.height.dtype).eps)
        previous = (old_height / goal).clamp(0, 1)
        current = (self.progress_height / goal).clamp(0, 1)
        progress_sample = self.quality_active if self.clearance_training is None else airborne & ~self.invalid
        self.height_progress.copy_(torch.where(progress_sample, (current - previous).clamp_min(0), 0.0))
        if self.body_wheel is not None:
            self.height_progress.mul_(self.apex_pose_quality)
        # Invalid first touchdown cannot become success by driving off the roof later.
        height_ok = jump_height_error(self.scored_height, self.height, self.settings) <= 1e-6
        if require_height is not None:
            height_ok |= ~require_height
        new_touch = flight & contact.any(-1) & ~self.first_touch
        if self.clearance_training is not None:
            # Use the last airborne sample; the solver may have already arrested vz on the contact step.
            self.first_touch_speed_pulse.copy_(torch.where(new_touch, (-self.last_air_vz).clamp_min(0), 0.0))
            self.last_air_vz.copy_(torch.where(airborne, vz, self.last_air_vz))
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
        if self.landing_settle_timeout_s is not None:
            # A confirmed takeoff ends the press deadline. Flight itself has no event timeout.
            missed_takeoff = ~self.took_off & (self.elapsed >= self.settings["event_duration_s"] - dt / 2)
            missed_landing = self.first_touch & (
                self.time_since_first_touch() >= self.landing_settle_timeout_s - dt / 2
            )
            expired = missed_takeoff | missed_landing
        else:
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

    def time_since_first_touch(self) -> torch.Tensor:
        first_touch_at = torch.where(self.touchdown_time >= 0, self.touchdown_time, self.elapsed[:, None]).amin(-1)
        return self.elapsed - first_touch_at

    def features(self) -> torch.Tensor:
        duration = self.settings["event_duration_s"]
        settle = self.landing_settle_timeout_s
        window = duration + (self.settings["landing_stable_s"] if settle is None else settle)
        elapsed = self.elapsed / window
        if settle is not None:
            # Reuse the critic's clock slot: takeoff timer, -1 for unbounded flight, then the settle timer.
            elapsed = torch.where(self.took_off, -1.0, self.elapsed / duration)
            elapsed = torch.where(self.first_touch, self.time_since_first_touch() / settle, elapsed)
        quality = self.quality_sum / self.quality_time.clamp_min(1e-6)[:, None]
        return torch.nan_to_num(
            torch.cat(
                (
                    elapsed[:, None],
                    (self.takeoff_time / self.settings.get("takeoff_confirmation_s", 0.03))[:, None],
                    (self.takeoff_peak_vz / self.settings.get("takeoff_upward_velocity_m_s", 0.1))[:, None],
                    self.took_off[:, None],
                    self.landed[:, None],
                    self.invalid[:, None],
                    (self.scored_height / self.height.clamp_min(0.01))[:, None],
                    (self.stable_time / self.settings["landing_stable_s"])[:, None],
                    (self.air_time / window)[:, None],
                    (self.apex_paid.float() if self.clearance_training is None else self.preparing.float())[:, None],
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

    @property
    def suppress_stand_walk(self) -> torch.Tensor:
        # update() clears active on a failed landing/takeoff before rewards are computed.
        pressed = self.active | (self.finished & (self.elapsed > 0))
        return pressed if self.band_width is not None else pressed & ~self.first_touch

    @property
    def scored_height(self) -> torch.Tensor:
        if self.band_width is not None:
            return self.band_scored_height
        return self.progress_height

    @property
    def progress_height(self) -> torch.Tensor:
        if self.body_wheel is not None:
            return self.peak_joint_clearance
        if self.clearance_training is not None:
            return self.peak_wheel_clearance
        return self.apex_z - self.start_z

    def _record_joint_peak(self, airborne, wheels_m, body_m, leg_angle_rad):
        cfg = self.body_wheel
        rise = body_m - self.start_body_clearance
        joint = torch.minimum(wheels_m, torch.minimum(body_m - cfg["body_margin_m"], rise / cfg["body_rise_fraction"]))
        angle = leg_angle_rad.abs().amax(-1)
        if self.band_width is not None:
            self._record_apex_band(airborne, joint, body_m, wheels_m, angle)
            return
        # If a peak is held, allow a better pose there, never a better pose at a lower height.
        better = (joint > self.peak_joint_clearance) | (
            (joint == self.peak_joint_clearance) & (angle < self.peak_leg_angle_rad)
        )
        record = airborne & better & (joint > 0)
        quality = torch.exp(-((angle - cfg["leg_deadband_rad"]).clamp_min(0) / cfg["leg_pose_scale_rad"]).square())
        for dest, value in (
            (self.peak_joint_clearance, joint),
            (self.peak_body_at_apex, body_m),
            (self.peak_wheel_at_apex, wheels_m),
            (self.peak_leg_angle_rad, angle),
            (self.apex_pose_quality, quality),
        ):
            dest.copy_(torch.where(record, value, dest))

    def _record_apex_band(self, airborne, joint, body, wheel, angle):
        slots = self.band_frames.shape[1]
        step = self.band_width / slots
        self.peak_joint_clearance.copy_(
            torch.where(airborne, torch.maximum(joint, self.peak_joint_clearance), self.peak_joint_clearance)
        )
        top = torch.floor(self.peak_joint_clearance / step)
        bucket = torch.floor(joint / step)
        col = bucket.long().remainder(slots)
        old = self.band_frames[self.band_rows, col]
        threshold = self.height - self.settings["height_tolerance_m"] - 1e-6
        # Never combine a below-target upright pose with another frame's passing height.
        ok, old_ok = joint >= threshold, old[:, 0] >= threshold
        better = (ok & ~old_ok) | (
            (ok == old_ok) & ((angle < old[:, 3]) | ((angle == old[:, 3]) & (joint > old[:, 0])))
        )
        replace = (
            airborne
            & (joint > 0)
            & (bucket > top - slots)
            & ((old[:, 0] == 0) | (torch.floor(old[:, 0] / step) != bucket) | better)
        )
        self.band_frames[self.band_rows, col] = torch.where(
            replace[:, None], torch.stack((joint, body, wheel, angle), -1), old
        )
        heights, angles = self.band_frames[..., 0], self.band_frames[..., 3]
        valid = (heights > 0) & (torch.floor(heights / step) > top[:, None] - slots)
        passing = valid & (heights >= threshold[:, None])
        eligible = valid & (~passing.any(-1)[:, None] | passing)
        best_angle = angles.masked_fill(~eligible, torch.inf).amin(-1, keepdim=True)
        index = heights.masked_fill(~(eligible & (angles == best_angle)), -torch.inf).argmax(-1)
        best = self.band_frames[self.band_rows, index]
        self.band_scored_height.copy_(best[:, 0])
        self.peak_body_at_apex.copy_(best[:, 1])
        self.peak_wheel_at_apex.copy_(best[:, 2])
        self.peak_leg_angle_rad.copy_(best[:, 3])
        cfg = self.body_wheel
        self.apex_pose_quality.copy_(
            torch.exp(-((best[:, 3] - cfg["leg_deadband_rad"]).clamp_min(0) / cfg["leg_pose_scale_rad"]).square())
            * valid.any(-1)
        )

    @property
    def apex_pose_ok(self) -> torch.Tensor:
        return (self.peak_joint_clearance > 0) & (self.peak_leg_angle_rad <= self.body_wheel["max_leg_angle_rad"])

    @property
    def target_reached(self) -> torch.Tensor:
        height_ok = jump_height_error(self.scored_height, self.height, self.settings) <= 1e-6
        return height_ok if self.body_wheel is None else height_ok & self.apex_pose_ok

    def _near_touchdown(self, vz: torch.Tensor, clearance: torch.Tensor, gravity: float) -> torch.Tensor:
        time_to_ground = (vz + torch.sqrt(vz.square() + 2 * gravity * clearance.clamp_min(0))) / gravity
        return (vz < 0) & (time_to_ground < self.settings["landing_prepare_time_s"])

    def references(self, vz: torch.Tensor, wheel_clearance: torch.Tensor, gravity: float) -> dict[str, torch.Tensor]:
        flight = self.active & self.took_off & ~self.landed
        before_takeoff = self.active & ~self.took_off
        if self.clearance_training is None:
            crouch = before_takeoff & (self.elapsed < self.settings["crouch_duration_s"])
            push = before_takeoff & ~crouch
            prepare = flight & self._near_touchdown(vz, wheel_clearance, gravity)
            tuck = flight & ~prepare
            takeoff_velocity = torch.sqrt(2 * gravity * self.height)
        else:
            # Start supported upward-motion guidance at the press, with no minimum preload time.
            crouch = torch.zeros_like(before_takeoff)
            push = before_takeoff
            flight &= ~self.first_touch
            prepare = flight & self.preparing
            tuck = flight & ~self.preparing
            takeoff_velocity = torch.full_like(self.height, self.clearance_training["takeoff_velocity_hint_m_s"])
        return {
            "crouch": crouch,
            "push": push,
            "flight": flight,
            "prepare": prepare,
            "tuck": tuck,
            "takeoff_velocity": takeoff_velocity,
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
