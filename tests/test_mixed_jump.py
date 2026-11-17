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


def test_legacy_mixed_commands_hold_60_percent_stationary(tmp_path):
    policy = yaml.safe_load((ROOT / "config/reference/scut_p3.yaml").read_text(encoding="utf-8"))
    tunnel = policy["stages"]["tunnel"]["tunnel"]
    tunnel.update(
        obstacle_fraction=0.4,
        obstacle_fraction_after_switch=0.7,
        mix_switch_iteration=2000,
        mix_require_basic_success=True,
        mix_basic_min_events=100,
        mix_basic_success_rate=0.7,
        vx_range_m_s=[0.5, 1.0],
    )
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


def test_standard_tunnel_is_solid_and_matches_rule_figure():
    model = mujoco.MjModel.from_xml_path(str(ROOT / "assets/tunnel/tunnel_standard.xml"))
    beam = model.geom("TunnelBeam")
    np.testing.assert_allclose(beam.size * 2, [0.35, 0.8, 0.27])
    np.testing.assert_allclose(beam.pos, [1.525, 0.0, 0.135])
    assert model.ngeom == 2  # Ground and one solid box; no rails or hole.
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)
    ray = np.array([0.0, 0.0, -1.0])
    distance = mujoco.mj_ray(model, data, np.array([1.525, 0.0, 1.0]), ray, None, 1, -1, np.zeros(1, np.int32))
    assert 1.0 - distance == pytest.approx(0.27)


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


def test_staged_commands_and_evaluation_separate_stationary_moving_and_beam():
    from wheelleg.evaluation import evaluation_cases

    robot = ROOT / "config/reference/scut_robot.template.yaml"
    policy = ROOT / "config/reference/scut_p3.yaml"
    flat = load_training("p3-jump", robot, policy)
    torch.manual_seed(2)
    commands = Commands(flat, 64, "cpu")
    commands.reset(torch.arange(64))
    target = commands.target.clone()
    assert (target[:, 0] == 0).any() and (target[:, 0] >= 0.6).any()
    assert not target[:, 1:].any()
    commands.step(30.0, torch.zeros(64, dtype=torch.bool))
    torch.testing.assert_close(commands.value, target)
    flat_cases = evaluation_cases(flat)
    assert sorted({case.command[0] for case in flat_cases if case.jump_count}) == pytest.approx([0.0, 0.6, 1.55, 2.5])
    assert sum(case.jump_count == 0 for case in flat_cases) == 4
    tunnel = load_training("p3-tunnel", robot, policy)
    commands = Commands(tunnel, 64, "cpu")
    assert commands.tunnel_obstacle.all()
    cases = evaluation_cases(tunnel)
    assert len({case.name for case in cases}) == len(cases) == 6
    assert all(case.jump_count == 1 and case.command[0] > 0 for case in cases)
    assert {case.press_distance_m for case in cases} == {0.9, 1.3}
    assert all(case.jump_height == pytest.approx(0.145) for case in cases)


@pytest.mark.parametrize("first_contact_valid", [False, True])
def test_beam_ignores_root_height_but_rejects_early_single_wheel_and_defers_apex(first_contact_valid):
    from wheelleg.rewards import jump_apex

    settings = yaml.safe_load((ROOT / "config/reference/scut_p3.yaml").read_text(encoding="utf-8"))["stages"]["tunnel"]
    settings["landing_stable_s"] = 0.03
    event = JumpEvent(settings, 1, "cpu")
    event.reset(torch.tensor([0]))
    event.trigger(torch.tensor([5.0]), torch.tensor([0.3]), torch.tensor([True]), torch.tensor([0.10]))

    def advance(z, vz, contact, valid):
        event.update(
            0.01,
            torch.tensor([5.0]),
            torch.tensor([z]),
            torch.tensor([vz]),
            torch.tensor([contact]),
            torch.tensor([True]),
            torch.tensor([valid]),
            torch.tensor([False]),
            wheel_clearance=torch.full((1, 2), 0.06),
            require_height=torch.tensor([False]),
        )

    for _ in range(28):
        advance(0.3, 0.0, (True, True), False)
    for z in (0.42, 0.52, 0.60, 0.61):
        advance(z, 1.0, (False, False), False)
    advance(0.60, -0.1, (False, False), False)
    assert event.took_off.item()
    assert event.apex_pulse.item()
    assert jump_apex({"jump": event}, {}).item() == 0
    advance(0.32, -0.3, (True, False), first_contact_valid)
    for _ in range(3):
        advance(0.30, 0.0, (True, True), True)
    assert event.landing_paid.item() == first_contact_valid
    assert event.failure_paid.item() != first_contact_valid


def test_stationary_and_moving_height_windows_advance_and_anneal_independently():
    settings = {
        "height_range_m": (0.04, 0.25),
        "curriculum_min_events": 100,
        "guidance_success_threshold": 0.7,
        "guidance_final_scale": 0.3,
        "guidance_decay_iterations": 2000,
    }
    stationary, moving = (JumpCurriculum(settings, "cpu") for _ in range(2))
    bins = torch.zeros(100, dtype=torch.long)
    stationary.record(bins, torch.ones(100, dtype=torch.bool), 10)
    moving.record(bins, torch.arange(100) < 60, 10)
    assert (stationary.maximum_level, moving.maximum_level) == (1, 0)
    assert stationary.guidance(bins[:1], 2010).item() == pytest.approx(0.3)
    assert moving.guidance(bins[:1], 2010).item() == 1.0
    assert not moving.sample(64)[0].any()
    restored = JumpCurriculum(settings, "cpu")
    restored.load_state_dict(moving.state_dict())
    restored.record(bins, torch.ones(100, dtype=torch.bool), 2010)
    assert restored.maximum_level == 1
    assert moving.maximum_level == 0


@pytest.mark.parametrize("dt", [0.01, 0.005])
def test_dense_apex_progress_pays_new_height_only_after_confirmed_takeoff(dt):
    from wheelleg.rewards import compute_rewards

    event = JumpEvent(
        dict(
            height_range_m=(0.2, 0.2),
            first_trigger_range_s=(0.0, 0.0),
            between_events_s=(2.0, 2.0),
            jump_count_probabilities=(0.0, 1.0, 0.0),
            event_duration_s=1.2,
            crouch_duration_s=0.25,
            landing_stable_s=1.0,
            height_tolerance_m=0.01,
            takeoff_confirmation_s=0.03,
        ),
        1,
        "cpu",
    )
    ids = torch.arange(1)
    event.reset(ids)
    yes, no = torch.tensor([True]), torch.tensor([False])
    event.trigger(torch.tensor([0.0]), torch.tensor([0.30]), yes)
    weight = {"jump_height_progress": 0.5}

    def step(z, vz, contact, obstacle=False):
        event.update(
            dt,
            torch.tensor([1.0]),
            torch.tensor([z]),
            torch.tensor([vz]),
            torch.full((1, 2), contact),
            yes,
            yes,
            torch.tensor([obstacle]),
            wheel_clearance=torch.full((1, 2), 0.04 if not contact else 0.0),
            require_height=no,
        )
        return compute_rewards(dict(jump=event, guidance_scale=torch.ones(1)), {}, weight, dt, 2.5)[
            "jump_height_progress"
        ].item()

    for _ in range(round(0.3 / dt)):
        assert step(0.39, 0.4, True) == 0  # Supported extension is not airborne height.
    assert step(0.35, 0.5, False) == 0  # One contact gap is not a confirmed jump.
    assert step(0.3, -0.5, True) == 0
    earned = sum(step(0.35, 0.5, False) for _ in range(round(0.03 / dt)))
    assert event.took_off.item()
    assert earned == pytest.approx(0.125)
    earned += step(0.44, 0.5, False)
    assert not step(0.38, -0.1, False)
    assert not step(0.44, 0.5, False)  # No replay of already-paid height.
    earned += step(0.51, 0.5, False)
    assert earned == pytest.approx(0.5)
    assert not step(0.55, 0.5, False, obstacle=True)
    assert event.failure_pulse.item()
    assert not step(0.60, 0.5, False)
    event.reset(ids)
    assert not event.height_progress.any()


def test_push_and_landing_extension_only_discount_short_legs():
    from types import SimpleNamespace

    from wheelleg.rewards import jump_prepare, jump_takeoff

    lengths = torch.tensor([[0.25, 0.25], [0.28, 0.28], [0.31, 0.32], [0.25, 0.32], [0.28, 0.28]])
    state = {
        "jump": SimpleNamespace(settings={"push_leg_length_m": 0.28, "landing_leg_length_m": 0.28}),
        "leg_length": lengths,
        "guidance_scale": torch.ones(5),
        "jump_ref": {"push": torch.ones(5), "prepare": torch.ones(5), "takeoff_velocity": torch.ones(5)},
        "velocity_w": torch.tensor([[0, 0, 0.5], [0, 0, 0.5], [0, 0, 0.5], [0, 0, 0.5], [0, 0, 1.0]]),
        "wheel_contact": torch.tensor([[True, True], [True, True], [True, True], [True, True], [False, False]]),
    }
    push = jump_takeoff(state, {})
    prepare = jump_prepare(state, {})
    assert push[0] < push[3] < push[1] == push[2] == 0.5
    assert push[4] == 0
    assert prepare[0] < prepare[3] < prepare[1] == prepare[2] == 1
    state["velocity_w"][1, 2] = 1.5
    assert jump_takeoff(state, {})[1] == 1  # Extra vertical speed does not pay extra past the target.


def test_flat_overshoot_does_not_reduce_scoring_but_remains_measurable():
    from types import SimpleNamespace

    from wheelleg.jump import jump_height_error, jump_height_overshoot
    from wheelleg.rewards import jump_apex

    cfg = load_training(
        "p3-jump", ROOT / "config/reference/scut_robot.template.yaml", ROOT / "config/reference/scut_p3.yaml"
    )
    stage = cfg.stage
    rise = torch.tensor([0.015, 0.04, 0.09])
    target = torch.full_like(rise, 0.04)
    event = SimpleNamespace(
        height=target,
        start_z=torch.zeros_like(rise),
        apex_z=rise,
        settings=stage,
        landing_pulse=torch.ones(3, dtype=torch.bool),
        invalid=torch.zeros(3, dtype=torch.bool),
        failure_paid=torch.zeros(3, dtype=torch.bool),
    )
    assert (jump_height_error(rise, target, stage) <= 1e-6).tolist() == [False, True, True]
    assert (jump_height_overshoot(rise, target, stage) > 1e-6).tolist() == [False, False, True]
    score = jump_apex({"jump": event}, {})
    assert score[0] < score[1] == score[2] == 1.0
    assert jump_height_error(rise, target, {**stage, "height_is_minimum": False})[-1] > 0
    event.landing_pulse[-1] = False
    assert jump_apex({"jump": event}, {})[-1] == 0  # Going high alone never replaces a stable landing.


@pytest.mark.parametrize(
    "scenario,expected",
    [("recovers_after_old_deadline", True), ("repeated_bounce", False), ("no_touchdown", False)],
)
def test_flat_recovery_grace_does_not_renew_on_bounce(scenario, expected):
    cfg = load_training(
        "p3-jump", ROOT / "config/reference/scut_robot.template.yaml", ROOT / "config/reference/scut_p3.yaml"
    )
    event = JumpEvent(cfg.stage, 1, "cpu")
    event.reset(torch.tensor([0]))
    event.remaining.fill_(1)
    yes = torch.tensor([True])
    no = ~yes
    event.trigger(torch.tensor([5.0]), torch.tensor([0.3]), yes)
    dt = 0.01
    for step in range(1, 600):
        t = step * dt
        if t < 0.30:
            contact, z, vz = (True, True), 0.30, 0.0
        elif t < 0.70 or scenario == "no_touchdown":
            contact, z, vz = (False, False), 0.36, 0.5
        elif step == 70:
            contact, z, vz = (True, False), 0.31, -0.4  # Deadline must start at the first wheel.
        elif step == 71 or (scenario == "recovers_after_old_deadline" and t >= 1.75):
            contact, z, vz = (True, True), 0.30, 0.0
        elif scenario == "repeated_bounce" and (step // 10) % 2:
            contact, z, vz = (True, True), 0.30, 0.0
        else:
            contact, z, vz = (False, False), 0.32, 0.0
        event.update(
            dt,
            torch.tensor([5.0 + t]),
            torch.tensor([z]),
            torch.tensor([vz]),
            torch.tensor([contact]),
            yes,
            yes,
            no,
            wheel_clearance=torch.full((1, 2), z - 0.30),
            require_height=no,
        )
        if event.finished.item():
            break
    assert event.finished.item()
    assert event.landing_paid.item() == expected
    assert event.failure_paid.item() != expected
    expected_time = {"recovers_after_old_deadline": 2.74, "repeated_bounce": 3.20, "no_touchdown": 1.20}[scenario]
    assert event.elapsed.item() == pytest.approx(expected_time, abs=dt / 2)
    assert event.phase.item() == pytest.approx(1.0)  # Nominal Actor timing is not stretched.
