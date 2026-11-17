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
    terrain_profile: str | None = None
    press_distance_m: float | None = None


def evaluation_cases(cfg: TrainingConfig) -> list[EvaluationCase]:
    e = cfg.settings["evaluation"]
    family = TASKS[cfg.task].policy
    cases = []
    if cfg.task == "p1-stairs":
        for name, profile in cfg.stage["terrain"]["profiles"].items():
            height = float(np.mean(profile["height_range_m"]))
            if profile["command_mode"] == "motion":
                cases.append(EvaluationCase("flat_stand", (0.0, 0.0, 0.0), height, terrain_profile=name))
                for yaw in (
                    *cfg.stage["course"]["small_turn_range_rad_s"],
                    max(abs(v) for v in profile["yaw_range_rad_s"]),
                ):
                    for sign in (-1, 1):
                        cases.append(
                            EvaluationCase(
                                f"flat_turn_{sign * yaw:.2f}", (0.0, 0.0, sign * yaw), height, terrain_profile=name
                            )
                        )
                for sign in (-1, 1):
                    cases.append(
                        EvaluationCase(
                            f"flat_combined_{sign}",
                            (
                                sign * profile["speed_range_m_s"][1],
                                0.0,
                                sign * cfg.stage["course"]["small_turn_range_rad_s"][1],
                            ),
                            height,
                            terrain_profile=name,
                        )
                    )
            for speed in dict.fromkeys(profile["speed_range_m_s"]):
                if speed == 0:
                    continue
                for sign in (1, -1):
                    cases.append(
                        EvaluationCase(
                            f"{name}_vx_{sign * speed:.2f}", (sign * speed, 0.0, 0.0), height, terrain_profile=name
                        )
                    )
    elif family == "p3":
        if cfg.task == "p3-tunnel":
            tunnel = cfg.stage["tunnel"]
            presses = (
                tunnel["press_distance_range_m"]
                if "press_distance_range_m" in tunnel
                else (tunnel["trigger_distance_m"],)
            )
            rise = (
                float(np.mean(cfg.stage["height_range_m"]))
                if cfg.stage["height_range_m"] is not None
                else tunnel["beam_height_m"] + tunnel["clearance_margin_m"]
            )
            for i, vx in enumerate(np.unique(np.linspace(*tunnel["vx_range_m_s"], 3))):
                for j, press in enumerate(dict.fromkeys(presses)):
                    cases.append(
                        EvaluationCase(
                            f"tunnel_speed{i}_press{j}",
                            (float(vx), 0.0, 0.0),
                            e["height_m"],
                            jump_count=1,
                            jump_height=rise,
                            press_distance_m=press,
                        )
                    )
        else:
            vx = cfg.settings["commands"]["vx_range_m_s"]
            speeds = np.unique([0.0, *np.linspace(*vx, 3)])
            heights = cfg.stage.get("height_levels_m")
            if heights is None:
                heights = np.unique(np.linspace(*cfg.stage["height_range_m"], 5))
            for i, speed in enumerate(speeds):
                cmd = (float(speed), 0.0, 0.0)
                cases.append(EvaluationCase(f"flat_speed{i}_no_press", cmd, e["height_m"]))
                for j, rise in enumerate(heights):
                    cases.append(
                        EvaluationCase(
                            f"flat_speed{i}_height{j}",
                            cmd,
                            e["height_m"],
                            jump_count=1,
                            jump_height=float(rise),
                        )
                    )
    elif family == "p2":
        speeds = np.linspace(*cfg.stage["translation_speed_range_m_s"], 3)
        rates = (*cfg.stage["spin_low_range_rad_s"], *cfg.stage["spin_high_range_rad_s"])
        for rate in rates:
            for speed in speeds:
                for sign in (-1, 1):
                    cases.append(
                        EvaluationCase(
                            f"spin_{sign * rate:.2f}_translate_{speed:.2f}",
                            (0.0, 0.0, sign * rate),
                            e["height_m"],
                            (float(speed), 0.0),
                        )
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
