from types import SimpleNamespace

import torch

from wheelleg.air_retraction import AirRetractionTracker
from wheelleg.rewards import jump_air_leg_smoothness


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
