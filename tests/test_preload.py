from copy import deepcopy
from pathlib import Path

import pytest
import torch
import yaml

from wheelleg.jump import JumpEvent
from wheelleg.multi_actor import resume_contract_matches
from wheelleg.preload import PreloadGuide
from wheelleg.training import load_training


def settings():
    data = yaml.safe_load(Path("config/reference/scut_p3_multi_actor.yaml").read_text(encoding="utf-8"))
    stage = data["stages"]["jump"]
    guide = stage["clearance_jump"]["crouch_guidance"]
    guide.pop("takeoff_bonus", None)
    guide.pop("prepare_window_s", None)
    return stage


def test_l5_success_requires_supported_bilateral_crouch_then_extension():
    cfg = settings()["clearance_jump"]["crouch_guidance"]
    guide = PreloadGuide(cfg, 0.25, 6, "cpu")
    ids = torch.arange(6)
    start = torch.full((6, 2), 0.21)
    z = torch.full((6,), 0.30)
    guide.begin(ids, start, z)
    height = torch.tensor([0.1975, 0.25, 0.30, 0.25, 0.25, 0.25])
    active = torch.ones(6, dtype=torch.bool)
    contact = torch.ones((6, 2), dtype=torch.bool)

    def step(time, length, body_z):
        guide.update(0.01, active, torch.full((6,), time), height, contact, length, body_z, active)

    step(0.01, start, z)
    crouched = torch.full_like(start, 0.18)
    crouched[3, 1] = 0.21  # Alternating legs must not combine into a bilateral crouch.
    contact[4] = False  # Air tuck must never count, including after recontact.
    step(0.02, crouched, z - 0.03)
    contact[4] = True
    extended = start.clone()
    extended[3] = torch.tensor([0.21, 0.18])
    extended[5] = 0.18  # A held squat did not use the added extension stroke.
    step(0.03, extended, z)
    success = torch.tensor([True, True, False, True, True, True])
    assert not guide.success_bonus(success).any()  # No reward before an actual support loss.
    contact[:] = False
    step(0.04, extended, z + 0.01)
    bonus = guide.success_bonus(success)
    assert bonus.tolist() == pytest.approx([0, 0.2, 0, 0, 0, 0])
    assert guide.added_stroke_m[1].item() == pytest.approx(0.03)
    assert not guide.success_bonus(success).any()


def test_no_body_drop_no_late_or_landing_credit_and_repeated_cycles_are_bounded():
    cfg = settings()["clearance_jump"]["crouch_guidance"]
    guide = PreloadGuide(cfg, 0.25, 4, "cpu")
    ids = torch.arange(4)
    start = torch.full((4, 2), 0.21)
    z = torch.full((4,), 0.30)
    guide.begin(ids, start, z)
    active = torch.ones(4, dtype=torch.bool)
    height = torch.full((4,), 0.25)
    contact = torch.ones((4, 2), dtype=torch.bool)
    for time in (0.01, 0.02, 0.03, 0.04, 0.30, 0.31):
        length = start.clone()
        body = z.clone()
        if time in (0.02, 0.04, 0.30):
            length[:] = 0.16  # Going deeper than the target cannot increase the maximum bonus.
            body -= 0.05
            body[0] = z[0]  # Fold by leg swing with no actual lowering.
            if time < 0.30:
                length[1] = start[1]  # Only crouches outside the window.
        contact[2] = time != 0.01  # Recontact cannot reopen the preload window.
        guide.update(0.01, active, torch.full((4,), time), height, contact, length, body, active)
    contact[:] = False
    guide.update(0.01, active, torch.full((4,), 0.32), height, contact, start, z + 0.01, active)
    assert guide.success_bonus(active).tolist() == pytest.approx([0, 0, 0, 0.2])
    guide.begin(ids, start, z)
    assert not guide.used_score.any() and not guide.paid.any()
    assert not guide.left_support.any()


def test_standing_after_squat_or_non_rising_support_loss_cannot_subsidize_later_jump():
    guide = PreloadGuide(settings()["clearance_jump"]["crouch_guidance"], 0.25, 3, "cpu")
    ids = torch.arange(3)
    start, z = torch.full((3, 2), 0.21), torch.full((3,), 0.30)
    active, contact = torch.ones(3, dtype=torch.bool), torch.ones((3, 2), dtype=torch.bool)
    height = torch.full((3,), 0.25)
    guide.begin(ids, start, z)
    guide.update(0.01, active, z * 0 + 0.01, height, contact, start, z, active)
    guide.update(0.01, active, z * 0 + 0.02, height, contact, start - 0.03, z - 0.03, active)
    guide.update(0.01, active, z * 0 + 0.03, height, contact, start, z, torch.tensor([False, True, True]))
    contact[2] = False
    guide.update(0.01, active, z * 0 + 0.04, height, contact, start, z, torch.tensor([True, False, False]))
    contact[:] = False
    guide.update(0.01, active, z * 0 + 0.05, height, contact, start + 0.01, z + 0.01, active)
    assert not guide.success_bonus(active).any()


def test_jump_event_uses_sampled_l5_target_and_keeps_fixed_feature_count():
    stage = settings()
    event = JumpEvent(stage, 1, "cpu")
    ids = torch.tensor([0])
    event.reset(ids)
    event.remaining[:] = 1
    with pytest.raises(ValueError, match="leg lengths"):
        event.trigger(torch.tensor([1.0]), torch.tensor([0.30]), torch.tensor([True]), require_trigger_time=False)
    event.trigger(
        torch.tensor([1.0]),
        torch.tensor([0.30]),
        torch.tensor([True]),
        target_height=torch.tensor([0.04]),
        require_trigger_time=False,
        body_clearance_m=torch.tensor([0.20]),
        leg_length_m=torch.full((1, 2), 0.21),
    )
    event.height[:] = 0.25  # Actual curriculum sampling happens after trigger in Isaac.
    for length, root_z in ((0.21, 0.30), (0.18, 0.27), (0.21, 0.30)):
        event.update(
            0.01,
            torch.tensor([1.0]),
            torch.tensor([root_z]),
            torch.tensor([1.0 if length == 0.21 else 0.0]),
            torch.ones((1, 2), dtype=torch.bool),
            torch.tensor([False]),
            torch.tensor([True]),
            torch.tensor([False]),
            wheel_clearance=torch.zeros((1, 2)),
            body_clearance_m=torch.tensor([0.20]),
            leg_angle_rad=torch.zeros((1, 2)),
            leg_length_m=torch.full((1, 2), length),
        )
    assert event.preload.used_score.item() == pytest.approx(1)
    assert event.features().shape == (1, 16)


def test_crouch_migration_is_explicit_and_preserves_frozen_actor_and_other_settings():
    stage = settings()
    saved = {"actor_bundle": {"frozen": "hash"}, "jump_event_stage": deepcopy(stage)}
    del saved["jump_event_stage"]["clearance_jump"]["crouch_guidance"]
    current = deepcopy(saved)
    current["jump_event_stage"] = stage
    assert not resume_contract_matches(saved, current)
    assert resume_contract_matches(saved, current, crouch_guidance_update=True)
    assert "crouch_guidance" not in saved["jump_event_stage"]["clearance_jump"]
    for branch, key, value in (
        ("actor_bundle", "frozen", "changed"),
        ("jump_event_stage", "height_levels_m", [0.01]),
        ("jump_event_stage", "landing_stable_s", 0.1),
    ):
        bad = deepcopy(current)
        bad[branch][key] = value
        assert not resume_contract_matches(saved, bad, crouch_guidance_update=True)


def test_preload_configuration_validates_bounds(tmp_path):
    data = yaml.safe_load(Path("config/reference/scut_p3_multi_actor.yaml").read_text(encoding="utf-8"))
    policy = tmp_path / "policy.yaml"
    guide = data["stages"]["jump"]["clearance_jump"]["crouch_guidance"]
    policy.write_text(yaml.safe_dump(data), encoding="utf-8")
    cfg = load_training("p3-jump", Path("config/reference/scut_robot.template.yaml"), policy)
    assert cfg.stage["clearance_jump"]["crouch_guidance"]["start_level"] == 5
    for key, value in (("start_level", 0), ("max_bonus", 0.3), ("window_s", 2.0), ("target_leg_length_m", 0.50)):
        old = guide[key]
        guide[key] = value
        policy.write_text(yaml.safe_dump(data), encoding="utf-8")
        with pytest.raises(ValueError, match="crouch_guidance"):
            load_training("p3-jump", Path("config/reference/scut_robot.template.yaml"), policy)
        guide[key] = old


def test_actual_environment_pays_only_final_full_success_without_dt_scaling():
    import ast
    from types import SimpleNamespace

    source = Path("isaac/wheelleg_tasks/multi_actor.py").read_text(encoding="utf-8")
    cls = next(n for n in ast.parse(source).body if isinstance(n, ast.ClassDef))
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "_get_rewards")

    class Base:
        def _get_rewards(self):
            return torch.zeros(5)

    cls.bases = [ast.Name(id="Base", ctx=ast.Load())]
    cls.body = [method]
    namespace = {"Base": Base, "torch": torch}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[cls], type_ignores=[])), "env-reward", "exec"), namespace)
    env = namespace["MultiActorEnv"]()
    guide = PreloadGuide(settings()["clearance_jump"]["crouch_guidance"], 0.25, 5, "cpu")
    guide.used_score[:] = 1
    guide.eligible[:] = True
    guide.left_support[:] = True
    guide.added_stroke_m[:] = 0.03
    env.jump = SimpleNamespace(
        preload=guide,
        landing_guide=None,
        invalid=torch.zeros(5, dtype=torch.bool),
        failure_paid=torch.zeros(5, dtype=torch.bool),
        takeoff_pulse=torch.zeros(5, dtype=torch.bool),
        finished=torch.ones(5, dtype=torch.bool),
        landing_pulse=torch.tensor([True, True, True, True, False]),
    )
    env.numerical_bad = torch.zeros(5, dtype=torch.bool)
    env.iteration_preload_launch_stats = torch.zeros((2, 2))
    env.handoff_pulse = env.jump.landing_pulse.clone()
    # Final outcome already incorporates height, speed, heading and settle checks.
    env.handoff_failed = torch.tensor([False, True, True, True, False])
    env.handoff_cost_pulse = torch.zeros(5, dtype=torch.bool)
    env.handoff_left = torch.zeros(5)
    env.actor_bundle = {"handoff": {"failure_cost": 0.0}}
    env.commands = SimpleNamespace(target=torch.zeros((5, 3)))
    env.reward_sums = {"jump_preload_success": torch.zeros(5), "jump_preload_takeoff": torch.zeros(5)}
    env.iteration_preload_stats = torch.zeros((2, 6))
    env.iteration_handoff_cost_stats = torch.zeros(3)
    env.extras = {"evaluation": {}}
    assert env._get_rewards().tolist() == pytest.approx([0.2, 0, 0, 0, 0])
    assert not env._get_rewards().any()
