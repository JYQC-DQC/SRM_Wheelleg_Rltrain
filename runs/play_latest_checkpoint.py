from pathlib import Path
import time
from isaaclab.app import AppLauncher
app = AppLauncher(headless=False, experience=str(Path("runs/isaaclab_live.kit").resolve())).app
try:
    import torch
    from wheelleg.training import load_training
    from wheelleg.checkpoints import load_actor
    from isaac.wheelleg_tasks.env import WheelLegEnv
    from isaac.wheelleg_tasks.env_cfg import make_env_cfg
    robot = Path("runs/scut_current_resume200/params/robot.yaml")
    policy = Path("config/reference/scut_p1_original_targets.yaml")
    cfg = load_training("p1-flat", robot, policy)
    actor = load_actor(Path("runs/scut_original_4096_5000/model_500.pt"), cfg.policy).to("cuda:0")
    env = WheelLegEnv(make_env_cfg(cfg, 1, "cuda:0", evaluation=True))
    try:
        env.commands_fixed = True
        env.fixed_command = (torch.tensor([0.3, 0.0, 0.0], device="cuda:0"), 0.22)
        env.reset()
        env.sim.set_camera_view(eye=[2.5, 2.5, 1.8], target=[0.0, 0.0, 0.25])
        print("CHECKPOINT_VIEW_READY", flush=True)
        with torch.inference_mode():
            while app.is_running():
                obs = env._get_observations()["policy"]
                env.step(actor(obs))
                time.sleep(env.step_dt)
    finally:
        env.close()
except Exception:
    import traceback
    traceback.print_exc()
    raise
finally:
    app.close()
