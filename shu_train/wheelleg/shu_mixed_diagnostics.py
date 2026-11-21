"""P1 mixed traversal telemetry only; no reward, termination, or curriculum decisions."""

from math import ceil, isfinite

import torch

FREE, FORWARD_UP, FORWARD_DOWN, REVERSE_DOWN = range(-1, 3)
ROUTE_NAMES = ("forward_up", "forward_down", "reverse_down")
_GROUP_SHAPE = (len(ROUTE_NAMES), 2, 2)  # route, plain/lip, straight/oblique
_FREE_GROUP = len(ROUTE_NAMES) * 4
_COUNTS = (
    "episode_count",
    "completed_count",
    "incomplete_count",
    "fall_count",
    "timeout_count",
    "numerical_failure_count",
    "other_termination_count",
    "stuck_episode_count",
    "force_episode_count",
    "bad_force_sample_count",
    "non_main_contact_episode_count",
    "guide_contact_episode_count",
)
_TOTALS = ("left_fz_impulse_ns", "right_fz_impulse_ns", "non_main_contact_s", "guide_contact_s")
_PEAKS = ("left_fz_peak_max_n", "right_fz_peak_max_n", "non_main_peak_max_n", "guide_peak_max_n")


class ShuMixedDiagnostics:
    def __init__(
        self,
        count,
        device,
        *,
        wheels,
        guides,
        body_count,
        physics_dt,
        step_dt,
        contact_force_n,
        window_s=1.0,
        distance_m=0.05,
    ):
        if not isfinite(window_s) or window_s <= 0 or not isfinite(distance_m) or distance_m < 0:
            raise ValueError("mixed stall window_s must be positive and distance_m nonnegative (both finite)")
        self._window_steps = max(1, ceil(window_s / step_dt - 1e-9))
        self._distance_m = distance_m
        self._physics_dt = physics_dt
        self._contact_force_n = contact_force_n
        self._wheels = list(wheels)  # sensor indices in L/R order
        self._contact_groups = (sorted(set(range(body_count)) - set(self._wheels)), list(guides))
        self._group = torch.full((count,), _FREE_GROUP, device=device, dtype=torch.long)
        self._born_tick = torch.zeros_like(self._group)
        self._last_contact_tick = -1
        self._spawn_heading_w = torch.zeros(count, 2, device=device)
        self._window = torch.zeros(self._window_steps, count, device=device)
        self._cursor = 0
        self._projected_m = torch.zeros(count, device=device, dtype=torch.float64)
        self._consecutive = torch.zeros_like(self._group)
        self.stuck_now = torch.zeros(count, dtype=torch.bool, device=device)
        self.ever_stuck = torch.zeros_like(self.stuck_now)
        self.completed = torch.zeros_like(self.stuck_now)
        self.wheel_fz_peak_n = torch.zeros_like(self._spawn_heading_w)
        self.wheel_fz_impulse_ns = torch.zeros_like(self.wheel_fz_peak_n)
        self._contact_peak_n = torch.zeros_like(self.wheel_fz_peak_n)
        self._contact_ticks = torch.zeros(count, 2, device=device, dtype=torch.long)
        self._force_samples = torch.zeros_like(self._group)
        self._bad_force_samples = torch.zeros_like(self._group)
        self._rollout = None
        self._episode_ends = None

    def reset(self, env_ids, *, route, with_lip, oblique, spawn_yaw_rad, tick):
        """Register new episodes after assignment and spawn. The four tensors are sliced to env_ids."""
        group = 4 * route + 2 * with_lip.long() + oblique.long()
        self._group[env_ids] = torch.where(route == FREE, _FREE_GROUP, group)
        self._born_tick[env_ids] = tick
        self._spawn_heading_w[env_ids] = torch.stack((spawn_yaw_rad.cos(), spawn_yaw_rad.sin()), dim=-1)
        self._window[:, env_ids] = 0
        for value in (
            self._projected_m,
            self._consecutive,
            self.stuck_now,
            self.ever_stuck,
            self.completed,
            self.wheel_fz_peak_n,
            self.wheel_fz_impulse_ns,
            self._contact_peak_n,
            self._contact_ticks,
            self._force_samples,
            self._bad_force_samples,
        ):
            value[env_ids] = 0

    @torch.no_grad()
    def sample_contacts(self, tick, forces_w_n):
        """Use one fresh (N, B, 3) world net-force sample per physics tick, through first completion.

        Integrate positive world Fz per main wheel (includes sustained support, not a single-hit
        impulse or a local surface normal). Use net force magnitude for all non-main bodies and
        separately for the guide subset. Guide contact on a lip route is a proxy, not a lip hit.
        """
        if tick <= self._last_contact_tick:
            return
        self._last_contact_tick = tick
        fresh = (tick > self._born_tick) & (self._group != _FREE_GROUP) & ~self.completed
        finite = forces_w_n.isfinite().all(dim=(1, 2))
        use = fresh & finite
        self._force_samples += use
        self._bad_force_samples += fresh & ~finite
        wheel_fz = torch.where(use[:, None], forces_w_n[:, self._wheels, 2].clamp_min(0), 0.0)
        self.wheel_fz_peak_n.copy_(torch.maximum(self.wheel_fz_peak_n, wheel_fz))
        self.wheel_fz_impulse_ns.add_(wheel_fz, alpha=self._physics_dt)
        norm = torch.linalg.vector_norm(forces_w_n, dim=-1)
        for i, bodies in enumerate(self._contact_groups):
            if bodies:
                peak = torch.where(use, norm[:, bodies].amax(-1), 0.0)
                self._contact_peak_n[:, i] = torch.maximum(self._contact_peak_n[:, i], peak)
                self._contact_ticks[:, i] += use & (peak > self._contact_force_n)

    @torch.no_grad()
    def step_route(self, displacement_xy_w_m, vx_cmd_m_s, *, completed, invalid_motion):
        """Consume one policy interval with the command actually issued for it.

        Signed progress is displacement projected onto the *spawn* heading times the issued
        longitudinal command's sign. This measures the assigned route intention, not world +X,
        path length, or current yaw. The rolling window rounds up to a whole policy interval.
        """
        route = self._group != _FREE_GROUP
        self.completed |= route & completed
        projection = (displacement_xy_w_m * self._spawn_heading_w).sum(-1) * vx_cmd_m_s.sign()
        active = (
            route
            & ~self.completed
            & ~invalid_motion
            & vx_cmd_m_s.isfinite()
            & (vx_cmd_m_s != 0)
            & projection.isfinite()
        )
        progress = torch.where(active, projection, 0.0).to(self._window.dtype)
        previous = self._window[self._cursor]
        # Accumulate at higher precision so a long rollout doesn't drift around the strict cutoff.
        self._projected_m += progress.double() - previous
        previous.copy_(progress)
        self._cursor = (self._cursor + 1) % self._window_steps
        # The count gates the sum until all slots preceding an interruption have rolled out.
        self._consecutive.copy_(torch.where(active, (self._consecutive + 1).clamp_max(self._window_steps), 0))
        self.stuck_now.copy_((self._consecutive == self._window_steps) & (self._projected_m < self._distance_m))
        self.ever_stuck |= self.stuck_now

    def _reduce_ended(self, env_ids, *, terminated, timeout, physical_failure, numerical_failure):
        terminated, timeout = terminated[env_ids], timeout[env_ids]
        group = torch.where(terminated | timeout, self._group[env_ids], _FREE_GROUP)
        done = self.completed[env_ids]
        numeric = numerical_failure[env_ids]
        fall = physical_failure[env_ids] & ~numeric
        timed_out = timeout & ~(fall | numeric | terminated)
        other = terminated & ~(fall | numeric)
        contact_ticks = self._contact_ticks[env_ids]
        counts = torch.stack(
            (
                torch.ones_like(done),
                done,
                ~done,
                fall,
                timed_out,
                numeric,
                other,
                self.ever_stuck[env_ids],
                self._force_samples[env_ids] > 0,
                self._bad_force_samples[env_ids],
                contact_ticks[:, 0] > 0,
                contact_ticks[:, 1] > 0,
            ),
            dim=-1,
        )
        totals = torch.cat((self.wheel_fz_impulse_ns[env_ids], contact_ticks * self._physics_dt), dim=-1)
        peaks = torch.cat((self.wheel_fz_peak_n[env_ids], self._contact_peak_n[env_ids]), dim=-1)
        rows = []
        for values, reduce in ((counts, "sum"), (totals, "sum"), (peaks, "amax")):
            bins = values.new_zeros(_FREE_GROUP + 1, values.shape[1])
            if reduce == "sum":
                bins.index_add_(0, group, values)
            else:
                bins.scatter_reduce_(0, group[:, None].expand_as(values), values, reduce="amax")
            rows.append(bins[:_FREE_GROUP])
        return rows

    def summarize(self, env_ids, *, terminated, timeout, physical_failure, numerical_failure):
        """Return additive counts/sums and maxima for ended rounds, each shaped (route, lip, oblique).

        End flags are full-env masks. Completion is first supported arrival, so an episode can
        complete and later fall/time out. Force samples only cover birth to first completion/end.
        """
        rows = self._reduce_ended(
            env_ids,
            terminated=terminated,
            timeout=timeout,
            physical_failure=physical_failure,
            numerical_failure=numerical_failure,
        )
        keys = (_COUNTS, tuple(name + "_sum" for name in _TOTALS), _PEAKS)
        return {
            name: value
            for names, row in zip(keys, rows)
            for name, value in zip(names, row.view(*_GROUP_SHAPE, -1).unbind(-1))
        }

    def record_ended(
        self,
        env_ids,
        *,
        terminated,
        timeout,
        physical_failure,
        numerical_failure,
        boundary_timeout=None,
        normal_time_limit=None,
        atlas=None,
    ):
        """Accumulate once per reset batch, before changing old birth labels or clearing telemetry."""
        rows = self._reduce_ended(
            env_ids,
            terminated=terminated,
            timeout=timeout,
            physical_failure=physical_failure,
            numerical_failure=numerical_failure,
        )
        if self._rollout is None:
            self._rollout = rows
        else:
            self._rollout[0].add_(rows[0])
            self._rollout[1].add_(rows[1])
            torch.maximum(self._rollout[2], rows[2], out=self._rollout[2])
        if boundary_timeout is not None:
            ended = (terminated | timeout)[env_ids]
            boundary = boundary_timeout[env_ids] & timeout[env_ids] & ~terminated[env_ids]
            horizon = normal_time_limit[env_ids] & timeout[env_ids] & ~terminated[env_ids]
            on_map = atlas[env_ids]
            counts = torch.stack((ended, boundary, horizon, ended & on_map, horizon & on_map)).sum(1)
            if self._episode_ends is None:
                self._episode_ends = counts
            else:
                self._episode_ends.add_(counts)

    def take(self) -> dict[str, int | float]:
        """Drain rollout scalars; leave all in-flight episode state untouched."""
        if self._rollout is None:
            return {}
        # As with landing logs, the runner can drain outside rollout inference_mode.
        rows = torch.cat([row.double() for row in self._rollout], dim=-1).cpu().tolist()
        self._rollout = None
        out = {}
        if self._episode_ends is not None:
            total, boundary, horizon, on_map, map_horizon = self._episode_ends.tolist()
            self._episode_ends = None
            for name, n, h in (("all", total, horizon), ("atlas", on_map, map_horizon)):
                if n:
                    prefix = f"Mixed/{name}/"
                    out[prefix + "ended_episode_count"] = n
                    out[prefix + "boundary_timeout_count"] = boundary
                    out[prefix + "normal_time_limit_count"] = h
                    out[prefix + "boundary_timeout_fraction"] = boundary / n
                    out[prefix + "normal_time_limit_fraction"] = h / n
        for group, row in enumerate(rows):
            counts = dict(zip(_COUNTS, map(int, row[: len(_COUNTS)])))
            n = counts["episode_count"]
            if not n:
                continue
            route = ROUTE_NAMES[group // 4]
            edge = "lip" if group & 2 else "plain"
            angle = "oblique" if group & 1 else "straight"
            prefix = f"Mixed/{route}/{edge}/{angle}/"
            out.update({prefix + name: count for name, count in counts.items()})
            out[prefix + "completion_rate"] = counts["completed_count"] / n
            out[prefix + "fall_rate"] = counts["fall_count"] / n
            out[prefix + "stuck_rate"] = counts["stuck_episode_count"] / n
            force_n = counts["force_episode_count"]
            if force_n:
                out[prefix + "non_main_contact_rate"] = counts["non_main_contact_episode_count"] / force_n
                out[prefix + "guide_contact_rate"] = counts["guide_contact_episode_count"] / force_n
                for name, value in zip(_TOTALS, row[len(_COUNTS) : len(_COUNTS) + len(_TOTALS)]):
                    out[prefix + name + "_mean"] = value / force_n
                out.update({prefix + name: value for name, value in zip(_PEAKS, row[-len(_PEAKS) :])})
        return out
