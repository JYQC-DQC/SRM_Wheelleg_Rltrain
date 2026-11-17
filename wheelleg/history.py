from __future__ import annotations

from typing import TYPE_CHECKING

from .observation import OBS_DIM

if TYPE_CHECKING:
    import torch

HISTORY_FRAMES = 5
HISTORY_DIM = HISTORY_FRAMES * OBS_DIM
VELOCITY_DIM = 3
ENCODER_HIDDEN_DIMS = (128, 64)


def history_contract() -> dict:
    return {
        "frames": HISTORY_FRAMES,
        "input_dim": HISTORY_DIM,
        "order": "oldest_to_newest",
        "refill": "repeat_first_observation_on_reset_or_policy_switch",
        "encoder_hidden_dims": list(ENCODER_HIDDEN_DIMS),
        "output_dim": VELOCITY_DIM,
        "output": "body_linear_velocity_xyz_m_s",
    }


class HistoryBuffer:
    """One history per env; update with the exact current Actor observation at policy rate."""

    def __init__(self, num_envs: int, device: str | torch.device) -> None:
        import torch

        self.frames = torch.zeros(num_envs, HISTORY_FRAMES, OBS_DIM, device=device)
        self.fresh = torch.ones(num_envs, dtype=torch.bool, device=device)
        self.refill = torch.zeros_like(self.fresh)

    def reset(self, ids: torch.Tensor) -> None:
        """Mark true episode resets; first contact and control handover are not resets."""
        self.fresh[ids] = True

    def update(self, frame: torch.Tensor, new_step: bool) -> None:
        import torch

        if new_step:
            self.frames[:, :-1].copy_(self.frames[:, 1:].clone())
            self.refill.copy_(self.fresh)
        else:
            self.refill.logical_or_(self.fresh)
        self.frames[:, -1] = frame
        # On repeated reads of the first tick, all five entries still describe the first frame.
        torch.where(self.refill[:, None, None], frame[:, None, :], self.frames, out=self.frames)
        self.fresh.zero_()

    def flat(self) -> torch.Tensor:
        """View shaped (N, 175), valid until the next update; copy it when recording."""
        return self.frames.flatten(1)
