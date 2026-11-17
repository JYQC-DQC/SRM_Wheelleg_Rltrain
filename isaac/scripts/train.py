import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

from wheelleg.tasks import TASKS
from wheelleg.training import load_training, runner_config


def main() -> None:
    parser = argparse.ArgumentParser(description="Train SRM P1/P2/P3 with Isaac Lab 2.3.2 / rsl_rl 3.1.2")
    parser.add_argument("--task", choices=TASKS, required=True)
    parser.add_argument("--robot", type=Path, default=Path("config/robot.yaml"))
    parser.add_argument("--policy", type=Path)
    parser.add_argument("--check-only", action="store_true", help="List missing values without importing Isaac/Torch")
    parser.add_argument(
        "--allow-unvalidated-baseline",
        action="store_true",
        help="Explicitly bypass only the baseline-evaluation gate and record the override in run.json",
    )
    parser.add_argument("--run-name")
    parser.add_argument("--num-envs", type=int)
    parser.add_argument("--iterations", type=int)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--resume", type=Path, help="Restore this task's policy, critic, optimizer and iteration")
    group.add_argument("--initialize-from", type=Path, help="Transfer actor weights to a new stage/policy")
    parser.add_argument(
        "--inherit-action-std",
        action="store_true",
        help="With --initialize-from: also retain the checkpoint's learned per-action exploration std",
    )
    parser.add_argument(
        "--command-fraction",
        type=float,
        help="With --resume: restart the P1 command curriculum at this fraction (open window discarded)",
    )
    parser.add_argument(
        "--restart-air-height",
        action="store_true",
        help="With --resume on p1-landing: restart the air-birth height curriculum at its first level",
    )
    args, _ = parser.parse_known_args()
    if args.inherit_action_std and not args.initialize_from:
        parser.error("--inherit-action-std needs --initialize-from")
    if args.command_fraction is not None and (not args.resume or not 0 < args.command_fraction <= 1):
        parser.error("--command-fraction needs --resume and a value in (0, 1]")
    if args.restart_air_height and (not args.resume or args.task != "p1-landing"):
        parser.error("--restart-air-height needs --resume and --task p1-landing")
    path = args.policy or Path(f"config/policies/{TASKS[args.task].policy}/policy_meta.yaml")
    cfg = load_training(args.task, args.robot, path)
    if args.check_only:
        print(
            json.dumps(
                {"task": args.task, "initialize_from_task": TASKS[args.task].initialize_from, "missing": cfg.missing()},
                ensure_ascii=False,
                indent=2,
            )
        )
        return
    if args.task == "p3-tunnel" and "press_distance_range_m" in cfg.stage["tunnel"]:
        if not (args.resume or args.initialize_from):
            parser.error("Train p3-jump first and pass its checkpoint with --initialize-from")
    cfg.require_ready(allow_unvalidated_baseline=args.allow_unvalidated_baseline)
    if not args.run_name or Path(args.run_name).name != args.run_name:
        parser.error("--run-name must be one directory name")
    from isaaclab.app import AppLauncher

    AppLauncher.add_app_launcher_args(parser)
    args = parser.parse_args()
    from wheelleg.checkpoints import initialize_actor, require_target_runtime

    require_target_runtime()
    num_envs = cfg.settings["num_envs"] if args.num_envs is None else args.num_envs
    iterations = cfg.settings["max_iterations"] if args.iterations is None else args.iterations
    if num_envs <= 0 or iterations <= 0:
        parser.error("--num-envs and --iterations must be positive")
    output = Path("runs") / args.run_name
    output.mkdir(parents=True, exist_ok=False)
    params = output / "params"
    params.mkdir()
    shutil.copy2(args.robot, params / "robot.yaml")
    shutil.copy2(path, params / "policy_meta.yaml")
    commit = subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    manifest = dict(
        task=args.task,
        git_commit=commit,
        workspace_dirty=bool(
            subprocess.run(["git", "status", "--porcelain"], check=True, capture_output=True, text=True).stdout.strip()
        ),
        num_envs=num_envs,
        iterations=iterations,
        resume=str(args.resume) if args.resume else None,
        initialize_from=str(args.initialize_from) if args.initialize_from else None,
        inherit_action_std=args.inherit_action_std,
        allow_unvalidated_baseline=args.allow_unvalidated_baseline,
        control_hz=cfg.robot.control_hz,
        policy_hz=cfg.robot.policy_hz,
        obs_version=cfg.policy.obs_version,
        guide_version="2.2",
        guide_sha256=hashlib.sha256(Path("docs/轮腿RL_推进指南_v2.md").read_bytes()).hexdigest(),
    )
    (params / "run.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    app = AppLauncher(args).app
    try:
        from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper

        from isaac.wheelleg_tasks.env import WheelLegEnv
        from isaac.wheelleg_tasks.env_cfg import make_env_cfg
        from isaac.wheelleg_tasks.runner import WheelLegRunner

        env = WheelLegEnv(
            make_env_cfg(cfg, num_envs, args.device, allow_unvalidated_baseline=args.allow_unvalidated_baseline)
        )
        try:
            # Never clip at the wrapper: obs_v2 contains the previous RAW action.
            wrapped = RslRlVecEnvWrapper(env, clip_actions=None)
            runner = WheelLegRunner(wrapped, runner_config(cfg), log_dir=str(output), device=args.device)
            runner.add_git_repo_to_log(__file__)
            if args.resume:
                old = json.loads((args.resume.parent / "params/run.json").read_text(encoding="utf-8"))
                if old["task"] != args.task or old["obs_version"] != cfg.policy.obs_version:
                    raise ValueError("--resume requires the same task and observation contract; use --initialize-from")
                runner.load(
                    str(args.resume), load_optimizer=True, restart_command_curriculum=args.command_fraction is not None
                )
                runner.current_learning_iteration += 1
                env.training_iteration_offset = runner.current_learning_iteration
                if args.task == "p3-tunnel" and "mix_switch_iteration" in cfg.stage["tunnel"]:
                    # Initial construction precedes loading the absolute iteration.
                    # Reapply the mix at episode reset before collecting resumed rollouts.
                    env.reset()
                if args.command_fraction is not None:
                    if env.command_curriculum is None:
                        raise ValueError("--command-fraction applies only to P1 tasks")
                    env.command_curriculum.restart(args.command_fraction)
                    env.commands.command_fraction = args.command_fraction
                    print(f"COMMAND_FRACTION_RESET {args.command_fraction}")
                if args.restart_air_height:
                    env.air_height_curriculum.restart()
                    # Gate counts were taken in the old newest band; refill them from the first one.
                    env.command_curriculum.discard_landing()
                    print(f"AIR_HEIGHT_RESET {env.air_height_curriculum.upper}")
            elif args.initialize_from:
                initialize_actor(runner, args.initialize_from, inherit_action_std=args.inherit_action_std)
                if args.inherit_action_std:
                    print(f"INHERITED_ACTION_STD {runner.alg.policy.std.detach().tolist()}")
            # Mixed jump episodes use physical-age triggers and one full attempt.
            # A randomized initial timeout can cut them off before takeoff.
            runner.learn(num_learning_iterations=iterations, init_at_random_ep_len=TASKS[args.task].policy != "p3")
        except Exception:
            import traceback

            traceback.print_exc()
            raise
        finally:
            env.close()
    except Exception:
        import traceback

        traceback.print_exc()
        raise
    finally:
        app.close()


if __name__ == "__main__":
    main()
