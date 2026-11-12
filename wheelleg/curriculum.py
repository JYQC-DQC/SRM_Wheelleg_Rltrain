import torch


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

    def record(self, offsets: torch.Tensor, successful: torch.Tensor) -> None:
        top = offsets >= self.band_floor
        self.events += int(top.sum())
        self.successes += int((successful & top).sum())
        if self.events >= self.settings["min_events"]:
            self.last_rate = self.successes / self.events
            if self.last_rate >= self.settings["success_rate"] and self.level < len(self.levels) - 1:
                self.level += 1
            self.events = 0
            self.successes = 0

    def state_dict(self) -> dict:
        return dict(level=self.level, events=self.events, successes=self.successes, last_rate=self.last_rate)

    def load_state_dict(self, state: dict) -> None:
        self.level, self.events, self.successes = state["level"], state["events"], state["successes"]
        self.last_rate = state["last_rate"]


class JumpCurriculum:
    """Success-gated height bins and per-bin guidance annealing, guide section 6.6."""

    def __init__(self, settings: dict, device: str, levels: tuple[float, ...] | None = None):
        self.settings = settings
        self.levels = (
            torch.linspace(*settings["height_range_m"], 5, device=device)
            if levels is None
            else torch.tensor(levels, device=device)
        )
        self.attempts = torch.zeros_like(self.levels)
        self.successes = torch.zeros_like(self.levels)
        self.anneal_start = torch.full_like(self.levels, -1)
        self.maximum_level = 0

    def sample(self, count: int) -> tuple[torch.Tensor, torch.Tensor]:
        bins = torch.randint(self.maximum_level + 1, (count,), device=self.levels.device)
        return bins, self.levels[bins]

    def record(self, bins: torch.Tensor, successful: torch.Tensor, iteration: float) -> None:
        if not bins.numel():
            return
        self.attempts.scatter_add_(0, bins, torch.ones_like(bins, dtype=torch.float))
        self.successes.scatter_add_(0, bins, successful.float())
        rate = self.successes / self.attempts.clamp_min(1)
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
        )

    def load_state_dict(self, state: dict) -> None:
        self.attempts.copy_(state["attempts"])
        self.successes.copy_(state["successes"])
        self.anneal_start.copy_(state["anneal_start"])
        self.maximum_level = state["maximum_level"]
