"""Bilateral, supported preload credit; never a reward for holding a squat."""

import torch


class PreloadGuide:
    def __init__(self, settings: dict, minimum_height_m: float, count: int, device: str):
        self.settings = settings
        self.minimum_height_m = minimum_height_m
        self.start_length = torch.zeros((count, 2), device=device)
        self.compressed_length = torch.zeros_like(self.start_length)
        self.start_z = torch.zeros(count, device=device)
        self.support_time = torch.zeros_like(self.start_z)
        self.best_score = torch.zeros_like(self.start_z)
        self.used_score = torch.zeros_like(self.start_z)
        self.added_stroke_m = torch.zeros_like(self.start_z)
        self.left_support = torch.zeros(count, dtype=torch.bool, device=device)
        self.eligible = torch.zeros_like(self.left_support)
        self.paid = torch.zeros_like(self.left_support)
        self.takeoff_paid = torch.zeros_like(self.left_support)

    def reset(self, ids: torch.Tensor) -> None:
        for value in (
            self.start_length,
            self.compressed_length,
            self.start_z,
            self.support_time,
            self.best_score,
            self.used_score,
            self.added_stroke_m,
            self.left_support,
            self.eligible,
            self.paid,
            self.takeoff_paid,
        ):
            value[ids] = 0

    def begin(self, ids: torch.Tensor, length_m: torch.Tensor, z_m: torch.Tensor) -> None:
        self.reset(ids)
        self.start_length[ids] = length_m[ids]
        self.compressed_length[ids] = length_m[ids]
        self.start_z[ids] = z_m[ids]

    def update(
        self,
        dt: float,
        active: torch.Tensor,
        elapsed_s: torch.Tensor,
        height_m: torch.Tensor,
        contact: torch.Tensor,
        length_m: torch.Tensor,
        z_m: torch.Tensor,
        rising: torch.Tensor,
    ) -> None:
        cfg = self.settings
        # Use the sampled target, not the cohort's maximum unlocked level.
        self.eligible.copy_(height_m >= self.minimum_height_m - 1e-6)
        leaving = active & ~self.left_support & ~contact.all(-1)
        self.left_support |= leaving
        supported = active & self.eligible & ~self.left_support & contact.all(-1)
        self.support_time += dt * supported
        collect = supported & (elapsed_s <= cfg["window_s"] + 1e-6)
        collect &= self.support_time >= cfg["support_dwell_s"] - dt * 0.5
        collect &= self.start_z - z_m >= cfg["min_body_drop_m"]
        depth = (self.start_length - length_m.clamp_min(cfg["target_leg_length_m"])).clamp_min(0)
        distance = (self.start_length - cfg["target_leg_length_m"]).clamp_min(cfg["min_added_stroke_m"])
        score = (depth / distance).clamp(0, 1).amin(-1)
        better = collect & (score > self.best_score)
        # Keep both lengths from the same frame; alternating left/right squats cannot combine.
        self.compressed_length[better] = length_m[better].clamp_min(cfg["target_leg_length_m"])
        self.best_score.copy_(torch.where(better, score, self.best_score))
        recovered = supported & (length_m >= self.start_length - 1e-6).all(-1)
        # An unrelated squat followed by standing still must not subsidize a later jump.
        stopped = supported & ~rising & (recovered | (self.used_score > 0))
        self.best_score.masked_fill_(stopped, 0)
        self.compressed_length[stopped] = self.start_length[stopped]
        self.used_score.copy_(torch.where(recovered & rising, self.best_score, self.used_score))
        stroke = (self.start_length - self.compressed_length).clamp_min(0).amin(-1)
        self.added_stroke_m.copy_(torch.where(recovered & rising, stroke, self.added_stroke_m))
        stale = stopped | (leaving & ~rising)
        self.used_score.masked_fill_(stale, 0)
        self.added_stroke_m.masked_fill_(stale, 0)

    def success_bonus(self, success: torch.Tensor) -> torch.Tensor:
        pay = success & self.eligible & self.left_support & ~self.paid
        split = self.settings.get("takeoff_bonus")
        if split is not None:
            pay &= self.takeoff_paid
        self.paid |= pay
        budget = self.settings["max_bonus"] if split is None else self.settings["max_bonus"] - split
        return budget * self.used_score * pay

    def takeoff_bonus(self, confirmed: torch.Tensor, valid: torch.Tensor) -> torch.Tensor:
        if "takeoff_bonus" not in self.settings:
            return torch.zeros_like(self.used_score)
        pay = confirmed & valid & self.eligible & self.left_support & ~self.takeoff_paid & (self.used_score > 0)
        self.takeoff_paid |= pay
        return self.settings["takeoff_bonus"] * self.used_score * pay
