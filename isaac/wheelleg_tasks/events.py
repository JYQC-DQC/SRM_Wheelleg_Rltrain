import torch


def randomize_inertia(env, env_ids: torch.Tensor | None, scale_range: tuple[float, float]) -> None:
    """One scalar per body preserves positive-definite inertia; follows mass randomization."""
    robot = env.scene["robot"]
    inertia = robot.root_physx_view.get_inertias().clone()
    if env_ids is None:
        env_ids = torch.arange(env.num_envs, device="cpu")
    else:
        env_ids = env_ids.cpu()
    scale = scale_range[0] + torch.rand(len(env_ids), robot.num_bodies, 1) * (scale_range[1] - scale_range[0])
    inertia[env_ids] *= scale
    robot.root_physx_view.set_inertias(inertia, env_ids)
