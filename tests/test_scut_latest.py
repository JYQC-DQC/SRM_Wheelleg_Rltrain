from pathlib import Path

import pytest
import torch
import yaml

from wheelleg.tensor_ops import reference_pd_torque
from wheelleg.training import load_training

ROOT = Path(__file__).resolve().parents[1]


def test_reference_pd_wheel_position_does_not_create_torque():
    q = torch.tensor([[0.0, 0.0, 999.0, 0.0, 0.0, -999.0]])
    qd = torch.zeros_like(q)
    target = torch.ones_like(q)
    velocity = torch.tensor([[0.0, 0.0, 60.0, 0.0, 0.0, -60.0]])
    kp = torch.tensor([60.0, 60.0, 0.0, 60.0, 60.0, 0.0])
    kd = torch.tensor([2.0, 2.0, 0.2, 2.0, 2.0, 0.2])
    limits = torch.tensor([[40.0, 40.0, 5.0, 40.0, 40.0, 5.0]])
    result = reference_pd_torque(q, qd, target, velocity, kp, kd, limits, torch.ones_like(q), [2, 5])
    torch.testing.assert_close(result, torch.tensor([[40.0, 40.0, 5.0, 40.0, 40.0, -5.0]]))
    assert torch.isfinite(result).all()


def test_reference_only_exempts_unused_dc_fields(tmp_path):
    robot = yaml.safe_load((ROOT / "config/reference/scut_robot.template.yaml").read_text(encoding="utf-8"))
    robot["asset"].update(
        usd_path="not_installed.usd", reference_package="not_installed", collision_body_names=["base_link"]
    )
    robot["training"]["hip_pivot_positions_b_m"] = [[0.0, 0.17925, 0.0], [0.0, -0.17925, 0.0]]
    path = tmp_path / "robot.yaml"
    path.write_text(yaml.safe_dump(robot), encoding="utf-8")
    cfg = load_training("p1-flat", path, ROOT / "config/reference/scut_p1.yaml")
    assert cfg.missing() == ["robot.asset.initial_root_position_m[2]"]
    # Synthetic fixture height; the real template must still wait for USD-derived zero-pose geometry.
    robot["asset"]["initial_root_position_m"][2] = 0.3
    path.write_text(yaml.safe_dump(robot), encoding="utf-8")
    cfg = load_training("p1-flat", path, ROOT / "config/reference/scut_p1.yaml")
    assert cfg.missing() == []
    with pytest.raises(ValueError, match="does not exist"):
        cfg.require_ready()
    robot["variant"] = "chassis_only"
    path.write_text(yaml.safe_dump(robot), encoding="utf-8")
    with pytest.raises(ValueError, match="simulation-only"):
        load_training("p1-flat", path, ROOT / "config/reference/scut_p1.yaml")


def test_srm_missing_parameters_are_not_bypassed():
    cfg = load_training("p1-flat", ROOT / "config/robot.yaml", ROOT / "config/policies/p1/policy_meta.yaml")
    assert "robot.asset.usd_path" in cfg.missing()
    assert any("no_load_speed" in key for key in cfg.missing())


def test_reference_p1_has_sixteen_valid_evaluation_commands():
    from wheelleg.evaluation import evaluation_cases

    cfg = load_training(
        "p1-flat", ROOT / "config/reference/scut_robot.template.yaml", ROOT / "config/reference/scut_p1.yaml"
    )
    cases = evaluation_cases(cfg)
    assert len(cases) == 16
    assert all(len(case.command) == 3 for case in cases)
