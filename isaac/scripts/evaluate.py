import argparse
import json
from dataclasses import replace
from pathlib import Path

import yaml

from wheelleg.tasks import TASKS
from wheelleg.training import _freeze, load_training, mutable


def main() -> None:
    parser = argparse.ArgumentParser(description="Fixed command evaluation; reset episodes never count as successes")
    parser.add_argument("--task", choices=TASKS, required=True)
    parser.add_argument("--robot", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, nargs="+", required=True)
    parser.add_argument("--evaluation-policy", type=Path, help="Read only training.evaluation from this policy YAML")
    parser.add_argument("--suite", choices=("auto", "legacy"), default="auto")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--video", action="store_true")
    args, _ = parser.parse_known_args()
    cfg = load_training(args.task, args.robot, args.policy)
    detailed = args.task == "p1-flat" and args.suite == "auto"
    if args.evaluation_policy:
        override = yaml.safe_load(args.evaluation_policy.read_text(encoding="utf-8"))
        settings = mutable(cfg.settings)
        settings["evaluation"] = override["training"]["evaluation"]
        cfg = replace(cfg, settings=_freeze(settings))
    if detailed:
        from wheelleg.flat_evaluation import validate_flat_suite

        validate_flat_suite(cfg)
    elif len(args.checkpoint) != 1:
        parser.error("Multiple checkpoints are supported by the detailed p1-flat suite only")
    cfg.require_ready(evaluation=True)
    from isaaclab.app import AppLauncher

    AppLauncher.add_app_launcher_args(parser)
    args = parser.parse_args()
    if args.video:
        args.enable_cameras = True
    app = AppLauncher(args).app
    try:
        if detailed:
            from isaac.scripts.flat_evaluate import run

            run(args, cfg)
            return
        import gymnasium as gym
        import numpy as np
        import torch

        from isaac.wheelleg_tasks.env import WheelLegEnv
        from isaac.wheelleg_tasks.env_cfg import make_env_cfg
        from wheelleg.checkpoints import load_policy_module
        from wheelleg.evaluation import evaluation_cases, metrics

        settings = cfg.settings["evaluation"]
        count = settings["episodes_per_case"]
        stairs = cfg.task == "p1-stairs"
        if stairs and count < cfg.stage["terrain"]["rows"]:
            raise ValueError("Stairs evaluation needs at least one episode per terrain difficulty row")
        duration = (
            max(settings["duration_s"], cfg.stage["course"]["episode_length_s"]) if stairs else settings["duration_s"]
        )
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
                video_length=int(duration / raw.step_dt),
            )
        try:
            # Reset may mutate rollout inference tensors; keep all cases in the same inference scope.
            with torch.inference_mode():
                actor = load_policy_module(args.checkpoint[0], cfg.policy).to(args.device)
                report, observations, histories = [], [], []
                handover = {key: [] for key in ("root_state", "joint_position", "joint_velocity")}
                raw.commands_fixed = True
                for case in evaluation_cases(cfg):
                    command = torch.tensor(case.command, device=args.device)
                    raw.fixed_command = (command, case.height)
                    if stairs:
                        # terrain_importer.py:315-355: assign verified types/levels and origins before reset.
                        group = raw.stair_course.names.index(case.terrain_profile)
                        columns = (raw.stair_course.column_groups == group).nonzero().flatten()
                        slots = torch.arange(count, device=args.device)
                        rows = cfg.stage["terrain"]["rows"]
                        raw.terrain.terrain_types.copy_(columns[(slots // rows) % len(columns)])
                        raw.terrain.terrain_levels.copy_(slots % rows)
                        raw.terrain.env_origins.copy_(
                            raw.terrain.terrain_origins[slots % rows, raw.terrain.terrain_types]
                        )
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
                    traversed = torch.zeros_like(alive)
                    stopped = torch.zeros_like(alive)
                    escaped = torch.zeros_like(alive)
                    neutral_exit = torch.zeros_like(alive)
                    tracking = torch.zeros(count, device=args.device)
                    levels = raw.terrain.terrain_levels.cpu().numpy().copy() if stairs else None
                    errors, valid, displacement = [], [], []
                    start_position = raw.robot.data.root_pos_w.clone()
                    with torch.inference_mode():
                        for step in range(int(duration / raw.step_dt)):
                            actions = actor(obs["policy"], obs.get("history"))
                            if len(observations) < 1000:
                                observations.extend(obs["policy"][alive].cpu().numpy())
                                if "history" in obs:
                                    histories.extend(obs["history"][alive].cpu().numpy())
                            obs, _, terminated, timeout, extras = env.step(actions)
                            if not stairs and step >= int(duration / raw.step_dt) - 10:
                                keep = alive & ~(terminated | timeout)
                                root_state = raw.robot.data.root_state_w[keep].clone()
                                root_state[:, :3] -= raw.terrain.env_origins[keep]
                                handover["root_state"].append(root_state.cpu().numpy())
                                handover["joint_position"].append(raw.robot.data.joint_pos[keep].cpu().numpy().copy())
                                handover["joint_velocity"].append(raw.robot.data.joint_vel[keep].cpu().numpy().copy())
                            info = extras["evaluation"]
                            failed |= alive & info["failed"]
                            if not stairs:
                                succeeded |= alive & info["jump_success"]
                            if stairs:
                                traversed |= alive & info["stair_traversed"]
                                stopped |= alive & info["stair_stopped"]
                                ended = terminated | timeout | (step + 1 == int(duration / raw.step_dt))
                                succeeded = torch.where(alive & ended, info["stair_success"] & ~terminated, succeeded)
                                escaped |= alive & info["stair_escaped"]
                                neutral_exit |= alive & info["stair_neutral_exit"]
                                tracking.copy_(torch.where(alive, info["stair_tracking"], tracking))
                                keep = alive & ended & info["stair_success"] & ~terminated
                                for key in handover:
                                    handover[key].append(info[key][keep].cpu().numpy().copy())
                            errors.append(info["errors"].cpu().numpy())
                            valid.append((alive & (step * raw.step_dt >= settings["settling_s"])).cpu().numpy())
                            displacement.append(
                                torch.where(alive, (info["position"] - start_position)[:, :2].norm(dim=-1), 0.0)
                                .cpu()
                                .numpy()
                            )
                            alive &= ~(terminated | timeout)
                            if stairs and not alive.any():
                                break
                    result = metrics(np.stack(errors), np.stack(valid), failed.cpu().numpy())
                    result.update(
                        case=case.name,
                        jump_requested=case.jump_count,
                        jump_successes=0 if stairs else int(succeeded.sum()),
                        completed_duration=int(alive.sum()),
                        maximum_displacement_m=float(np.max(displacement)),
                    )
                    if stairs:
                        eligible = ~neutral_exit
                        succeeded &= eligible
                        eligible_count = int(eligible.sum())
                        success_array = succeeded.cpu().numpy()
                        result.update(
                            terrain_profile=case.terrain_profile,
                            neutral_exits=int(neutral_exit.sum()),
                            eligible_episodes=eligible_count,
                            task_successes=int(succeeded.sum()),
                            task_success_rate=int(succeeded.sum()) / eligible_count if eligible_count else None,
                            geometry_crossings=int(traversed.sum()),
                            final_stops=int(stopped.sum()),
                            traversal_successes=int((traversed & eligible & ~failed).sum()),
                            traversal_success_rate=int((traversed & eligible & ~failed).sum()) / eligible_count
                            if eligible_count
                            else None,
                            escaped=int(escaped.sum()),
                            mean_tracking_return=float(tracking.mean()),
                            difficulty_rows={},
                        )
                        for level in range(cfg.stage["terrain"]["rows"]):
                            selected = levels == level
                            valid_selected = selected & eligible.cpu().numpy()
                            valid_count = int(valid_selected.sum())
                            result["difficulty_rows"][str(level)] = dict(
                                episodes=int(selected.sum()),
                                eligible_episodes=valid_count,
                                neutral_exits=int(neutral_exit.cpu().numpy()[selected].sum()),
                                task_successes=int(success_array[selected].sum()),
                                task_success_rate=int(success_array[valid_selected].sum()) / valid_count
                                if valid_count
                                else None,
                                geometry_crossings=int(traversed.cpu().numpy()[selected].sum()),
                                final_stops=int(stopped.cpu().numpy()[selected].sum()),
                                failures=int(failed.cpu().numpy()[selected].sum()),
                            )
                    if cfg.task == "p2-spin":
                        # terrain_importer.py:348 assigns environments to terrain columns.
                        # Groups describe the spawn patch; translating robots can cross patch boundaries.
                        terrain = cfg.stage["terrain"]
                        columns = raw.terrain.terrain_types.cpu().numpy()
                        lower = 0
                        result["spawn_terrain_groups"] = {}
                        for name in ("flat", "rough", "slope"):
                            upper = lower + round(terrain[f"{name}_proportion"] * terrain["columns"])
                            selected = (columns >= lower) & (columns < upper)
                            if selected.any():
                                result["spawn_terrain_groups"][name] = metrics(
                                    np.stack(errors)[:, selected],
                                    np.stack(valid)[:, selected],
                                    failed.cpu().numpy()[selected],
                                )
                            lower = upper
                    report.append(result)
                (args.output / "evaluation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
                rollout = dict(observation=np.asarray(observations, dtype=np.float32))
                if histories:
                    rollout["history"] = np.asarray(histories, dtype=np.float32)
                np.savez(args.output / "rollout.npz", **rollout)
                np.savez(
                    args.output / "transition_states.npz",
                    **{key: np.concatenate(values, axis=0) for key, values in handover.items()},
                    joint_names=np.asarray(raw.robot.joint_names),
                )
                lines = [
                    "| Case | Episodes | Failures | e_v | e_w | e_h | Task successes / jumps |",
                    "|---|---:|---:|---:|---:|---:|---:|",
                ]
                for row in report:
                    successes = row["task_successes"] if stairs else row["jump_successes"]
                    lines.append(
                        f"| {row['case']} | {row['episodes']} | {row['failures']} | "
                        f"{row['mean_abs_velocity_error']} | {row['mean_abs_yaw_rate_error']} | "
                        f"{row['mean_abs_height_error']} | {successes} |"
                    )
                (args.output / "evaluation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
                print(json.dumps(report, indent=2))
        finally:
            env.close()
    finally:
        app.close()


if __name__ == "__main__":
    main()
