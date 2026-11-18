"""SHU P1 commands. All motion clocks count executed 100 Hz policy intervals, not physics substeps."""

from collections.abc import Callable
from copy import deepcopy
from math import ceil, floor, isfinite, pi

import torch

from .shu_curriculum import BRAKE_REVERSE, COMBINED, DASH, N_KINDS, STRAIGHT, TURN, FlatCommandCurriculum

Criterion = Callable[[torch.Tensor, torch.Tensor, torch.Tensor], torch.Tensor]
_DT = 0.01


class ShuCommands:
    """One driver for flat or landing. ``prepare`` -> physics -> ``finish`` once per policy tick.

    Keep settings equal across transfer. Six buckets are the requested motion profiles; braking
    still has zero-translation semantics. From rest, a brake/reverse request first draws a real straight lead-in;
    never score a fictitious brake.
    ``value`` is the ACTUALLY issued [vx, 0, wz], including heading replacement and birth restrictions.
    All yaw/phase/age arguments have shape (N,); age_steps=0 on the first interval after birth.
    """

    def __init__(
        self,
        settings: dict,
        count: int,
        device: str,
        *,
        flat: FlatCommandCurriculum | None = None,
        landing_metadata: dict | None = None,
        _fixed_mixed: bool = False,
        _route_settings: dict | None = None,
    ):
        if sum((flat is not None, landing_metadata is not None, _fixed_mixed)) != 1:
            raise ValueError("pass either flat curriculum or landing_metadata from a fully open p1-flat run")
        self.settings = {}
        for key in (
            "segment_probabilities",
            "segment_duration_s",
            "height_duration_s",
            "vx_range_m_s",
            "wz_range_rad_s",
            "dash_speed_abs_m_s",
            "height_range_m",
            "combined_wz_limit_rad_s",
            "linear_slew_m_s2",
            "angular_slew_rad_s2",
            "heading_kp",
            "heading_max_wz",
        ):
            v = settings[key]
            self.settings[key] = list(v) if isinstance(v, (list, tuple)) else v
        p = self.settings
        for key in (
            "vx_range_m_s",
            "wz_range_rad_s",
            "dash_speed_abs_m_s",
            "height_range_m",
            "segment_duration_s",
            "height_duration_s",
        ):
            lo, hi = p[key]
            if not (isfinite(lo) and isfinite(hi) and lo <= hi):
                raise ValueError(f"invalid {key} interval")
        if p["dash_speed_abs_m_s"][0] <= 0:
            raise ValueError("dash_speed_abs_m_s requires positive magnitudes")
        for key in ("segment_duration_s", "height_duration_s"):
            lo, hi = self._ticks(key)
            if lo <= 0 or lo > hi:
                raise ValueError(f"{key} must admit at least one positive 100 Hz duration")
        for key in (
            "combined_wz_limit_rad_s",
            "linear_slew_m_s2",
            "angular_slew_rad_s2",
            "heading_kp",
            "heading_max_wz",
        ):
            if not isfinite(p[key]) or p[key] <= 0:
                raise ValueError(f"{key} must be positive and finite")
        self.flat = flat
        if landing_metadata is not None:
            m = landing_metadata
            if not (
                m.get("stage") == "p1-flat"
                and m.get("all_full") is True
                and m.get("fractions") == [1.0] * N_KINDS
                and m.get("commands") == p
            ):
                raise ValueError("landing requires full p1-flat fractions and the same final command settings")
        self.value = torch.zeros(count, 3, device=device)
        self.prob = self.value.new_tensor(p["segment_probabilities"])
        if (
            self.prob.shape != (N_KINDS,)
            or not (torch.isfinite(self.prob) & (self.prob >= 0)).all()
            or self.prob.sum() <= 0
        ):
            raise ValueError("segment_probabilities must have six nonnegative finite weights with positive sum")
        if self.prob[BRAKE_REVERSE] > 0 and not (p["vx_range_m_s"][0] < 0 < p["vx_range_m_s"][1]):
            raise ValueError("brake/reverse needs bidirectional vx_range_m_s for an executable lead-in and reversal")
        self.target = torch.zeros_like(self.value)
        self.height = self.value.new_zeros(count, 1)
        self.height_target = torch.zeros_like(self.height)
        self.height_rate = self.value.new_zeros(count)
        self.kind = torch.zeros(count, device=device, dtype=torch.long)
        self.remaining = torch.zeros_like(self.kind)
        self.height_remaining = torch.zeros_like(self.kind)
        self.steps = torch.zeros_like(self.kind)
        self.fraction = torch.ones_like(self.height_rate)
        self.reference_yaw = torch.zeros_like(self.height_rate)
        self.vx_active = torch.zeros_like(self.kind, dtype=torch.bool)
        self.wz_active = self.vx_active.clone()
        self.heading_active = self.vx_active.clone()
        self.route = self.vx_active.clone()
        self._route_open = self.vx_active.clone()
        self._route_settings = _route_settings
        self._driving = self.vx_active.clone()
        self._recovering = self.vx_active.clone()
        self._air_limit = self.vx_active.clone()
        self._first_interval = self.vx_active.clone()
        self._brake_pending = self.vx_active.clone()
        self._whole_drive = self.vx_active.clone()
        self._height_held = self.vx_active.clone()
        self._issued = torch.zeros_like(self.value)
        self._error_sum = torch.zeros_like(self.value)
        self._magnitude_sum = torch.zeros_like(self.value)
        self._previous = torch.zeros_like(self.value)
        self._rates = self.value.new_tensor([p["linear_slew_m_s2"], 0.0, p["angular_slew_rad_s2"]]) * _DT

    @classmethod
    def for_mixed(cls, settings: dict, count: int, device: str, *, route: dict | None = None) -> "ShuCommands":
        """Fixed full-range free driver, plus independent route settings for route-labelled episodes."""
        return cls(settings, count, device, _fixed_mixed=True, _route_settings=route)

    @property
    def zero_translation(self) -> torch.Tensor:
        return ~self.vx_active

    def transfer_metadata(self) -> dict:
        """Portable checkpoint proof; never infer all_full from PPO iteration or the loaded network."""
        if self.flat is None:
            raise ValueError("only p1-flat can supply landing transfer metadata")
        fractions = self.flat.fraction.tolist()
        return dict(
            stage="p1-flat",
            all_full=all(f == 1 for f in fractions),
            fractions=fractions,
            commands=deepcopy(self.settings),
        )

    def _ticks(self, key: str) -> tuple[int, int]:
        lo, hi = self.settings[key]
        return ceil(lo * 100 - 1e-9), floor(hi * 100 + 1e-9)

    def _duration(self, ids: torch.Tensor, key: str) -> torch.Tensor:
        lo, hi = self._ticks(key)
        return torch.randint(lo, hi + 1, (len(ids),), device=ids.device)

    def _uniform(self, ids: torch.Tensor, key: str) -> torch.Tensor:
        lo, hi = self.settings[key]
        return lo + (hi - lo) * torch.rand(len(ids), device=ids.device)

    def _motion(self, ids: torch.Tensor) -> None:
        if not ids.numel():
            return
        if self._route_settings is not None:
            route_ids = ids[self.route[ids]]
            if route_ids.numel():
                lo, hi = self._route_settings["vx_range_m_s"]
                self.target[route_ids] = 0
                self.target[route_ids, 0] = lo + (hi - lo) * torch.rand(len(route_ids), device=ids.device)
                self.kind[route_ids] = STRAIGHT
                self.remaining[route_ids] = self._duration(route_ids, "segment_duration_s")
                self.steps[route_ids] = 0
                self._brake_pending[route_ids] = False
            ids = ids[~self.route[ids]]
            if not ids.numel():
                return
        k = torch.multinomial(self.prob, len(ids), replacement=True)
        incoming = self.value[ids, 0]
        # A transition needs an actual incoming velocity. Preserve the requested brake until the
        # lead-in has really executed, rather than relabeling zero-to-zero as a successful brake.
        k = torch.where(self._brake_pending[ids], BRAKE_REVERSE, k)
        needs_lead = (k == BRAKE_REVERSE) & (incoming == 0)
        self._brake_pending[ids] = needs_lead
        k = torch.where(needs_lead, STRAIGHT, k)
        self.kind[ids] = k
        f = self.flat.fraction[k] if self.flat is not None else torch.ones_like(incoming)
        self.fraction[ids] = f
        self.remaining[ids] = self._duration(ids, "segment_duration_s")
        self.steps[ids] = 0
        self._magnitude_sum[ids] = self._error_sum[ids] = 0
        self._whole_drive[ids] = True
        self.target[ids] = 0
        vx = self._uniform(ids, "vx_range_m_s") * f
        magnitude = self._uniform(ids, "dash_speed_abs_m_s") * f
        dash = torch.where(torch.rand_like(magnitude) < 0.5, magnitude, -magnitude)
        vx_lo, vx_hi = self.settings["vx_range_m_s"]
        reverse = (-incoming).clamp(vx_lo * f, vx_hi * f)
        reverse = torch.where(torch.rand_like(reverse) < 0.5, reverse, 0.0)
        self.target[ids, 0] = torch.where(
            k == DASH,
            dash,
            torch.where(k == BRAKE_REVERSE, reverse, torch.where((k == STRAIGHT) | (k == COMBINED), vx, 0.0)),
        )
        wz = self._uniform(ids, "wz_range_rad_s") * f
        limit = max(abs(v) for v in self.settings["wz_range_rad_s"]) * f
        scale = (self.settings["combined_wz_limit_rad_s"] / limit.clamp_min(torch.finfo(f.dtype).tiny)).clamp_max(1.0)
        self.target[ids, 2] = torch.where(k == TURN, wz, torch.where(k == COMBINED, wz * scale, 0.0))

    def _heights(self, ids: torch.Tensor) -> None:
        lo, hi = self.settings["height_range_m"]
        mid = (lo + hi) / 2
        self.height_target[ids, 0] = mid + self.fraction[ids] * (self._uniform(ids, "height_range_m") - mid)
        self.height_remaining[ids] = self._duration(ids, "height_duration_s")

    def reset(self, ids: torch.Tensor, *, route: torch.Tensor | None = None) -> None:
        """True resets only. Route labels are set before the first motion sample."""
        if route is not None:
            if self._route_settings is None:
                raise ValueError("Route-labelled resets require mixed terrain route settings")
            self.route[ids] = self._route_open[ids] = route
        self.value[ids] = 0
        self._brake_pending[ids] = False
        self._first_interval[ids] = True
        self._driving[ids] = self.heading_active[ids] = self.vx_active[ids] = self.wz_active[ids] = False
        self._motion(ids)
        self._heights(ids)
        self.height[ids] = self.height_target[ids]
        self.height_rate[ids] = self.reference_yaw[ids] = 0

    def _issue(self, ids: torch.Tensor, yaw: torch.Tensor, latch: torch.Tensor) -> None:
        # yaw/latch here are local to ids. A subset reissue at handoff consumes NO extra slew step.
        k = self.kind[ids]
        moving = (k == STRAIGHT) | (k == DASH) | (k == COMBINED) | ((k == BRAKE_REVERSE) & (self.target[ids, 0] != 0))
        turning = (k == TURN) | (k == COMBINED)
        rise = self._recovering[ids]
        self.vx_active[ids] = moving & ~rise
        self.wz_active[ids] = turning & ~rise
        heading = moving & ~turning & self._driving[ids] & ~rise
        self.heading_active[ids] = heading
        self.reference_yaw[ids] = torch.where(heading & latch, yaw, self.reference_yaw[ids])
        error = torch.remainder(self.reference_yaw[ids] - yaw + pi, 2 * pi) - pi
        wz_range = max(abs(v) for v in self.settings["wz_range_rad_s"]) * self.fraction[ids]
        limit = wz_range.clamp_max(self.settings["heading_max_wz"])
        correction = (self.settings["heading_kp"] * error).clamp(-limit, limit)
        prev = self._previous[ids]
        cmd = prev + (self.target[ids] - prev).clamp(-self._rates, self._rates)
        cmd[:, 2] = torch.where(heading, correction, cmd[:, 2])
        air = self._air_limit[ids]
        cmd[:, 0] = torch.where(air, cmd[:, 0].clamp(-2.5, 2.5), cmd[:, 0])
        cmd[:, 2] = torch.where(air, cmd[:, 2].clamp(-pi / 2, pi / 2), cmd[:, 2])
        self.value[ids] = torch.where(rise[:, None], 0.0, cmd)
        if self._route_settings is not None:
            route = self.route[ids]
            active = route & self._route_open[ids] & self._driving[ids] & ~rise
            self.vx_active[ids] = torch.where(route, active, self.vx_active[ids])
            self.wz_active[ids] &= ~route
            self.heading_active[ids] = torch.where(route, active, self.heading_active[ids])
            self.reference_yaw[ids] = torch.where(route, 0.0, self.reference_yaw[ids])
            limit = self._route_settings["heading_max_wz_rad_s"]
            route_error = torch.remainder(pi - yaw, 2 * pi) - pi
            route_yaw = (self._route_settings["heading_kp"] * route_error).clamp(-limit, limit)
            cmd[:, 2] = prev[:, 2] + (route_yaw - prev[:, 2]).clamp(-self._rates[2], self._rates[2])
            route_cmd = torch.where(active[:, None], cmd, 0.0)
            self.value[ids] = torch.where(route[:, None], route_cmd, self.value[ids])

    def prepare_reset_rows(
        self,
        ids: torch.Tensor,
        yaw: torch.Tensor,
        driving: torch.Tensor,
        recovering: torch.Tensor,
        air_birth: torch.Tensor,
        age_steps: torch.Tensor,
        *,
        route_open: torch.Tensor | None = None,
    ) -> None:
        """Issue the first observation after a subset reset on an already-prepared physics tick.

        Inputs other than ids are full (N,) vectors, just like prepare(). reset(ids) already
        sampled motion and set height=height_target, height_rate=0. No clocks, RNG or survivors
        are touched. A repeated call before the next true reset does not apply slew twice.
        """
        ids = ids[self._first_interval[ids]]
        if not ids.numel():
            return
        if route_open is not None:
            self._route_open[ids] = route_open[ids]
        drive, rise, air = driving[ids], recovering[ids], air_birth[ids]
        self._driving[ids], self._recovering[ids], self._height_held[ids] = drive, rise, rise
        self._air_limit[ids] = air & (age_steps[ids] < 300)
        self._previous[ids] = torch.where(air[:, None], self.target[ids], self.value[ids])
        self._issue(ids, yaw[ids], self._first_interval[ids])
        self._issued[ids] = torch.stack((self.value[ids, 0], self.value[ids, 2], self.height[ids, 0]), -1)
        self._whole_drive[ids] &= drive & ~rise
        self._first_interval[ids] = False

    def prepare(
        self,
        yaw: torch.Tensor,
        driving: torch.Tensor,
        recovering: torch.Tensor,
        air_birth: torch.Tensor,
        age_steps: torch.Tensor,
        *,
        route_open: torch.Tensor | None = None,
    ) -> None:
        """Before policy execution; recovering=True throughout release/rise; driving=False until handoff."""
        if route_open is not None:
            self._route_open.copy_(route_open)
        new = self.remaining == 0
        self._motion(new.nonzero().flatten())
        # An independently running height target survives a motion change only inside the new envelope.
        due = self.height_remaining == 0
        lo, hi = self.settings["height_range_m"]
        mid = (lo + hi) / 2
        due |= new & ((self.height_target[:, 0] - mid).abs() > (hi - lo) / 2 * self.fraction)
        self._height_held.copy_(recovering)
        self._heights((due & ~recovering).nonzero().flatten())
        issued_height = torch.where(recovering[:, None], self.height, self.height_target)
        self.height_rate.copy_((issued_height[:, 0] - self.height[:, 0]) / _DT)
        self.height.copy_(issued_height)
        latch = (self.steps == 0) | (~self._driving & driving)
        self._driving.copy_(driving)
        self._recovering.copy_(recovering)
        self._air_limit.copy_(air_birth & (age_steps < 300))
        # Air starts at a moving request, independent of sampled root speed. Apply the birth
        # cap in _issue; after the first interval, ordinary slew and segment resampling resume.
        self._previous.copy_(torch.where((air_birth & self._first_interval)[:, None], self.target, self.value))
        self._first_interval.zero_()
        self._issue(torch.arange(len(yaw), device=yaw.device), yaw, latch)
        # Freeze the evidence for the interval. A post-physics handoff cannot rewrite its sampled commands.
        self._issued[:, 0], self._issued[:, 1], self._issued[:, 2] = (
            self.value[:, 0],
            self.value[:, 2],
            self.height[:, 0],
        )
        self._whole_drive &= driving & ~recovering

    def handoff(self, mask: torch.Tensor, yaw: torch.Tensor) -> None:
        """After event detection, BEFORE handing the same observation/reward to driving. No second timer tick."""
        ids = mask.nonzero().flatten()
        self._driving[ids], self._recovering[ids] = True, False
        self._issue(ids, yaw[ids], mask[ids])

    def finish(
        self,
        actual: torch.Tensor,
        fell: torch.Tensor,
        interrupted: torch.Tensor,
        criterion: Criterion | None = None,
        *,
        invalid: torch.Tensor | None = None,
    ) -> None:
        """After one policy interval (before reset): actual = heading vx, body wz, ground-relative root z.

        External horizon at a natural segment end leaves that completed segment intact. A physical fall wins
        even on the last tick. invalid (e.g. numerical failure) always censors, even at the exact end;
        it is distinct from an ordinary external horizon. Never score a partial recovery/handoff fragment.
        criterion(kind[M], mean_abs_error[M,3], mean_abs_command[M,3]) -> bool[M], flat only.
        """
        self.remaining -= 1
        self.height_remaining -= (~self._height_held).long()
        self.steps += 1
        if self.flat is None:
            return
        self._error_sum += (actual - self._issued).abs()
        self._magnitude_sum += self._issued.abs()
        at_end = self.remaining == 0
        # Nonfinite telemetry poisons the entire interval, even if a permissive criterion ignores that axis.
        bad = ~(torch.isfinite(self._error_sum).all(-1) & torch.isfinite(self._magnitude_sum).all(-1))
        if invalid is not None:
            bad |= invalid
        # Bad telemetry is not a physical failure. Record once at settlement/reset (not a fictitious early boundary).
        done = at_end | fell | interrupted
        if invalid is not None:
            done |= invalid
        ids = (done & self._whole_drive).nonzero().flatten()
        if not ids.numel():
            return
        ok = at_end[ids] & ~fell[ids] & ~bad[ids]
        passed = torch.zeros_like(ok)
        completed = ids[ok]
        if completed.numel():
            if criterion is None:
                raise ValueError("flat command segment success criterion is not calibrated")
            n = self.steps[completed, None]
            passed[ok] = criterion(
                self.kind[completed], self._error_sum[completed] / n, self._magnitude_sum[completed] / n
            )
        self.flat.record(
            self.kind[ids],
            self.fraction[ids],
            ok,
            passed,
            fell[ids] & ~bad[ids],
            bad[ids] | (interrupted[ids] & ~at_end[ids]),
        )
        self._whole_drive[ids] = False
