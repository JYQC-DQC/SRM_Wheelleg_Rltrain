"""SHU P1 curricula. Call record once per settled event, not once per reset/rollout."""

from collections.abc import Sequence
from math import isfinite

import torch

# Six sampled motion profiles (brake/reverse is conditional on the previous issued vx).
STAND, STRAIGHT, TURN, COMBINED, DASH, BRAKE_REVERSE = range(6)
N_KINDS = 6


class FlatCommandCurriculum:
    """Per-profile difficulty and counts on device. Minimum window sizes are NOT SHU defaults."""

    def __init__(self, initial_fraction: float | Sequence[float], min_segments: int | Sequence[int], device: str):
        self.fraction = torch.as_tensor(initial_fraction, device=device, dtype=torch.float32).expand(N_KINDS).clone()
        self.minimum = torch.as_tensor(min_segments, device=device).expand(N_KINDS).clone()
        if not ((self.fraction > 0) & (self.fraction <= 1)).all():
            raise ValueError("initial_fraction must be in (0,1] for every flat command bucket")
        if self.minimum.is_floating_point() or self.minimum.dtype == torch.bool or not (self.minimum > 0).all():
            raise ValueError("min_segments must be positive integers")
        self.attempts = torch.zeros(N_KINDS, device=device, dtype=torch.long)
        self.successes = torch.zeros_like(self.attempts)
        self.completed = torch.zeros_like(self.attempts)  # lifetime: includes normal tracking failures
        self.falls = torch.zeros_like(self.attempts)
        self.interruptions = torch.zeros_like(self.attempts)

    def record(
        self,
        kind: torch.Tensor,
        fraction: torch.Tensor,
        completed: torch.Tensor,
        successful: torch.Tensor,
        fell: torch.Tensor,
        interrupted: torch.Tensor,
    ) -> None:
        """(M,) finalized segments; a fall beats completion and is a failed attempt, not a truncation."""
        interrupted = interrupted & ~fell
        completed = completed & ~fell & ~interrupted
        for counter, mask in ((self.completed, completed), (self.falls, fell), (self.interruptions, interrupted)):
            counter.scatter_add_(0, kind, mask.long())
        same_level = fraction == self.fraction[kind]  # pending older segments cannot promote the new level
        self.attempts.scatter_add_(0, kind, ((completed | fell) & same_level).long())
        self.successes.scatter_add_(0, kind, (successful & completed & same_level).long())
        closed = self.attempts >= self.minimum
        promote = closed & (5 * self.successes >= 3 * self.attempts)
        next_fraction = self.fraction + 0.1
        # Last binary32 addition can land one ULP below 1. Keep all_full a strict, transferable fact.
        next_fraction = torch.where(next_fraction >= 1 - torch.finfo(next_fraction.dtype).eps, 1.0, next_fraction)
        self.fraction.copy_(torch.where(promote, next_fraction, self.fraction))
        self.attempts.masked_fill_(closed, 0)
        self.successes.masked_fill_(closed, 0)

    def state_dict(self) -> dict:
        return {k: v.clone() for k, v in vars(self).items()}

    def load_state_dict(self, state: dict) -> None:
        if not torch.equal(self.minimum, state["minimum"].to(self.minimum.device)):
            raise ValueError("flat segment window configuration differs from checkpoint")
        for key, value in vars(self).items():
            value.copy_(state[key])


class AirHeightCurriculum:
    """Four drop-offset bands, three promotions. Zero-based level/birth_band; H4 provisionally 0.45 m.

    H0..H4 are explicit, strictly increasing reviewed inputs, never inferred from a reference car.
    Only the latest band supplies the 512-event windows. Split stances and light scrapes are not vetoes.
    """

    def __init__(self, edges_m: Sequence[float], device: str):
        if (
            len(edges_m) != 5
            or not all(isfinite(v) and v >= 0 for v in edges_m)
            or any(b <= a for a, b in zip(edges_m, edges_m[1:]))
        ):
            raise ValueError("edges_m must contain calibrated H0 < H1 < H2 < H3 < H4 in metres")
        self.edges_m = tuple(edges_m)
        self.edges = torch.tensor(edges_m, dtype=torch.float32, device=device)
        self.level = self.events = self.successes = 0
        self.last_rate = None

    def sample(self, count: int) -> tuple[torch.Tensor, torch.Tensor]:
        """Returns (offset_m, actual_birth_band), each (N,), for air births only."""
        e, level = self.edges, self.level
        u = torch.rand(count, device=e.device)
        if level < 2:
            h = e[0] + (e[level + 1] - e[0]) * u
        else:
            latest = torch.rand_like(u) < 0.40
            h = torch.where(latest, e[level + 1] - (e[level + 1] - e[level]) * u, e[0] + (e[level] - e[0]) * u)
        return h, torch.bucketize(h, e[1:-1], right=False)

    def record(self, birth_band: torch.Tensor, caught: torch.Tensor, valid: torch.Tensor) -> None:
        """Event pulses: first catch or hard hit/fall/post-touch timeout; never external cut/no-touch/bad spawn.

        Stable input order breaks ties at a policy tick. Overflow after a failed window starts the next one;
        after promotion, overflow still belongs to the old band. At the top, keep reporting fresh windows.
        """
        results = caught[valid & (birth_band == self.level)]
        while results.numel():
            n = min(512 - self.events, results.numel())
            self.successes += int(results[:n].sum())
            self.events += n
            results = results[n:]
            if self.events == 512:
                self.last_rate = self.successes / 512
                promote = self.successes >= 308 and self.level < 3
                self.events = self.successes = 0
                if promote:
                    self.level += 1
                    break

    def state_dict(self) -> dict:
        return {k: getattr(self, k) for k in ("edges_m", "level", "events", "successes", "last_rate")}

    def load_state_dict(self, state: dict) -> None:
        if tuple(state["edges_m"]) != self.edges_m:
            raise ValueError("drop-height edges differ from checkpoint")
        self.level, self.events, self.successes, self.last_rate = (
            state[k] for k in ("level", "events", "successes", "last_rate")
        )
