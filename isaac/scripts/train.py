import argparse
import hashlib
import json
import math
import shutil
import subprocess
from pathlib import Path

from wheelleg.tasks import TASKS
from wheelleg.training import load_training, runner_config


def main() -> None:
    parser = argparse.ArgumentParser(description="Train SRM P1/P2/P3 with Isaac Lab 2.3.2 / rsl_rl 3.1.2")
    parser.add_argument("--handoff-duration", type=float, help="Post-handoff observation seconds; 0 ends at settle")
    parser.add_argument(
        "--air-motion-update", action="store_true", help="Explicitly migrate only air-motion reward settings"
    )
    parser.add_argument(
        "--crouch-guidance-update", action="store_true", help="Explicitly migrate only supported crouch guidance"
    )
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
    parser.add_argument("--actor-bundle", type=Path, help="Frozen base and trainable specialist manifest")
    parser.add_argument(
        "--handoff-vertical-speed",
        type=float,
        help="Explicitly override only the bundle handoff vertical-speed limit (m/s), including on resume",
    )
    parser.add_argument("--num-envs", type=int)
    parser.add_argument("--iterations", type=int)
    parser.add_argument(
        "--initial-jump-level", type=int, help="One-based starting level for both fresh flat-jump curricula"
    )
    parser.add_argument(
        "--restart-jump-level",
        type=int,
        help="With --resume: reset both flat-jump acceptance windows at this one-based level",
    )
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
    if args.handoff_vertical_speed is not None and (
        not math.isfinite(args.handoff_vertical_speed) or args.handoff_vertical_speed <= 0
    ):
        parser.error("--handoff-vertical-speed must be finite and positive")
    if args.handoff_duration is not None and (not math.isfinite(args.handoff_duration) or args.handoff_duration < 0):
        parser.error("--handoff-duration must be finite and nonnegative")
    if args.inherit_action_std and not args.initialize_from:
        parser.error("--inherit-action-std needs --initialize-from")
    if args.command_fraction is not None and (not args.resume or not 0 < args.command_fraction <= 1):
        parser.error("--command-fraction needs --resume and a value in (0, 1]")
    if args.restart_air_height and (not args.resume or args.task != "p1-landing"):
        parser.error("--restart-air-height needs --resume and --task p1-landing")
    path = args.policy or Path(f"config/policies/{TASKS[args.task].policy}/policy_meta.yaml")
    cfg = load_training(args.task, args.robot, path)
    if args.restart_jump_level is not None and (
        not args.resume
        or args.initial_jump_level is not None
        or args.task != "p3-jump"
        or "moving_probability" not in cfg.stage
        or not 1 <= args.restart_jump_level <= len(cfg.stage.get("height_levels_m", ()))
    ):
        parser.error("--restart-jump-level requires --resume on staged p3-jump and a valid level")
    if args.initial_jump_level is not None and (
        args.resume
        or args.task != "p3-jump"
        or "moving_probability" not in cfg.stage
        or not 1 <= args.initial_jump_level <= len(cfg.stage.get("height_levels_m", ()))
    ):
        parser.error("--initial-jump-level needs fresh staged flat-jump curricula and a valid level")
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
    if args.actor_bundle is None and args.resume:
        saved_bundle = args.resume.parent / "params/actor_bundle.yaml"
        if saved_bundle.exists():
            args.actor_bundle = saved_bundle
    if args.handoff_vertical_speed is not None and args.actor_bundle is None:
        parser.error("--handoff-vertical-speed requires an actor bundle")
    if args.handoff_duration is not None and args.actor_bundle is None:
        parser.error("--handoff-duration requires an actor bundle")
    if args.air_motion_update and (not args.resume or args.actor_bundle is None):
        parser.error("--air-motion-update requires a multi-actor --resume")
    if args.crouch_guidance_update and (not args.resume or args.actor_bundle is None):
        parser.error("--crouch-guidance-update requires a multi-actor --resume")
    if "crouch_guidance" in cfg.stage.get("clearance_jump", {}) and args.actor_bundle is None:
        parser.error("crouch_guidance requires multi-actor full-outcome grading")
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
        initial_jump_level=args.initial_jump_level,
        restart_jump_level=args.restart_jump_level,
        handoff_vertical_speed_override=args.handoff_vertical_speed,
        handoff_duration_override=args.handoff_duration,
        air_motion_reward_update=args.air_motion_update,
        crouch_guidance_update=args.crouch_guidance_update,
        allow_unvalidated_baseline=args.allow_unvalidated_baseline,
        control_hz=cfg.robot.control_hz,
        policy_hz=cfg.robot.policy_hz,
        obs_version=cfg.policy.obs_version,
        guide_version="2.2",
        guide_sha256=hashlib.sha256(Path("docs/轮腿RL_推进指南_v2.md").read_bytes()).hexdigest(),
    )
    bundle = None
    if args.actor_bundle:
        import yaml

        from wheelleg.multi_actor import read_bundle

        if args.task != "p3-jump":
            parser.error("Specialist training currently supports p3-jump")
        bundle = read_bundle(args.actor_bundle)
        from wheelleg.jump_outcomes import HANDOFF_COST_TIMING

        manifest["handoff_failure_cost_timing"] = HANDOFF_COST_TIMING
        if args.handoff_duration is not None:
            manifest["previous_handoff_duration_s"] = bundle["handoff"]["duration_s"]
            bundle["handoff"]["duration_s"] = args.handoff_duration
            if args.handoff_duration == 0:
                bundle["handoff"]["failure_cost"] = 0.0
        if args.handoff_vertical_speed is not None:
            manifest["previous_handoff_vertical_speed_m_s"] = bundle["handoff"]["vertical_speed_m_s"]
            bundle["handoff"]["vertical_speed_m_s"] = args.handoff_vertical_speed
        from copy import deepcopy

        portable = deepcopy(bundle)
        for name, spec in bundle["actors"].items():
            destination = params / "actors" / name
            destination.mkdir(parents=True)
            for key, filename in (("checkpoint", "model.pt"), ("policy", "policy_meta.yaml"), ("robot", "robot.yaml")):
                shutil.copy2(spec[key], destination / filename)
                portable["actors"][name][key] = str(Path("actors") / name / filename)
        (params / "actor_bundle.yaml").write_text(yaml.safe_dump(portable, sort_keys=False), encoding="utf-8")
        manifest["actor_bundle"] = str((params / "actor_bundle.yaml").resolve())
        if not args.resume and not args.initialize_from:
            manifest["initialize_from"] = bundle["actors"][bundle["trainable_actor"]]["checkpoint"]
    (params / "run.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    app = AppLauncher(args).app
    try:
        from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper

        from isaac.wheelleg_tasks.env import WheelLegEnv
        from isaac.wheelleg_tasks.env_cfg import make_env_cfg
        from isaac.wheelleg_tasks.runner import WheelLegRunner

        env_cfg = make_env_cfg(cfg, num_envs, args.device, allow_unvalidated_baseline=args.allow_unvalidated_baseline)
        if bundle is None:
            env = WheelLegEnv(env_cfg)
        else:
            from isaac.wheelleg_tasks.multi_actor import MultiActorEnv

            env = MultiActorEnv(env_cfg, bundle)
        try:
            if args.initial_jump_level is not None:
                for curriculum in env.flat_jump_curricula:
                    curriculum.maximum_level = args.initial_jump_level - 1
            # Never clip at the wrapper: obs_v2 contains the previous RAW action.
            wrapped = RslRlVecEnvWrapper(env, clip_actions=None)
            runner = WheelLegRunner(wrapped, runner_config(cfg), log_dir=str(output), device=args.device)
            runner.add_git_repo_to_log(__file__)
            if args.resume:
                old = json.loads((args.resume.parent / "params/run.json").read_text(encoding="utf-8"))
                if old["task"] != args.task or old["obs_version"] != cfg.policy.obs_version:
                    raise ValueError("--resume requires the same task and observation contract; use --initialize-from")
                restored = runner.load(
                    str(args.resume),
                    load_optimizer=True,
                    restart_command_curriculum=args.command_fraction is not None,
                    handoff_vertical_speed=args.handoff_vertical_speed,
                    handoff_duration=args.handoff_duration,
                    air_motion_update=args.air_motion_update,
                    crouch_guidance_update=args.crouch_guidance_update,
                )
                if bundle is not None:
                    manifest["previous_handoff_failure_cost_timing"] = restored.get(
                        "handoff_failure_cost_timing", "observation_end"
                    )
                    (params / "run.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
                    previous_timing = manifest["previous_handoff_failure_cost_timing"]
                    print(f"HANDOFF_FAILURE_COST_TIMING {previous_timing} -> {HANDOFF_COST_TIMING}")
                runner.current_learning_iteration += 1
                env.training_iteration_offset = runner.current_learning_iteration
                if args.handoff_vertical_speed is not None or args.handoff_duration is not None:
                    # The old window used a different acceptance limit; retain levels and learned guidance.
                    for curriculum in env.flat_jump_curricula:
                        curriculum.attempts.zero_()
                        curriculum.successes.zero_()
                        curriculum.latest_rate.zero_()
                    env.reset()
                    print(f"HANDOFF_ACCEPTANCE_RESET {bundle['handoff']}")
                if args.restart_jump_level is not None:
                    for curriculum in env.flat_jump_curricula:
                        curriculum.restart(args.restart_jump_level)
                    # Discard physical states sampled at the old level; actor/critic/optimizer stay restored.
                    env.reset()
                    height = env.flat_jump_curricula[0].levels[args.restart_jump_level - 1].item()
                    print(f"JUMP_LEVEL_RESET level={args.restart_jump_level} height_m={height}")
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
            elif bundle is not None:
                initialize_actor(runner, Path(bundle["actors"][bundle["trainable_actor"]]["checkpoint"]))
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
