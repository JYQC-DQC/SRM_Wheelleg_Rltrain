"""Exogenous SHU P1 events. All tensors here are simulator-side, not actor observations.

One reset per actual birth; begin_step, five fresh physics samples, then one update per policy step.
Use reward_phase for this step's continuous terms, phase for the next action. Never clear history on handoff.
"""

import math
from collections.abc import Mapping, Sequence

import torch

from wheelleg.safety import leaky_termination
from wheelleg.shu_impact import ShuImpact
from wheelleg.shu_rewards import AIR, CATCH, DRIVE, RELEASE, RISE

_TILT = math.radians(10)


class ShuLanding:
    def __init__(
        self,
        count: int,
        wheels: Sequence[int],
        guides: Sequence[int],
        links: Sequence[int],
        undesired: Sequence[int],
        termination: Sequence[int],
        body_count: int,
        settings: Mapping[str, float],
        device: str,
        physics_dt: float = 0.002,
        dt: float = 0.01,
    ):
        """Body IDs are contact-sensor indices, wheels in L/R order; guide_vz_w must follow guides order.

        Required model/settings keys: contact_force_n, wheel_contact_force_n, support_force_n,
        termination_force_n, termination_tilt_rad, termination_duration_s, termination_decay_s,
        release_s. Decay is time to drain a *full* physical termination counter.
        """
        wheels, guides, links = list(wheels), list(guides), list(links)
        wheel, guide, link = set(wheels), set(guides), set(links)
        bad, terminal, bodies = set(undesired), set(termination), set(range(body_count))
        if (
            len(wheels) != 2
            or len(wheel) != 2
            or len(guide) != len(guides)
            or len(link) != len(links)
            or wheel & (bad | terminal | guide | link)
            or guide & link
            or not (guide | link) <= bad
            or not (wheel | terminal | bad) <= bodies
        ):
            raise ValueError("invalid contact body lists: check sensor order, two main wheels and leg/guide membership")
        self.wheels, self.guides = wheels, guides
        self._nonwheel = sorted(bodies - wheel)
        self._hard = sorted(bodies - wheel - guide)
        self._allowed = sorted(guide | link)
        self._other_bad = sorted(bad - guide - link)
        self._terminal = sorted(terminal)
        self._rise_terminal = sorted(terminal - guide - link)
        self.p, self.physics_dt, self.dt = settings, physics_dt, dt
        self._substeps = round(dt / physics_dt)
        self._hold_steps = round(0.5 / dt)
        self._air_limit = round(2.0 / physics_dt)
        self._rise_limit = round(5.0 / physics_dt)
        self._release_ticks = math.ceil(settings["release_s"] / physics_dt - 1e-9)
        self._reset_buffers = []

        def buf(dtype=torch.float32, width=None, fill=0):
            x = torch.full((count,) if width is None else (count, width), fill, dtype=dtype, device=device)
            self._reset_buffers.append((x, fill))
            return x

        b, i = torch.bool, torch.long
        self.phase, self.reward_phase = buf(i), buf(i)
        self.air_birth, self.preset_birth, self.active = buf(b), buf(b), buf(b)
        self.born, self.last_tick, self.touch_tick, self.takeover_tick = (
            buf(i),
            buf(i),
            buf(i, fill=-1),
            buf(i, fill=-1),
        )
        self.invalid_birth, self.unknown_guide, self.hard_guide, self.body_collision = (buf(b) for _ in range(4))
        self.touched_bodies, self.first_bodies, self.first_nonwheel_bodies = (buf(b, body_count) for _ in range(3))
        self.clean = buf(b, fill=True)
        self.impact = ShuImpact(count, device)
        self.guide_peak_speed_m_s = buf(fill=torch.nan)
        self._previous_vz = buf(width=len(guides), fill=torch.nan)
        self._previous_guide = buf(b, len(guides))
        self._wheel_now, self._wheel_previous, self.wheel_contact = (buf(b, 2) for _ in range(3))
        self._support, self._rise_support, self._terminal_hit, self._rise_terminal_hit = (buf(b) for _ in range(4))
        self.leg_or_guide_contact, self.other_undesired_contact, self._bad_sample = (buf(b) for _ in range(3))
        self._samples, self.held_steps = buf(i), buf(i)
        self.fall_steps, self.best, self._angle_sum = buf(), buf(), buf()
        self.confirm_mean_rad, self.catch_time_s = buf(fill=torch.nan), buf(fill=torch.nan)
        self._takeover_xy = buf(width=2)
        self.rise_max_drift_m = buf()
        self.rise_time_s = buf(fill=torch.nan)
        self.resolved, self.succeeded, self.air_timeout, self.handoff, self.truncated, self.ended = (
            buf(b) for _ in range(6)
        )
        self.rise_succeeded, self.rise_failed, self.rise_timeout = (buf(b) for _ in range(3))
        self.physical_failure, self.numerical_failure = buf(b), buf(b)
        self.event_terms = {
            k: buf() for k in ("landing_progress", "landing_outcome", "landing_guide_contact", "rise_progress")
        }

    def reset(self, ids, air, preset, tick: int, birth_contact=None) -> None:
        """air/preset: mutually exclusive bool (len(ids),). Optional birth_contact is measured *at reset*.

        A collision after release, even in the first 2 ms, is not evidence of an invalid birth.
        Never feed stale pre-reset sensor readings as birth_contact.
        """
        for x, fill in self._reset_buffers:
            x[ids] = fill
        self.impact.reset(ids)
        self.air_birth[ids], self.preset_birth[ids] = air, preset
        self.born[ids] = self.last_tick[ids] = tick
        self.phase[ids] = torch.where(air, AIR, torch.where(preset, RELEASE, DRIVE))
        self.reward_phase[ids] = self.phase[ids]
        self.active[ids] = air | preset
        if birth_contact is not None:
            self.invalid_birth[ids] = air & birth_contact

    def begin_step(self) -> None:
        self._support.fill_(True)
        self._rise_support.zero_()
        for x in (
            self._wheel_now,
            self._samples,
            self._bad_sample,
            self.leg_or_guide_contact,
            self.other_undesired_contact,
            self._terminal_hit,
            self._rise_terminal_hit,
            self.event_terms["landing_guide_contact"],
        ):
            x.zero_()

    def sample(
        self,
        tick: int,
        forces_w,
        guide_vz_w,
        leg_length_m,
        leg_angle_rad=None,
        *,
        spring_compression_m=None,
        fresh_mask=None,
    ) -> None:
        """Fresh forces (N,B,3) in N, signed guide world vz (N,G) in m/s, L/R lengths (N,2) in m.

        Same tick can be seen at the action/done hook boundary. Do not integrate or advance history twice.
        """
        fresh = tick > self.last_tick
        if fresh_mask is not None:
            fresh &= fresh_mask
        finite = torch.isfinite(forces_w).all(dim=(1, 2)) & torch.isfinite(leg_length_m).all(-1)
        guide_finite = torch.isfinite(guide_vz_w).all(-1)
        self._bad_sample |= fresh & ~(finite & guide_finite)
        use = fresh & finite
        norm = torch.linalg.vector_norm(forces_w, dim=-1)
        contact = norm > self.p["contact_force_n"]
        nonwheel = contact[:, self._nonwheel].any(-1)
        allowed = contact[:, self._allowed].any(-1)
        fz = forces_w[:, self.wheels, 2].clamp_min(0)
        wheel = fz > self.p["wheel_contact_force_n"]
        # A wheel may touch and rebound inside one 10 ms policy interval. Never use this OR for confirmation.
        self._wheel_now |= use[:, None] & wheel
        self._samples += fresh
        self._support &= ~fresh | (finite & (fz > self.p["support_force_n"]).all(-1) & ~nonwheel)
        self._rise_support.copy_(torch.where(fresh, finite & (wheel.any(-1) | allowed), self._rise_support))
        self.leg_or_guide_contact |= use & allowed
        self.other_undesired_contact |= use & contact[:, self._other_bad].any(-1)
        terminal = norm > self.p["termination_force_n"]
        self._terminal_hit |= use & terminal[:, self._terminal].any(-1)
        self._rise_terminal_hit |= use & terminal[:, self._rise_terminal].any(-1)

        # First touch switches phase even if the impact resolves the event. A bounce cannot reopen it.
        first = use & (self.phase == AIR) & contact.any(-1)
        self.touch_tick.masked_fill_(first, tick)
        self.phase.masked_fill_(first, CATCH)
        observe = (
            use
            & self.active
            & self.air_birth
            & ~(self.body_collision | self.hard_guide | self.unknown_guide | self.invalid_birth)
        )
        first_nonwheel = observe & nonwheel & self.clean
        self.touched_bodies |= observe[:, None] & contact
        self.first_bodies |= (first & observe)[:, None] & contact
        self.first_nonwheel_bodies[:, self._nonwheel] |= first_nonwheel[:, None] & contact[:, self._nonwheel]
        self.clean &= ~(observe & nonwheel)
        self.impact.sample(
            tick,
            self.physics_dt,
            observe,
            first & observe,
            self.last_tick == tick - 1,
            observe & (self.touch_tick >= 0),
            fz,
            wheel,
            leg_length_m,
            leg_angle_rad,
            spring_compression_m,
        )
        self.body_collision |= observe & contact[:, self._hard].any(-1)
        if self.guides:
            now = contact[:, self.guides]
            new = observe[:, None] & now & ~self._previous_guide
            known = self._previous_vz.isfinite() & (self.last_tick == tick - 1)[:, None]
            self.unknown_guide |= (new & ~known).any(-1)
            down = torch.where(new & known, (-self._previous_vz).clamp_min(0), 0.0).amax(-1)
            hit = (new & known).any(-1)
            self.guide_peak_speed_m_s.copy_(
                torch.where(hit, torch.fmax(self.guide_peak_speed_m_s, down), self.guide_peak_speed_m_s)
            )
            self.hard_guide |= hit & (down >= 1.5)
            brush = hit & ~(self.body_collision | self.hard_guide | self.unknown_guide)
            self.event_terms["landing_guide_contact"] -= torch.where(brush, 0.7 * down / 1.5, 0.0)
            self._previous_guide.copy_(torch.where(fresh[:, None], now, self._previous_guide))
            self._previous_vz.copy_(torch.where(fresh[:, None], guide_vz_w, self._previous_vz))
        self.last_tick.masked_fill_(fresh, tick)

    def update(self, tick: int, state: Mapping[str, torch.Tensor], physical, timeout, numerical) -> None:
        """One policy interval. Physical is independent protection, not the ordinary contact counter.

        roll/pitch in radians, angular_velocity in body rad/s, velocity_w in world m/s, height_error is
        measured height minus the fixed rise target (m), position_xy_w is root world XY (m).
        Read terminal masks and event_terms before reset. rise_timeout is not an external timeout.
        """
        tilt = torch.maximum(state["roll"].abs(), state["pitch"].abs())
        omega = state["angular_velocity"][:, :2].abs().amax(-1)
        vz = state["velocity_w"][:, 2].abs()
        height = state["height_error"].abs()
        xy = state["position_xy_w"]
        finite = (
            torch.stack((tilt, height), -1).isfinite().all(-1)
            & xy.isfinite().all(-1)
            & state["angular_velocity"].isfinite().all(-1)
            & state["velocity_w"].isfinite().all(-1)
        )
        self.numerical_failure.copy_(numerical | self._bad_sample | ~finite)
        self.wheel_contact.copy_(self._wheel_now | self._wheel_previous)
        self._wheel_previous.copy_(self._wheel_now)
        release, rise, catch = (self.phase == x for x in (RELEASE, RISE, CATCH))
        risk = (tilt > self.p["termination_tilt_rad"]) | torch.where(rise, self._rise_terminal_hit, self._terminal_hit)
        # Same slow leak for ordinary physics in all controlled phases, not the same exemption list.
        steps, sustained = leaky_termination(
            self.fall_steps, risk & ~release, self.dt, self.p["termination_duration_s"], self.p["termination_decay_s"]
        )
        self.fall_steps.copy_(torch.where(release, 0.0, steps))
        self.physical_failure.copy_((physical | sustained) & ~self.numerical_failure)
        broken = self.numerical_failure | self.invalid_birth
        stop = broken | self.physical_failure | timeout
        takeover = release & self.active & (tick - self.born >= self._release_ticks) & ~stop
        self.takeover_tick.masked_fill_(takeover, tick)
        self._takeover_xy.copy_(torch.where(takeover[:, None], xy, self._takeover_xy))
        drift = torch.linalg.vector_norm(xy - self._takeover_xy, dim=-1)
        self.rise_max_drift_m.copy_(
            torch.where(
                rise & self.active & ~broken, torch.maximum(self.rise_max_drift_m, drift), self.rise_max_drift_m
            )
        )
        self.reward_phase.copy_(self.phase)  # the last release interval really was at zero torque
        self.phase.masked_fill_(takeover, RISE)
        since_touch = tick - self.touch_tick
        since_control = tick - self.takeover_tick
        # OR contact is for wheel-off diagnostics only. Require actual Fz throughout this policy interval.
        support = self._support & (self._samples == self._substeps)
        stable = support & (tilt <= _TILT) & (omega <= 0.5) & (vz <= 0.2) & ~(broken | self.physical_failure)
        stable &= (catch & (since_touch >= self._substeps)) | (rise & (height <= 0.05))
        self.held_steps.copy_(torch.where(stable, self.held_steps + 1, 0))
        self._angle_sum.copy_(torch.where(stable, self._angle_sum + tilt, 0.0))
        confirmed = stable & (self.held_steps >= self._hold_steps)
        air = self.air_birth & self.active
        hard = self.body_collision | self.hard_guide
        # A timeout cannot censor a known physical loss. Unknown guide speed is not a measured hard impact.
        # External cuts censor a timely confirmation, not the physical evidence from that interval.
        # Otherwise reaching a deadline on the very same tick would turn a censored success into a loss.
        air_on_time = confirmed & (since_touch <= self._air_limit)
        rise_on_time = confirmed & (since_control <= self._rise_limit)
        self.succeeded.copy_(air & catch & air_on_time & ~hard & ~self.unknown_guide & ~timeout)
        expired = catch & (since_touch >= self._air_limit)
        self.air_timeout.copy_(
            air & expired & ~air_on_time & ~(hard | self.physical_failure | broken | self.unknown_guide)
        )
        failed = air & ~broken & (hard | self.physical_failure | self.air_timeout)
        self.resolved.copy_(self.succeeded | failed)
        self.rise_succeeded.copy_(rise & self.active & rise_on_time & ~timeout)
        self.rise_timeout.copy_(
            rise & self.active & (since_control >= self._rise_limit) & ~(rise_on_time | self.physical_failure | broken)
        )
        self.rise_failed.copy_(self.rise_timeout | (self.preset_birth & self.active & self.physical_failure & ~broken))
        self.rise_time_s.copy_(
            torch.where(
                rise & (self.rise_succeeded | self.rise_failed), since_control * self.physics_dt, self.rise_time_s
            )
        )
        # Late stabilization still returns control, but can never reopen the resolved event.
        self.handoff.copy_(
            (catch & confirmed & ~timeout & (~air | self.succeeded | self.air_timeout)) | self.rise_succeeded
        )
        self.phase.masked_fill_(self.handoff, DRIVE)
        self.reward_phase.masked_fill_(self.handoff, DRIVE)

        height_q = torch.exp(-height.square() / 0.025)  # unannealed wide kernel, not an extra height reward
        self.best.copy_(torch.where(takeover, height_q, self.best))
        air_q = torch.exp(-((tilt / _TILT).square() + (omega / 0.5).square() + (vz / 0.2).square()) / 3.0)
        can_pay = self.active & ~(stop | hard | self.unknown_guide | self.air_timeout | self.rise_timeout)
        air_gain = torch.where(can_pay & catch & support, (air_q - self.best).clamp_min(0.0), 0.0)
        rise_gain = torch.where(
            can_pay & rise & self._rise_support & (self.last_tick == tick), (height_q - self.best).clamp_min(0.0), 0.0
        )
        self.event_terms["landing_progress"].copy_(0.75 * air_gain)
        self.event_terms["rise_progress"].copy_(0.75 * rise_gain)
        self.best += air_gain + rise_gain
        angle = self._angle_sum / self.held_steps.clamp_min(1)
        elapsed = since_touch * self.physics_dt
        self.catch_time_s.copy_(torch.where(self.succeeded, elapsed, self.catch_time_s))
        self.confirm_mean_rad.copy_(torch.where(self.succeeded, angle, self.confirm_mean_rad))
        result = 1.5 * (0.7 * torch.exp(-(elapsed - 0.5).clamp_min(0)) + 0.3 * (1.0 - angle / _TILT).clamp(0, 1))
        self.event_terms["landing_outcome"].copy_(torch.where(self.succeeded, result, -failed.float()))
        self.event_terms["landing_guide_contact"].masked_fill_(stop | self.unknown_guide | hard | self.air_timeout, 0.0)
        self.truncated.copy_(self.active & timeout & ~(self.resolved | self.rise_failed | broken | self.unknown_guide))
        self.ended.copy_(
            self.active & (self.resolved | self.rise_succeeded | self.rise_failed | stop | self.unknown_guide)
        )
        self.active &= ~self.ended

    def metrics(self) -> dict[str, torch.Tensor]:
        """Device tensors, not scalar log averages. Aggregate on `resolved` BEFORE reset, not on every step.

        Sum clean_count/resolved_count over the logging window before dividing; clean_rate is this batch only.
        For wheel channels require wheel_touched[:,side] and a finite measurement. First-patch peak/impulse
        are NaN if a sample is missing in that patch; event_peak_n is the maximum actually observed.
        """
        resolved_count = self.resolved.count_nonzero()
        clean_count = (self.clean & self.resolved).count_nonzero()
        return {
            "resolved_count": resolved_count,
            "success_count": self.succeeded.count_nonzero(),
            "clean_count": clean_count,
            "clean_rate": torch.where(resolved_count > 0, clean_count / resolved_count.clamp_min(1), torch.nan),
            "ended": self.ended,
            "resolved": self.resolved,
            "succeeded": self.succeeded,
            "clean": self.clean,
            "truncated": self.truncated,
            "numerical_failure": self.numerical_failure,
            "invalid_birth": self.invalid_birth,
            "unknown_guide": self.unknown_guide,
            "hard_guide": self.hard_guide,
            "body_collision": self.body_collision,
            "guide_peak_speed_m_s": self.guide_peak_speed_m_s,
            "air_timeout": self.air_timeout,
            "physical_failure": self.physical_failure,
            "rise_succeeded": self.rise_succeeded,
            "rise_failed": self.rise_failed,
            "rise_timeout": self.rise_timeout,
            "rise_max_drift_m": self.rise_max_drift_m,
            "first_contact_s": torch.where(
                self.touch_tick >= 0, (self.touch_tick - self.born) * self.physics_dt, torch.nan
            ),
            "rise_time_s": self.rise_time_s,
            "touch_tick": self.touch_tick,
            "catch_time_s": self.catch_time_s,
            "confirm_mean_rad": self.confirm_mean_rad,
            "first_bodies": self.first_bodies,
            "first_nonwheel_bodies": self.first_nonwheel_bodies,
            "touched_bodies": self.touched_bodies,
            "wheel_touched": self.impact.first_tick >= 0,
            "wheel_first_tick": self.impact.first_tick,
            "first_touch_gap_s": self.impact.first_touch_gap_s(self.physics_dt),
            "first_peak_n": self.impact.first_peak_n,
            "first_impulse_ns": self.impact.first_impulse_ns,
            "event_peak_n": self.impact.event_peak_n,
            "leg_compression_m": self.impact.compression_m,
            "touch_leg_length_m": self.impact.touch_leg_length_m,
            "touch_leg_angle_rad": self.impact.touch_leg_angle_rad,
            "spring_peak_compression_m": self.impact.spring_peak_compression_m,
            "spring_compression_stroke_m": self.impact.spring_compression_stroke_m,
        }
