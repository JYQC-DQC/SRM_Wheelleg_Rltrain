import argparse
from pathlib import Path

from wheelleg.config import load_policy, load_robot, missing_parameters
from wheelleg.history import ESTIMATE_DIM, actor_input_dim
from wheelleg.observation import OBS_DIM


def main() -> None:
    parser = argparse.ArgumentParser(description="Check configuration syntax and list missing measurements")
    parser.add_argument("--robot", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()
    robot, policy = load_robot(args.robot), load_policy(args.policy)
    layers = (actor_input_dim(policy), *policy.hidden_dims, len(robot.joint_order))
    count = sum((a + 1) * b for a, b in zip(layers[:-1], layers[1:], strict=True))
    if policy.history_frames:
        estimator = (policy.history_frames * OBS_DIM, *policy.estimator_hidden_dims, ESTIMATE_DIM)
        count += sum((a + 1) * b for a, b in zip(estimator[:-1], estimator[1:], strict=True))
        print(f"History estimator specification: {estimator}")
    print(f"{robot.name}: control={robot.control_hz} Hz, policy={robot.policy_hz} Hz, decimation={robot.decimation}")
    print(f"Actor specification: {layers}, {count} parameters, {count * 4} weight bytes (FP32)")
    missing = missing_parameters(robot, policy)
    for field in missing:
        print(f"MISSING {field}")
    print(f"Unresolved fields: {len(missing)}")
    if args.require_ready and missing:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
