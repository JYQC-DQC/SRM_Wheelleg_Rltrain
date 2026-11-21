from pathlib import Path

import pytest
import torch
import yaml
from torch import nn

from wheelleg.curriculum import JumpCurriculum
from wheelleg.multi_actor import ActorBank, BundlePolicy, actor_mask, masked_mean
from wheelleg.training import load_training


def test_explicit_handoff_limit_migration_does_not_bypass_other_contract_changes():
    from copy import deepcopy

    from wheelleg.multi_actor import resume_contract_matches

    saved = {
        "mode_contract_revision": 1,
        "actor_bundle": {
            "frozen": {"landing": "fixed-hash"},
            "handoff_critic_features": 2,
            "handoff": {"vertical_speed_m_s": 0.2, "duration_s": 2.0},
        },
    }
    current = deepcopy(saved)
    current["actor_bundle"]["handoff"]["vertical_speed_m_s"] = 0.3
    assert not resume_contract_matches(saved, current)
    assert resume_contract_matches(saved, current, 0.3)
    assert saved["actor_bundle"]["handoff"]["vertical_speed_m_s"] == 0.2
    for changed in ("frozen", "handoff_critic_features"):
        bad = deepcopy(current)
        bad["actor_bundle"][changed] = "changed"
        assert not resume_contract_matches(saved, bad, 0.3)
    bad = deepcopy(current)
    bad["mode_contract_revision"] = 2
    assert not resume_contract_matches(saved, bad, 0.3)
    bad = deepcopy(current)
    bad["actor_bundle"]["handoff"]["duration_s"] = 3
    assert not resume_contract_matches(saved, bad, 0.3)


def test_zero_handoff_resume_removes_cost_but_keeps_frozen_actor_contract():
    from copy import deepcopy

    from wheelleg.multi_actor import resume_contract_matches

    saved = {"actor_bundle": {"frozen": "hash", "handoff": {"duration_s": 2.0, "failure_cost": -4.0}}}
    current = deepcopy(saved)
    current["actor_bundle"]["handoff"].update(duration_s=0.0, failure_cost=0.0)
    assert not resume_contract_matches(saved, current)
    assert resume_contract_matches(saved, current, handoff_duration=0)
    current["actor_bundle"]["frozen"] = "different"
    assert not resume_contract_matches(saved, current, handoff_duration=0)


def test_no_observation_finishes_at_settle_without_cost_or_duplicate_counts():
    import ast
    from types import SimpleNamespace

    from wheelleg.jump_outcomes import JumpOutcomeTracker

    # Run the actual environment terminal path without importing Isaac Sim.
    source = Path("isaac/wheelleg_tasks/multi_actor.py").read_text(encoding="utf-8")
    node = next(n for n in ast.parse(source).body if isinstance(n, ast.ClassDef))

    class Base:
        def _get_dones(self):
            return torch.zeros(6, dtype=torch.bool), torch.tensor([False] * 5 + [True])

        def _record_jump_curriculum(self, ids, success, iteration):
            self.recorded_success = success

    scope = dict(torch=torch, WheelLegEnv=Base, JumpOutcomeTracker=JumpOutcomeTracker, HANDOFF_COST_TIMING="test")
    exec(compile(ast.Module(body=[node], type_ignores=[]), "multi_actor.py", "exec"), scope)
    env = scope["MultiActorEnv"].__new__(scope["MultiActorEnv"])
    env.actor_bundle = {"handoff": {"duration_s": 0.0}}
    env.state = {}  # No post-handoff state is read or used for acceptance.
    env.handoff_left = torch.zeros(6)
    for name in ("handoff_bad", "handoff_grade", "handoff_pulse", "handoff_failed", "handoff_cost_pulse"):
        setattr(env, name, torch.zeros(6, dtype=torch.bool))
    env.jump = SimpleNamespace(
        landing_pulse=torch.tensor([True, True, True, False, False, False]),
        target_reached=torch.tensor([True, False, True, False, False, False]),
        finished=torch.tensor([True, True, True, True, False, False]),
        elapsed=torch.ones(6),
    )
    env.jump_vx_qualified = torch.tensor([True, True, False, True, True, True])
    env.promotion_checks = None
    env.outcome_checks = torch.ones((6, 3), dtype=torch.bool)
    env.outcome_tracker = JumpOutcomeTracker(6, "cpu")
    env.commands = SimpleNamespace(target=torch.ones((6, 3)))
    env.iteration_handoff_counts = torch.zeros(2, dtype=torch.long)
    env.training_iteration_offset, env.common_step_counter = 0, 48
    env.training = SimpleNamespace(settings={"rollout_steps": 48})
    env.cfg = SimpleNamespace(evaluation=False)
    terminated, timeout = env._get_dones()
    assert terminated.tolist() == [True, True, True, False, False, False]
    assert timeout.tolist() == [False] * 5 + [True]
    assert env.recorded_success.tolist() == [True, False, False, False, False]
    assert env.outcome_tracker.counts[1].tolist() == [5, 1, 2, 1, 1, 0, 0]
    assert not env.handoff_cost_pulse.any() and not env.handoff_left.any()
    env._get_dones()
    assert env.outcome_tracker.counts[:, 0].sum() == 5


def test_specialist_mix_and_exact_sixty_percent_promotion():
    data = yaml.safe_load(
        (Path(__file__).resolve().parents[1] / "config/reference/scut_p3_multi_actor.yaml").read_text(encoding="utf-8")
    )
    stage = data["stages"]["jump"]
    assert stage["flat_episode_mix"]["fractions"] == [0, 0, 0.5, 0.5]
    assert data["training"]["save_interval"] == 200
    robot = Path(__file__).resolve().parents[1] / "sim2sim/checkpoints/jump_b99532e_model3400/params/robot.yaml"
    if robot.is_file():
        cfg = load_training(
            "p3-jump", robot, Path(__file__).resolve().parents[1] / "config/reference/scut_p3_multi_actor.yaml"
        )
        assert cfg.stage["flat_episode_mix"]["fractions"] == (0, 0, 0.5, 0.5)
    for threshold in (None, data["training"]["moving_jump_promote_rate"]):
        curriculum = JumpCurriculum(stage, "cpu", promote_rate=threshold, fresh_windows=True)
        count = stage["curriculum_min_events"]
        curriculum.record(torch.zeros(count, dtype=torch.long), torch.arange(count) < count * 0.6, 0)
        assert curriculum.maximum_level == 1


def toy_bank(count=4):
    bank = ActorBank.__new__(ActorBank)
    nn.Module.__init__(bank)
    bank.names = ("landing", "jump", "spin", "recovery")[:count]
    bank.default, bank.specialist = 0, 1
    bank.actors = nn.ModuleDict()
    for i, name in enumerate(bank.names):
        model = nn.Linear(35, 6)
        with torch.no_grad():
            model.weight.zero_()
            model.bias.fill_(i)
        model.requires_grad_(False)
        bank.actors[name] = model
    return bank


def test_four_actor_routes_are_independent_and_frozen():
    bank = toy_bank()
    obs = torch.randn(4, 35)
    result = bank(obs, torch.arange(4))
    torch.testing.assert_close(result, torch.arange(4).float().unsqueeze(-1).expand(4, 6))
    assert all(not parameter.requires_grad for parameter in bank.parameters())
    with pytest.raises(ValueError, match="Invalid actor"):
        bank(obs, torch.tensor([0, 1, 2, 4]))


def test_jump_route_returns_to_identical_base_actions():
    bank = toy_bank()
    policy = BundlePolicy(bank)
    obs = torch.zeros(3, 35)
    obs[:, 28] = torch.tensor([1.0, 0.0, 1.0])
    obs[1, 32] = 1
    torch.testing.assert_close(policy(obs), torch.tensor([0.0, 1.0, 0.0]).unsqueeze(-1).expand(3, 6))
    assert actor_mask(obs).tolist() == [False, True, False]


def test_frozen_steps_cannot_contribute_actor_loss_or_entropy_gradient():
    values = torch.tensor([100.0, 2.0, -100.0], requires_grad=True)
    loss = masked_mean(values, torch.tensor([0.0, 1.0, 0.0]))
    loss.backward()
    torch.testing.assert_close(values.grad, torch.tensor([0.0, 1.0, 0.0]))
    empty = masked_mean(values, torch.zeros(3))
    assert empty.item() == 0 and torch.isfinite(empty)
    assert masked_mean(torch.tensor([float("nan"), 2.0]), torch.tensor([0.0, 1.0])).item() == 2
