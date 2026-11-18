"""SHU fixed-command evaluation and manually specified P3 rollout collection."""

import argparse
import json
from math import isfinite
from pathlib import Path

from wheelleg.observation import POLICY_OBS_DIM
from wheelleg.tasks import TASKS
from wheelleg.training import load_training


def _manual_press(parser, args, cfg):
    is_p3 = TASKS[args.task].policy == "p3"
    manual = (args.vx_m_s, args.press_time_s, args.jump_height_m)
    if not is_p3:
        if args.no_press or any(value is not None for value in manual):
            parser.error("Manual speed and button options are only for P3 rollouts")
        return None

    tunnel = args.task == "p3-tunnel"
    lo, hi = cfg.stage["tunnel"]["vx_range_m_s"] if tunnel else cfg.settings["commands"]["vx_range_m_s"]
    vx = args.vx_m_s
    if vx is None or not isfinite(vx) or not ((not tunnel and vx == 0) or 0 < vx and lo <= vx <= hi):
        parser.error("P3 requires --vx-m-s in the configured forward range (or zero on p3-jump)")
    if args.no_press:
        if args.jump_height_m is not None:
            parser.error("--no-press cannot be combined with --jump-height-m")
        return (False, None)

    threshold = args.press_time_s
    if threshold is None or not isfinite(threshold) or threshold < 0:
        parser.error(f"{args.task} requires either --no-press or an explicit nonnegative --press-time-s")
    steps = round(cfg.settings["evaluation"]["duration_s"] * cfg.robot.policy_hz)
    if threshold > (steps - 1) * (1 / cfg.robot.policy_hz):
        parser.error("--press-time-s must fall on or before the last actionable policy tick")
    height = args.jump_height_m
    low, high = cfg.stage["height_range_m"]
    if height is None or not isfinite(height) or not low <= height <= high:
        parser.error("A pressed rollout requires --jump-height-m in the configured root-rise range")
    return (True, threshold)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", choices=TASKS, required=True)
    parser.add_argument("--robot", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True, help="Explicitly selected SHU obs_v3 checkpoint")
    parser.add_argument(
        "--from-p3-jump", action="store_true", help="Use a same-contract p3-jump checkpoint in p3-tunnel"
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--video", action="store_true")
    parser.add_argument("--vx-m-s", type=float, help="Manual P3 forward command in m/s")
    parser.add_argument("--jump-height-m", type=float, help="Manual P3 root-rise target, not obstacle height")
    button = parser.add_mutually_exclusive_group()
    button.add_argument("--no-press", action="store_true", help="Collect a manual P3 rollout without a button edge")
    button.add_argument("--press-time-s", type=float, help="Operator-selected press time for either P3 stage")
    args, _ = parser.parse_known_args()
    if args.from_p3_jump and args.task != "p3-tunnel":
        parser.error("--from-p3-jump requires --task p3-tunnel")
    cfg = load_training(args.task, args.robot, args.policy)
    cfg.require_ready(evaluation=True)
    press = _manual_press(parser, args, cfg)
    from isaaclab.app import AppLauncher

    AppLauncher.add_app_launcher_args(parser)
    args = parser.parse_args()
    from wheelleg.checkpoints import load_actor, load_landing_transfer

    source_task = "p3-jump" if args.from_p3_jump else args.task
    flat_transfer = None
    if args.task == "p1-landing":
        flat_transfer = load_landing_transfer(
            args.checkpoint, cfg.policy, source_task=source_task, commands=cfg.settings["commands"]
        )
    actor = load_actor(args.checkpoint, cfg.policy, source_task=source_task)
    if args.video:
        args.enable_cameras = True
    app = AppLauncher(args).app
    try:
        import numpy as np
        import torch

        from isaac.wheelleg_tasks.env import WheelLegEnv
        from isaac.wheelleg_tasks.env_cfg import make_env_cfg
        from wheelleg.evaluation import EvaluationCase, evaluation_cases, metrics
        from wheelleg.history import HISTORY_DIM

        settings = cfg.settings["evaluation"]
        count = settings["episodes_per_case"]
        env_cfg = make_env_cfg(cfg, count, args.device, evaluation=True, flat_transfer=flat_transfer)
        env_cfg.seed = settings["seed"]
        steps = round(settings["duration_s"] * cfg.robot.policy_hz)
        if count <= 0 or steps <= 0:
            raise ValueError("Evaluation requires a positive episode count and rollout duration")
        cases = (
            [EvaluationCase("manual_p3", (args.vx_m_s, 0.0, 0.0), settings["height_m"])]
            if press is not None
            else evaluation_cases(cfg)
        )
        args.output.mkdir(parents=True, exist_ok=False)
        raw = WheelLegEnv(env_cfg, render_mode="rgb_array" if args.video else None)
        env = raw
        try:
            if args.video:
                from gymnasium.wrappers import RecordVideo

                env = RecordVideo(
                    raw,
                    video_folder=str(args.output / "videos"),
                    episode_trigger=lambda episode: True,
                    video_length=steps,
                )
            actor = actor.to(args.device)
            report, observations, histories = [], [], []
            raw.commands_fixed = True
            for case in cases:
                raw.fixed_command = (torch.tensor(case.command, device=args.device), case.height)
                obs, _ = env.reset(seed=settings["seed"])
                alive = torch.ones(count, dtype=torch.bool, device=args.device)
                failed = torch.zeros_like(alive)
                press_sent = False
                button_down = False
                errors, valid = [], []
                start_position = raw.robot.data.root_pos_w.clone()
                max_displacement = torch.zeros((), device=args.device)
                with torch.inference_mode():
                    for step in range(steps):
                        if press is not None:
                            enabled, threshold = press
                            new_press = enabled and not press_sent and step * raw.step_dt >= threshold
                            if new_press or button_down:
                                level = alive if new_press else torch.zeros_like(alive)
                                obs = raw.set_jump_button(
                                    level, target_height_m=args.jump_height_m if new_press else None
                                )
                            press_sent |= new_press
                            button_down = new_press
                        actions = actor(obs["policy"], obs["history"])
                        if press is not None or len(observations) < 1000:
                            # Boolean indexing snapshots live history before env.step() mutates its buffer.
                            observations.extend(obs["policy"][alive].cpu().numpy())
                            histories.extend(obs["history"][alive].cpu().numpy())
                        obs, _, terminated, timeout, extras = env.step(actions)
                        if press is None:
                            info = extras["evaluation"]
                            failed |= alive & info["failed"]
                            errors.append(info["errors"].cpu().numpy())
                            valid.append((alive & (step * raw.step_dt >= settings["settling_s"])).cpu().numpy())
                            distance = (info["position"] - start_position)[:, :2].norm(dim=-1)
                            max_displacement = torch.maximum(max_displacement, distance[alive].max())
                        alive &= ~(terminated | timeout)
                        if not alive.any():
                            break
                if press is None:
                    result = metrics(np.stack(errors), np.stack(valid), failed.cpu().numpy())
                    result.update(
                        case=case.name,
                        completed_duration=int(alive.sum()),
                        maximum_displacement_m=max_displacement.item(),
                    )
                    report.append(result)
            np.savez(
                args.output / "rollout.npz",
                observation=np.asarray(observations, dtype=np.float32).reshape(-1, POLICY_OBS_DIM),
                obs_history=np.asarray(histories, dtype=np.float32).reshape(-1, HISTORY_DIM),
            )
            if press is not None:
                print("Saved a manual P3 rollout, not a jump evaluation or acceptance result.")
                return
            (args.output / "evaluation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
            lines = [
                "| Case | Episodes | Failures | Mean abs vx error | Mean abs yaw error | Mean abs height error |",
                "|---|---:|---:|---:|---:|---:|",
            ]
            for row in report:
                lines.append(
                    f"| {row['case']} | {row['episodes']} | {row['failures']} | "
                    f"{row['mean_abs_velocity_error']} | {row['mean_abs_yaw_rate_error']} | "
                    f"{row['mean_abs_height_error']} |"
                )
            (args.output / "evaluation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
            print(json.dumps(report, indent=2))
        finally:
            env.close()
    finally:
        app.close()


if __name__ == "__main__":
    main()
