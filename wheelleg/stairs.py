"""Stair-course geometry contract, scan interpretation and vectorized traversal state."""

import numpy as np
import torch

FEATURES = 14


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
    return [entry, exit_x], [0.0, 0.0, 0.0]


def scan_course(
    hits: torch.Tensor,
    position: torch.Tensor,
    yaw: torch.Tensor,
    wheels: torch.Tensor,
    direction: torch.Tensor,
    fallback: torch.Tensor,
    settings: dict,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Local wheel support reference and up/down edge distances. All lengths in metres."""
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
        up = torch.minimum(
            up, torch.where(good & (signed >= settings["edge_height_m"]), ahead, float("inf")).amin((1, 2))
        )
        down = torch.minimum(
            down, torch.where(good & (signed <= -settings["edge_height_m"]), ahead, float("inf")).amin((1, 2))
        )
    return ground, up, down


class StairCourse:
    def __init__(self, count: int, stage: dict, device: str):
        self.p, self.terrain = stage["course"], stage["terrain"]
        self.names = list(self.terrain["profiles"])
        columns = terrain_columns(self.terrain["profiles"], self.terrain["columns"])
        self.column_groups = torch.tensor([self.names.index(k) for k in columns], device=device)
        self.group = torch.zeros(count, dtype=torch.long, device=device)
        self.drop_terrain = torch.tensor(
            [self.terrain["profiles"][k]["kind"] in ("down", "mixed", "grid") for k in self.names],
            device=device,
        )
        self.age = torch.zeros(count, device=device)
        self.crossed = torch.zeros(count, 4, dtype=torch.bool, device=device)
        self.edges = torch.full((count, 4), float("inf"), device=device)
        self.edge_count = torch.zeros(count, dtype=torch.long, device=device)
        self.lane_ok = torch.ones(count, dtype=torch.bool, device=device)
        self.arrived = torch.zeros_like(self.lane_ok)
        self.success = torch.zeros_like(self.lane_ok)
        self.finished = torch.zeros_like(self.lane_ok)
        self.escaped = torch.zeros_like(self.lane_ok)
        self.hold = torch.zeros(count, device=device)
        self.track_sum = torch.zeros(count, device=device)
        self.track_count = torch.zeros(count, device=device)
        self.last_x = torch.zeros(count, device=device)
        self.progress = torch.zeros(count, device=device)
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
        self.speed_fraction = torch.full((len(self.names),), self.p["initial_speed_fraction"], device=device)
        self.completed = torch.zeros(len(self.names), device=device)
        self.passed = torch.zeros(len(self.names), device=device)
        self.latest_pass = torch.zeros(len(self.names), device=device)

    def reset(self, ids: torch.Tensor, terrain_types: torch.Tensor, origin: torch.Tensor, tick: int) -> None:
        self.group[ids] = self.column_groups[terrain_types]
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
            self.crossed,
            self.arrived,
            self.success,
            self.finished,
            self.escaped,
            self.hold,
            self.track_sum,
            self.track_count,
            self.last_x,
            self.progress,
            self.seen_support,
            self.contact,
            self.flight_time,
            self.previous_down,
            self.impact,
            self.cushion,
            self.flying,
        ):
            field[ids] = 0
        self.lane_ok[ids] = True
        self.support_z[ids] = origin[:, 2:3]
        self.last_tick[ids] = tick

    def begin_step(self) -> None:
        self.impact.zero_()

    def sample(self, tick: int, dt: float, force: torch.Tensor, wheel_z: torch.Tensor, wheel_vz: torch.Tensor) -> None:
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
        self.flying.copy_((self.flight_time >= self.p["min_flight_s"]).all(-1) & self.seen_support.all(-1))

    def update(
        self, state: dict, origin: torch.Tensor, dt: float, terminated: torch.Tensor, reward_parameters: dict
    ) -> None:
        self.age += dt
        x = state["wheel_position_w"][:, :, 0] - origin[:, 0:1]
        center = x.mean(-1)
        lateral = (state["wheel_position_w"][:, :, 1] - origin[:, 1:2]).abs().amax(-1)
        self.lane_ok &= lateral <= self.p["lane_half_width_m"]
        end = self.terrain["tile_size_m"][0] - self.terrain["spawn_x_m"] - self.p["edge_clearance_m"]
        self.escaped.copy_(~self.lane_ok | (center < -self.p["backtrack_limit_m"]) | (x.amax(-1) > end))
        reached = (x.amin(-1)[:, None] >= self.edges + self.p["edge_clearance_m"]) & self.lane_ok[:, None]
        self.crossed |= reached
        goal = self.terrain["finish_x_m"] - self.terrain["spawn_x_m"]
        self.arrived.copy_((x.amin(-1) >= goal) & (self.crossed.sum(-1) >= self.edge_count) & self.lane_ok)
        tracking = torch.exp(-state["linear_error"].square() / self.p["tracking_sigma"])
        band = reward_parameters["height_gate_zero_error_m"] - reward_parameters["height_gate_full_error_m"]
        tracking *= ((reward_parameters["height_gate_zero_error_m"] - state["height_error"].abs()) / band).clamp(0, 1)
        tracking = torch.where(terminated, 0.0, tracking)
        counted = ~self.arrived & ~self.flying & (self.cushion <= 0) & (self.age > self.p["tracking_warmup_s"])
        self.track_sum += torch.where(counted, tracking, 0.0)
        self.track_count += counted
        stable = self.arrived & state["wheel_contact"].all(-1) & ~terminated & ~self.escaped
        stable &= state["undesired_force"].amax(-1) <= reward_parameters["contact_force_n"]
        stable &= state["height_error"].abs() <= reward_parameters["height_gate_full_error_m"]
        stable &= (state["roll"].abs() < self.p["finish_tilt_rad"]) & (state["pitch"].abs() < self.p["finish_tilt_rad"])
        stable &= state["angular_velocity"][:, :2].abs().amax(-1) < self.p["finish_angular_rad_s"]
        stable &= state["heading_velocity"].norm(dim=-1) < self.p["finish_speed_m_s"]
        self.hold.copy_(torch.where(stable, self.hold + dt, 0.0))
        self.finished.copy_(self.hold >= self.p["finish_hold_s"])
        mean = self.track_sum / self.track_count.clamp_min(1)
        self.success.copy_(self.finished & (self.track_count > 0) & (mean >= self.p["tracking_promote"]))
        self.progress.copy_(torch.where(self.lane_ok & ~self.arrived & (self.age > dt), center - self.last_x, 0.0))
        self.last_x.copy_(center)

    def curriculum(
        self, ids: torch.Tensor, terminated: torch.Tensor, out_of_bounds: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor]:
        eligible = (
            ((self.age[ids] >= self.p["minimum_episode_s"]) | self.finished[ids]) & (self.age[ids] > 0) & ~out_of_bounds
        )
        average = self.track_sum[ids] / self.track_count[ids].clamp_min(1)
        up = eligible & self.success[ids] & ~terminated
        down = (
            eligible
            & ~up
            & (
                terminated
                | self.escaped[ids]
                | (self.age[ids] >= self.p["episode_length_s"])
                | ((self.track_count[ids] > 0) & (average < self.p["tracking_demote"]))
            )
        )
        # Premature physical failure is evidence even when the minimum normal evaluation duration was not reached.
        down |= (self.age[ids] > 0) & ~out_of_bounds & (terminated | self.escaped[ids])
        self.completed.scatter_add_(0, self.group[ids], (eligible | down).float())
        self.passed.scatter_add_(0, self.group[ids], up.float())
        ready = self.completed >= self.p["speed_window_episodes"]
        rate = self.passed / self.completed.clamp_min(1)
        increase = ready & (rate >= self.p["speed_promote_rate"])
        decrease = ready & (rate < self.p["speed_demote_rate"])
        self.speed_fraction.copy_(
            (self.speed_fraction + self.p["speed_increment"] * (increase.float() - decrease.float())).clamp(
                self.p["minimum_speed_fraction"], 1
            )
        )
        self.latest_pass.copy_(torch.where(ready, rate, self.latest_pass))
        self.completed[ready] = 0
        self.passed[ready] = 0
        return up, down

    def features(self, state: dict, origin: torch.Tensor) -> torch.Tensor:
        length = self.terrain["finish_x_m"] - self.terrain["spawn_x_m"]
        result = torch.cat(
            (
                (self.last_x / length)[:, None],
                (self.crossed.sum(-1) / self.edge_count.clamp_min(1))[:, None],
                ((state["wheel_position_w"][:, :, 1].mean(-1) - origin[:, 1]) / self.p["lane_half_width_m"])[:, None],
                (self.hold / self.p["finish_hold_s"])[:, None],
                self.flight_time,
                self.support_z - state["wheel_position_w"][:, :, 2],
                self.seen_support.float(),
                (self.cushion / self.p["cushion_s"])[:, None],
                self.arrived.float()[:, None],
                (self.track_sum / self.track_count.clamp_min(1))[:, None],
                self.speed_fraction[self.group, None],
            ),
            -1,
        ).clamp(-1, 1)
        return torch.nan_to_num(result)
