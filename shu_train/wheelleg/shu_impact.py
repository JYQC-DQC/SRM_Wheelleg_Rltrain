"""SHU P1 first-impact observations (2 ms world-frame forces, never used as a reward)."""

import torch


class ShuImpact:
    def __init__(self, count: int, device: str):
        pair = torch.zeros(count, 2, device=device)
        self.first_tick = torch.full_like(pair, -1, dtype=torch.long)
        self.first_segment = torch.zeros_like(pair, dtype=torch.bool)
        self.first_peak_n = pair.clone()
        self.first_impulse_ns = pair.clone()
        self.event_peak_n = pair.clone()
        self.compression_m = pair.clone()
        self._longest_m = pair.clone()
        self._previous_length_m = torch.full_like(pair, torch.nan)
        self.touch_leg_length_m = self._previous_length_m.clone()
        self.touch_leg_angle_rad = self._previous_length_m.clone()
        self._previous_angle_rad = self._previous_length_m.clone()
        self.spring_peak_compression_m = self._previous_length_m.clone()
        self.spring_compression_stroke_m = self._previous_length_m.clone()
        self._spring_min_m = self._previous_length_m.clone()
        self._previous_spring_m = self._previous_length_m.clone()

    def reset(self, ids: torch.Tensor) -> None:
        self.first_tick[ids] = -1
        self.first_segment[ids] = False
        for x in (self.first_peak_n, self.first_impulse_ns, self.event_peak_n, self.compression_m, self._longest_m):
            x[ids] = 0
        for x in (
            self.touch_leg_length_m,
            self.touch_leg_angle_rad,
            self._previous_length_m,
            self._previous_angle_rad,
            self.spring_peak_compression_m,
            self.spring_compression_stroke_m,
            self._spring_min_m,
            self._previous_spring_m,
        ):
            x[ids] = torch.nan

    def sample(
        self,
        tick,
        dt,
        observe,
        first_touch,
        adjacent,
        in_catch,
        fz,
        wheel_contact,
        leg_length_m,
        leg_angle_rad,
        spring_compression_m,
    ):
        # L/R first continuous patches close independently; a rebound can only update the event peak.
        hit = observe[:, None] & wheel_contact
        first = hit & (self.first_tick < 0)
        # Across a missing force sample we cannot distinguish a continued first patch from a rebound.
        # NaN flags an incomplete patch (wheel_touched still reports the observed strike).
        gap = observe[:, None] & ~adjacent[:, None] & self.first_segment
        self.first_peak_n.masked_fill_(gap, torch.nan)
        self.first_impulse_ns.masked_fill_(gap, torch.nan)
        self.first_tick.masked_fill_(first, tick)
        self.first_segment.copy_(torch.where(observe[:, None], (self.first_segment | first) & hit, self.first_segment))
        patch_force = torch.where(hit & self.first_segment, fz, 0.0)
        self.first_peak_n.copy_(torch.maximum(self.first_peak_n, patch_force))
        self.first_impulse_ns.add_(patch_force * dt)
        self.event_peak_n.copy_(torch.maximum(self.event_peak_n, torch.where(observe[:, None], fz, 0.0)))

        # Stroke is the greatest shortening from a preceding length, not max-min in arbitrary time order.
        # Previous substep captures compression already underway in the first contact sample.
        pre_length = torch.where(adjacent[:, None], self._previous_length_m, torch.nan)
        self.touch_leg_length_m.copy_(torch.where(first_touch[:, None], pre_length, self.touch_leg_length_m))
        pre_angle = torch.where(adjacent[:, None], self._previous_angle_rad, torch.nan)
        self.touch_leg_angle_rad.copy_(torch.where(first_touch[:, None], pre_angle, self.touch_leg_angle_rad))
        start = torch.where(first_touch[:, None] & pre_length.isfinite(), pre_length, self._longest_m)
        peak = torch.maximum(start, leg_length_m)
        self._longest_m.copy_(torch.where(in_catch[:, None], peak, self._longest_m))
        self.compression_m.copy_(
            torch.where(in_catch[:, None], torch.maximum(self.compression_m, peak - leg_length_m), self.compression_m)
        )
        self._previous_length_m.copy_(torch.where(observe[:, None], leg_length_m, self._previous_length_m))
        if spring_compression_m is not None:
            # Axial compression is positive. Log both absolute peak and added stroke, excluding flight preload.
            pre_spring = torch.where(adjacent[:, None], self._previous_spring_m, torch.nan)
            start = torch.where(first_touch[:, None], pre_spring, self._spring_min_m)
            low = torch.fmin(start, spring_compression_m)
            valid = in_catch[:, None] & spring_compression_m.isfinite()
            self._spring_min_m.copy_(torch.where(valid, low, self._spring_min_m))
            self.spring_peak_compression_m.copy_(
                torch.where(
                    valid,
                    torch.fmax(self.spring_peak_compression_m, spring_compression_m),
                    self.spring_peak_compression_m,
                )
            )
            self.spring_compression_stroke_m.copy_(
                torch.where(
                    valid,
                    torch.fmax(self.spring_compression_stroke_m, spring_compression_m - low),
                    self.spring_compression_stroke_m,
                )
            )
            self._previous_spring_m.copy_(
                torch.where(
                    observe[:, None],
                    torch.where(spring_compression_m.isfinite(), spring_compression_m, torch.nan),
                    self._previous_spring_m,
                )
            )
        else:
            self._previous_spring_m.masked_fill_(observe[:, None], torch.nan)
        if leg_angle_rad is not None:
            self._previous_angle_rad.copy_(
                torch.where(
                    observe[:, None],
                    torch.where(leg_angle_rad.isfinite(), leg_angle_rad, torch.nan),
                    self._previous_angle_rad,
                )
            )
        else:
            self._previous_angle_rad.masked_fill_(observe[:, None], torch.nan)

    def first_touch_gap_s(self, physics_dt: float) -> torch.Tensor:
        """Absolute left/right delay; missing observations must not look like simultaneous contact."""
        left, right = self.first_tick.unbind(-1)
        return torch.where((left >= 0) & (right >= 0), (left - right).abs() * physics_dt, torch.nan)
