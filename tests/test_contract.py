from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
import yaml

from tools.gen_c_config import generate_header
from wheelleg.config import load_policy, load_robot, missing_parameters
from wheelleg.observation import OBS_DIM, build_observation

ROOT = Path(__file__).resolve().parents[1]
ROBOT = ROOT / "config/robot.yaml"
POLICY = ROOT / "config/policies/p1/policy_meta.yaml"


def test_confirmed_parameters_and_export_gate():
    robot, policy = load_robot(ROBOT), load_policy(POLICY)
    assert (robot.control_hz, robot.policy_hz, robot.decimation) == (500, 100, 5)
    assert robot.wheel_reduction_ratio == 15.76
    assert robot.spring_stroke_m == 0.075
    assert "motor_sweep_and_held_out_validation" in missing_parameters(robot, policy)
    with pytest.raises(ValueError, match="Cannot export"):
        generate_header(ROBOT, POLICY)
    bootstrap = generate_header(ROBOT, POLICY, interface_only=True)
    assert "#define WL_DEPLOYMENT_CONFIG_READY 0" in bootstrap
    assert "kWheelLegDefaultQ" not in bootstrap


def test_observation_layout_and_wheel_positions():
    # 合成数值仅用于测试，不能写回实车配置。
    robot = replace(load_robot(ROBOT), q_default_rad=(0.1, 0.2, None, 0.3, 0.4, None))
    policy = load_policy(POLICY)
    obs = build_observation(
        robot,
        policy,
        command=np.array([[1.0, 0.0, 2.0]]),
        height=np.array([[0.2]]),
        angular_velocity=np.array([[2.0, 4.0, 6.0]]),
        gravity=np.array([[0.0, 0.0, -1.0]]),
        joint_position=np.array([[1.1, 2.2, 100.0, 3.3, 4.4, -100.0]]),
        joint_velocity=np.array([[10.0, 20.0, 30.0, 40.0, 50.0, 60.0]]),
        previous_action=np.array([[1.0, 2.0, 3.0, 4.0, 5.0, 6.0]]),
        mode=np.array([[1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]),
    )
    expected = [
        1,
        0,
        2,
        1,
        1,
        2,
        3,
        0,
        0,
        -1,
        1,
        2,
        0,
        3,
        4,
        0,
        1,
        2,
        3,
        4,
        5,
        6,
        1,
        2,
        3,
        4,
        5,
        6,
        1,
        0,
        0,
        0,
        0,
        0,
        0,
    ]
    assert obs.shape == (1, OBS_DIM)
    assert obs.dtype == np.float32
    np.testing.assert_allclose(obs[0], expected, atol=1e-6)


@pytest.mark.parametrize(
    "field,value,match",
    [
        ("policy_hz", 101, "divisible"),
        ("wheel_reduction_ratio", -1.0, "positive"),
        ("motor_direction", [0] * 6, "motor_direction"),
        ("wheel_indices", [0, 5], "partition"),
    ],
)
def test_invalid_config_fails_at_load(tmp_path, field, value, match):
    data = yaml.safe_load(ROBOT.read_text(encoding="utf-8"))
    data[field] = value
    path = tmp_path / "robot.yaml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(ValueError, match=match):
        load_robot(path)


def test_header_tracks_config_changes(tmp_path):
    data = yaml.safe_load(ROBOT.read_text(encoding="utf-8"))
    data["wheel_reduction_ratio"] = 16.0
    path = tmp_path / "robot.yaml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    assert "WL_WHEEL_REDUCTION_RATIO 16.0f" in generate_header(path, POLICY, interface_only=True)


def test_missing_field_names_file(tmp_path):
    data = yaml.safe_load(POLICY.read_text(encoding="utf-8"))
    del data["action_scales"]
    path = tmp_path / "missing_policy.yaml"
    path.write_text(yaml.safe_dump(data), encoding="utf-8")
    with pytest.raises(ValueError, match="missing_policy.yaml: missing required field action_scales"):
        load_policy(path)


def test_complete_synthetic_export_contains_all_scales(tmp_path):
    robot = yaml.safe_load(ROBOT.read_text(encoding="utf-8"))
    policy = yaml.safe_load(POLICY.read_text(encoding="utf-8"))
    robot["pending_measurements"] = {key: "synthetic test evidence" for key in robot["pending_measurements"]}
    robot["q_default_rad"] = [0.0] * 6
    robot["q_zero_offset_rad"] = [0.1] * 6
    robot["motor_direction"] = [1, -1, 1, -1, 1, -1]
    for key in ("kp", "kd", "torque_limit_nm"):
        policy[key] = [1.0] * 6
    policy["action_clip"] = 2.0
    robot_path, policy_path = tmp_path / "robot.yaml", tmp_path / "policy.yaml"
    robot_path.write_text(yaml.safe_dump(robot), encoding="utf-8")
    policy_path.write_text(yaml.safe_dump(policy), encoding="utf-8")
    header = generate_header(robot_path, policy_path)
    assert "WL_DEPLOYMENT_CONFIG_READY 1" in header
    assert "WL_OBS_JOINT_VELOCITY_SCALE 0.1f" in header
    assert "kWheelLegCommandScale[3]" in header
    assert "kWheelLegLegIndices[4] = {0u, 1u, 3u, 4u}" in header
    assert "kWheelLegMotorDirection[6] = {1.0f, -1.0f, 1.0f, -1.0f, 1.0f, -1.0f}" in header


def test_batch_observation_and_invalid_input():
    robot = replace(load_robot(ROBOT), q_default_rad=(0.0,) * 6)
    policy = load_policy(POLICY)
    fields = dict(
        command=np.zeros((4096, 3)),
        height=np.zeros((4096, 1)),
        angular_velocity=np.zeros((4096, 3)),
        gravity=np.zeros((4096, 3)),
        joint_position=np.zeros((4096, 6)),
        joint_velocity=np.zeros((4096, 6)),
        previous_action=np.zeros((4096, 6)),
        mode=np.zeros((4096, 7)),
    )
    assert build_observation(robot, policy, **fields).shape == (4096, 35)
    fields["angular_velocity"][0, 0] = np.nan
    with pytest.raises(ValueError, match="angular_velocity"):
        build_observation(robot, policy, **fields)
    fields["angular_velocity"][0, 0] = 0.0
    with pytest.raises(ValueError, match="calibration is incomplete"):
        build_observation(load_robot(ROBOT), policy, **fields)


def test_integer_sensor_arrays_preserve_fractional_zero_offsets():
    robot = replace(load_robot(ROBOT), q_default_rad=(0.25,) * 6)
    policy = load_policy(POLICY)
    obs = build_observation(
        robot,
        policy,
        command=np.zeros(3),
        height=np.zeros(1),
        angular_velocity=np.zeros(3),
        gravity=np.array([0, 0, -1]),
        joint_position=np.ones(6, dtype=np.int32),
        joint_velocity=np.zeros(6),
        previous_action=np.zeros(6),
        mode=np.zeros(7),
    )
    np.testing.assert_allclose(obs[10:16], [0.75, 0.75, 0.0, 0.75, 0.75, 0.0])
