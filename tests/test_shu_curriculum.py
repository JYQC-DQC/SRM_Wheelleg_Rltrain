"""CPU tests; window sizes/difficulties below are test fixtures, not SHU settings."""

import pytest
import torch

from wheelleg.shu_curriculum import AirHeightCurriculum, FlatCommandCurriculum

EDGES = (0.01, 0.03, 0.12, 0.36, 0.45)  # intentionally unequal widths


def settle(c, n, yes, *, band=None):
    c.record(
        torch.full((n,), c.level if band is None else band), torch.arange(n) < yes, torch.ones(n, dtype=torch.bool)
    )


def test_exact_latest_windows_with_overflow_and_three_promotions():
    c = AirHeightCurriculum(EDGES, "cpu")
    settle(c, 513, 307)  # failed closed window; 513th sample (false) is retained for next
    assert (c.level, c.events, c.successes, c.last_rate) == (0, 1, 0, 307 / 512)
    settle(c, 600, 308)
    assert (c.level, c.events, c.successes, c.last_rate) == (1, 0, 0, 308 / 512)
    settle(c, 512, 512, band=0)  # older in-flight births cannot close the new band
    c.record(torch.ones(512, dtype=torch.long), torch.ones(512, dtype=torch.bool), torch.zeros(512, dtype=torch.bool))
    assert c.events == 0
    for level in [1, 2, 3]:
        settle(c, 511, 307)
        assert c.level == level
        settle(c, 1, 1)
        assert c.level == min(level + 1, 3) and c.last_rate == 308 / 512
    settle(c, 512, 307)
    assert c.level == 3 and c.last_rate == 307 / 512


def test_sampling_first_two_uniform_late_bands_40_and_old_proportional_to_width():
    torch.manual_seed(77)
    c = AirHeightCurriculum(EDGES, "cpu")
    for level in range(4):
        h, b = c.sample(18000)
        assert h.min() >= EDGES[0] and h.max() <= EDGES[level + 1]
        assert b.equal(torch.bucketize(h, torch.tensor(EDGES[1:-1])))
        # Compare continuous CDF at mid-band and at every boundary; not just frequency of latest.
        for j in range(level + 1):
            x = (EDGES[j] + EDGES[j + 1]) / 2
            if level < 2:
                want = (x - EDGES[0]) / (EDGES[level + 1] - EDGES[0])
            elif j < level:
                want = 0.6 * (x - EDGES[0]) / (EDGES[level] - EDGES[0])
            else:
                want = 0.8
            assert (h <= x).float().mean().item() == pytest.approx(want, abs=0.017)
        settle(c, 512, 512)


def test_air_checkpoint_retains_band_window_not_reassigned_to_changed_geometry():
    c = AirHeightCurriculum(EDGES, "cpu")
    settle(c, 512, 512)
    settle(c, 511, 307)
    other = AirHeightCurriculum(EDGES, "cpu")
    other.load_state_dict(c.state_dict())
    settle(other, 1, 1)
    assert other.level == 2
    with pytest.raises(ValueError, match="edges"):
        AirHeightCurriculum((0, 0.03, 0.12, 0.36, 0.45), "cpu").load_state_dict(c.state_dict())
    with pytest.raises(ValueError):
        AirHeightCurriculum((0, 0.03, 0.02, 0.36, 0.45), "cpu")


def test_flat_buckets_falls_truncations_exact_sixty_stale_and_restore():
    c = FlatCommandCurriculum(0.4, [5] * 6, "cpu")
    k = torch.tensor([0] * 6 + [2] * 5)
    yes = torch.tensor([1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0], dtype=torch.bool)
    fell = torch.zeros_like(yes)
    fell[4] = True
    cut = torch.zeros_like(yes)
    cut[5] = True
    c.record(k, c.fraction[k], ~(cut | fell), yes, fell, cut)
    assert c.fraction.tolist() == pytest.approx([0.5, 0.4, 0.4, 0.4, 0.4, 0.4])
    assert c.completed.tolist() == [4, 0, 5, 0, 0, 0] and c.falls[0] == 1 and c.interruptions[0] == 1
    k = torch.zeros(8, dtype=torch.long)
    yes = torch.ones(8, dtype=torch.bool)
    f = torch.full((8,), 0.4)
    f[-3:] = 0.5
    c.record(k, f, yes, yes, ~yes, ~yes)
    assert c.attempts[0] == 3 and c.successes[0] == 3
    other = FlatCommandCurriculum(0.1, 5, "cpu")
    other.load_state_dict(c.state_dict())
    assert torch.equal(other.fraction, c.fraction) and torch.equal(other.successes, c.successes)


def test_flat_last_increment_snaps_to_exactly_one_without_tolerating_an_actual_shortfall():
    start = torch.nextafter(torch.tensor(0.9), torch.tensor(0.0)).item()
    c = FlatCommandCurriculum([start, 0.899, 0.2, 0.3, 0.4, 0.5], 1, "cpu")
    k = torch.arange(6)
    t = k >= 0
    c.record(k, c.fraction.clone(), t, t, ~t, ~t)
    assert c.fraction[0].item() == 1.0 and c.fraction[1].item() == pytest.approx(0.999)
    for _ in range(7):
        c.record(k, c.fraction.clone(), t, t, ~t, ~t)
    assert c.fraction.tolist() == [1.0] * 6
