import argparse
import json
from pathlib import Path

from wheelleg.tasks import TASKS
from wheelleg.training import load_training


def main() -> None:
    parser = argparse.ArgumentParser(description="Fixed command evaluation; reset episodes never count as successes")
    parser.add_argument("--task", choices=TASKS, required=True)
    parser.add_argument("--robot", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--video", action="store_true")
    args, _ = parser.parse_known_args()
    cfg = load_training(args.task, args.robot, args.policy)
    cfg.require_ready(evaluation=True)
    from isaaclab.app import AppLauncher

    AppLauncher.add_app_launcher_args(parser)
    args = parser.parse_args()
    if args.video:
        args.enable_cameras = True
    app = AppLauncher(args).app
    try:
        import gymnasium as gym
        import numpy as np
        import torch

        from isaac.wheelleg_tasks.env import WheelLegEnv
        from isaac.wheelleg_tasks.env_cfg import make_env_cfg
        from wheelleg.checkpoints import load_actor
        from wheelleg.evaluation import evaluation_cases, metrics

        settings = cfg.settings["evaluation"]
        count = settings["episodes_per_case"]
        env_cfg = make_env_cfg(cfg, count, args.device, evaluation=True)
        env_cfg.seed = settings["seed"]
        env = WheelLegEnv(env_cfg, render_mode="rgb_array" if args.video else None)
        raw = env
        args.output.mkdir(parents=True, exist_ok=False)
        if args.video:
            env = gym.wrappers.RecordVideo(
                env,
                video_folder=str(args.output / "videos"),
                episode_trigger=lambda episode: True,
                video_length=int(settings["duration_s"] / raw.step_dt),
            )
        try:
            actor = load_actor(args.checkpoint, cfg.policy).to(args.device)
            report, observations = [], []
            handover = {key: [] for key in ("root_state", "joint_position", "joint_velocity")}
            raw.commands_fixed = True
            for case in evaluation_cases(cfg):
                command = torch.tensor(case.command, device=args.device)
                raw.fixed_command = (command, case.height)
                obs, _ = env.reset(seed=settings["seed"])
                raw.commands.translation[:] = torch.tensor(case.translation, device=args.device)
                raw.commands.translation_target.copy_(raw.commands.translation)
                if raw.jump is not None:
                    raw.jump.remaining[:] = case.jump_count
                    raw.fixed_jump_height = case.jump_height
                    raw.jump.next_trigger[:] = cfg.stage["first_trigger_range_s"][0]
                    if cfg.task == "p3-tunnel":
                        # Fixed evaluation count overrides the reset sample; restore/hide the beam accordingly.
                        raw._reset_tunnel(torch.arange(count, device=args.device))
                obs = raw._get_observations()
                alive = torch.ones(count, dtype=torch.bool, device=args.device)
                failed = torch.zeros_like(alive)
                succeeded = torch.zeros_like(alive)
                errors, valid, displacement = [], [], []
                start_position = raw.robot.data.root_pos_w.clone()
                with torch.inference_mode():
                    for step in range(int(settings["duration_s"] / raw.step_dt)):
                        actions = actor(obs["policy"])
                        if len(observations) < 1000:
                            observations.extend(obs["policy"][alive].cpu().numpy())
                        obs, _, terminated, timeout, extras = env.step(actions)
                        if step >= int(settings["duration_s"] / raw.step_dt) - 10:
                            keep = alive & ~(terminated | timeout)
                            root_state = raw.robot.data.root_state_w[keep].clone()
                            root_state[:, :3] -= raw.terrain.env_origins[keep]
                            handover["root_state"].append(root_state.cpu().numpy())
                            handover["joint_position"].append(raw.robot.data.joint_pos[keep].cpu().numpy().copy())
                            handover["joint_velocity"].append(raw.robot.data.joint_vel[keep].cpu().numpy().copy())
                        info = extras["evaluation"]
                        failed |= alive & info["failed"]
                        succeeded |= alive & info["jump_success"]
                        errors.append(info["errors"].cpu().numpy())
                        valid.append((alive & (step * raw.step_dt >= settings["settling_s"])).cpu().numpy())
                        displacement.append((info["position"] - start_position)[:, :2].norm(dim=-1).cpu().numpy())
                        alive &= ~(terminated | timeout)
                result = metrics(np.stack(errors), np.stack(valid), failed.cpu().numpy())
                result.update(
                    case=case.name,
                    jump_requested=case.jump_count,
                    jump_successes=int(succeeded.sum()),
                    completed_duration=int(alive.sum()),
                    maximum_displacement_m=float(np.max(displacement)),
                )
                report.append(result)
            (args.output / "evaluation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
            np.savez(args.output / "rollout.npz", observation=np.asarray(observations, dtype=np.float32))
            np.savez(
                args.output / "transition_states.npz",
                **{key: np.concatenate(values, axis=0) for key, values in handover.items()},
                joint_names=np.asarray(raw.robot.joint_names),
            )
            lines = [
                "| Case | Episodes | Failures | |e_v| | |e_w| | |e_h| | Jump successes |",
                "|---|---:|---:|---:|---:|---:|---:|",
            ]
            for row in report:
                lines.append(
                    f"| {row['case']} | {row['episodes']} | {row['failures']} | "
                    f"{row['mean_abs_velocity_error']} | {row['mean_abs_yaw_rate_error']} | "
                    f"{row['mean_abs_height_error']} | {row['jump_successes']} |"
                )
            (args.output / "evaluation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
            print(json.dumps(report, indent=2))
        finally:
            env.close()
    finally:
        app.close()


if __name__ == "__main__":
    main()
