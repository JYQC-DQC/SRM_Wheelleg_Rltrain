"""Stair-course geometry contract, scan interpretation and vectorized traversal state."""

import numpy as np
import torch

FEATURES = 19


def advance_height_assist(
    trigger: torch.Tensor,
    supported: torch.Tensor,
    remaining: torch.Tensor,
    target: torch.Tensor,
    previous_trigger: torch.Tensor,
    stage: dict,
    dt: float,
    ceiling: float,
    command_height: torch.Tensor,
    step_rise: torch.Tensor,
    randomize: bool,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    # Keep assistance throughout a slow approach, then hold briefly after the edge leaves the scan.
    # Actual guide contact cancels it for retraction; no contact-termination exemption is added.
    entered = trigger & ~previous_trigger & (remaining <= 0) & ~supported
    # Root clearance above the next tread; clamp the interval BEFORE sampling so
    # short steps keep height diversity instead of accumulating samples at the ceiling.
    low, high = stage["step_height_clearance_range_m"]
    lower = torch.maximum(command_height, step_rise + low).clamp(max=ceiling)
    upper = torch.maximum(lower, step_rise + high).clamp(max=ceiling)
    fraction = torch.rand_like(target) if randomize else 0.5
    sampled = lower + fraction * (upper - lower)
    target = torch.where(entered, sampled, target)
    remaining = torch.where(
        trigger & (entered | (remaining > 0)), stage["step_height_hold_s"], (remaining - dt).clamp_min(0)
    )
    remaining = torch.where(supported, 0.0, remaining)
    return remaining, target, trigger


def terrain_columns(profiles: dict, columns: int) -> list[str]:
    """Same deterministic column assignment as terrain_generator.py:241-249."""
    names = list(profiles)
    cumulative = np.cumsum([profiles[k]["proportion"] for k in names])
    return [names[int(np.searchsorted(cumulative, i / columns + 0.001, side="right"))] for i in range(columns)]


def step_layout(terrain: dict, profile: dict, difficulty: float) -> tuple[list[float], list[float]]:
    """Tile-local x edges and interval heights (m); positive travel is world +x."""
    count = profile["step_count"]
    low, high = terrain["step_height_range_m"]
    h = low + difficulty * (high - low)
    width = terrain["step_width_m"]
    entry, exit_x = terrain["entry_x_m"], terrain["exit_x_m"]
    if profile["kind"] == "up":
        return [entry + i * width for i in range(count)], [i * h for i in range(count + 1)]
    if profile["kind"] == "down":
        return [entry + i * width for i in range(count)], [(count - i) * h for i in range(count + 1)]
    if profile["kind"] == "mixed":
        edges = [entry + i * width for i in range(count)]
        edges += [exit_x - (count - 1 - i) * width for i in range(count)]
        return edges, [i * h for i in range(count + 1)] + [i * h for i in reversed(range(count))]
    if "surface_x_range_m" in terrain and profile["kind"] in ("grid", "slope", "rough"):
        return list(terrain["surface_x_range_m"]), [0.0, 0.0, 0.0]
    return [entry, exit_x], [0.0, 0.0, 0.0]


def grid_layout(terrain: dict, difficulty: float) -> tuple[list[tuple[float, float, float, float]], float]:
    """Shared non-overlapping bar rectangles for Isaac and MuJoCo; old snapshots keep their four bars."""
    g = terrain["grid"]
    rng = np.random.default_rng(np.random.SeedSequence([terrain["seed"], round(difficulty * 1000000)]))
    width = rng.uniform(*g["width_range_m"])
    height = g["height_range_m"][0] + difficulty * np.ptp(g["height_range_m"])
    spacing_x, spacing_y = rng.uniform(*g["spacing_range_m"], size=2)
    start, end = (
        terrain["surface_x_range_m"] if "surface_x_range_m" in terrain else (terrain["entry_x_m"], terrain["exit_x_m"])
    )
    cx, cy = (start + end) / 2, terrain["tile_size_m"][1] / 2
    if "surface_x_range_m" in terrain:
        nx = int((end - start - width) / (2 * spacing_x))
        ny = int((2 * g["half_span_m"] - width) / (2 * spacing_y))
        xs = cx + np.arange(-nx, nx + 1) * spacing_x
        ys = cy + np.arange(-ny, ny + 1) * spacing_y
    else:
        xs = cx + np.array([-0.5, 0.5]) * spacing_x
        ys = cy + np.array([-0.5, 0.5]) * spacing_y
    vertical = [(x - width / 2, x + width / 2) for x in xs]
    rectangles = [(a, b, cy - g["half_span_m"], cy + g["half_span_m"]) for a, b in vertical]
    for y in ys:
        left = start
        for a, b in [*vertical, (end, end)]:
            if a > left:
                rectangles.append((left, a, y - width / 2, y + width / 2))
            left = b
    return rectangles, float(height)


def scan_course(
    hits: torch.Tensor,
    position: torch.Tensor,
    yaw: torch.Tensor,
    wheels: torch.Tensor,
    direction: torch.Tensor,
    fallback: torch.Tensor,
    settings: dict,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    """Wheel ground, up/down distances and nearest upward riser height, all in metres."""
    valid = torch.isfinite(hits).all(-1)
    clean = torch.where(valid[..., None], hits, position[:, None])
    delta = clean[:, :, :2] - position[:, None, :2]
    c, s = yaw.cos()[:, None], yaw.sin()[:, None]
    x = c * delta[:, :, 0] + s * delta[:, :, 1]
    y = -s * delta[:, :, 0] + c * delta[:, :, 1]
    wd = wheels[:, :, :2] - position[:, None, :2]
    wx = c * wd[:, :, 0] + s * wd[:, :, 1]
    wy = -s * wd[:, :, 0] + c * wd[:, :, 1]
    # A narrow ray neighbourhood around each wheel, not the median of both sides of a step.
    distance = (clean[:, None, :, :2] - wheels[:, :, None, :2]).square().sum(-1)
    distance = torch.where(valid[:, None], distance, float("inf"))
    nearest = distance.argmin(-1)
    support = clean[:, :, 2].gather(1, nearest)
    local = distance.amin(-1) <= settings["scan_resolution_m"] ** 2
    support = torch.where(local, support, fallback[:, None])
    ground = support.mean(-1)
    # Bin yaw-aligned rays in x, averaging only rays in the corresponding wheel lane.
    spacing, half = settings["scan_resolution_m"], settings["scan_half_length_m"]
    bins = round(2 * half / spacing) + 1
    index = ((x + half) / spacing).round().long().clamp(0, bins - 1)
    lane = valid[:, None] & ((y[:, None] - wy[:, :, None]).abs() <= settings["scan_lane_half_width_m"])
    total = x.new_zeros((len(x), 2, bins))
    counts = torch.zeros_like(total)
    indices = index[:, None].expand(-1, 2, -1)
    total.scatter_add_(2, indices, torch.where(lane, clean[:, None, :, 2], 0.0))
    counts.scatter_add_(2, indices, lane.float())
    z = total / counts.clamp_min(1)
    up = torch.full_like(ground, float("inf"))
    down = up.clone()
    rise = torch.zeros_like(ground)
    # One/two-bin jumps handle a riser split by slight yaw; same-sign outer gradients reject a slope.
    # Opposite-sign neighbours are allowed: a narrow bar genuinely has adjacent up/down edges.
    for span in (1, 2):
        start = z[:, :, 1 : -span - 1]
        end = z[:, :, 1 + span : -1]
        heights = end - start
        left = start - z[:, :, : -span - 2]
        right = z[:, :, span + 2 :] - end
        gradient = torch.maximum((left * heights.sign()).clamp_min(0), (right * heights.sign()).clamp_min(0))
        good = counts.unfold(-1, span + 3, 1).amin(-1) >= settings["scan_min_rays"]
        good &= heights.abs() - span * gradient >= settings["edge_gradient_excess_m"]
        centers = (torch.arange(start.shape[-1], device=x.device) + 1 + span / 2) * spacing - half
        ahead = (centers[None, None] - wx[:, :, None]) * direction[:, None, None]
        good &= (ahead > 0) & (ahead <= settings["detection_distance_m"])
        signed = heights * direction[:, None, None]
        up_ahead = torch.where(good & (signed >= settings["edge_height_m"]), ahead, float("inf"))
        nearest_up = up_ahead.amin((1, 2))
        nearest_rise = torch.where(
            torch.isfinite(up_ahead) & (up_ahead == nearest_up[:, None, None]), signed, 0.0
        ).amax((1, 2))
        rise = torch.where(
            nearest_up < up, nearest_rise, torch.where(nearest_up == up, torch.maximum(rise, nearest_rise), rise)
        )
        up = torch.minimum(up, nearest_up)
        down = torch.minimum(
            down, torch.where(good & (signed <= -settings["edge_height_m"]), ahead, float("inf")).amin((1, 2))
        )
    return ground, up, down, rise


class StairCourse:
    def __init__(self, count: int, stage: dict, device: str):
        self.p, self.terrain = stage["course"], stage["terrain"]
        self.names = list(self.terrain["profiles"])
        columns = terrain_columns(self.terrain["profiles"], self.terrain["columns"])
        self.column_groups = torch.tensor([self.names.index(k) for k in columns], device=device)
        self.terrain_type = torch.zeros(count, dtype=torch.long, device=device)
        self.first_column = torch.tensor([columns.index(k) for k in self.names], device=device)
        self.last_column = torch.tensor([len(columns) - 1 - columns[::-1].index(k) for k in self.names], device=device)
        self.group = torch.zeros(count, dtype=torch.long, device=device)
        self.motion_groups = torch.tensor(
            [self.terrain["profiles"][k]["command_mode"] == "motion" for k in self.names], device=device
        )
        self.motion = torch.zeros(count, dtype=torch.bool, device=device)
        self.step_groups = torch.tensor(
            [self.terrain["profiles"][k]["kind"] in ("up", "down", "mixed") for k in self.names],
            device=device,
        )
        self.steps = torch.zeros_like(self.motion)
        self.heading = torch.zeros_like(self.motion)
        self.training_level = torch.zeros(count, dtype=torch.long, device=device)
        self.motion_boundary = torch.zeros_like(self.motion)
        self.traversed = torch.zeros_like(self.motion)
        self.traverse_hold = torch.zeros(count, device=device)
        self.guide_support = torch.zeros_like(self.motion)
        self.yaw_track_sum = torch.zeros(count, device=device)
        self.drop_terrain = torch.tensor(
            [self.terrain["profiles"][k]["kind"] in ("down", "mixed", "grid") for k in self.names],
            device=device,
        )
        self.age = torch.zeros(count, device=device)
        self.diagnostics = torch.zeros(count, 8, device=device)
        self.crossed = torch.zeros(count, 4, dtype=torch.bool, device=device)
        self.edges = torch.full((count, 4), float("inf"), device=device)
        self.edge_count = torch.zeros(count, dtype=torch.long, device=device)
        self.arrived = torch.zeros_like(self.motion)
        self.success = torch.zeros_like(self.motion)
        self.finished = torch.zeros_like(self.motion)
        self.escaped = torch.zeros_like(self.motion)
        self.hold = torch.zeros(count, device=device)
        self.track_sum = torch.zeros(count, device=device)
        self.track_count = torch.zeros(count, device=device)
        self.last_x = torch.zeros(count, device=device)
        self.seen_support = torch.zeros(count, 2, dtype=torch.bool, device=device)
        self.contact = torch.zeros_like(self.seen_support)
        self.flight_time = torch.zeros(count, 2, device=device)
        self.support_z = torch.zeros(count, 2, device=device)
        self.previous_down = torch.zeros(count, 2, device=device)
        self.last_tick = torch.full((count,), -1, dtype=torch.long, device=device)
        self.impact = torch.zeros(count, device=device)
        self.cushion = torch.zeros(count, device=device)
        self.flying = torch.zeros(count, dtype=torch.bool, device=device)
        self.forward_sign = torch.ones(count, device=device)
        # A low step cannot promote speeds for an unmastered high step.
        self.speed_fraction = torch.full(
            (len(self.names), self.terrain["rows"]), self.p["initial_speed_fraction"], device=device
        )
        self.completed = torch.zeros_like(self.speed_fraction)
        self.passed = torch.zeros_like(self.speed_fraction)
        self.latest_pass = torch.zeros_like(self.speed_fraction)
        self.episode_speed_fraction = torch.zeros(count, device=device)
        # Per-rollout counts: resets, eligible, successes, crossings, stops, neutral exits.
        self.reset_counts = torch.zeros(len(self.names), 6, device=device)

    def reset(self, ids: torch.Tensor, terrain_types: torch.Tensor, origin: torch.Tensor, tick: int) -> None:
        self.group[ids] = self.column_groups[terrain_types]
        self.terrain_type[ids] = terrain_types
        self.episode_speed_fraction[ids] = self.speed_fraction[self.group[ids], self.training_level[ids]]
        self.motion[ids] = self.motion_groups[self.group[ids]]
        self.steps[ids] = self.step_groups[self.group[ids]]
        self.heading[ids] = (~self.motion[ids]) & (
            torch.rand(len(ids), device=ids.device) < self.p["heading_probability"]
        )
        self.forward_sign[ids] = torch.where(
            torch.rand(len(ids), device=ids.device) < self.p["reverse_probability"], -1.0, 1.0
        )
        self.edges[ids] = float("inf")
        for k, name in enumerate(self.names):
            selected = ids[self.group[ids] == k]
            edges, _ = step_layout(self.terrain, self.terrain["profiles"][name], 0.0)
            self.edges[selected, : len(edges)] = self.edges.new_tensor(edges) - self.terrain["spawn_x_m"]
            self.edge_count[selected] = len(edges)
        for field in (
            self.age,
            self.diagnostics,
            self.crossed,
            self.arrived,
            self.success,
            self.finished,
            self.escaped,
            self.hold,
            self.track_sum,
            self.track_count,
            self.last_x,
            self.seen_support,
            self.contact,
            self.flight_time,
            self.previous_down,
            self.impact,
            self.cushion,
            self.flying,
            self.motion_boundary,
            self.traversed,
            self.traverse_hold,
            self.guide_support,
            self.yaw_track_sum,
        ):
            field[ids] = 0
        self.support_z[ids] = origin[:, 2:3]
        self.last_tick[ids] = tick

    def begin_step(self) -> None:
        self.impact.zero_()

    def sample(
        self,
        tick: int,
        dt: float,
        force: torch.Tensor,
        wheel_z: torch.Tensor,
        wheel_vz: torch.Tensor,
        guide_supported: torch.Tensor,
    ) -> None:
        use = tick > self.last_tick
        self.last_tick[use] = tick
        contact = force > self.p["contact_force_n"]
        duration = torch.where(contact, 0.0, self.flight_time + dt)
        landing = use[:, None] & contact & ~self.contact & self.seen_support
        landing &= self.drop_terrain[self.group, None]
        landing &= self.flight_time >= self.p["min_flight_s"]
        landing &= self.support_z - wheel_z >= self.p["min_drop_m"]
        # Down-step impact only: pre-contact vertical wheel speed, once per wheel flight; no hip-torque penalty.
        speed = (
            (self.previous_down - self.p["impact_free_speed_m_s"]).clamp_min(0) / self.p["impact_speed_scale_m_s"]
        ).square()
        self.impact += torch.where(landing, speed.clamp_max(self.p["impact_clip"]), 0.0).sum(-1) / 2
        # One bounded cushioning interval per drop, not extended by contact chatter.
        start_cushion = landing.any(-1) & (self.cushion <= 0)
        self.cushion.copy_(torch.where(start_cushion, self.p["cushion_s"], (self.cushion - dt * use).clamp_min(0)))
        self.flight_time.copy_(torch.where(use[:, None], duration, self.flight_time))
        self.support_z.copy_(torch.where(use[:, None] & contact, wheel_z, self.support_z))
        self.seen_support |= use[:, None] & contact
        self.contact.copy_(torch.where(use[:, None], contact, self.contact))
        self.previous_down.copy_(torch.where(use[:, None], (-wheel_vz).clamp_min(0), self.previous_down))
        self.flying.copy_(
            (self.flight_time >= self.p["min_flight_s"]).all(-1) & self.seen_support.all(-1) & ~guide_supported
        )

    def update(
        self, state: dict, origin: torch.Tensor, dt: float, terminated: torch.Tensor, reward_parameters: dict
    ) -> None:
        self.age += dt
        x = state["wheel_position_w"][:, :, 0] - origin[:, 0:1]
        center = x.mean(-1)
        sx, sy = self.terrain["tile_size_m"]
        margin = self.terrain["boundary_margin_m"]
        x_margin = self.p["edge_clearance_m"]
        x_low = torch.where(self.motion, -sx / 2 + margin, x_margin - self.terrain["spawn_x_m"])
        x_high = torch.where(self.motion, sx / 2 - margin, sx - self.terrain["spawn_x_m"] - x_margin)
        y_half = sy / 2 - margin
        y_max = (state["wheel_position_w"][:, :, 1] - origin[:, 1:2]).abs().amax(-1)
        # A pure boundary exit is a neutral truncation; physical termination stays separate.
        self.escaped.copy_((x.amin(-1) < x_low) | (x.amax(-1) > x_high) | (y_max > y_half))
        # Flat tiles form one contiguous homogeneous block; other kinds stay in their own difficulty tile.
        wx = state["wheel_position_w"][:, :, 0]
        wy = state["wheel_position_w"][:, :, 1] - origin[:, 1:2]
        left = (self.first_column[self.group] - self.terrain_type - 0.5) * sy + margin
        right = (self.last_column[self.group] - self.terrain_type + 0.5) * sy - margin
        flat_exit = (
            (wx.abs() > self.terrain["rows"] * sx / 2 - margin) | (wy < left[:, None]) | (wy > right[:, None])
        ).any(-1)
        self.escaped.copy_(torch.where(self.motion, flat_exit, self.escaped))
        self.motion_boundary.copy_(self.motion & self.escaped)
        reached = (x.amin(-1)[:, None] >= self.edges + self.p["edge_clearance_m"]) & ~self.escaped[:, None]
        self.crossed |= reached
        goal = self.terrain["finish_x_m"] - self.terrain["spawn_x_m"]
        self.arrived.copy_(
            (x.amin(-1) >= goal) & (self.crossed.sum(-1) >= self.edge_count) & ~self.escaped & ~self.motion
        )
        tracking = torch.exp(-state["linear_error"].square() / self.p["tracking_sigma"])
        # Recovery already grades height; do not grade it again through the speed score.
        tracking = torch.where(terminated, 0.0, tracking)
        yaw_tracking = torch.exp(-state["angular_error"].square() / reward_parameters["angular_sigma"])
        yaw_tracking = torch.where(terminated, 0.0, yaw_tracking)
        counted = (
            ~self.arrived
            & ~self.flying
            & ~self.guide_support
            & (self.cushion <= 0)
            & (self.age > self.p["tracking_warmup_s"])
        )
        self.track_sum += torch.where(counted, tracking, 0.0)
        self.yaw_track_sum += torch.where(counted, yaw_tracking, 0.0)
        self.track_count += counted
        stable = state["wheel_contact"].all(-1) & ~terminated & ~self.escaped
        stable &= state["undesired_force"].amax(-1) <= reward_parameters["contact_force_n"]
        recovered = stable & (state["height_error"].abs() <= self.p["traversal_height_error_m"])
        recovered &= (state["roll"].abs() < self.p["traversal_tilt_rad"]) & (
            state["pitch"].abs() < self.p["traversal_tilt_rad"]
        )
        recovered &= state["angular_velocity"][:, :2].abs().amax(-1) < self.p["traversal_angular_rad_s"]
        stable &= state["height_error"].abs() <= reward_parameters["height_gate_full_error_m"]
        stable &= (state["roll"].abs() < self.p["finish_tilt_rad"]) & (state["pitch"].abs() < self.p["finish_tilt_rad"])
        stable &= state["angular_velocity"][:, :2].abs().amax(-1) < self.p["finish_angular_rad_s"]
        # Past crossings are diagnostic history: recovery must occur beyond the last edge now.
        cleared = (reached.sum(-1) >= self.edge_count) & ~self.escaped & ~self.motion
        self.traverse_hold.copy_(torch.where(cleared & recovered, self.traverse_hold + dt, 0.0))
        self.traversed |= self.traverse_hold >= self.p["traversal_hold_s"]
        stopped = stable & self.arrived & (state["heading_velocity"].norm(dim=-1) < self.p["finish_speed_m_s"])
        self.hold.copy_(torch.where(stopped, self.hold + dt, 0.0))
        self.finished.copy_(self.hold >= self.p["finish_hold_s"])
        mean = self.track_sum / self.track_count.clamp_min(1)
        task_done = self.traversed | (self.motion & recovered & (self.age >= self.p["minimum_episode_s"]))
        yaw_mean = self.yaw_track_sum / self.track_count.clamp_min(1)
        self.success.copy_(
            task_done
            & ~terminated
            & ~self.escaped
            & (self.track_count > 0)
            & (mean >= self.p["tracking_promote"])
            & (yaw_mean >= self.p["tracking_promote"])
        )
        self.last_x.copy_(center)

    def curriculum(
        self, ids: torch.Tensor, terminated: torch.Tensor, neutral_exit: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor]:
        ran = self.age[ids] > 0
        valid = ran & ~neutral_exit
        counts = torch.stack(
            (
                ran,
                valid,
                self.success[ids] & valid & ~terminated,
                self.traversed[ids] & valid & ~terminated,
                self.finished[ids] & valid & ~terminated,
                neutral_exit & ran,
            ),
            -1,
        ).float()
        self.reset_counts.index_add_(0, self.group[ids], counts)
        eligible = (
            ((self.age[ids] >= self.p["minimum_episode_s"]) | self.traversed[ids]) & (self.age[ids] > 0) & ~neutral_exit
        )
        average = self.track_sum[ids] / self.track_count[ids].clamp_min(1)
        up = eligible & self.success[ids] & ~terminated
        down = eligible & ~up & (terminated | ((self.track_count[ids] > 0) & (average < self.p["tracking_demote"])))
        # Premature physical failure is evidence even when the minimum normal evaluation duration was not reached.
        down |= (self.age[ids] > 0) & ~neutral_exit & terminated
        group, level = self.group[ids], self.training_level[ids]
        cell = group * self.terrain["rows"] + level
        current_speed = (self.episode_speed_fraction[ids] - self.speed_fraction[group, level]).abs() < 1e-6
        counted = ~self.motion[ids] & current_speed & ~neutral_exit
        self.completed.view(-1).scatter_add_(0, cell, ((eligible | down) & counted).float())
        self.passed.view(-1).scatter_add_(0, cell, (up & counted).float())
        ready = self.completed >= self.p["speed_window_episodes"]
        rate = self.passed / self.completed.clamp_min(1)
        increase = ready & (rate >= self.p["speed_promote_rate"])
        decrease = ready & (rate < self.p["speed_demote_rate"])
        next_speed = (self.speed_fraction + self.p["speed_increment"] * (increase.float() - decrease.float())).clamp(
            self.p["minimum_speed_fraction"], 1
        )
        changed = next_speed != self.speed_fraction
        self.speed_fraction.copy_(next_speed)
        self.latest_pass.copy_(torch.where(ready, rate, self.latest_pass))
        self.completed[ready] = 0
        self.passed[ready] = 0
        advance = ~self.motion[ids] & current_speed & ~changed[group, level]
        return up & advance, down & advance

    def features(self, state: dict, origin: torch.Tensor) -> torch.Tensor:
        length = self.terrain["finish_x_m"] - self.terrain["spawn_x_m"]
        result = torch.cat(
            (
                (self.last_x / length)[:, None],
                (self.crossed.sum(-1) / self.edge_count.clamp_min(1))[:, None],
                (
                    (state["wheel_position_w"][:, :, 1].mean(-1) - origin[:, 1])
                    / (self.terrain["tile_size_m"][1] / 2 - self.terrain["boundary_margin_m"])
                )[:, None],
                (self.hold / self.p["finish_hold_s"])[:, None],
                self.flight_time,
                self.support_z - state["wheel_position_w"][:, :, 2],
                self.seen_support.float(),
                (self.cushion / self.p["cushion_s"])[:, None],
                self.arrived.float()[:, None],
                (self.track_sum / self.track_count.clamp_min(1))[:, None],
                self.episode_speed_fraction[:, None],
                self.motion.float()[:, None],
                self.traversed.float()[:, None],
                (self.traverse_hold / self.p["traversal_hold_s"])[:, None],
                self.guide_support.float()[:, None],
                (self.yaw_track_sum / self.track_count.clamp_min(1))[:, None],
            ),
            -1,
        ).clamp(-1, 1)
        return torch.nan_to_num(result)
