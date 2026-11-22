from types import SimpleNamespace

import torch

from wheelleg.air_retraction import AirRetractionTracker
from wheelleg.rewards import jump_air_leg_smoothness


def test_reward_migration_does_not_allow_changed_height_or_frozen_actor():
    from copy import deepcopy

    from wheelleg.multi_actor import resume_contract_matches

    stage = {
        "clearance_jump": {"reward_overrides": {"jump_air_leg_smoothness": -0.08}},
        "body_wheel_jump": {"air_leg_guard": {}},
        "height_levels_m": [0.04, 0.0925],
    }
    saved = {"actor_bundle": {"frozen": "fixed"}, "jump_event_stage": stage}
    current = deepcopy(saved)
    current["jump_event_stage"]["clearance_jump"].update(
        air_smoothness={"deadband_raw": 0.05, "quadratic_limit_raw": 0.5}
    )
    current["jump_event_stage"]["clearance_jump"]["reward_overrides"]["jump_air_leg_smoothness"] = -0.6
    current["jump_event_stage"]["body_wheel_jump"]["air_leg_guard"].update(
        tuck_extension_tolerance_m=0.01, tuck_extension_cost_per_m=4.0
    )
    assert not resume_contract_matches(saved, current)
    assert resume_contract_matches(saved, current, air_motion_update=True)
    bad = deepcopy(current)
    bad["jump_event_stage"]["height_levels_m"] = [0.01]
    assert not resume_contract_matches(saved, bad, air_motion_update=True)
    bad = deepcopy(current)
    bad["actor_bundle"]["frozen"] = "changed"
    assert not resume_contract_matches(saved, bad, air_motion_update=True)


def test_large_air_jerks_keep_costing_more_but_ground_is_free():
    state = {
        "jump": SimpleNamespace(
            clearance_training={"air_smoothness": {"deadband_raw": 0.05, "quadratic_limit_raw": 0.5}}
        ),
        "leg_action_second_difference": torch.tensor([[0.04] * 4, [0.5] * 4, [1.0] * 4, [4.0] * 4]),
        "jump_ref": {"flight": torch.ones(4)},
    }
    cost = jump_air_leg_smoothness(state, {})
    assert cost[0] == 0 and torch.all(cost[1:] > cost[:-1])
    assert torch.isfinite(cost).all()
    state["jump_ref"]["flight"].zero_()
    assert not jump_air_leg_smoothness(state, {}).any()


def test_tuck_guard_allows_retraction_and_small_correction_but_charges_repeated_extension():
    guard = AirRetractionTracker(1, 0.01, "cpu")
    active = torch.tensor([True])
    total = 0.0
    for length in [0.30, 0.26, 0.22, 0.20, 0.205, 0.20]:
        total += guard.update(torch.full((1, 2), -length), active).sum().item()
    assert total == 0
    first = guard.update(torch.full((1, 2), -0.23), active).sum().item()
    assert first > 0
    assert guard.update(torch.full((1, 2), -0.23), active).sum() == 0
    guard.update(torch.full((1, 2), -0.20), active)
    assert guard.update(torch.full((1, 2), -0.23), active).sum().item() == first
    assert guard.excursion_count.tolist() == [[2, 2]]
    # Stage exit and a new jump must not charge a position discontinuity as a reversal.
    guard.update(torch.full((1, 2), -0.18), torch.tensor([False]))
    assert not guard.update(torch.full((1, 2), -0.30), active).any()
    guard.reset(torch.tensor([0]))
    assert not guard.update(torch.full((1, 2), -0.32), active).any()
