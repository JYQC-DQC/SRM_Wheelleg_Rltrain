"""Rollout-local TensorBoard scalars for SHU first landing and preset rise events."""

import torch

from wheelleg.shu_landing import ShuLanding

# Columns of the packed device accumulator. Only take() reads them on the host.
_FLAGS = (
    "ended",
    "resolved",
    "success",
    "clean",
    "hard",
    "hard_guide",
    "body_collision",
    "physical_failure",
    "air_timeout",
    "rise_timeout",
    "truncated",
    "numerical",
    "invalid_birth",
    "unknown_guide",
)
_WHEEL = ("first_peak_n", "first_impulse_ns", "event_peak_n")
_LEG = (
    "leg_compression_m",
    "spring_peak_compression_m",
    "spring_compression_stroke_m",
    "touch_leg_length_m",
    "touch_leg_angle_rad",
)
_AIR_SCALARS = ("first_contact_s", "first_touch_gap_s", "catch_time_s", "confirm_mean_rad", "guide_peak_speed_m_s")
_MEASURES = (
    *_AIR_SCALARS,
    *(f"{side}/{key}" for key in (*_WHEEL, *_LEG) for side in ("left", "right")),
    "rise_success_time_s",
    "rise_failure_time_s",
    "rise_max_drift_m",
)
_GROUPS = ("Landing/all", "Landing/top_band", "Rise/all")


class ShuLandingLog:
    """One collector per vector env. add() after update, before reset; take() once per rollout.

    top_band is the actual birth band 3, not the current curriculum level. Air rates use all valid
    resolutions (including non-clean failures); rise rates use successes + failures, not cuts.
    Diagnostic means/maxima use finite observations only. Each has valid_count/missing_count
    against its own eligible population. For example stroke requires chassis first touch, not
    same-side wheel contact; first wheel impulse requires that wheel and a complete first patch.
    """

    def __init__(self) -> None:
        self._seen_birth: torch.Tensor | None = None
        self._window: torch.Tensor | None = None  # (3 groups, 4 statistics, padded columns)

    @torch.inference_mode()
    def add(self, event: ShuLanding, band: torch.Tensor) -> None:
        """band (N,) stores each environment's original birth band until after settlement."""
        m = event.metrics()
        if self._seen_birth is None:
            self._seen_birth = torch.full_like(event.born, -1)
        pulse = m["ended"] & (event.born != self._seen_birth)
        self._seen_birth.copy_(torch.where(pulse, event.born, self._seen_birth))
        air_end, rise_end = pulse & event.air_birth, pulse & event.preset_birth
        # Fixed-size reductions avoid per-step dynamic indexing, host synchronization and rollout histories.
        groups = torch.stack((air_end, air_end & (band == 3), rise_end))
        air, rise = m["resolved"], m["rise_succeeded"] | m["rise_failed"]
        caught = m["succeeded"] & air
        hard = m["hard_guide"] | m["body_collision"]
        flags = torch.stack(
            (
                torch.ones_like(pulse),
                air | rise,
                caught | m["rise_succeeded"],
                air & m["clean"],
                air & hard,
                air & m["hard_guide"],
                air & m["body_collision"],
                (air | rise) & m["physical_failure"],
                air & m["air_timeout"],
                rise & m["rise_timeout"],
                m["truncated"],
                m["numerical_failure"],
                m["invalid_birth"],
                m["unknown_guide"],
            ),
            dim=1,
        )

        # (value, eligible population, observed mask), in _MEASURES order. For wheel rows the latter
        # is per side. Leg/spring displacement can be observed at guide-first touch even without wheel contact.
        touch, wheels = m["touch_tick"] >= 0, m["wheel_touched"]
        guide = m["touched_bodies"][:, event.guides].any(-1)
        fields = [
            (m["first_contact_s"], air, touch),
            (m["first_touch_gap_s"], air, wheels.all(-1)),
            (m["catch_time_s"], caught, caught),
            (m["confirm_mean_rad"], caught, caught),
            (m["guide_peak_speed_m_s"], air & guide, guide),
        ]
        for key in (*_WHEEL, *_LEG):
            for side in (0, 1):
                fields.append((m[key][:, side], air, wheels[:, side] if key in _WHEEL else touch))
        fields.extend(
            (
                (m["rise_time_s"], m["rise_succeeded"], rise),
                (m["rise_time_s"], m["rise_failed"], rise),
                (m["rise_max_drift_m"], rise, event.takeover_tick >= 0),
            )
        )
        values, eligible, observed = (torch.stack(cols, dim=1) for cols in zip(*fields, strict=True))
        valid = observed & values.isfinite()
        if self._window is None:
            self._window = values.new_zeros((3, 4, len(_FLAGS) + values.shape[1]))
            self._window[:, 3].fill_(-torch.inf)
        w = self._window
        # (population, env, measured quantity); no per-env or per-quantity device reductions.
        eligible_here = groups[:, :, None] & eligible
        measured = eligible_here & valid
        counts = torch.cat((groups[:, :, None] & flags, eligible_here, measured), dim=2).sum(dim=1, dtype=values.dtype)
        offset = len(_FLAGS)
        split = offset + len(_MEASURES)
        w[:, 0].add_(counts[:, :split])
        w[:, 1, offset:].add_(counts[:, split:])
        w[:, 2, offset:].add_(torch.where(measured, values, 0.0).sum(1))
        torch.maximum(w[:, 3, offset:], torch.where(measured, values, -torch.inf).amax(1), out=w[:, 3, offset:])

    def take(self) -> dict[str, int | float]:
        """Drain only rollout totals. An empty rollout returns {}; absent means/rates are omitted, not NaN."""
        if self._window is None:
            return {}
        # The runner can drain outside rollout inference_mode: read the old tensor, never mutate it.
        rows = self._window.cpu().tolist()
        self._window = None
        out = {}
        for i, (exposure, valid, total, maximum) in enumerate(rows):
            counts = dict(zip(_FLAGS, map(int, exposure)))
            if not counts["ended"]:
                continue
            prefix = _GROUPS[i] + "/"
            rise = i == 2
            common = ("ended", "resolved", "success", "physical_failure", "truncated", "numerical")
            extras = (
                ("rise_timeout",)
                if rise
                else ("clean", "hard", "hard_guide", "body_collision", "air_timeout", "invalid_birth", "unknown_guide")
            )
            out.update({prefix + k + "_count": counts[k] for k in (*common, *extras)})
            resolved = counts["resolved"]
            if resolved:
                rates = (
                    {"success_rate": "success"}
                    if rise
                    else {"allow_light_catch_rate": "success", "clean_rate": "clean", "hard_rate": "hard"}
                )
                out.update({prefix + k: counts[n] / resolved for k, n in rates.items()})
            for j, name in enumerate(_MEASURES, start=len(_FLAGS)):
                if not exposure[j]:
                    continue
                tag = prefix + name + "/"
                n = int(valid[j])
                out[tag + "valid_count"] = n
                out[tag + "missing_count"] = int(exposure[j]) - n
                if n:
                    out[tag + "mean"] = total[j] / n
                    out[tag + "max"] = maximum[j]
        return out
