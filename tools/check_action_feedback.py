"""Diagnose raw actor feedback through obs_v2 previous_action, without a simulator."""

import argparse
import json
from pathlib import Path

import numpy as np
import torch

from wheelleg.checkpoints import load_actor
from wheelleg.config import load_policy, load_robot
from wheelleg.observation import OBS_FIELDS


def feedback_report(actor: torch.nn.Module, observations: torch.Tensor, action_slice: slice,
                    bounds: tuple[float, float], *, clipping: bool) -> dict:
    obs = observations.clone()
    exceeded = torch.zeros(len(obs), dtype=torch.bool)
    nonfinite = torch.zeros_like(exceeded)
    maximum = 0.0
    with torch.inference_mode():
        for _ in range(400):
            if clipping:
                obs[:, action_slice] = torch.nan_to_num(obs[:, action_slice].clamp(*bounds),
                                                        nan=0.0, posinf=0.0, neginf=0.0)
            action = actor(obs)
            exceeded |= (action.abs() > 1e6).any(-1)
            nonfinite |= ~torch.isfinite(action).all(-1)
            peak = torch.nan_to_num(action.abs(), nan=float("inf"), posinf=float("inf")).amax().item()
            maximum = max(maximum, peak)
            obs[:, action_slice] = action
    return dict(clipping=clipping, steps=400, environments=len(obs),
                exceeded_1e6=int(exceeded.sum()), nonfinite_environments=int(nonfinite.sum()),
                max_abs_raw_action=maximum if np.isfinite(maximum) else "non-finite")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--checkpoint", type=Path, required=True)
    p.add_argument("--robot", type=Path, required=True)
    p.add_argument("--policy", type=Path, required=True)
    p.add_argument("--observations", type=Path, required=True,
                   help="NPZ containing finite observation[N,35]; other components stay fixed")
    a = p.parse_args()
    robot, policy = load_robot(a.robot), load_policy(a.policy)
    actor = load_actor(a.checkpoint, policy)
    with np.load(a.observations, allow_pickle=False) as data:
        observations = np.asarray(data["observation"], dtype=np.float32)
    dimension = sum(width for _, width in OBS_FIELDS)
    if observations.ndim != 2 or observations.shape[1] != dimension or not len(observations):
        raise ValueError(f"Expected observation[N,{dimension}], N > 0")
    if not np.isfinite(observations).all():
        raise ValueError("Fixed starting observations must be finite")
    offset = 0
    for name, width in OBS_FIELDS:
        if name == "previous_action":
            action_slice = slice(offset, offset+width)
            break
        offset += width
    results = [feedback_report(actor, torch.from_numpy(observations), action_slice,
                               dict(robot.observation_clip)["previous_action"], clipping=enabled)
               for enabled in (False, True)]
    print(json.dumps(results, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
