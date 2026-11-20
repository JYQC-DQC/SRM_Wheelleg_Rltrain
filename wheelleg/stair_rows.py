"""Per-environment stair-row curriculum, settled on episode reset."""

from math import isfinite

import torch


class StairRowCurriculum:
    def __init__(
        self,
        num_envs: int,
        rows: int,
        tile_length: float,
        device: str | torch.device,
        *,
        generator: torch.Generator | None = None,
    ) -> None:
        if rows < 1:
            raise ValueError("rows must be positive")
        if not isfinite(tile_length) or tile_length <= 0:
            raise ValueError("tile_length must be finite and positive (meters)")
        self.rows = rows
        self._half_tile = tile_length / 2
        self._generator = generator
        self.levels = torch.randint(min(6, rows), (num_envs,), device=device, generator=generator)

    def update(
        self,
        env_ids: torch.Tensor,
        displacement: torch.Tensor,
        tracking_fraction: torch.Tensor,
        reverse_descent_completed: torch.Tensor,
    ) -> torch.Tensor:
        """Settle unique finished IDs; return their new rows in ID order.

        All inputs are aligned 1-D tensors on the curriculum device. Displacement is
        horizontal distance in meters; reverse_descent_completed is a boolean completion flag.
        """
        up = (displacement > self._half_tile) | reverse_descent_completed
        down = (tracking_fraction < 0.4) & ~up
        levels = (self.levels[env_ids] + up.long() - down.long()).clamp_min_(0)
        # Entering the highest row is not a clear; promotion from it triggers replay only.
        replay = (levels >= self.rows).nonzero(as_tuple=True)[0]
        levels[replay] = torch.randint(self.rows, replay.shape, device=levels.device, generator=self._generator)
        self.levels[env_ids] = levels
        return levels

    def state_dict(self) -> dict[str, torch.Tensor]:
        return {"levels": self.levels.clone()}

    def load_state_dict(self, state: dict[str, torch.Tensor]) -> None:
        levels = state["levels"]  # Older checkpoints may also include an unused tower-unlock flag.
        if levels.shape != self.levels.shape:
            raise ValueError("stair-row checkpoint must match the number of environments")
        if levels.dtype != torch.long:
            raise ValueError("stair-row checkpoint requires integer levels")
        if ((levels < 0) | (levels >= self.rows)).any():
            raise ValueError("stair-row checkpoint levels are outside the configured rows")
        self.levels.copy_(levels)
