"""Rollout-local TensorBoard scalars for SHU first landing and preset rise events."""

from math import pi

import torch

from shu_train.wheelleg.shu_landing import ShuLanding

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
_GROUPS = (
    "Landing/all",
    "Landing/top_band",
    "Rise/all",
    "Landing/birth_leg_diff_below_45deg",
    "Landing/birth_leg_diff_at_least_45deg",
    "Landing/birth_forward_same_direction",
    "Landing/birth_forward_opposite_direction",
    "Landing/birth_forward_near_zero",
)


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
        self._window: torch.Tensor | None = None
        self._birth_window = None

    @torch.inference_mode()
    def add(self, event: ShuLanding, band: torch.Tensor, air_debug=None) -> None:
        """band (N,) stores each environment's original birth band until after settlement."""
        m = event.metrics()
        if self._seen_birth is None:
            self._seen_birth = torch.full_like(event.born, -1)
        pulse = m["ended"] & (event.born != self._seen_birth)
        self._seen_birth.copy_(torch.where(pulse, event.born, self._seen_birth))
        air_end, rise_end = pulse & event.air_birth, pulse & event.preset_birth
        # Fixed-size reductions avoid per-step dynamic indexing, host synchronization and rollout histories.
        groups = (air_end, air_end & (band == 3), rise_end)
        if air_debug is None:
            groups += (torch.zeros_like(air_end),) * (len(_GROUPS) - len(groups))
        else:
            angle_diff, vx_at_birth, first_vx_cmd, rim_sq_sum, rim_ticks = air_debug
            valid_angle = air_end & angle_diff.isfinite()
            valid_speed = air_end & vx_at_birth.isfinite() & first_vx_cmd.isfinite()
            # Reporting bins only. Near zero includes either the sampled speed or its first issued target.
            near_zero = torch.minimum(vx_at_birth.abs(), first_vx_cmd.abs()) < 0.1
            same = (vx_at_birth * first_vx_cmd) > 0
            groups += (
                valid_angle & (angle_diff < pi / 4),
                valid_angle & (angle_diff >= pi / 4),
                valid_speed & ~near_zero & same,
                valid_speed & ~near_zero & ~same,
                valid_speed & near_zero,
            )
        groups = torch.stack(groups)
        air, rise = m["resolved"], m["rise_succeeded"] | m["rise_failed"]
        if air_debug is not None:
            with_rim = groups & air & (rim_ticks > 0)
            sums = torch.stack(
                (
                    torch.where(with_rim, rim_sq_sum, 0).sum(1),
                    torch.where(with_rim, rim_ticks, 0).sum(1),
                ),
                dim=-1,
            )
            if self._birth_window is None:
                self._birth_window = sums
            else:
                self._birth_window.add_(sums)
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
            self._window = values.new_zeros((len(_GROUPS), 4, len(_FLAGS) + values.shape[1]))
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
        birth_rows = None if self._birth_window is None else self._birth_window.tolist()
        self._birth_window = None
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
            if birth_rows is not None:
                rim_sq_sum, rim_ticks = birth_rows[i]
                if rim_ticks:
                    out[prefix + "air_wheel_rim_rmse_m_s"] = (rim_sq_sum / rim_ticks) ** 0.5
                    out[prefix + "air_wheel_rim_policy_sample_count"] = int(rim_ticks)
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


class ShuRewardLog:
    """Per-term means over enabled, finite policy steps and fraction changed by clipping."""

    def __init__(self):
        self._window = None
        self._names = ()

    def add(self, terms, valid):
        self._names = tuple(terms)
        pre, post, enabled, saturated = (torch.stack(values) for values in zip(*terms.values(), strict=True))
        use = enabled & valid & pre.isfinite() & post.isfinite()
        stats = torch.stack(
            (
                torch.where(use, pre, 0).sum(-1),
                torch.where(use, post, 0).sum(-1),
                (use & saturated).sum(-1),
                use.sum(-1),
            ),
            dim=-1,
        )
        if self._window is None:
            self._window = stats
        else:
            self._window.add_(stats)

    def take(self):
        if self._window is None:
            return {}
        rows = self._window.tolist()
        self._window = None
        out = {}
        for name, (pre, post, saturated, valid) in zip(self._names, rows, strict=True):
            if valid:
                prefix = f"Reward_Diagnostics/{name}/"
                out[prefix + "pre_clip_mean"] = pre / valid
                out[prefix + "post_clip_mean"] = post / valid
                out[prefix + "saturation_fraction"] = saturated / valid
                out[prefix + "sample_count"] = int(valid)
        return out
