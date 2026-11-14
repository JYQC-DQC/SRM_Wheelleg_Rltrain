import math

import torch

from .tasks import TASKS
from .tensor_ops import rotate_xy, slew
from .training import TrainingConfig


def uniform(bounds: tuple[float, float], shape: tuple[int, ...], device: str) -> torch.Tensor:
    return bounds[0] + torch.rand(shape, device=device) * (bounds[1] - bounds[0])


class Commands:
    def __init__(self, cfg: TrainingConfig, count: int, device: str):
        self.cfg, self.device = cfg, device
        self.family = TASKS[cfg.task].policy
        self.settings = cfg.settings["commands"]
        self.value = torch.zeros(count, 3, device=device)
        self.target = torch.zeros_like(self.value)
        self.height = torch.zeros(count, 1, device=device)
        self.height_rate = torch.zeros(count, device=device)  # slewed height command rate, m/s
        self.target_height = torch.zeros_like(self.height)
        self.remaining = torch.zeros(count, device=device)
        self.height_remaining = torch.zeros_like(self.remaining)
        self.translation = torch.zeros(count, 2, device=device)
        self.translation_target = torch.zeros_like(self.translation)
        self.reference_yaw = torch.zeros_like(self.remaining)
        self.rates = self.value.new_tensor(
            [self.settings["linear_slew_m_s2"], self.settings["linear_slew_m_s2"], self.settings["angular_slew_rad_s2"]]
        )
        self.command_fraction = cfg.settings["command_curriculum"]["initial_fraction"]
        self.course = None  # Assigned by the stairs environment before the first reset.

    def reset(self, ids: torch.Tensor) -> None:
        self.value[ids] = 0
        self.remaining[ids] = 0
        self.height_remaining[ids] = 0
        self.translation[ids] = 0
        self._resample(ids)
        self._resample_height(ids)
        self.height[ids] = self.target_height[ids]
        self.height_rate[ids] = 0

    def _resample(self, ids: torch.Tensor) -> None:
        n = len(ids)
        if not n:
            return
        self.remaining[ids] = uniform(self.settings["segment_duration_s"], (n,), self.device)
        self.target[ids] = 0
        if self.cfg.task == "p1-stairs":
            course = self.course
            self.remaining[ids] = uniform(self.cfg.stage["course"]["segment_duration_s"], (n,), self.device)
            for k, name in enumerate(course.names):
                selected = ids[course.group[ids] == k]
                profile = self.cfg.stage["terrain"]["profiles"][name]
                bounds = profile["speed_range_m_s"]
                # SCUT cfg_utils.py:281-313: axis-aligned travel, slow/fast ranges, limited turning.
                if profile["command_mode"] == "motion":
                    kinds = (
                        torch.multinomial(
                            self.value.new_tensor(course.p["motion_segment_probabilities"]),
                            len(selected),
                            replacement=True,
                        )
                        if len(selected)
                        else selected
                    )
                    speed = uniform((-bounds[1], bounds[1]), (len(selected),), self.device)
                    yaw = uniform(profile["yaw_range_rad_s"], (len(selected),), self.device)
                    small = uniform(course.p["small_turn_range_rad_s"], (len(selected),), self.device)
                    small *= torch.where(torch.rand(len(selected), device=self.device) < 0.5, -1.0, 1.0)
                    yaw = torch.where(
                        torch.rand(len(selected), device=self.device) < course.p["small_turn_probability"], small, yaw
                    )
                    self.target[selected, 0] = torch.where((kinds == 1) | (kinds == 3), speed, 0.0)
                    self.target[selected, 2] = torch.where((kinds == 2) | (kinds == 3), yaw, 0.0)
                    self.target[selected, 2] = torch.where(
                        kinds == 3,
                        self.target[selected, 2].clamp(
                            -self.settings["combined_wz_limit_rad_s"], self.settings["combined_wz_limit_rad_s"]
                        ),
                        self.target[selected, 2],
                    )
                else:
                    fraction = (course.episode_speed_fraction[selected] - course.p["minimum_speed_fraction"]) / (
                        1 - course.p["minimum_speed_fraction"]
                    )
                    start = self.value.new_tensor(profile["start_speed_range_m_s"])
                    scaled = start + fraction[:, None] * (self.value.new_tensor(bounds) - start)
                    speed = scaled[:, 0] + torch.rand(len(selected), device=self.device) * (scaled[:, 1] - scaled[:, 0])
                    self.target[selected, 0] = speed * course.forward_sign[selected]
                    self.target[selected, 2] = uniform(profile["yaw_range_rad_s"], (len(selected),), self.device)
            return
        if self.cfg.task == "p3-tunnel":
            self.target[ids, 0] = uniform(self.cfg.stage["tunnel"]["vx_range_m_s"], (n,), self.device)
            return
        if self.family == "p2":
            stage = self.cfg.stage
            low = uniform(stage["spin_low_range_rad_s"], (n,), self.device)
            high = uniform(stage["spin_high_range_rad_s"], (n,), self.device)
            self.target[ids, 2] = torch.where(torch.rand(n, device=self.device) < 0.5, low, high)
            self.target[ids, 2] *= torch.where(torch.rand(n, device=self.device) < 0.5, -1.0, 1.0)
            speed = uniform(stage["translation_speed_range_m_s"], (n,), self.device)
            heading = uniform((-math.pi, math.pi), (n,), self.device)
            self.translation_target[ids] = torch.stack((speed * heading.cos(), speed * heading.sin()), -1)
            self.reference_yaw[ids] = stage["reference_yaw_rad"]
            return
        kinds = torch.multinomial(self.value.new_tensor(self.settings["segment_probabilities"]), n, replacement=True)
        vx = uniform(self.settings["vx_range_m_s"], (n,), self.device) * self.command_fraction
        wz = uniform(self.settings["wz_range_rad_s"], (n,), self.device) * self.command_fraction
        if self.family == "p1":
            # “直行加转向”片段的转向单独封顶：课程放大后的转向上限超过 combined_wz_limit_rad_s 时，
            # 把这类片段的转向等比例缩到该上限以内（仍是均匀分布）；纯转向、纯直行和冲刺片段不变。
            wz_limit = max(abs(v) for v in self.settings["wz_range_rad_s"]) * self.command_fraction  # rad/s
            scale = min(1.0, self.settings["combined_wz_limit_rad_s"] / wz_limit)
            wz = torch.where(kinds == 3, wz * scale, wz)
        self.target[ids, 0] = torch.where((kinds == 1) | (kinds >= 3), vx, 0)
        self.target[ids, 2] = torch.where((kinds == 2) | (kinds == 3), wz, 0)
        dash = uniform(self.settings["dash_range_m_s"], (n,), self.device) * self.command_fraction
        self.target[ids, 0] = torch.where(kinds == 4, dash, self.target[ids, 0])
        # Stop/reverse segments depend on the preceding segment, not independent random commands.
        reverse = -self.value[ids, 0]
        reverse = torch.where(torch.rand(n, device=self.device) < 0.5, reverse, 0)
        self.target[ids, 0] = torch.where(kinds == 5, reverse, self.target[ids, 0])

    def _resample_height(self, ids: torch.Tensor) -> None:
        if self.cfg.task == "p1-stairs":
            p = self.cfg.stage["course"]
            for k, name in enumerate(self.course.names):
                selected = ids[self.course.group[ids] == k]
                bounds = self.cfg.stage["terrain"]["profiles"][name]["height_range_m"]
                self.target_height[selected, 0] = uniform(bounds, (len(selected),), self.device)
            self.height_remaining[ids] = uniform(p["height_duration_s"], (len(ids),), self.device)
            return
        self.target_height[ids, 0] = uniform(self.settings["height_range_m"], (len(ids),), self.device)
        self.height_remaining[ids] = uniform(self.settings["height_duration_s"], (len(ids),), self.device)

    def step(self, dt: float, frozen: torch.Tensor) -> None:
        self.remaining -= dt
        self.height_remaining -= dt
        self._resample(((self.remaining <= 0) & ~frozen).nonzero().flatten())
        self._resample_height(((self.height_remaining <= 0) & ~frozen).nonzero().flatten())
        self.value = torch.where(frozen[:, None], self.value, slew(self.value, self.target, self.rates, dt))
        previous = self.height
        self.height = torch.where(
            frozen[:, None], self.height, slew(self.height, self.target_height, self.settings["height_slew_m_s"], dt)
        )
        self.height_rate.copy_((self.height - previous)[:, 0] / dt)
        self.translation = slew(self.translation, self.translation_target, self.settings["linear_slew_m_s2"], dt)

    def mode(
        self,
        yaw: torch.Tensor,
        stair: torch.Tensor,
        recovering: torch.Tensor,
        jump_active: torch.Tensor,
        jump_height: torch.Tensor,
        phase: torch.Tensor,
    ) -> torch.Tensor:
        mode = self.value.new_zeros(len(yaw), 7)
        if self.family == "p1":
            mode[:, 0] = 1
            mode[:, 1] = stair
            mode[:, 3] = recovering
        elif self.family == "p2":
            mode[:, 1] = 1
            mode[:, 2] = torch.linalg.vector_norm(self.translation, dim=-1)
            heading = torch.atan2(self.translation[:, 1], self.translation[:, 0])
            mode[:, 3], mode[:, 4] = heading.sin(), heading.cos()
            relative = self.reference_yaw - yaw
            mode[:, 5], mode[:, 6] = relative.sin(), relative.cos()
        else:
            mode[:, 4] = jump_active
            mode[:, 5] = jump_height * self.cfg.policy.height_scale * jump_active
            mode[:, 6] = phase * jump_active
        return mode

    def world_translation(self) -> torch.Tensor:
        return rotate_xy(self.translation, self.reference_yaw)
