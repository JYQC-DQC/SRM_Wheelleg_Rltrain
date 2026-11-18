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
    jump = JumpEvent(flat.stage, 64, "cpu")
    jump.reset(torch.arange(64))
    assert (jump.remaining == 1).all()
    assert ((jump.next_trigger >= 2.0) & (jump.next_trigger <= 5.0)).all()
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
    stationary, moving = (JumpCurriculum(settings, "cpu", fresh_windows=True) for _ in range(2))
    bins = torch.zeros(100, dtype=torch.long)
    stationary.record(bins, torch.ones(100, dtype=torch.bool), 10)
    for _ in range(4):
        moving.record(bins, torch.zeros(100, dtype=torch.bool), 10)
    moving.record(bins, torch.arange(100) < 60, 10)
    assert (stationary.maximum_level, moving.maximum_level) == (1, 0)
    assert stationary.guidance(bins[:1], 2010).item() == pytest.approx(0.3)
    assert moving.guidance(bins[:1], 2010).item() == 1.0
    assert not moving.sample(64)[0].any()
    assert moving.latest_rate[0].item() == pytest.approx(0.6)
    assert not moving.attempts.any() and not moving.successes.any()

    # Restore a half-filled window. Exactly 70/100 in this new window promotes despite old failures.
    moving.record(bins[:50], torch.ones(50, dtype=torch.bool), 2009)
    restored = JumpCurriculum(settings, "cpu", fresh_windows=True)
    restored.load_state_dict(moving.state_dict())
    restored.record(bins[:50], torch.arange(50) < 20, 2010)
    assert restored.maximum_level == 1
    assert restored.latest_rate[0].item() == pytest.approx(0.7)
    assert not restored.attempts.any() and not restored.successes.any()
    assert moving.maximum_level == 0

    # Easy attempts can still be sampled, but cannot carry promotion at the current cap.
    restored.record(bins, torch.ones(100, dtype=torch.bool), 2011)
    assert not restored.attempts.any()
    restored.record(bins + 1, torch.ones(100, dtype=torch.bool), 2012)
    assert restored.maximum_level == 2
    assert set(restored.sample(128)[0].tolist()) == {0, 1, 2}


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
        "jump_pose_scale": 1.0,
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


def test_flat_clearance_awards_partial_undershoot_but_does_not_penalize_overshoot():
    from types import SimpleNamespace

    from wheelleg.jump import jump_height_error, jump_height_overshoot
    from wheelleg.rewards import jump_apex

    cfg = load_training(
        "p3-jump", ROOT / "config/reference/scut_robot.template.yaml", ROOT / "config/reference/scut_p3.yaml"
    )
    stage = cfg.stage
    rise = torch.tensor([0.20, 0.24, 0.30])
    target = torch.full_like(rise, 0.25)
    event = SimpleNamespace(
        height=target,
        scored_height=rise,
        apex_pose_quality=torch.ones_like(rise),
        settings=stage,
        landing_pulse=torch.ones(3, dtype=torch.bool),
        invalid=torch.zeros(3, dtype=torch.bool),
        failure_paid=torch.zeros(3, dtype=torch.bool),
    )
    assert (jump_height_error(rise, target, stage) <= 1e-6).tolist() == [False, True, True]
    assert (jump_height_overshoot(rise, target, stage) > 1e-6).tolist() == [False, False, True]
    score = jump_apex({"jump": event}, {})
    assert score[0].item() == pytest.approx(0.5272924)
    assert score[1:].tolist() == [1.0, 1.0]
    assert jump_height_error(rise, target, {**stage, "height_is_minimum": False})[-1] > 0
    event.landing_pulse[-1] = False
    assert jump_apex({"jump": event}, {})[-1] == 0  # Going high alone never replaces a stable landing.


@pytest.mark.parametrize(
    "scenario,finished_at,success",
    [
        ("no_takeoff", 1.20, False),
        ("long_flight_then_recovers", 9.04, True),
        ("repeated_bounce", 5.70, False),
        ("no_touch_before_episode_ends", 8.00, False),
    ],
)
def test_flat_jump_uses_separate_takeoff_and_landing_deadlines(scenario, finished_at, success):
    cfg = load_training(
        "p3-jump", ROOT / "config/reference/scut_robot.template.yaml", ROOT / "config/reference/scut_p3.yaml"
    )
    event = JumpEvent(cfg.stage, 1, "cpu")
    event.reset(torch.tensor([0]))
    event.remaining.fill_(1)
    yes = torch.tensor([True])
    no = ~yes
    event.trigger(torch.tensor([5.0]), torch.tensor([0.3]), yes, body_clearance_m=torch.tensor([0.10]))
    dt = 0.01
    for step in range(1, 1000):
        if step < 30 or scenario == "no_takeoff":
            contact, z, vz = (True, True), 0.30, 0.0
        elif scenario == "long_flight_then_recovers":
            if step < 430:
                contact, z, vz = (False, False), 0.36, 0.5
            elif step == 430:
                contact, z, vz = (True, False), 0.31, -0.4
            elif step == 431 or step >= 825:
                contact, z, vz = (True, True), 0.30, 0.0
            else:
                contact, z, vz = (False, False), 0.32, 0.0
        elif scenario == "repeated_bounce" and step >= 70:
            # Start the five-second timer on the single-wheel touch, not the subsequent dual contact.
            contact = (True, False) if step == 70 else (True, True) if (step // 10) % 2 else (False, False)
            z, vz = 0.30, 0.0
        else:
            contact, z, vz = (False, False), 0.36, 0.5
        event.update(
            dt,
            torch.tensor([5.0 + step * dt]),
            torch.tensor([z]),
            torch.tensor([vz]),
            torch.tensor([contact]),
            yes,
            yes,
            no,
            wheel_clearance=torch.full((1, 2), z - 0.30),
            body_clearance_m=torch.tensor([z - 0.20]),
            leg_angle_rad=torch.zeros(1, 2),
            failed=torch.tensor([scenario == "no_touch_before_episode_ends" and step == 800]),
            require_height=no,
        )
        if scenario == "long_flight_then_recovers" and step == 400:
            assert event.active.item() and not event.first_touch.item()
            assert event.features()[0, 0].item() == -1.0
        if event.finished.item():
            break
    assert event.finished.item()
    assert event.landing_paid.item() == success
    assert event.failure_paid.item() != success
    assert event.elapsed.item() == pytest.approx(finished_at, abs=dt / 2)
    assert event.phase.item() == pytest.approx(1.0)  # Nominal Actor timing is not stretched.


def test_staged_flat_samples_highest_open_level_more_often_but_keeps_all_lower_levels():
    from wheelleg.evaluation import evaluation_cases

    cfg = load_training(
        "p3-jump", ROOT / "config/reference/scut_robot.template.yaml", ROOT / "config/reference/scut_p3.yaml"
    )
    expected = [0.04, 0.0925, 0.145, 0.1975, 0.25, 0.30, 0.35, 0.40]
    curriculum = JumpCurriculum(cfg.stage, "cpu", fresh_windows=True)
    assert curriculum.levels.tolist() == pytest.approx(expected)
    assert sorted({case.jump_height for case in evaluation_cases(cfg) if case.jump_count}) == pytest.approx(expected)
    bins, _ = curriculum.sample(100)
    assert (bins == 0).all()
    torch.manual_seed(17)
    assert cfg.stage["curriculum_min_events"] == 500
    for cap in range(1, len(expected)):
        previous = torch.full((499,), cap - 1)
        curriculum.record(previous, torch.arange(499) < 349, cap)
        assert curriculum.maximum_level == cap - 1  # No promotion before the 500th settled attempt.
        curriculum.record(previous[:1], torch.ones(1, dtype=torch.bool), cap)
        assert curriculum.maximum_level == cap  # Exactly 350/500 meets the 70% gate.
        assert curriculum.latest_rate[cap - 1].item() == pytest.approx(0.70)
        bins, heights = curriculum.sample(20_000)
        frequencies = torch.bincount(bins, minlength=len(expected)).float() / len(bins)
        assert frequencies[cap].item() == pytest.approx(0.60, abs=0.02)
        assert frequencies[:cap].tolist() == pytest.approx([0.40 / cap] * cap, abs=0.02)
        assert not frequencies[cap + 1 :].any()
        torch.testing.assert_close(heights, curriculum.levels[bins])
    assert heights.max().item() == pytest.approx(0.40)


@pytest.fixture
def clearance_jump():
    stage = load_training(
        "p3-jump", ROOT / "config/reference/scut_robot.template.yaml", ROOT / "config/reference/scut_p3.yaml"
    ).stage
    event = JumpEvent(stage, 1, "cpu")
    event.reset(torch.arange(1))
    event.trigger(
        torch.tensor([5.0]),
        torch.tensor([0.3]),
        torch.tensor([True]),
        torch.tensor([0.25]),
        body_clearance_m=torch.tensor([0.10]),
    )
    return event


def clearance_step(
    event, wheel, vz=0.5, contact=(False, False), stable=True, z=0.55, failed=False, body=0.60, angles=(0.0, 0.0)
):
    event.update(
        0.01,
        torch.tensor([6.0]),
        torch.tensor([z]),
        torch.tensor([vz]),
        torch.tensor([contact]),
        torch.tensor([stable]),
        torch.tensor([True]),
        torch.tensor([False]),
        wheel_clearance=torch.tensor([wheel]),
        body_clearance_m=torch.tensor([body]),
        leg_angle_rad=torch.tensor([angles]),
        failed=torch.tensor([failed]),
        require_height=torch.tensor([False]),
    )
    return event.references(torch.tensor([vz]), torch.tensor([min(wheel)]), 9.81)


def test_stand_walk_reward_gate_ends_after_jump_settlement(clearance_jump):
    event = clearance_jump
    assert event.suppress_stand_walk.item()
    for _ in range(3):
        clearance_step(event, (0.28, 0.28))
    assert event.suppress_stand_walk.item()
    clearance_step(event, (0.0, 0.0), vz=-0.5, contact=(True, False))
    assert event.suppress_stand_walk.item()
    clearance_step(event, (0.05, 0.05), vz=0.5)
    assert event.suppress_stand_walk.item()  # Still suppressed after a bounce.
    for _ in range(80):
        clearance_step(event, (0.0, 0.0), vz=0.0, contact=(True, True))
        assert event.suppress_stand_walk.item()
    assert event.landing_pulse.item()
    event.reset(torch.arange(1))
    assert not event.suppress_stand_walk.item()
    event.trigger(torch.tensor([5.0]), torch.tensor([0.3]), torch.tensor([True]), body_clearance_m=torch.tensor([0.10]))
    clearance_step(event, (0.0, 0.0), vz=0.0, contact=(True, True), failed=True)
    assert event.failure_pulse.item() and not event.active.item() and event.suppress_stand_walk.item()
    event.reset(torch.arange(1))
    event.fail_pending(torch.tensor([True]))
    assert not event.suppress_stand_walk.item()  # A failure before the press does not suppress ordinary rewards.


@pytest.mark.parametrize(
    "peak,speed_ok,body_hit,paid",
    [(0.28, True, False, True), (0.20, True, False, False), (0.28, False, False, False), (0.28, True, True, False)],
)
def test_takeoff_response_latches_latency_and_only_pays_on_full_success(clearance_jump, peak, speed_ok, body_hit, paid):
    from math import exp

    from wheelleg.rewards import compute_rewards

    event = clearance_jump
    weight = event.clearance_training["reward_overrides"]["jump_takeoff_response"]
    state = {"jump": event, "jump_vx_qualified": torch.tensor([speed_ok])}

    def bonus():
        return compute_rewards(state, {}, {"jump_takeoff_response": weight}, 0.01, 2.5)["jump_takeoff_response"].item()

    for _ in range(17):
        clearance_step(event, (0.0, 0.0), vz=0.0, contact=(True, True))
    for _ in range(3):
        clearance_step(event, (peak, peak))
    assert event.takeoff_latency_s.item() == pytest.approx(0.20)
    for _ in range(10):
        clearance_step(event, (peak, peak))
    assert event.takeoff_latency_s.item() == pytest.approx(0.20)
    assert bonus() == 0  # Not paid in the air, even if the target was met.
    for step in range(80):
        clearance_step(event, (0.0, 0.0), vz=0.0, contact=(True, True), failed=body_hit and step == 0)
    assert bonus() == pytest.approx(0.20 * exp(-((0.2 / 0.6) ** 2)) if paid else 0.0)
    clearance_step(event, (0.0, 0.0), vz=0.0, contact=(True, True))
    assert bonus() == 0
    event.reset(torch.arange(1))
    assert event.takeoff_latency_s.item() == 0


def test_flat_clearance_counts_only_both_wheels_pre_touch_after_confirmation(clearance_jump):
    event = clearance_jump
    for _ in range(2):
        clearance_step(event, (0.35, 0.33))
        assert not event.took_off.item() and event.scored_height.item() == 0
    clearance_step(event, (0.30, 0.08), z=0.62)
    assert event.took_off.item()
    assert event.scored_height.item() == pytest.approx(0.08)
    assert event.height_progress.item() == pytest.approx(0.32)
    clearance_step(event, (0.08, 0.30))
    assert event.height_progress.item() == 0
    clearance_step(event, (0.28, 0.27))
    assert event.scored_height.item() == pytest.approx(0.27)
    assert event.height_progress.item() == pytest.approx(0.68)
    clearance_step(event, (0.39, 0.38), vz=-0.5, contact=(True, False))
    assert event.first_touch.item()
    refs = clearance_step(event, (0.43, 0.42), vz=1.0)
    assert not any(refs[key].item() for key in ("tuck", "prepare", "flight"))
    assert event.height_progress.item() == 0
    assert event.scored_height.item() == pytest.approx(0.27)


def test_flat_takeoff_is_state_driven_from_the_press(clearance_jump):
    from wheelleg.rewards import jump_push_symmetry, jump_takeoff

    event = clearance_jump
    refs = clearance_step(event, (0.0, 0.0), vz=0.0, contact=(True, True))
    assert refs["push"].item() and not refs["crouch"].item()
    state = dict(
        jump=event,
        jump_ref=refs,
        jump_pose_scale=1.0,
        leg_length=torch.full((1, 2), 0.28),
        wheel_force=torch.full((1, 2), 10.0),
        wheel_contact=torch.ones(1, 2, dtype=torch.bool),
        velocity_w=torch.zeros(1, 3),
    )
    assert jump_takeoff(state, {}).item() == jump_push_symmetry(state, {}).item() == 0
    state["velocity_w"][0, 2] = 0.5
    assert jump_takeoff(state, {}).item() > 0 and jump_push_symmetry(state, {}).item() == 1
    for _ in range(3):
        clearance_step(event, (0.03, 0.03), vz=0.5)
    assert event.took_off.item() and event.elapsed.item() == pytest.approx(0.04)


def test_flat_tuck_and_prepare_do_not_reactivate_when_legs_move(clearance_jump):
    event = clearance_jump
    for _ in range(3):
        refs = clearance_step(event, (0.31, 0.30))
    assert refs["tuck"].item() and not refs["prepare"].item()
    assert refs["takeoff_velocity"].item() == event.clearance_training["takeoff_velocity_hint_m_s"]
    refs = clearance_step(event, (0.29, 0.30), vz=-0.10)
    assert refs["tuck"].item() and not refs["prepare"].item()
    # Still far above ground, but already descending: start landing extension immediately.
    refs = clearance_step(event, (0.29, 0.30), vz=-0.25)
    assert not refs["tuck"].item() and refs["prepare"].item()
    for wheel, vz in (((0.08, 0.09), -1.2), ((0.30, 0.31), 0.1)):
        refs = clearance_step(event, wheel, vz=vz)
        assert not refs["tuck"].item() and refs["prepare"].item()
    refs = clearance_step(event, (0.0, 0.01), vz=-0.5, contact=(True, False))
    assert not refs["tuck"].item() and not refs["prepare"].item()
    event.reset(torch.arange(1))
    assert not event.preparing.item()


def test_joint_apex_cannot_be_bought_with_stationary_body_or_separate_peaks(clearance_jump):
    e = clearance_jump
    for _ in range(3):
        clearance_step(e, (0.40, 0.35), body=0.10)
    assert e.scored_height.item() == 0 and e.height_progress.item() == 0
    clearance_step(e, (0.04, 0.05), body=0.40)
    assert e.scored_height.item() == pytest.approx(0.04)
    clearance_step(e, (0.30, 0.31), body=0.23, angles=(0.10, 0.95))
    assert e.scored_height.item() == pytest.approx(0.20) and not e.target_reached.item()
    clearance_step(e, (0.30, 0.31), body=0.29, angles=(0.0, 0.95))
    assert e.scored_height.item() == pytest.approx(0.26)
    assert not e.apex_pose_ok.item() and e.apex_pose_quality.item() < 0.25
    clearance_step(e, (0.18, 0.19), body=0.32, angles=(0.0, 0.0))
    assert not e.target_reached.item()  # Upright at a different, lower peak is not enough.
    clearance_step(e, (0.30, 0.31), body=0.30, angles=(0.10, -0.20))
    assert e.target_reached.item() and e.apex_pose_quality.item() == 1
    clearance_step(e, (0.0, 0.1), body=0.29, contact=(True, False))
    clearance_step(e, (0.40, 0.40), body=0.50)
    assert e.peak_body_at_apex.item() == pytest.approx(0.30)
    assert e.peak_wheel_at_apex.item() == pytest.approx(0.30)
    assert e.height_progress.item() == 0
    e.reset(torch.arange(1))
    assert e.scored_height.item() == e.apex_pose_quality.item() == 0


def test_wheel_only_snapshot_keeps_legacy_scoring(clearance_jump):
    old = dict(clearance_jump.settings)
    del old["body_wheel_jump"]
    e = JumpEvent(old, 1, "cpu")
    e.reset(torch.arange(1))
    e.trigger(torch.tensor([5.0]), torch.tensor([0.3]), torch.tensor([True]), torch.tensor([0.25]))
    for _ in range(3):
        clearance_step(e, (0.30, 0.28), body=0.10, angles=(1.0, -1.0))
    assert e.target_reached.item() and e.scored_height.item() == pytest.approx(0.28)


def test_peak_band_evicts_old_frames_and_never_borrows_below_threshold_pose(clearance_jump):
    e = clearance_jump

    def frame(h, angle):
        clearance_step(e, (h, h), body=0.60, angles=(angle, angle))

    for _ in range(3):
        frame(0.2395, 0.1)
    frame(0.2402, 0.90)
    assert not e.target_reached.item()  # Good pose at 23.95 cm is below the 24 cm pass threshold.
    frame(0.2422, 0.2)
    frame(0.2432, 0.90)
    assert e.target_reached.item() and e.scored_height.item() == pytest.approx(0.2422)
    frame(0.2473, 0.90)
    assert not e.target_reached.item()  # Good frame has left the band.
    frame(0.2462, 0.1)
    assert e.target_reached.item() and e.scored_height.item() == pytest.approx(0.2462)
    assert e.height_progress.item() == 0  # Descending within the band never pays progress twice.


def test_flat_tuck_and_air_smoothness_are_bounded(clearance_jump):
    from wheelleg.rewards import jump_air_leg_smoothness, jump_tuck

    state = dict(
        jump=clearance_jump,
        jump_ref={"tuck": torch.tensor([True] * 4), "flight": torch.tensor([True, True, True, False])},
        jump_pose_scale=1.0,
        guidance_scale=0.3,
        leg_length=torch.tensor([[0.28, 0.28], [0.15, 0.215], [0.15, 0.15], [0.14, 0.14]]),
        leg_action_second_difference=torch.tensor([[0.0] * 4, [1.0] * 4, [100.0] * 4, [100.0] * 4]),
    )
    torch.testing.assert_close(jump_tuck(state, {}), torch.tensor([0.0, 0.25, 1.0, 1.0]))
    smooth = jump_air_leg_smoothness(state, {})
    assert 0 == smooth[0] < smooth[1] < smooth[2] < 1
    assert smooth[3] == 0


@pytest.mark.parametrize("after_wheel_touch", [False, True])
def test_flat_body_contact_aborts_attempt_even_if_support_recovers(clearance_jump, after_wheel_touch):
    event = clearance_jump
    for _ in range(3):
        clearance_step(event, (0.28, 0.28))
    if after_wheel_touch:
        clearance_step(event, (0.0, 0.0), vz=0.0, contact=(True, True))
    clearance_step(event, (0.0, 0.0), vz=0.0, contact=(True, True), stable=False, failed=True)
    assert event.invalid.item() and event.failure_pulse.item() and event.finished.item()
    for _ in range(105):
        clearance_step(event, (0.0, 0.0), vz=0.0, contact=(True, True))
    assert not event.landing_paid.item() and not event.failure_pulse.item()


def test_flat_landing_checks_rates_and_recovers_after_bounce(clearance_jump):
    from wheelleg.jump import landing_rates_ok
    from wheelleg.rewards import jump_fast_touchdown, jump_landing_recovery, jump_rebound

    event = clearance_jump
    rates_ok = landing_rates_ok(
        torch.tensor([0.0, 0.25, 0.0]), torch.tensor([[0.0, 0.0], [0.0, 0.0], [0.0, 1.3]]), event.clearance_training
    )
    assert rates_ok.tolist() == [True, False, False]
    for _ in range(3):
        clearance_step(event, (0.28, 0.28))
    clearance_step(event, (0.03, 0.03), vz=-4.0)
    clearance_step(event, (0.0, 0.0), vz=0.0, contact=(True, False), stable=False)
    assert jump_fast_touchdown({"jump": event}, {}).item() == 1
    for _ in range(110):
        clearance_step(event, (0.0, 0.0), vz=0.0, contact=(True, True), stable=bool(rates_ok[2]))
        assert jump_fast_touchdown({"jump": event}, {}).item() == 0
    assert not event.landing_paid.item() and event.stable_time.item() == 0
    state = dict(
        jump=event,
        velocity_w=torch.tensor([[1.5, 0.0, 0.0]]),
        angular_velocity=torch.zeros(1, 3),
        roll=torch.zeros(1),
        pitch=torch.zeros(1),
        linear_error=torch.zeros(1),
        wheel_contact=torch.ones(1, 2, dtype=torch.bool),
    )
    assert jump_landing_recovery(state, {}).item() == 0  # Moving at command speed is stable, not stopping.
    state["linear_error"].fill_(-1.5)
    assert jump_landing_recovery(state, {}).item() > 0.9
    state["wheel_contact"].zero_()
    state["velocity_w"][0, 2] = 1.0
    assert jump_rebound(state, {}).item() == 1
    clearance_step(event, (0.06, 0.06), vz=1.0)
    for _ in range(79):
        clearance_step(event, (0.0, 0.0), vz=0.0, contact=(True, True))
        assert not event.landing_pulse.item()
    clearance_step(event, (0.0, 0.0), vz=0.0, contact=(True, True))
    assert event.landing_pulse.item() and not event.failure_paid.item()
