"""World-XY bounds and command caps for the P1 mixed-terrain free driver."""

from bisect import bisect_right
from itertools import accumulate
from math import isfinite

import torch


class ShuFreeMap:
    def __init__(self, generator, settings, device):
        # SCUT wheelbipe_V14/env.py:_get_rough_terrain_boundary_time_out uses the
        # full mesh (including border), inset by 0.5 m in rough_rotation_stair.
        margin = settings.get("edge_margin_m", 0.5)
        margin = 0.0 if margin is None else margin
        sx, sy = generator.size
        self.half_x = sx * generator.num_rows / 2
        self.half_y = sy * generator.num_cols / 2
        self.num_cols = generator.num_cols
        self.tile_y = sy
        edge_x = self.half_x + generator.border_width - margin
        edge_y = self.half_y + generator.border_width - margin
        if not (isfinite(margin) and margin >= 0 and min(edge_x, edge_y) > 0):
            raise ValueError("terrain.free_map.edge_margin_m must be nonnegative and leave a positive map extent")
        self.edge_x, self.edge_y = edge_x, edge_y

        limits = settings.get("command_limits") or {}
        terrains = generator.sub_terrains
        if unknown := limits.keys() - terrains.keys():
            raise ValueError(f"terrain.free_map.command_limits has unknown generated terrain keys: {sorted(unknown)}")
        caps = []
        fields = ("vx_abs_max_m_s", "wz_abs_max_rad_s")
        for name in terrains:
            profile = limits.get("slope" if name == "slope_inverted" else name) or {}
            if profile.keys() - set(fields):
                raise ValueError(f"terrain.free_map.command_limits.{name} accepts only {fields}")
            values = [profile.get(field) for field in fields]
            if any(v is not None and not (isfinite(v) and v > 0) for v in values):
                raise ValueError(f"terrain.free_map.command_limits.{name} caps must be positive or null")
            caps.append([torch.inf if v is None else v for v in values])
        self.column_caps = None
        # Production MixedTerrainGenerator lays out exactly one named profile per column.
        # Generic Isaac generators can repeat profiles according to their proportions.
        if len(terrains) == self.num_cols:
            columns = list(range(self.num_cols))
        else:
            weights = [getattr(cfg, "proportion", 1.0) for cfg in terrains.values()]
            cumulative = list(accumulate(w / sum(weights) for w in weights))
            columns = [
                min(bisect_right(cumulative, c / self.num_cols + 1.0e-3), len(caps) - 1) for c in range(self.num_cols)
            ]
        names = list(terrains)
        self.column_nonflat = torch.tensor([names[c] != "flat" for c in columns], device=device)
        self.column_pyramid = torch.tensor([names[c].startswith("pyramid_") for c in columns], device=device)
        if any(isfinite(v) for pair in caps for v in pair):
            if not generator.curriculum:
                raise ValueError("terrain.free_map.command_limits requires the fixed-column terrain curriculum")
            self.column_caps = torch.tensor([caps[c] for c in columns], dtype=torch.float32, device=device)

    def outside(self, position_w: torch.Tensor) -> torch.Tensor:
        x, y = position_w[:, :2].abs().unbind(-1)
        return (x > self.edge_x) | (y > self.edge_y)

    def _tile_at(self, position_w: torch.Tensor):
        x, y = position_w[:, :2].unbind(-1)
        col = ((y + self.half_y) / self.tile_y).floor().long().clamp_(0, self.num_cols - 1)
        # The outer border mesh has no terrain type; do not extend the last tile's caps onto it.
        in_tiles = (x >= -self.half_x) & (x < self.half_x) & (y >= -self.half_y) & (y < self.half_y)
        return col, in_tiles

    def reward_masks_at(self, position_w: torch.Tensor):
        """Physical shaping follows the current surface; the outer border is flat."""
        col, inside = self._tile_at(position_w)
        return inside & self.column_nonflat[col], inside & self.column_pyramid[col]

    def limits_at(self, position_w: torch.Tensor) -> torch.Tensor | None:
        if self.column_caps is None:
            return None
        col, in_tiles = self._tile_at(position_w)
        return torch.where(in_tiles[:, None], self.column_caps[col], torch.inf)
