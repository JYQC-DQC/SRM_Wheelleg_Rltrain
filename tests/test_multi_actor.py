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
