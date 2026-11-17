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
    parser.add_argument("--run-name")
    parser.add_argument("--num-envs", type=int)
    parser.add_argument("--iterations", type=int)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--resume", type=Path, help="Restore this task's policy, critic, optimizer and iteration")
    group.add_argument("--initialize-from", type=Path, help="Transfer the Actor and velocity encoder to a fresh stage")
    args, _ = parser.parse_known_args()
    path = args.policy or Path(f"config/policies/{TASKS[args.task].policy}/policy_meta.yaml")
    cfg = load_training(args.task, args.robot, path)
    simulate_jump_button = TASKS[args.task].policy == "p3"
    if args.check_only:
        print(
            json.dumps(
                {
                    "task": args.task,
                    "initialize_from_task": TASKS[args.task].initialize_from,
                    "missing": cfg.missing(simulate_jump_button=simulate_jump_button),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return
    if args.task in ("p1-landing", "p1-stairs", "p3-tunnel") and not (args.resume or args.initialize_from):
        source = TASKS[args.task].initialize_from
        parser.error(f"{args.task} requires --initialize-from an explicitly selected {source} checkpoint or --resume")
    cfg.require_ready(simulate_jump_button=simulate_jump_button)  # Before simulator startup.
    if not args.run_name or Path(args.run_name).name != args.run_name:
        parser.error("--run-name must be one directory name")
    from isaaclab.app import AppLauncher

    AppLauncher.add_app_launcher_args(parser)
    args = parser.parse_args()
    from wheelleg.actor import policy_contract
    from wheelleg.checkpoints import initialize_actor, load_actor, load_landing_transfer, require_target_runtime

    require_target_runtime()
    flat_transfer = None
    if args.task == "p1-landing":
        flat_transfer = load_landing_transfer(
            args.resume or args.initialize_from,
            cfg.policy,
            source_task="p1-landing" if args.resume else "p1-flat",
            commands=cfg.settings["commands"],
        )
    elif args.task == "p1-stairs":
        load_actor(
            args.resume or args.initialize_from, cfg.policy, source_task="p1-stairs" if args.resume else "p1-landing"
        )
    if args.task == "p3-tunnel" and args.initialize_from:
        load_actor(args.initialize_from, cfg.policy, source_task="p3-jump")
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
    guide_root = Path("docs/上大轮腿训练方案")
    guide_names = ["上大轮腿训练方案_决策记录_20261115.md"]
    if TASKS[args.task].policy == "p1":
        guide_names.extend(
            (
                "P1_FLAT_REWARD_DESIGN_20261115.md",
                "P1_LANDING_DESIGN_20261116.md",
                "P1_LANDING_REWARD_CURRICULUM_COMPARISON_20261116.md",
            )
        )
    guide_paths = [guide_root / name for name in guide_names]
    guide_payload = b"\0".join(p.read_bytes() for p in guide_paths)
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
        control_hz=cfg.robot.control_hz,
        policy_hz=cfg.robot.policy_hz,
        obs_version=cfg.policy.obs_version,
        policy_contract=policy_contract(cfg.policy),
        guide_sources=[p.as_posix() for p in guide_paths],
        guide_sha256=hashlib.sha256(guide_payload).hexdigest(),
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
            make_env_cfg(
                cfg,
                num_envs,
                args.device,
                flat_transfer=flat_transfer,
                simulate_jump_button=simulate_jump_button,
            )
        )
        try:
            # Never clip at the wrapper: the policy frame contains the previous RAW action.
            wrapped = RslRlVecEnvWrapper(env, clip_actions=None)
            runner = WheelLegRunner(wrapped, runner_config(cfg), log_dir=str(output), device=args.device)
            runner.add_git_repo_to_log(__file__)
            if args.resume:
                old = json.loads((args.resume.parent / "params/run.json").read_text(encoding="utf-8"))
                if old["task"] != args.task or old["obs_version"] != cfg.policy.obs_version:
                    raise ValueError("--resume requires the same task and observation contract; use --initialize-from")
                runner.load(str(args.resume), load_optimizer=True)
                runner.current_learning_iteration += 1
                env.training_iteration_offset = runner.current_learning_iteration
            elif args.initialize_from:
                initialize_actor(runner, args.initialize_from)
            runner.learn(num_learning_iterations=iterations, init_at_random_ep_len=False)
        finally:
            env.close()
    finally:
        app.close()


if __name__ == "__main__":
    main()
