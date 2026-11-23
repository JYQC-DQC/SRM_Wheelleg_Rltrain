from copy import deepcopy
from pathlib import Path

import pytest
import torch
import yaml

from wheelleg.jump import JumpEvent
from wheelleg.multi_actor import resume_contract_matches
from wheelleg.rewards import compute_rewards, jump_reward_weight
from wheelleg.training import load_training


def stage():
    return yaml.safe_load(Path("config/reference/scut_p3_multi_actor.yaml").read_text(encoding="utf-8"))["stages"][
        "jump"
    ]


def landed_event(heights):
    event = JumpEvent(stage(), len(heights), "cpu")
    event.height[:] = torch.tensor(heights)
    event.peak_joint_clearance[:] = event.band_scored_height[:] = event.height
    event.peak_leg_angle_rad.zero_()
    event.apex_pose_quality.fill_(1)
    event.took_off.fill_(True)
    event.landing_pulse.fill_(True)
    event.tuck_gain.fill_(1)
    return event


def terms(event):
    weights = event.settings["clearance_jump"]["reward_overrides"]
    weights = {k: weights[k] for k in ("jump_apex", "jump_landing", "jump_tuck_progress")}
    return compute_rewards({"jump": event}, {}, weights, 0.01, 0.001)


def test_l5_boundary_and_low_level_reviews_preserve_the_total_budget():
    event = landed_event([0.04, 0.0925, 0.145, 0.1975, 0.25, 0.30, 0.35, 0.40, 0.45])
    payouts = terms(event)
    torch.testing.assert_close(payouts["jump_apex"], torch.tensor([1.0] * 4 + [2.0] * 5))
    torch.testing.assert_close(payouts["jump_landing"], torch.tensor([1.0] * 4 + [0.5] * 5))
    torch.testing.assert_close(payouts["jump_tuck_progress"], torch.tensor([0.5] * 4 + [0.25] * 5))
    guide = event.landing_guide.cfg
    retained = jump_reward_weight(event, "jump_retained_extension", guide["retained_bonus"])
    stopped = jump_reward_weight(event, "jump_stop_quality", guide["stop_bonus"])
    total = sum(payouts.values()) + retained + stopped + guide["full_success_bonus"]
    torch.testing.assert_close(total, torch.full((9,), 4.25))


def test_high_near_miss_cannot_collect_attainment_portion():
    event = landed_event([0.1975, 0.25, 0.35, 0.25])
    event.band_scored_height[:] -= torch.tensor([0.02, 0.02, 0.02, 0.01])
    bonus = terms(event)["jump_apex"]
    assert 0.5 < bonus[0] < 1  # L4 retains the old continuous apex score.
    assert 0 < bonus[1] <= 0.5 and 0 < bonus[2] <= 0.5
    assert bonus[3] == pytest.approx(2)  # Same existing 1 cm acceptance tolerance.


@pytest.mark.parametrize("invalid", ["no_takeoff", "body_contact", "failure_paid", "not_settled", "pose"])
def test_no_attainment_bonus_for_invalid_flight_or_landing(invalid):
    event = landed_event([0.25])
    if invalid == "no_takeoff":
        event.took_off.zero_()
    elif invalid == "body_contact":
        event.invalid.fill_(True)
    elif invalid == "failure_paid":
        event.failure_paid.fill_(True)
    elif invalid == "not_settled":
        event.landing_pulse.zero_()
    else:
        event.peak_leg_angle_rad.fill_(1.5)
    bonus = terms(event)["jump_apex"]
    assert bonus.item() <= 0.5
    if invalid in ("body_contact", "failure_paid", "not_settled"):
        assert bonus.item() == 0


def test_one_high_wheel_cannot_buy_the_height_bonus():
    event = landed_event([0.25])
    event.peak_joint_clearance.zero_()
    event.band_scored_height.zero_()
    event.start_body_clearance.fill_(0.1)
    event.active.fill_(True)
    event.update(
        0.01,
        torch.tensor([1.0]),
        torch.tensor([0.5]),
        torch.tensor([0.3]),
        torch.zeros((1, 2), dtype=torch.bool),
        torch.tensor([False]),
        torch.tensor([True]),
        torch.tensor([False]),
        wheel_clearance=torch.tensor([[0.35, 0.10]]),
        body_clearance_m=torch.tensor([0.5]),
        leg_angle_rad=torch.zeros((1, 2)),
        leg_length_m=torch.full((1, 2), 0.2),
    )
    event.landing_pulse.fill_(True)
    assert not event.target_reached.item()
    assert terms(event)["jump_apex"].item() <= 0.5


def test_legacy_snapshot_without_priority_keeps_its_old_rewards():
    event = landed_event([0.25])
    del event.settings["clearance_jump"]["height_priority"]
    payout = terms(event)
    assert {k: v.item() for k, v in payout.items()} == pytest.approx(
        {"jump_apex": 1.0, "jump_landing": 1.0, "jump_tuck_progress": 0.5}
    )


@pytest.mark.parametrize("height,expected", [(0.1975, 1.0), (0.25, 2.0)])
def test_apex_pays_only_once_after_real_takeoff_and_continuous_settlement(height, expected):
    event = JumpEvent(stage(), 1, "cpu")
    event.remaining.fill_(1)
    event.trigger(
        torch.tensor([5.0]),
        torch.tensor([0.3]),
        torch.tensor([True]),
        target_height=torch.tensor([height]),
        require_trigger_time=False,
        body_clearance_m=torch.tensor([0.1]),
        leg_length_m=torch.full((1, 2), 0.21),
    )
    total = 0.0
    paid = 0
    for tick in range(120):
        air = tick < 6
        event.update(
            0.01,
            torch.tensor([5 + (tick + 1) * 0.01]),
            torch.tensor([0.7 if air else 0.3]),
            torch.tensor([0.5 if air else 0.0]),
            torch.full((1, 2), not air),
            torch.tensor([not air]),
            torch.tensor([True]),
            torch.tensor([False]),
            wheel_clearance=torch.full((1, 2), 0.3 if air else 0.0),
            body_clearance_m=torch.tensor([0.5 if air else 0.1]),
            leg_angle_rad=torch.zeros((1, 2)),
            leg_length_m=torch.full((1, 2), 0.21),
            require_height=torch.tensor([False]),
        )
        payout = terms(event)["jump_apex"].item()
        if tick < 80:
            assert payout == 0
        total += payout
        paid += payout > 0
    assert total == pytest.approx(expected)
    assert paid == 1


def test_height_update_requires_explicit_migration_and_cannot_change_other_contracts():
    current = {"actor_bundle": {"frozen": "hash"}, "jump_event_stage": stage()}
    saved = deepcopy(current)
    del saved["jump_event_stage"]["clearance_jump"]["height_priority"]
    assert not resume_contract_matches(saved, current)
    assert resume_contract_matches(saved, current, height_priority_update=True)
    current["jump_event_stage"]["failure_cost"] = -8
    assert not resume_contract_matches(saved, current, height_priority_update=True)
    current["jump_event_stage"]["failure_cost"] = -4
    current["actor_bundle"]["frozen"] = "changed"
    assert not resume_contract_matches(saved, current, height_priority_update=True)


@pytest.mark.parametrize("invalid", ["start_level", "cap", "budget", "penalty"])
def test_invalid_priority_configuration_is_rejected(tmp_path, invalid):
    cfg = yaml.safe_load(Path("config/reference/scut_p3_multi_actor.yaml").read_text(encoding="utf-8"))
    priority = cfg["stages"]["jump"]["clearance_jump"]["height_priority"]
    if invalid == "start_level":
        priority["start_level"] = 10
    elif invalid == "cap":
        priority["apex_progress_bonus"] = 2
    elif invalid == "budget":
        priority["reward_overrides"]["jump_apex"] = 3
    else:
        priority["reward_overrides"]["lin_vel_error"] = -1
    path = tmp_path / "policy.yaml"
    path.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    with pytest.raises(ValueError, match="height_priority"):
        load_training("p3-jump", "sim2sim/checkpoints/jump_preload_split_model27400/params/robot.yaml", path)
