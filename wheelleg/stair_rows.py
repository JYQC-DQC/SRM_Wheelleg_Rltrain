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
        self.top_cleared = torch.zeros_like(self.levels, dtype=torch.bool)

    def update(
        self,
        env_ids: torch.Tensor,
        displacement: torch.Tensor,
        tracking_fraction: torch.Tensor,
        reverse_center_goal: torch.Tensor,
    ) -> torch.Tensor:
        """Settle unique finished IDs; return their new rows in ID order.

        All inputs are aligned 1-D tensors on the curriculum device. Displacement is
        horizontal distance in meters; reverse_center_goal is a boolean completion flag.
        """
        up = (displacement > self._half_tile) | reverse_center_goal
        down = (tracking_fraction < 0.4) & ~up
        levels = (self.levels[env_ids] + up.long() - down.long()).clamp_min_(0)
        # Entering the highest row is not a clear; promotion from it unlocks later sampling.
        replay = (levels >= self.rows).nonzero(as_tuple=True)[0]
        levels[replay] = torch.randint(self.rows, replay.shape, device=levels.device, generator=self._generator)
        self.top_cleared[env_ids[replay]] = True
        self.levels[env_ids] = levels
        return levels

    def state_dict(self) -> dict[str, torch.Tensor]:
        return {"levels": self.levels.clone(), "top_cleared": self.top_cleared.clone()}

    def load_state_dict(self, state: dict[str, torch.Tensor]) -> None:
        levels, top_cleared = state["levels"], state["top_cleared"]
        if levels.shape != self.levels.shape or top_cleared.shape != self.top_cleared.shape:
            raise ValueError("stair-row checkpoint must match the number of environments")
        if levels.dtype != torch.long or top_cleared.dtype != torch.bool:
            raise ValueError("stair-row checkpoint requires long levels and bool top_cleared")
        if ((levels < 0) | (levels >= self.rows)).any():
            raise ValueError("stair-row checkpoint levels are outside the configured rows")
        self.levels.copy_(levels)
        self.top_cleared.copy_(top_cleared)
