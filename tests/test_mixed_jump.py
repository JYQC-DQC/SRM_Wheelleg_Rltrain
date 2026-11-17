from dataclasses import replace
from pathlib import Path
from types import MappingProxyType

import mujoco
import numpy as np
import pytest
import torch
import yaml

from wheelleg.commands import Commands
from wheelleg.curriculum import JumpCurriculum
from wheelleg.jump import JumpEvent, tunnel_landing
from wheelleg.training import load_training

ROOT = Path(__file__).resolve().parents[1]


def test_scut_trial_configuration_is_ready_with_prepared_asset():
    robot = ROOT / "sim2sim/checkpoints/stairs_edge_speed_model1400/params/robot.yaml"
    if not robot.exists():
        pytest.skip("Prepared local SCUT asset snapshot is unavailable")
    cfg = load_training("p3-tunnel", robot, ROOT / "config/reference/scut_p3.yaml")
    assert cfg.missing() == []
    assert cfg.stage["feasible_height_m"] is None
    assert cfg.stage["simulation_height_limit_m"] == 0.4


def test_baseline_override_is_explicit_and_does_not_bypass_missing_values(tmp_path):
    robot = ROOT / "sim2sim/checkpoints/stairs_edge_speed_model1400/params/robot.yaml"
    if not robot.exists():
        pytest.skip("Prepared local SCUT asset snapshot is unavailable")
    cfg = load_training("p3-tunnel", robot, ROOT / "config/reference/scut_p3.yaml")
    usd = tmp_path / "reference.usd"
    usd.touch()
    module = tmp_path / "agent_world/assets/wheelbipe_V14_2.py"
    module.parent.mkdir(parents=True)
    module.touch()
    asset = dict(cfg.asset, usd_path=str(usd), reference_package=str(tmp_path))
    cfg = replace(cfg, asset=MappingProxyType(asset))
    with pytest.raises(ValueError, match="baseline evaluation"):
        cfg.require_ready()
    cfg.require_ready(allow_unvalidated_baseline=True)
    incomplete = load_training(
        "p3-tunnel", ROOT / "config/reference/scut_robot.template.yaml", ROOT / "config/reference/scut_p3.yaml"
    )
    with pytest.raises(ValueError):
        incomplete.require_ready(allow_unvalidated_baseline=True)


def test_mixed_commands_hold_60_percent_stationary(tmp_path):
    policy = yaml.safe_load((ROOT / "config/reference/scut_p3.yaml").read_text(encoding="utf-8"))
    policy["stages"]["tunnel"]["tunnel"]["vx_range_m_s"] = [0.5, 1.0]
    path = tmp_path / "policy.yaml"
    path.write_text(yaml.safe_dump(policy), encoding="utf-8")
    cfg = load_training("p3-tunnel", ROOT / "config/reference/scut_robot.template.yaml", path)
    commands = Commands(cfg, 4096, "cpu")
    commands.reset(torch.arange(4096))
    assert commands.tunnel_obstacle.sum().item() == 1638
    assert (commands.target[~commands.tunnel_obstacle] == 0).all()
    assert (commands.target[commands.tunnel_obstacle, 0] >= 0.5).all()
    commands.set_tunnel_mix(torch.arange(4096), 1999.99)
    assert commands.tunnel_obstacle.sum().item() == 1638
    # Episodes outside this reset retain their old task until their own reset.
    commands.set_tunnel_mix(torch.arange(4096), 2000)
    assert commands.tunnel_obstacle.sum().item() == 1638
    commands.record_basic_jump(torch.ones(100, dtype=torch.bool))
    commands.set_tunnel_mix(torch.tensor([2000, 3000]), 2000)
    assert commands.tunnel_obstacle[2000].item()
    assert not commands.tunnel_obstacle[2001].item()
    assert not commands.tunnel_obstacle[3000].item()
    commands.set_tunnel_mix(torch.arange(4096), 2000)
    commands.reset(torch.arange(4096))
    assert commands.tunnel_obstacle.sum().item() == 2867
    assert (commands.target[~commands.tunnel_obstacle] == 0).all()
    # Resuming above the switch applies the same absolute-iteration schedule.
    resumed = Commands(cfg, 4096, "cpu")
    resumed.basic_jump_gate = dict(commands.basic_jump_gate)
    resumed.set_tunnel_mix(torch.arange(4096), 2500)
    assert torch.equal(resumed.tunnel_obstacle, commands.tunnel_obstacle)


def test_tunnel_curriculum_strict_thresholds_stale_episodes_and_resume():
    settings = {
        "curriculum_min_events": 100,
        "guidance_success_threshold": 0.7,
        "curriculum_demote_rate": 0.2,
    }
    levels = (0.138, 0.192, 0.246, 0.300, 0.354)
    curriculum = JumpCurriculum(settings, "cpu", levels)

    def record(level, successes):
        curriculum.record(torch.full((100,), level), torch.arange(100) < successes, 1.0)

    record(0, 70)
    assert curriculum.maximum_level == 0
    record(0, 71)
    assert curriculum.maximum_level == 1
    record(0, 0)
    assert curriculum.attempts.sum().item() == 0
    record(1, 20)
    assert curriculum.maximum_level == 1
    record(1, 19)
    assert curriculum.maximum_level == 0
    record(0, 0)
    assert curriculum.maximum_level == 0
    for level in range(5):
        record(level, 100)
    assert curriculum.maximum_level == 4
    restored = JumpCurriculum(settings, "cpu", levels)
    restored.load_state_dict(curriculum.state_dict())
    assert restored.maximum_level == 4
    torch.testing.assert_close(restored.latest_rate, curriculum.latest_rate)


@pytest.mark.parametrize("level, top", [(1, 0.108), (2, 0.162), (3, 0.216), (4, 0.270), (5, 0.324)])
def test_generated_tunnel_height_and_dimensions(level, top):
    model = mujoco.MjModel.from_xml_path(str(ROOT / f"assets/tunnel/tunnel_level{level}.xml"))
    beam = model.geom("TunnelBeam")
    assert beam.pos[2] + beam.size[2] == pytest.approx(top)
    np.testing.assert_allclose(beam.size * 2, [0.35, 1.6, 0.02])
    assert model.geom("RailLeft").size[2] * 2 == pytest.approx(0.6)
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)
    ray = np.array([0.0, 0.0, -1.0])
    distance = mujoco.mj_ray(model, data, np.array([0.175, 0.0, 1.0]), ray, None, 1, -1, np.zeros(1, np.int32))
    assert 1.0 - distance == pytest.approx(top)


def test_tunnel_roof_is_not_a_valid_landing():
    wheels = torch.tensor([[[0.6, -0.1, 0.33], [0.6, 0.1, 0.33]]])
    body = torch.tensor([[[0.6, 0.0, 0.5]]])
    valid = tunnel_landing(wheels, 0.06, body, torch.tensor([0.35]), torch.tensor([0.0]), 0.05, 0.03)
    assert not valid.item()
    wheels[:, :, 2] = 0.06
    assert tunnel_landing(wheels, 0.06, body, torch.tensor([0.35]), torch.tensor([0.0]), 0.05, 0.03).item()


def test_legacy_jump_curriculum_can_restore_an_old_checkpoint():
    settings = {
        "height_range_m": [0.04, 0.12],
        "curriculum_min_events": 100,
        "guidance_success_threshold": 0.7,
        "guidance_decay_iterations": 2000,
        "guidance_final_scale": 0.3,
    }
    course = JumpCurriculum(settings, "cpu")
    course.record(torch.zeros(100, dtype=torch.long), torch.ones(100, dtype=torch.bool), 10.0)
    assert course.maximum_level == 1
    state = course.state_dict()
    state.pop("latest_rate")
    restored = JumpCurriculum(settings, "cpu")
    restored.load_state_dict(state)
    assert restored.maximum_level == 1
    assert restored.guidance(torch.tensor([0]), 2010.0).item() == pytest.approx(0.3)


def test_no_takeoff_cannot_receive_landing_success():
    settings = yaml.safe_load((ROOT / "config/reference/scut_p3.yaml").read_text(encoding="utf-8"))["stages"]["tunnel"]
    jump = JumpEvent(settings, 1, "cpu")
    jump.reset(torch.tensor([0]))
    jump.trigger(torch.tensor([5.0]), torch.tensor([0.3]), torch.tensor([True]), torch.tensor([0.138]))
    for frame in range(230):
        jump.update(
            0.01,
            torch.tensor([5.0 + frame * 0.01]),
            torch.tensor([0.3]),
            torch.tensor([0.0]),
            torch.tensor([[True, True]]),
            torch.tensor([True]),
            torch.tensor([True]),
            torch.tensor([False]),
        )
    assert not jump.landing_paid.item()
