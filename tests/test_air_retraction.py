import pytest
import torch

from wheelleg.air_retraction import AirRetractionTracker

# Binary-exact lengths keep equality-at-tolerance cases unambiguous.
TICK_M = 1 / 128


@pytest.mark.parametrize(
    ("lengths", "deltas"),
    [
        pytest.param([30, 31, 32, 31, 30, 29, 27, 27], [0, 0, 0, 0, 0, 3, 2, 0], id="slow-fall-from-new-peak"),
        pytest.param([32, 31, 32, 30, 31, 30, 32, 30], [0] * 8, id="subthreshold-sawtooth"),
        pytest.param([32, 25, 26, 25, 27, 25, 24, 25], [0, 7, 0, 0, 0, 0, 1, 0], id="no-double-count"),
        pytest.param([40, 30, 31, 32, 33, 34, 32, 31, 30], [0, 10, 0, 0, 0, 0, 0, 3, 1], id="partial-rebound"),
    ],
)
def test_each_frame_reports_only_new_excess(lengths, deltas):
    tracker = AirRetractionTracker(1, 2 * TICK_M, "cpu")
    for length, delta in zip(lengths, deltas, strict=True):
        actual = tracker.update(torch.tensor([[length, 40]]) * TICK_M, torch.tensor([True]))
        torch.testing.assert_close(actual, torch.tensor([[delta, 0]]) * TICK_M, rtol=0, atol=0)


def test_independent_legs_and_eligibility_windows():
    tracker = AirRetractionTracker(2, 2 * TICK_M, "cpu")
    # Env 0 loses eligibility on a falling frame, then re-enters far below its last length.
    frames = [
        ([[40, 30], [30, 40]], [True, False], [[0, 0], [0, 0]]),
        ([[30, 34], [32, 38]], [True, True], [[10, 0], [0, 0]]),
        ([[33, 33], [28, 39]], [True, True], [[0, 0], [4, 0]]),
        ([[30, 29], [29, 32]], [True, True], [[3, 5], [0, 7]]),
        ([[20, 20], [27, 35]], [False, True], [[0, 0], [1, 0]]),
        ([[10, 12], [26, 32]], [True, True], [[0, 0], [1, 3]]),
        ([[7, 8], [26, 32]], [True, True], [[3, 4], [0, 0]]),
    ]
    for lengths, eligible, deltas in frames:
        actual = tracker.update(torch.tensor(lengths) * TICK_M, torch.tensor(eligible))
        torch.testing.assert_close(actual, torch.tensor(deltas) * TICK_M, rtol=0, atol=0)


def test_reset_only_selected_ids():
    tracker = AirRetractionTracker(3, 2 * TICK_M, "cpu")
    eligible = torch.ones(3, dtype=torch.bool)
    tracker.update(torch.full((3, 2), 40 * TICK_M), eligible)
    tracker.update(torch.full((3, 2), 30 * TICK_M), eligible)
    tracker.reset(torch.tensor([2, 0]))
    actual = tracker.update(torch.full((3, 2), 25 * TICK_M), eligible)
    torch.testing.assert_close(actual, torch.tensor([[0, 0], [5, 5], [0, 0]]) * TICK_M, rtol=0, atol=0)
    actual = tracker.update(torch.full((3, 2), 22 * TICK_M), eligible)
    torch.testing.assert_close(actual, torch.tensor([[3, 3], [3, 3], [3, 3]]) * TICK_M, rtol=0, atol=0)


def test_half_centimeter_equality_then_charge_full_excursion():
    t = AirRetractionTracker(1, 0.005, "cpu")
    for length, expected in [(0.30, 0), (0.295, 0), (0.294, .006), (.293, .001), (.31, 0), (.30, .01)]:
        torch.testing.assert_close(t.update(torch.full((1, 2), length), torch.tensor([True])),
                                   torch.full((1, 2), float(expected)), atol=1e-7, rtol=0)
