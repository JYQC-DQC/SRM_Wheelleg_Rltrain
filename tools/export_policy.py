import argparse
import hashlib
import json
import shutil
from pathlib import Path

import numpy as np
import torch
import yaml

from wheelleg.checkpoints import load_actor
from wheelleg.config import load_policy, load_robot, missing_parameters


def export_policy(checkpoint: Path, policy_path: Path, robot_path: Path, rollout: Path, output: Path) -> dict:
    import onnxruntime as ort

    from tools.gen_c_config import generate_header

    policy, robot = load_policy(policy_path), load_robot(robot_path)
    missing = missing_parameters(robot, policy)
    if missing:
        raise ValueError("Cannot export a deployment policy; missing: " + ", ".join(missing))
    with np.load(rollout, allow_pickle=False) as data:
        obs = np.asarray(data["observation"], dtype=np.float32)
    if obs.ndim != 2 or obs.shape[1] != 35 or len(obs) < 100 or not np.isfinite(obs).all():
        raise ValueError("rollout must contain at least 100 finite real observations with shape (N,35)")
    sample = obs[np.linspace(0, len(obs) - 1, 100, dtype=int)]
    actor = load_actor(checkpoint, policy)
    output.mkdir(parents=True, exist_ok=False)
    onnx_path = output / "policy.onnx"
    torch.onnx.export(
        actor,
        torch.from_numpy(sample[:1]),
        str(onnx_path),
        input_names=["obs"],
        output_names=["actions"],
        opset_version=17,
        dynamo=False,
    )
    with torch.inference_mode():
        expected = actor(torch.from_numpy(sample)).numpy()
    session = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
    actual = np.concatenate([session.run(["actions"], {"obs": row[None]})[0] for row in sample])
    error = float(np.max(np.abs(actual - expected)))
    if not np.isfinite(actual).all() or error >= 1e-5:
        raise ValueError(f"ONNX validation failed: max abs error {error}")
    np.savez(output / "golden.npz", observation=sample, actions=expected)
    lines = ["// Generated from real rollout observations; do not edit.", "#pragma once"]
    for name, values in (("kGoldenObs", sample), ("kGoldenActions", expected)):
        lines.append(f"static const float {name}[{len(values)}][{values.shape[1]}] = {{")
        for row in values:
            lines.append("    {" + ", ".join(f"{float(x):.9e}f" for x in row) + "},")
        lines.append("};")
    (output / "golden.h").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (output / "gen_config.h").write_text(generate_header(robot_path, policy_path), encoding="utf-8")
    meta = yaml.safe_load(policy_path.read_text(encoding="utf-8"))
    robot_values = yaml.safe_load(robot_path.read_text(encoding="utf-8"))
    meta["deployment"] = {
        "q_default_rad": list(robot.q_default_rad),
        "joint_order": list(robot.joint_order),
        "motor_direction": list(robot.motor_direction),
        "q_zero_offset_rad": list(robot.q_zero_offset_rad),
        "joint_lower_rad": robot_values["training"]["joint_lower_rad"],
        "joint_upper_rad": robot_values["training"]["joint_upper_rad"],
        "joint_target_margin_rad": robot_values["training"]["joint_target_margin_rad"],
        "wheel_speed_limit_rad_s": robot_values["training"]["wheel_speed_limit_rad_s"],
        "spring": robot_values["training"]["spring"],
    }
    if any(value is None for key in ("joint_lower_rad", "joint_upper_rad") for value in meta["deployment"][key]):
        raise ValueError("Deployment requires measured joint target limits")
    (output / "policy_meta.yaml").write_text(yaml.safe_dump(meta, sort_keys=False), encoding="utf-8")
    shutil.copy2(robot_path, output / "robot.yaml")
    manifest = dict(
        checkpoint=str(checkpoint.resolve()),
        checkpoint_sha256=hashlib.sha256(checkpoint.read_bytes()).hexdigest(),
        observation_version=policy.obs_version,
        onnx_max_absolute_error=error,
        golden_count=100,
        cubeai_generated=False,
        source_rollout=str(rollout.resolve()),
    )
    run = json.loads((checkpoint.parent / "params/run.json").read_text(encoding="utf-8"))
    manifest.update(training_git_commit=run["git_commit"], task=run["task"])
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    p = argparse.ArgumentParser(description="Export a calibrated rsl_rl checkpoint and real rollout golden vectors")
    for name in ("checkpoint", "policy", "robot", "rollout", "output"):
        p.add_argument(f"--{name}", type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(export_policy(a.checkpoint, a.policy, a.robot, a.rollout, a.output), indent=2))


if __name__ == "__main__":
    main()
