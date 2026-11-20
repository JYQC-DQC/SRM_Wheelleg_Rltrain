"""P1 mixed-terrain sampling and same-direction triple-step prerequisites."""

from math import isclose, isfinite

import torch

FLAT_PROPORTION = 0.30
BASE_PROFILES = ("flat", "rough", "grid", "slope", "single_up", "double_up", "single_down", "double_down")
PREREQUISITES = {
    "triple_up": ("single_up", "double_up"),
    "triple_down": ("single_down", "double_down"),
}
MIXED_PROFILES = BASE_PROFILES + tuple(PREREQUISITES)
STAIR_PROFILES = MIXED_PROFILES[4:]
MIXED_COLUMN_PROFILES = MIXED_PROFILES + STAIR_PROFILES


def mixed_columns(settings):
    # (logical approach profile, raised edge, full concentric pyramid).
    cols = [(name, i >= len(MIXED_PROFILES), False) for i, name in enumerate(MIXED_COLUMN_PROFILES)]
    if "pyramid" in settings:
        cols.extend((name, lip, True) for lip in (False, True) for name in STAIR_PROFILES)
    return cols


def pyramid_extent(size, first_edge, tread, count, lip_width):
    sx, sy = size
    half_x = sx / 2 - first_edge
    half_y = min(half_x, sy / 2 - first_edge)
    if first_edge <= lip_width or min(half_x, half_y) - (count - 1) * tread <= lip_width:
        raise ValueError("pyramid must leave room for outer flat, treads, lip and central platform")
    return half_x, half_y


def stair_lip_dimensions(settings: dict) -> tuple[float, float]:
    lip = settings.get("stair_lip")
    if lip is None:
        raise ValueError("terrain.stair_lip requires measured height_m and width_m")
    height, width = lip.get("height_m"), lip.get("width_m")
    if any(value is None or not isfinite(value) or value <= 0 for value in (height, width)):
        raise ValueError("terrain.stair_lip.height_m and width_m must be positive and finite")
    return height, width


class MixedTerrainCurriculum:
    """Immutable direction unlocks from finalized outcomes at each prerequisite's configured row."""

    def __init__(self, gates: dict):
        self.gates = gates
        self.unlocked = dict.fromkeys(PREREQUISITES, False)
        self.passed = {profile: False for pair in PREREQUISITES.values() for profile in pair}
        self.counts = dict.fromkeys(self.passed, (0, 0))
        for profile in self.passed:
            gate = gates[profile]
            if type(gate["row"]) is not int or gate["row"] < 0:
                raise ValueError(f"{profile}: required zero-based difficulty row is not set")
            if type(gate["window"]) is not int or gate["window"] <= 0:
                raise ValueError(f"{profile}: positive attempt window is required")
            fraction = gate["success_fraction"]
            if fraction is None or not 0 < fraction <= 1:
                raise ValueError(f"{profile}: success_fraction must be in (0, 1]")

    def record(self, profile: str, row: torch.Tensor, success: torch.Tensor) -> None:
        """Record one batch of finalized attempts for a single profile; other rows don't count."""
        if profile not in self.passed or self.passed[profile]:
            return
        gate = self.gates[profile]
        results = success[row == gate["row"]]
        if not results.numel():
            return
        attempts, successes = self.counts[profile]
        attempts += results.numel()
        successes += int(results.sum())
        if attempts < gate["window"]:
            self.counts[profile] = (attempts, successes)
            return
        self.counts[profile] = (0, 0)
        self.passed[profile] = successes / attempts >= gate["success_fraction"]
        for triple, pair in PREREQUISITES.items():
            self.unlocked[triple] = all(self.passed[name] for name in pair)

    def proportions(self, groups: dict, stair_weights: dict, locked_stair_weights: dict) -> dict[str, float]:
        """Split each direction's fixed stair quota using its own unlock state."""
        if (
            set(groups) != {"rough", "grid", "slope", "stairs"}
            or any(v is None or not isfinite(v) or v <= 0 for v in groups.values())
            or not isclose(sum(groups.values()), 1 - FLAT_PROPORTION)
        ):
            raise ValueError("rough/grid/slope/stairs need explicit positive fractions summing to 0.70")
        result = {name: groups[name] for name in ("rough", "grid", "slope")}
        result["flat"] = FLAT_PROPORTION
        if (
            locked_stair_weights is None
            or set(locked_stair_weights) != {"single", "double"}
            or any(v is None or not isfinite(v) or v <= 0 for v in locked_stair_weights.values())
        ):
            raise ValueError("terrain.locked_stair_weights needs positive single and double weights")
        # Preserve both directions' quotas: unlocking ascent must not reduce descent sampling.
        stair_names = tuple(name for pair in PREREQUISITES.values() for name in pair)
        for name in (*stair_names, *(key for key, enabled in self.unlocked.items() if enabled)):
            value = stair_weights[name]
            if value is None or not isfinite(value) or value <= 0:
                raise ValueError(f"{name}: an explicit positive stair weight is required")
        base_total = sum(stair_weights[name] for name in stair_names)
        for triple, pair in PREREQUISITES.items():
            share = groups["stairs"] * sum(stair_weights[name] for name in pair) / base_total
            if self.unlocked[triple]:
                weights = {name: stair_weights[name] for name in (*pair, triple)}
            else:
                weights = {name: locked_stair_weights[name.split("_")[0]] for name in pair}
            denominator = sum(weights.values())
            result.update({name: share * weight / denominator for name, weight in weights.items()})
        return {name: result.get(name, 0.0) for name in MIXED_PROFILES}


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


class MixedTerrainRuntime(MixedTerrainCurriculum):
    """Assign physical tile columns while recording curriculum by logical profile."""

    def __init__(self, settings: dict, count: int, device: str):
        super().__init__(settings["gates"])
        self.settings = settings
        profiles = settings["profiles"]
        columns = mixed_columns(settings)
        self.pyramid_share = settings.get("pyramid", {}).get("share_of_stairs", 0.0)
        if self.pyramid_share is None or not 0 <= self.pyramid_share <= 1:
            raise ValueError("terrain.pyramid.share_of_stairs must be confirmed in [0,1]")
        self.column_profiles = torch.tensor([MIXED_PROFILES.index(name) for name, _, _ in columns], device=device)
        self.rows = torch.tensor([profiles[name]["row_range"] for name in MIXED_PROFILES], device=device)
        if self.rows.shape != (len(MIXED_PROFILES), 2) or self.rows.dtype != torch.long:
            raise ValueError("Mixed terrain needs two integer row_range endpoints per profile")
        if not (
            (self.rows[:, 0] >= 0) & (self.rows[:, 0] <= self.rows[:, 1]) & (self.rows[:, 1] < settings["rows"])
        ).all():
            raise ValueError("Mixed terrain row_range must be ordered and within the generated rows")
        for name, gate in self.gates.items():
            low, high = profiles[name]["row_range"]
            if not low <= gate["row"] <= high or profiles[name]["command_mode"] != "traverse":
                raise ValueError(f"{name}: gate must be reachable by a sampled traverse episode")
        modes = [profiles[name]["command_mode"] for name in MIXED_PROFILES]
        if any(mode not in ("free", "traverse") for mode in modes) or modes[0] != "free":
            raise ValueError("Mixed terrain command_mode must be free or traverse, with flat always free")
        self.route_columns = torch.tensor([mode == "traverse" for mode in modes], device=device)
        route = settings["route"]
        lo, hi = route["vx_range_m_s"]
        if not (isfinite(lo) and isfinite(hi) and 0 < lo <= hi):
            raise ValueError("terrain.route.vx_range_m_s must be positive and ordered")
        for key in ("heading_kp", "heading_max_wz_rad_s"):
            if not (isfinite(route[key]) and route[key] > 0):
                raise ValueError(f"terrain.route.{key} must be positive and finite")
        sx, sy = settings["tile_size_m"]
        width, clearance = route["corridor_width_m"], route["clearance_m"]
        if not (isfinite(width) and isfinite(clearance) and 0 < 2 * clearance < width <= sy):
            raise ValueError("terrain.route needs 0 < 2 * clearance_m < corridor_width_m <= tile width")
        _, lip_width = stair_lip_dimensions(settings)
        exits, starts, ends = [], [], []
        for name, mode in zip(MIXED_PROFILES, modes, strict=True):
            if mode != "traverse":
                exits.append(0.0)
                starts.append(0.0)
                ends.append(0.0)
                continue
            p = profiles[name]
            g = p["geometry"]
            spawn = g["spawn_x_m"]
            if name.endswith(("_up", "_down")):
                count_steps = {"single": 1, "double": 2, "triple": 3}[name.split("_")[0]]
                obstacle_start = g["first_edge_x_m"]
                obstacle_end = obstacle_start + (count_steps - 1) * g["step_width_m"]
                if name.endswith("_down"):
                    obstacle_start -= lip_width
                else:
                    obstacle_end += lip_width
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
            exits.append(distance)
            starts.append(clearance - spawn)
            ends.append(sx - clearance - spawn)
        physical_exits = [exits[MIXED_PROFILES.index(name)] for name, _, _ in columns]
        for i, (name, lip, pyramid) in enumerate(columns):
            if not pyramid:
                continue
            g = profiles[name]["geometry"]
            count_steps = {"single": 1, "double": 2, "triple": 3}[name.split("_")[0]]
            hx, hy = pyramid_extent((sx, sy), g["first_edge_x_m"], g["step_width_m"], count_steps, lip_width)
            if width / 2 > hy - (count_steps - 1) * g["step_width_m"] - lip_width:
                raise ValueError(f"{name}: corridor must cross all pyramid tiers without bypassing the center")
            first = sx / 2 - hx
            # Same margin to the far edge as at entry. An inverted lip projects onto the outer deck.
            if not clearance <= g["spawn_x_m"] < first - clearance - lip_width:
                raise ValueError(f"{name}: pyramid spawn and exit need a clear outer platform")
            physical_exits[i] = sx - 2 * g["spawn_x_m"]
        self.exit_distances = torch.tensor(physical_exits, device=device)
        self.x_min = torch.tensor(starts, device=device)
        self.x_max = torch.tensor(ends, device=device)
        self.y_limit = width / 2 - clearance
        self.traverse = torch.zeros(count, dtype=torch.bool, device=device)
        self.assigned = torch.zeros_like(self.traverse)
        self.crossed = torch.zeros_like(self.traverse)
        self.left_corridor = torch.zeros_like(self.traverse)
        self.reward_active = torch.zeros_like(self.traverse)
        self.weights = torch.empty(len(MIXED_PROFILES), device=device)
        self._update_weights()

    def _update_weights(self) -> None:
        weights = self.proportions(
            self.settings["groups"], self.settings["stair_weights"], self.settings.get("locked_stair_weights")
        )
        self.weights.copy_(self.weights.new_tensor(list(weights.values())))

    @property
    def route_open(self) -> torch.Tensor:
        return self.traverse & ~self.left_corridor & ~self.crossed

    def step(
        self,
        terrain,
        previous_w: torch.Tensor,
        position_w: torch.Tensor,
        forward_m_s: torch.Tensor,
        terminated: torch.Tensor,
    ) -> None:
        """Latch a forward crossing in the assigned column, never a later return after leaving it."""
        route = self.route_open
        cols = self.column_profiles[terrain.terrain_types]
        origin = terrain.env_origins[:, :2]
        x, y = (position_w[:, :2] - origin).unbind(-1)
        previous_x, previous_y = (previous_w[:, :2] - origin).unbind(-1)
        outside = (
            (torch.maximum(y.abs(), previous_y.abs()) > self.y_limit)
            | (torch.minimum(x, previous_x) < self.x_min[cols])
            | (torch.maximum(x, previous_x) > self.x_max[cols])
        )
        self.left_corridor |= route & outside
        active = route_active(route & ~outside & ~terminated, forward_m_s)
        self.reward_active.copy_(active)
        exit_x = self.exit_distances[terrain.terrain_types]
        self.crossed |= active & (previous_x < exit_x) & (x >= exit_x)

    def reset(
        self, terrain, ids: torch.Tensor, completed: torch.Tensor, terminated: torch.Tensor, *, evaluation: bool
    ) -> None:
        if not evaluation:
            finished = ids[completed[ids] & self.assigned[ids]]
            cols = self.column_profiles[terrain.terrain_types[finished]]
            rows = terrain.terrain_levels[finished]
            success = self.crossed[finished] & ~terminated[finished]
            before = tuple(self.unlocked.values())
            for name in self.gates:
                match = (cols == MIXED_PROFILES.index(name)) & (
                    terrain.terrain_types[finished] < len(MIXED_COLUMN_PROFILES)
                )
                self.record(name, rows[match], success[match])
            if tuple(self.unlocked.values()) != before:
                self._update_weights()
        if not ids.numel():
            return
        profiles = torch.multinomial(self.weights, len(ids), replacement=True)
        lo, hi = self.rows[profiles].unbind(-1)
        if evaluation:
            rows = hi
        else:
            rows = lo + (torch.rand(len(ids), device=ids.device) * (hi - lo + 1)).long()
        is_stair = profiles >= len(MIXED_PROFILES) - len(STAIR_PROFILES)
        with_lip = is_stair & (torch.rand(len(ids), device=ids.device) < 0.5)
        cols = profiles + with_lip * len(STAIR_PROFILES)
        if self.pyramid_share:
            # A mixed triple traverses both directions: neither prerequisite may be bypassed.
            eligible = is_stair & ((profiles < MIXED_PROFILES.index("triple_up")) | all(self.unlocked.values()))
            pyramid = eligible & (torch.rand(len(ids), device=ids.device) < self.pyramid_share)
            cols = torch.where(pyramid, cols + 2 * len(STAIR_PROFILES), cols)
        terrain.terrain_types[ids] = cols
        terrain.terrain_levels[ids] = rows
        terrain.env_origins[ids] = terrain.terrain_origins[rows, cols]
        self.traverse[ids] = self.route_columns[profiles]
        self.assigned[ids] = True
        self.crossed[ids] = self.left_corridor[ids] = self.reward_active[ids] = False

    def state_dict(self) -> dict:
        return dict(passed=self.passed.copy(), counts=self.counts.copy())

    def load_state_dict(self, state: dict) -> None:
        self.passed.update(state["passed"])
        self.counts.update(state["counts"])
        for triple, pair in PREREQUISITES.items():
            self.unlocked[triple] = all(self.passed[name] for name in pair)
        self._update_weights()
