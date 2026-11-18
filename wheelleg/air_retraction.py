"""Per-frame excess leg retraction during eligible pre-contact descent (meters)."""

import torch


class AirRetractionTracker:
    """Track peak-to-trough excursions independently for both legs of each environment."""

    def __init__(
        self, num_envs: int, tolerance_m: float, device: str | torch.device, *, dtype: torch.dtype = torch.float32,
        base_threshold_m: float | None = None,
    ) -> None:
        if tolerance_m < 0:
            raise ValueError("tolerance_m must be nonnegative")
        self.tolerance_m = tolerance_m
        if base_threshold_m is not None and base_threshold_m <= tolerance_m:
            raise ValueError("base_threshold_m must exceed the length-counting tolerance")
        self.base_threshold_m = base_threshold_m
        self._peak = torch.zeros(num_envs, 2, device=device, dtype=dtype)
        self._trough = torch.zeros_like(self._peak)
        self._active = torch.zeros(num_envs, device=device, dtype=torch.bool)
        # Both diagnostics are [environment, leg]; the fourth-excursion mask is a one-frame pulse.
        self.excursion_count = torch.zeros_like(self._peak, dtype=torch.long)
        self.fourth_excursion = torch.zeros_like(self._peak, dtype=torch.bool)
        self.base_crossing = torch.zeros_like(self.fourth_excursion)

    def reset(self, ids: torch.Tensor) -> None:
        """Start a new jump and take the next eligible frame as its baseline."""
        self._active[ids] = False
        self.excursion_count[ids] = 0
        self.fourth_excursion[ids] = False
        self.base_crossing[ids] = False

    @torch.no_grad()
    def update(self, lengths_m: torch.Tensor, eligible: torch.Tensor) -> torch.Tensor:
        """Once an excursion qualifies, charge its full length, then only newly reached depth."""
        continuous = (eligible & self._active)[:, None]
        threshold = self.tolerance_m + torch.finfo(lengths_m.dtype).eps
        rebound = lengths_m - self._trough > threshold
        new_peak = ~continuous | rebound | (lengths_m > self._peak)
        peak = torch.where(new_peak, lengths_m, self._peak)
        old_trough = torch.where(new_peak, lengths_m, self._trough)
        trough = torch.minimum(old_trough, lengths_m)

        # A fall back to an already charged trough contributes nothing.
        previous, current = peak - old_trough, peak - trough
        # Account for float32 cancellation when e.g. 0.300 - 0.295 should equal the tolerance.
        previous_qualified, qualified = previous > threshold, current > threshold
        delta = torch.where(qualified, current, 0.0) - torch.where(previous_qualified, previous, 0.0)
        new_excursion = eligible[:, None] & qualified & ~previous_qualified
        self.excursion_count.add_(new_excursion)
        self.fourth_excursion.copy_(new_excursion & (self.excursion_count == 4))
        if self.base_threshold_m is not None:
            base = self.base_threshold_m + torch.finfo(lengths_m.dtype).eps
            self.base_crossing.copy_(eligible[:, None] & (current > base) & (previous <= base))
        self._peak.copy_(peak)
        self._trough.copy_(trough)
        self._active.copy_(eligible)
        return delta
