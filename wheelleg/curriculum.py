import torch


class GroundPromotionGate:
    """Fixed-command ground checks with separate stationary and straight pass criteria."""

    def __init__(self, settings: dict, count: int, dt: float, device: str):
        self.settings = settings
        self.dt = dt
        self.start = round(settings["warmup_s"] / dt)
        self.end = self.start + round(settings["window_s"] / dt)
        self.tail_start = self.end - round(settings["stationary_tail_s"] / dt)
        self.kind = torch.full((count,), -1, dtype=torch.long, device=device)
        self.age = torch.zeros_like(self.kind)
        self.complete = torch.zeros(count, dtype=torch.bool, device=device)
        self.failed = torch.zeros_like(self.complete)
        self.anchor = torch.zeros(count, 2, device=device)
        self.max_drift = torch.zeros(count, device=device)
        self.max_heading = torch.zeros_like(self.max_drift)
        self.tail_speed = torch.zeros_like(self.max_drift)
        self.forward_speed = torch.zeros_like(self.max_drift)
        self.yaw_rate = torch.zeros_like(self.max_drift)
        self.attempts = torch.zeros(2, device=device)
        self.successes = torch.zeros_like(self.attempts)
        self.latest_rate = torch.zeros_like(self.attempts)
        self.streak = 0

    @property
    def ready(self) -> bool:
        return self.streak >= self.settings["consecutive_windows"]

    def reset(self, ids: torch.Tensor, groups: torch.Tensor, vx: torch.Tensor, straight_speed: float) -> None:
        self.kind[ids] = torch.where(
            (groups == 0) & (vx == 0), 0, torch.where((groups == 1) & (vx == straight_speed), 1, -1)
        )
        for value in (
            self.age,
            self.complete,
            self.failed,
            self.anchor,
            self.max_drift,
            self.max_heading,
            self.tail_speed,
            self.forward_speed,
            self.yaw_rate,
        ):
            value[ids] = 0

    def step(
        self,
        xy: torch.Tensor,
        velocity: torch.Tensor,
        forward: torch.Tensor,
        heading: torch.Tensor,
        yaw_rate: torch.Tensor,
        ended: torch.Tensor,
    ) -> None:
        self.age += (self.kind >= 0) & (self.age < self.end)
        start = self.age == self.start
        self.anchor.copy_(torch.where(start[:, None], xy, self.anchor))
        sample = (self.kind >= 0) & (self.age > self.start) & (self.age <= self.end)
        # Completed checks can remain in their training episodes. Sample the final tick only once.
        sample &= ~self.complete
        self.max_drift.copy_(torch.maximum(self.max_drift, torch.where(sample, (xy - self.anchor).norm(dim=-1), 0)))
        self.max_heading.copy_(torch.maximum(self.max_heading, torch.where(sample, heading.abs(), 0)))
        self.tail_speed += torch.where(sample & (self.age > self.tail_start), velocity.norm(dim=-1), 0)
        self.forward_speed += torch.where(sample, forward, 0)
        self.yaw_rate += torch.where(sample, yaw_rate.abs(), 0)
        self.complete |= sample & (self.age == self.end)
        self.failed |= ended & ((self.age < self.end) | sample)

    def record(self, ids: torch.Tensor) -> None:
        kind = self.kind[ids]
        eligible = kind >= 0
        cfg = self.settings
        stationary = (self.max_drift[ids] <= cfg["stationary_max_drift_m"]) & (
            self.tail_speed[ids] / (self.end - self.tail_start) <= cfg["stationary_max_tail_speed_m_s"]
        )
        straight = (
            (self.max_heading[ids] <= cfg["straight_max_heading_rad"])
            & (self.forward_speed[ids] / (self.end - self.start) >= cfg["straight_min_vx_m_s"])
            & (self.yaw_rate[ids] / (self.end - self.start) <= cfg["straight_max_mean_wz_rad_s"])
        )
        passed = torch.where(kind == 0, stationary, straight) & self.complete[ids] & ~self.failed[ids]
        self.attempts.scatter_add_(0, kind[eligible], torch.ones_like(kind[eligible], dtype=self.attempts.dtype))
        self.successes.scatter_add_(0, kind[eligible], passed[eligible].float())
        if bool((self.attempts >= cfg["min_episodes_per_group"]).all()):
            self.latest_rate.copy_(self.successes / self.attempts)
            self.streak = self.streak + 1 if bool((self.latest_rate >= cfg["ground_pass_rate"]).all()) else 0
            self.attempts.zero_()
            self.successes.zero_()

    def state_dict(self) -> dict:
        return {key: getattr(self, key) for key in ("attempts", "successes", "latest_rate", "streak")}

    def load_state_dict(self, state: dict) -> None:
        for key in ("attempts", "successes", "latest_rate"):
            getattr(self, key).copy_(state[key])
        self.streak = state["streak"]


class CommandCurriculum:
    """Non-overlapping completed-episode windows; at most one promotion per window.

    With a landing gate (p1-landing), a window promotes only if the landing events resolved during it also
    reached the gate's success rate: faster commands mean faster air births, so speed must not outrun landing.
    """

    def __init__(self, settings: dict, landing_gate: dict | None = None):
        self.settings = settings
        self.minimum = settings["min_completed_episodes"]
        if type(self.minimum) is not int or self.minimum <= 0:
            raise ValueError("command_curriculum.min_completed_episodes must be a positive integer")
        self.landing_gate = landing_gate
        self.completed = 0
        self.successes = 0
        self.landing_events = 0
        self.landing_successes = 0
        self.last_landing_rate = None  # landing success rate of the last closed window
        self.fraction = settings["initial_fraction"]

    def record_landing(self, successful: torch.Tensor) -> None:
        self.landing_events += successful.numel()
        self.landing_successes += int(successful.sum())

    def discard_landing(self) -> None:
        """Drop the landing counts of the open window, e.g. when they belong to a height band no longer newest."""
        self.landing_events = self.landing_successes = 0
        self.last_landing_rate = None  # the logged rate also belonged to the old band

    def restart(self, fraction: float) -> None:
        """Resume at a given fraction; the open window is discarded so no old successes carry over."""
        self.fraction = fraction
        self.completed = self.successes = self.landing_events = self.landing_successes = 0

    def record(self, successful: torch.Tensor) -> float:
        self.completed += successful.numel()
        self.successes += int(successful.sum())
        if self.completed >= self.minimum:
            promote = self.successes / self.completed >= self.settings["success_fraction"]
            if self.landing_gate is not None:
                enough = self.landing_events >= self.landing_gate["min_events"]
                self.last_landing_rate = self.landing_successes / self.landing_events if self.landing_events else None
                promote &= enough and self.last_landing_rate >= self.landing_gate["success_rate"]
            if promote:
                self.fraction = min(1.0, self.fraction + self.settings["increment"])
            # The entire finishing batch belongs to this window; never reuse its successes.
            self.completed = 0
            self.successes = 0
            self.landing_events = 0
            self.landing_successes = 0
        return self.fraction

    def state_dict(self) -> dict:
        state = dict(completed=self.completed, successes=self.successes, fraction=self.fraction)
        if self.landing_gate is not None:  # absent otherwise, so flat checkpoints keep their format
            state.update(
                landing_events=self.landing_events,
                landing_successes=self.landing_successes,
                last_landing_rate=self.last_landing_rate,
            )
        return state

    def load_state_dict(self, state: dict) -> None:
        self.completed, self.successes, self.fraction = state["completed"], state["successes"], state["fraction"]
        if self.landing_gate is not None:
            self.landing_events, self.landing_successes = state["landing_events"], state["landing_successes"]
            self.last_landing_rate = state["last_landing_rate"]


class AirHeightCurriculum:
    """Upper bound of the landing air-birth height offset, raised one level at a time on landing success.

    Only events born in the newest band (previous upper bound to the current one) count, so easier low births
    cannot carry a promotion and events born before a promotion never count toward the next window.
    """

    def __init__(self, low: float, settings: dict):
        self.low, self.settings = low, settings
        self.levels = list(settings["levels_m"])
        self.level = 0
        self.events = 0
        self.successes = 0
        self.last_rate = None  # success rate of the last closed window

    @property
    def upper(self) -> float:
        return self.levels[self.level]

    @property
    def band_floor(self) -> float:
        return self.levels[self.level - 1] if self.level else self.low

    def restart(self) -> None:
        """Back to the first level with a fresh window, e.g. to resume a run from the easiest heights."""
        self.level = self.events = self.successes = 0
        self.last_rate = None

    def record(self, offsets: torch.Tensor, successful: torch.Tensor) -> bool:
        """Returns True when this batch promoted the upper bound to the next level."""
        top = offsets >= self.band_floor
        self.events += int(top.sum())
        self.successes += int((successful & top).sum())
        promoted = False
        if self.events >= self.settings["min_events"]:
            self.last_rate = self.successes / self.events
            if self.last_rate >= self.settings["success_rate"] and self.level < len(self.levels) - 1:
                self.level += 1
                promoted = True
            self.events = 0
            self.successes = 0
        return promoted

    def state_dict(self) -> dict:
        # upper_m keeps the reached height when levels_m is refined between runs; level alone would shift it.
        # lower_m identifies the band the open window was counted in.
        return dict(
            level=self.level,
            upper_m=self.upper,
            lower_m=self.band_floor,
            events=self.events,
            successes=self.successes,
            last_rate=self.last_rate,
        )

    def load_state_dict(self, state: dict) -> bool:
        """Returns False when the saved open window no longer matches the band and was discarded."""
        # Checkpoints before upper_m used levels_m [0.2, 0.28, 0.35, 0.42].
        upper = state["upper_m"] if "upper_m" in state else (0.2, 0.28, 0.35, 0.42)[state["level"]]
        reached = [i for i, level in enumerate(self.levels) if level <= upper + 1e-9]
        self.level = reached[-1] if reached else 0
        self.last_rate = state["last_rate"]
        same_band = "lower_m" in state and abs(self.band_floor - state["lower_m"]) < 1e-9
        if same_band and abs(self.upper - upper) < 1e-9:
            self.events, self.successes = state["events"], state["successes"]
            return True
        # The open window was counted in a band that no longer matches; start a fresh one.
        self.events = self.successes = 0
        return False


class JumpCurriculum:
    """Success-gated height bins and per-bin guidance annealing, guide section 6.6."""

    def __init__(
        self, settings: dict, device: str, levels: tuple[float, ...] | None = None, *,
        fresh_windows: bool = False, promote_rate: float | None = None,
    ):
        self.settings = settings
        self.fresh_windows = fresh_windows
        self.promote_rate = promote_rate
        if levels is None:
            levels = settings.get("height_levels_m")
        self.levels = (
            torch.linspace(*settings["height_range_m"], 5, device=device)
            if levels is None
            else torch.tensor(levels, device=device)
        )
        self.attempts = torch.zeros_like(self.levels)
        self.successes = torch.zeros_like(self.levels)
        self.anneal_start = torch.full_like(self.levels, -1)
        self.maximum_level = 0
        self.latest_rate = torch.zeros_like(self.levels)

    def sample(self, count: int) -> tuple[torch.Tensor, torch.Tensor]:
        if "curriculum_demote_rate" in self.settings:
            bins = torch.full((count,), self.maximum_level, dtype=torch.long, device=self.levels.device)
            return bins, self.levels[bins]
        highest_probability = self.settings.get("highest_level_probability")
        if highest_probability is None or self.maximum_level == 0:
            bins = torch.randint(self.maximum_level + 1, (count,), device=self.levels.device)
        else:
            lower = torch.randint(self.maximum_level, (count,), device=self.levels.device)
            highest = torch.rand(count, device=self.levels.device) < highest_probability
            bins = torch.where(highest, self.maximum_level, lower)
        return bins, self.levels[bins]

    def record(
        self, bins: torch.Tensor, successful: torch.Tensor, iteration: float, *, promotion_allowed: bool = True
    ) -> None:
        if not bins.numel():
            return
        demotion = "curriculum_demote_rate" in self.settings
        windowed = demotion or self.fresh_windows
        if windowed:
            current = bins == self.maximum_level
            bins, successful = bins[current], successful[current]
        self.attempts.scatter_add_(0, bins, torch.ones_like(bins, dtype=torch.float))
        self.successes.scatter_add_(0, bins, successful.float())
        rate = self.successes / self.attempts.clamp_min(1)
        if windowed:
            level = self.maximum_level
            if self.attempts[level] >= self.settings["curriculum_min_events"]:
                self.latest_rate[level] = rate[level]
                threshold = self.settings["guidance_success_threshold"]
                promote = threshold if self.promote_rate is None else self.promote_rate
                passed = rate[level] > promote if demotion else rate[level] >= promote
                if passed:
                    if rate[level] >= threshold and self.anneal_start[level] < 0:
                        self.anneal_start[level] = iteration
                    if promotion_allowed:
                        self.maximum_level = min(level + 1, len(self.levels) - 1)
                elif demotion and rate[level] < self.settings["curriculum_demote_rate"]:
                    self.maximum_level = max(level - 1, 0)
                # Count the whole finishing batch once; neither failures nor successes carry into the next window.
                self.attempts.zero_()
                self.successes.zero_()
            return
        learned = (self.attempts >= self.settings["curriculum_min_events"]) & (
            rate >= self.settings["guidance_success_threshold"]
        )
        self.anneal_start = torch.where(learned & (self.anneal_start < 0), iteration, self.anneal_start)
        if bool(learned[self.maximum_level]) and self.maximum_level < len(self.levels) - 1:
            self.maximum_level += 1

    def guidance(self, bins: torch.Tensor, iteration: float) -> torch.Tensor:
        start = self.anneal_start[bins]
        progress = ((iteration - start) / self.settings["guidance_decay_iterations"]).clamp(0, 1)
        progress = torch.where(start >= 0, progress, 0)
        return 1 - progress * (1 - self.settings["guidance_final_scale"])

    def state_dict(self) -> dict:
        return dict(
            attempts=self.attempts,
            successes=self.successes,
            anneal_start=self.anneal_start,
            maximum_level=self.maximum_level,
            latest_rate=self.latest_rate,
        )

    def load_state_dict(self, state: dict) -> None:
        self.attempts.copy_(state["attempts"])
        self.successes.copy_(state["successes"])
        self.anneal_start.copy_(state["anneal_start"])
        self.maximum_level = state["maximum_level"]
        if "latest_rate" in state:
            self.latest_rate.copy_(state["latest_rate"])
