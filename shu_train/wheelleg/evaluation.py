from dataclasses import dataclass

import numpy as np

from .tasks import TASKS
from .training import TrainingConfig


@dataclass(frozen=True)
class EvaluationCase:
    name: str
    command: tuple[float, float, float]
    height: float
    translation: tuple[float, float] = (0.0, 0.0)
    jump_count: int = 0
    jump_height: float = 0.0
    jump_press_threshold: float | None = None


def evaluation_cases(cfg: TrainingConfig) -> list[EvaluationCase]:
    e = cfg.settings["evaluation"]
    family = TASKS[cfg.task].policy
    cases = []
    if family == "p3":
        raise ValueError("P3 uses explicit runtime button input; no evaluation cases are defined")
    elif family == "p2":
        cases.extend(
            EvaluationCase(f"spin_{rate:+g}", (0.0, 0.0, rate), e["height_m"]) for rate in cfg.stage["spin_rates_rad_s"]
        )
    else:
        if len(e["vx_values_m_s"]) != 7 or len(e["wz_values_rad_s"]) != 6 or len(e["combined_commands"]) != 2:
            raise ValueError("Evaluation requires 7 straight, 6 turning, 2 combined and 1 standing case")
        for i, vx in enumerate(e["vx_values_m_s"]):
            cases.append(EvaluationCase(f"straight_{i}", (vx, 0.0, 0.0), e["height_m"]))
        for i, wz in enumerate(e["wz_values_rad_s"]):
            cases.append(EvaluationCase(f"turn_{i}", (0.0, 0.0, wz), e["height_m"]))
        for i, cmd in enumerate(e["combined_commands"]):
            cases.append(EvaluationCase(f"combined_{i}", tuple(cmd), e["height_m"]))
        cases.append(EvaluationCase("stand", (0.0, 0.0, 0.0), e["height_m"]))
    return cases


def metrics(errors: np.ndarray, valid: np.ndarray, failed: np.ndarray) -> dict:
    """errors=(T,N,3), valid=(T,N), failed=(N,); exclude post-reset samples."""
    values = np.abs(errors[valid])
    mean = values.mean(0).tolist() if len(values) else [None, None, None]
    return dict(
        episodes=int(len(failed)),
        failures=int(failed.sum()),
        mean_abs_velocity_error=mean[0],
        mean_abs_yaw_rate_error=mean[1],
        mean_abs_height_error=mean[2],
    )
