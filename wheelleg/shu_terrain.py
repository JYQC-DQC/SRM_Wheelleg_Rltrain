"""P1 mixed-terrain sampling and per-environment stair-row progression."""

from math import floor, isclose, isfinite
from typing import NamedTuple

import torch

from .stair_rows import StairRowCurriculum

FLAT_PROPORTION = 0.30
FREE_PROFILES = ("flat", "rough", "grid", "slope")
STAIR_PROFILES = ("pyramid_up", "pyramid_down")
MIXED_PROFILES = FREE_PROFILES + STAIR_PROFILES
MIXED_COLUMN_PROFILES = MIXED_PROFILES + STAIR_PROFILES + ("slope_inverted",)

# Straight-stair compatibility for synthetic fixtures only.
LEGACY_STEP_COUNTS = {"single": 1, "double": 2, "triple": 3}
LEGACY_STAIR_PROFILES = tuple(f"{steps}_{direction}" for direction in ("up", "down") for steps in LEGACY_STEP_COUNTS)
LEGACY_PROFILES = FREE_PROFILES + LEGACY_STAIR_PROFILES


def mixed_columns(settings, *, production=False):
    """Return (logical profile, raised edge, concentric pyramid) in physical atlas order."""
    configured = set(settings.get("profiles", MIXED_PROFILES))
    legacy = not production and configured == set(LEGACY_PROFILES)
    profiles, stairs = (LEGACY_PROFILES, LEGACY_STAIR_PROFILES) if legacy else (MIXED_PROFILES, STAIR_PROFILES)
    if configured != set(profiles):
        raise ValueError(f"terrain.profiles must contain exactly {', '.join(profiles)}")
    return (
        [(name, False, not legacy and name in stairs) for name in profiles]
        + [(name, True, not legacy) for name in stairs]
        + ([] if legacy else [("slope_inverted", False, False)])
    )


class PyramidLayout(NamedTuple):
    riser_half_widths_m: tuple[float, ...]  # Square main risers, outermost to innermost.
    platform_half_width_m: float
    obstacle_half_width_m: float  # Includes the first lip if it projects onto the outer apron.


def natural_pyramid_layout(size, geometry, *, down, lip_width_m):
    """Pack whole riser intervals outward from the exact square, clear central platform.

    first_edge_x_m is the minimum flat apron from a tile edge to the first
    obstruction (not the distance from spawn). The short tile axis limits the
    count; all unused width remains outside. Tread is main-riser pitch, so a
    lip takes some of the flat run between risers, but none of the center.
    """
    border, tread, platform = (geometry[k] for k in ("first_edge_x_m", "step_width_m", "platform_width_m"))
    if any(v is None or not isfinite(v) or v <= 0 for v in (border, tread, platform)):
        raise ValueError("pyramid first_edge_x_m, step_width_m and platform_width_m must be positive and finite")
    if not 0 <= lip_width_m < tread:
        raise ValueError("pyramid stair_lip.width_m must fit within the tread")
    half = platform / 2
    # Up: shift the last main riser outward to leave room for its lip. Down:
    # the lip is on the high side of each riser, including on the outer apron.
    available = min(size) / 2 - border - lip_width_m - half
    # Include an exact fit despite floating-point subtraction at nominal decimal dimensions.
    count = floor((available + 1e-9) / tread) + 1
    if count < 1:
        raise ValueError("pyramid cannot fit a riser between first_edge_x_m and the clear platform")
    inner_riser = half if down else half + lip_width_m
    risers = tuple(inner_riser + i * tread for i in reversed(range(count)))
    return PyramidLayout(risers, half, risers[0] + (lip_width_m if down else 0.0))


def stair_lip_dimensions(settings: dict) -> tuple[float, float]:
    lip = settings.get("stair_lip")
    if lip is None:
        raise ValueError("terrain.stair_lip requires measured height_m and width_m")
    height, width = lip.get("height_m"), lip.get("width_m")
    if any(value is None or not isfinite(value) or value <= 0 for value in (height, width)):
        raise ValueError("terrain.stair_lip.height_m and width_m must be positive and finite")
    return height, width


def route_active(traverse: torch.Tensor, forward_command: torch.Tensor) -> torch.Tensor:
    """World-route progress/stuck cannot apply to free driving, standstill or turn-in-place."""
    return traverse & (forward_command > 0)


def route_progress_and_stuck(
    active: torch.Tensor,
    x: torch.Tensor,
    previous_x: torch.Tensor,
    stuck_start_x: torch.Tensor,
    stuck_time: torch.Tensor,
    stuck: torch.Tensor,
    *,
    dt: float,
    window_s: float,
    distance_m: float,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    """World +X only. Leaving the active route clears the entire stall window."""
    progress = torch.where(active, x - previous_x, 0.0)
    elapsed = torch.where(active, stuck_time + dt, 0.0)
    ready = active & (elapsed >= window_s)
    start = torch.where(stuck_time > 0, stuck_start_x, previous_x)
    stuck = active & torch.where(ready, x - start < distance_m, stuck)
    start = torch.where(ready | ~active, x, start)
    return progress, start, torch.where(ready, 0.0, elapsed), stuck


class MixedTerrainRuntime:
    """Assign physical tile columns while recording curriculum by logical profile."""

    def __init__(self, settings: dict, count: int, device: str):
        self.stair_rows = StairRowCurriculum(count, settings["rows"], settings["tile_size_m"][0], device)
        self.settings = settings
        profiles = settings["profiles"]
        columns = mixed_columns(settings)
        self.natural_pyramids = columns[len(FREE_PROFILES)][2]
        self.profile_names = MIXED_PROFILES if self.natural_pyramids else LEGACY_PROFILES
        stair_profiles = self.profile_names[len(FREE_PROFILES) :]
        self.column_profiles = torch.tensor(
            [self.profile_names.index("slope" if name == "slope_inverted" else name) for name, _, _ in columns],
            device=device,
        )
        self.rows = torch.tensor([profiles[name]["row_range"] for name in self.profile_names], device=device)
        if self.rows.shape != (len(self.profile_names), 2) or self.rows.dtype != torch.long:
            raise ValueError("Mixed terrain needs two integer row_range endpoints per profile")
        if not (
            (self.rows[:, 0] >= 0) & (self.rows[:, 0] <= self.rows[:, 1]) & (self.rows[:, 1] < settings["rows"])
        ).all():
            raise ValueError("Mixed terrain row_range must be ordered and within the generated rows")
        if any(tuple(profiles[name]["row_range"]) != (0, settings["rows"] - 1) for name in stair_profiles):
            raise ValueError("stair profiles must cover all curriculum rows")
        modes = [profiles[name]["command_mode"] for name in self.profile_names]
        if any(mode not in ("free", "traverse") for mode in modes) or modes[0] != "free":
            raise ValueError("Mixed terrain command_mode must be free or traverse, with flat always free")
        if self.natural_pyramids and modes != ["free"] * len(FREE_PROFILES) + ["traverse"] * len(STAIR_PROFILES):
            raise ValueError("P1 production requires free terrain and traverse pyramid profiles")
        self.route_columns = torch.tensor([mode == "traverse" for mode in modes], device=device)
        route = settings["route"]
        lo, hi = route["vx_range_m_s"]
        if not (isfinite(lo) and isfinite(hi) and 0 < lo <= hi):
            raise ValueError("terrain.route.vx_range_m_s must be positive and ordered")
        sx, sy = settings["tile_size_m"]
        clearance = route["clearance_m"]
        if clearance is None or not isfinite(clearance) or not 0 < 2 * clearance < min(sx, sy):
            raise ValueError("terrain.route.clearance_m must leave room within the tile")
        self.reverse_share = route["reverse_descent_share_of_stairs"] if self.natural_pyramids else 0.0
        if self.reverse_share is None or not 0 <= self.reverse_share <= 1:
            raise ValueError("terrain.route.reverse_descent_share_of_stairs must be in [0, 1]")
        _, lip_width = stair_lip_dimensions(settings)
        self.tile_half = torch.tensor((sx / 2, sy / 2), device=device)
        self.clearance = clearance
        obstacles, exits = [], []
        for name, lip, pyramid in columns:
            p = profiles["slope" if name == "slope_inverted" else name]
            depth = lip_width if lip else 0.0
            down = name.endswith("_down")
            if pyramid:
                layout = natural_pyramid_layout((sx, sy), p["geometry"], down=down, lip_width_m=depth)
                if layout.platform_half_width_m <= clearance or layout.obstacle_half_width_m + 2 * clearance >= sx / 2:
                    raise ValueError(f"{name}: pyramid needs clear central and outer platforms")
                obstacles.append(layout.obstacle_half_width_m)
            else:
                obstacles.append(0.0)
            if pyramid or p["command_mode"] != "traverse":
                exits.append((0.0, 0.0, 0.0))
                continue
            # Synthetic straight fixtures measure their exit from the old off-center spawn.
            g = p["geometry"]
            spawn = g["spawn_x_m"]
            if name in stair_profiles:
                steps = LEGACY_STEP_COUNTS[name.split("_")[0]]
                first, tread = g["first_edge_x_m"], g["step_width_m"]
                obstacle_start = first - (depth if down else 0.0)
                obstacle_end = first + (steps - 1) * tread + (0.0 if down else depth)
            elif name == "slope":
                obstacle_start, obstacle_end = sx / 4, 3 * sx / 4
            else:
                obstacle_start, obstacle_end = g["surface_x_range_m"]
            distance = p["exit_distance_m"]
            if not (
                clearance <= spawn < obstacle_start - clearance
                and obstacle_end + clearance < spawn + distance < sx - clearance
            ):
                raise ValueError(f"{name}: route spawn and exit must clear the obstacle and tile boundaries")
            exits.append((distance, sx - clearance - spawn, sy / 2 - clearance))
        self.obstacle_half_widths = torch.tensor(obstacles, device=device)
        self.exit_boxes = torch.tensor(exits, device=device)
        if self.natural_pyramids:
            self.inverted_slope_col = columns.index(("slope_inverted", False, False))
        self.traverse = torch.zeros(count, dtype=torch.bool, device=device)
        self.assigned = torch.zeros_like(self.traverse)
        self.crossed = torch.zeros_like(self.traverse)
        self.reverse_completed = torch.zeros_like(self.traverse)
        self._outward_path = torch.zeros_like(self.traverse)
        self.reverse_descent = torch.zeros_like(self.traverse)
        self.reward_active = torch.zeros_like(self.traverse)
        self.draw_weights = self._distribution(device)

    def _distribution(self, device):
        groups = self.settings["groups"]
        if (
            set(groups) != {"rough", "grid", "slope", "stairs"}
            or not isclose(sum(groups.values()), 0.70)
            or any(not isfinite(v) or v <= 0 for v in groups.values())
        ):
            raise ValueError("non-flat groups must have positive shares totalling 0.70")
        draw = torch.zeros(3 if self.natural_pyramids else 1, len(self.profile_names), device=device)
        draw[0, : len(FREE_PROFILES)] = draw.new_tensor(
            [FLAT_PROPORTION, groups["rough"], groups["grid"], groups["slope"]]
        )
        if self.natural_pyramids:
            raised = self.profile_names.index("pyramid_up")
            inverted = self.profile_names.index("pyramid_down")
            draw[1, [raised, inverted]] = groups["stairs"] * (1 - self.reverse_share) / 2
            draw[2, raised] = groups["stairs"] * self.reverse_share
        else:
            for direction in ("up", "down"):
                names = [f"{steps}_{direction}" for steps in LEGACY_STEP_COUNTS]
                values = [self.settings["stair_weights"][name] for name in names]
                if any(v is None or not isfinite(v) or v <= 0 for v in values):
                    raise ValueError("stair weights must be positive and finite")
                draw[0, [self.profile_names.index(name) for name in names]] = draw.new_tensor(values) * (
                    groups["stairs"] / (2 * sum(values))
                )
        return draw.flatten()

    @property
    def route_open(self) -> torch.Tensor:
        # Production routes keep their commands through the whole episode.
        return self.traverse if self.natural_pyramids else self.traverse & ~self.crossed

    def step(
        self,
        terrain,
        previous_w: torch.Tensor,
        position_w: torch.Tensor,
        forward_m_s: torch.Tensor,
        terminated: torch.Tensor,
        wheel_contact: torch.Tensor | None = None,
    ) -> None:
        """Certify supported arrival separately from world +X progress/stuck scoring."""
        cols = terrain.terrain_types
        origin = terrain.env_origins[:, :2]
        xy = position_w[:, :2] - origin
        previous_xy = previous_w[:, :2] - origin
        route = self.route_open & ~terminated
        if self.natural_pyramids:
            if wheel_contact is None:
                raise ValueError("pyramid route acceptance requires current wheel_contact (N, 2)")
            route &= ~(self.crossed | self.reverse_completed)
            obstacle = self.obstacle_half_widths[cols, None]
            # Distance to the square obstruction, including any outer lip. Keep the
            # whole apron, including corners, but inset it from the neighboring tiles.
            xy, previous_xy = xy.abs(), previous_xy.abs()
            gap_sq = (xy - obstacle).clamp_min(0).square().sum(-1)
            # Require a path from the obstruction's footprint within this tile, not a
            # re-entry from a neighbor. A hop may clear the riser before it lands.
            previous_on_pyramid = (previous_xy <= obstacle).all(-1)
            self._outward_path.copy_(
                route
                & (xy < self.tile_half).all(-1)
                & (previous_xy < self.tile_half).all(-1)
                & (previous_on_pyramid | self._outward_path)
            )
            safe_floor = (gap_sq >= self.clearance**2) & (xy <= self.tile_half - self.clearance).all(-1)
            completed = self._outward_path & safe_floor & wheel_contact.any(-1)
            self.crossed |= completed & ~self.reverse_descent
            self.reverse_completed |= completed & self.reverse_descent
            self.reward_active.copy_(route_active(route & ~completed, forward_m_s))
        else:
            active = route_active(route, forward_m_s)
            self.reward_active.copy_(active)
            supported = route if wheel_contact is None else route & wheel_contact.any(-1)
            exit_x, end_x, exit_y = self.exit_boxes[cols].unbind(-1)
            x, y = xy.unbind(-1)
            at_exit = supported & (x >= exit_x) & (x <= end_x) & (y.abs() <= exit_y)
            self.crossed |= at_exit & active & (previous_xy[:, 0] < exit_x)

    def reset(
        self,
        terrain,
        ids: torch.Tensor,
        completed: torch.Tensor,
        terminated: torch.Tensor,
        *,
        evaluation: bool,
        final_xy=None,
        tracking_fraction=None,
    ) -> None:
        if not ids.numel():
            return
        if not evaluation:
            done = ids[completed[ids] & self.assigned[ids] & self.traverse[ids]]
            if done.numel():
                if final_xy is None or tracking_fraction is None:
                    raise ValueError("settling stairs requires final world XY and full-episode tracking score")
                displacement = (final_xy[done] - terrain.env_origins[done, :2]).norm(dim=-1)
                self.stair_rows.update(
                    done,
                    displacement,
                    tracking_fraction[done],
                )
        # Tower geometry is independent of row promotion/replay.
        draw = torch.multinomial(self.draw_weights, len(ids), replacement=True)
        n_profiles = len(self.profile_names)
        mode, profiles = draw // n_profiles, draw % n_profiles
        is_stair = profiles >= len(FREE_PROFILES)
        lo, hi = self.rows[profiles].unbind(-1)
        if evaluation:
            rows = hi
        else:
            free_row = lo + (torch.rand(len(ids), device=ids.device) * (hi - lo + 1)).long()
            rows = torch.where(is_stair, self.stair_rows.levels[ids], free_row)
        with_lip = is_stair & (torch.rand(len(ids), device=ids.device) < 0.5)
        cols = profiles + with_lip * (n_profiles - len(FREE_PROFILES))
        if self.natural_pyramids:
            slope = profiles == self.profile_names.index("slope")
            cols = torch.where(slope & (torch.rand(len(ids), device=ids.device) < 0.5), self.inverted_slope_col, cols)
        self.reverse_descent[ids] = mode == 2
        terrain.terrain_types[ids] = cols
        terrain.terrain_levels[ids] = rows
        terrain.env_origins[ids] = terrain.terrain_origins[rows, cols]
        self.traverse[ids] = self.route_columns[profiles]
        self.assigned[ids] = True
        self.crossed[ids] = self.reverse_completed[ids] = self.reward_active[ids] = False
        self._outward_path[ids] = False

    def state_dict(self) -> dict:
        return {"stair_rows": self.stair_rows.state_dict()}

    def load_state_dict(self, state: dict) -> None:
        if "stair_rows" not in state:
            raise ValueError(
                "old mixed-terrain checkpoint lacks per-environment stair rows; use weight-only initialization"
            )
        self.stair_rows.load_state_dict(state["stair_rows"])
        # The simulator may already have reset to a fresh tile before the runner loads.
        # Do not grade that unrelated initial episode against the restored difficulty.
        self.assigned.zero_()
