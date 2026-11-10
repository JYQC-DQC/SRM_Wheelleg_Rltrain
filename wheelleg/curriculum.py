import torch


class CommandCurriculum:
    """Non-overlapping completed-episode windows; at most one promotion per window."""

    def __init__(self, settings: dict):
        self.settings = settings
        self.minimum = settings["min_completed_episodes"]
        if type(self.minimum) is not int or self.minimum <= 0:
            raise ValueError("command_curriculum.min_completed_episodes must be a positive integer")
        self.completed = 0
        self.successes = 0
        self.fraction = settings["initial_fraction"]

    def record(self, successful: torch.Tensor) -> float:
        self.completed += successful.numel()
        self.successes += int(successful.sum())
        if self.completed >= self.minimum:
            if self.successes / self.completed >= self.settings["success_fraction"]:
                self.fraction = min(1.0, self.fraction + self.settings["increment"])
            # The entire finishing batch belongs to this window; never reuse its successes.
            self.completed = 0
            self.successes = 0
        return self.fraction

    def state_dict(self) -> dict:
        return dict(completed=self.completed, successes=self.successes, fraction=self.fraction)

    def load_state_dict(self, state: dict) -> None:
        self.completed, self.successes, self.fraction = state["completed"], state["successes"], state["fraction"]


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
