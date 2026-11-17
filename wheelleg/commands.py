import torch

from .tasks import TASKS
from .tensor_ops import rotate_xy, slew
from .training import TrainingConfig

SPIN_SIM_LIMIT_RAD_S = 18.0


def uniform(bounds: tuple[float, float], shape: tuple[int, ...], device: str) -> torch.Tensor:
    return bounds[0] + torch.rand(shape, device=device) * (bounds[1] - bounds[0])


class Commands:
    def __init__(self, cfg: TrainingConfig, count: int, device: str, *, sample_jump_motion: bool = False):
        self.cfg, self.device = cfg, device
        self.family = TASKS[cfg.task].policy
        self.sample_jump_motion = sample_jump_motion
        self.settings = cfg.settings["commands"]
        self.value = torch.zeros(count, 3, device=device)
        self.target = torch.zeros_like(self.value)
        self.height = torch.zeros(count, 1, device=device)
        self.target_height = torch.zeros_like(self.height)
        self.remaining = torch.zeros(count, device=device)
        self.height_remaining = torch.zeros_like(self.remaining)
        self.translation = torch.zeros(count, 2, device=device)
        self.translation_target = torch.zeros_like(self.translation)
        self.reference_yaw = torch.zeros_like(self.remaining)
        self.rates = self.value.new_tensor(
            [self.settings["linear_slew_m_s2"], self.settings["linear_slew_m_s2"], self.settings["angular_slew_rad_s2"]]
        )
        self.command_fraction = cfg.settings["command_curriculum"]["initial_fraction"] if self.family == "p1" else 1.0
        if self.family == "p2":
            stage = cfg.stage
            self.spin_rates = self.value.new_tensor(stage["spin_rates_rad_s"])
            self.spin_probabilities = self.value.new_tensor(stage["spin_probabilities"])
            if self.spin_rates.ndim != 1 or not (self.spin_rates.abs() <= SPIN_SIM_LIMIT_RAD_S).all():
                raise ValueError("P2 spin_rates_rad_s must be a vector within the +/-18 rad/s simulation limit")
            if (
                self.spin_probabilities.shape != self.spin_rates.shape
                or not (self.spin_probabilities >= 0).all()
                or not torch.isclose(self.spin_probabilities.sum(), self.value.new_tensor(1.0))
            ):
                raise ValueError("P2 spin_probabilities must match the signed rates, be nonnegative and sum to 1")

    def reset(self, ids: torch.Tensor) -> None:
        self.value[ids] = 0
        self.remaining[ids] = 0
        self.height_remaining[ids] = 0
        self.translation[ids] = 0
        self._resample(ids)
        self._resample_height(ids)
        self.height[ids] = self.target_height[ids]

    def _resample(self, ids: torch.Tensor) -> None:
        n = len(ids)
        if not n:
            return
        self.target[ids] = 0
        if self.family == "p3":
            if self.cfg.task == "p3-tunnel":
                speed = uniform(self.cfg.stage["tunnel"]["vx_range_m_s"], (n,), self.device)
            else:
                speed = uniform(self.settings["vx_range_m_s"], (n,), self.device)
            # Preserve the stationary/moving cohort and speed before, during and after the press.
            if self.sample_jump_motion:
                speed *= torch.rand(n, device=self.device) < self.cfg.stage["moving_probability"]
            self.target[ids, 0] = speed
            self.remaining[ids] = torch.inf
            return
        self.remaining[ids] = uniform(self.settings["segment_duration_s"], (n,), self.device)
        if self.family == "p2":
            kinds = torch.multinomial(self.spin_probabilities, n, replacement=True)
            self.target[ids, 2] = self.spin_rates[kinds]
            return
        kinds = torch.multinomial(self.value.new_tensor(self.settings["segment_probabilities"]), n, replacement=True)
        vx = uniform(self.settings["vx_range_m_s"], (n,), self.device) * self.command_fraction
        wz = uniform(self.settings["wz_range_rad_s"], (n,), self.device) * self.command_fraction
        self.target[ids, 0] = torch.where((kinds == 1) | (kinds >= 3), vx, 0)
        self.target[ids, 2] = torch.where((kinds == 2) | (kinds == 3), wz, 0)
        dash = uniform(self.settings["dash_range_m_s"], (n,), self.device) * self.command_fraction
        self.target[ids, 0] = torch.where(kinds == 4, dash, self.target[ids, 0])
        # Stop/reverse segments depend on the preceding segment, not independent random commands.
        reverse = -self.value[ids, 0]
        reverse = torch.where(torch.rand(n, device=self.device) < 0.5, reverse, 0)
        self.target[ids, 0] = torch.where(kinds == 5, reverse, self.target[ids, 0])

    def _resample_height(self, ids: torch.Tensor) -> None:
        self.target_height[ids, 0] = uniform(self.settings["height_range_m"], (len(ids),), self.device)
        self.height_remaining[ids] = uniform(self.settings["height_duration_s"], (len(ids),), self.device)

    def step(self, dt: float, frozen: torch.Tensor) -> None:
        self.remaining -= dt
        self.height_remaining -= dt
        self._resample(((self.remaining <= 0) & ~frozen).nonzero().flatten())
        self._resample_height(((self.height_remaining <= 0) & ~frozen).nonzero().flatten())
        motion = slew(self.value, self.target, self.rates, dt)
        # P3 keeps one motion target per episode, but issued speed must keep slewing during the jump.
        self.value = motion if self.family == "p3" else torch.where(frozen[:, None], self.value, motion)
        self.height = torch.where(
            frozen[:, None], self.height, slew(self.height, self.target_height, self.settings["height_slew_m_s"], dt)
        )
        if self.family == "p2":
            self.value[:, :2] = 0
            self.translation.zero_()
            self.translation_target.zero_()
        else:
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
        else:
            mode[:, 4] = jump_active
            mode[:, 5] = jump_height * self.cfg.policy.height_scale * jump_active
            mode[:, 6] = phase * jump_active
        return mode

    def world_translation(self) -> torch.Tensor:
        return rotate_xy(self.translation, self.reference_yaw)
