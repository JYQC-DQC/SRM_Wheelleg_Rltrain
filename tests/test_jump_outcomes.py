import torch

from wheelleg.curriculum import JumpCurriculum
from wheelleg.jump_outcomes import JumpOutcomeTracker


def test_final_event_is_counted_once_and_reasons_are_independent():
    tracker = JumpOutcomeTracker(5, "cpu")
    ids = torch.arange(5)
    moving = torch.tensor([False, False, True, True, True])
    checks = torch.tensor(
        [[True, True, True], [False, True, True], [True, False, False], [True, True, True], [True, True, True]]
    )
    event_failed = torch.tensor([False, False, False, False, True])
    handoff_failed = torch.tensor([False, False, True, True, False])
    fresh, success = tracker.record(ids, moving, checks, event_failed, handoff_failed)
    assert fresh.tolist() == [0, 1, 2, 3, 4]
    assert success.tolist() == [True, False, False, False, False]
    assert tracker.counts.tolist() == [[2, 1, 0, 1, 0, 0, 0], [3, 0, 1, 0, 1, 1, 2]]
    fresh, _ = tracker.record(ids, moving, checks, event_failed, handoff_failed)
    assert fresh.numel() == 0
    assert tracker.counts[:, 0].sum().item() == 5
    tracker.reset(torch.tensor([1]))
    tracker.record(ids, moving, checks, event_failed, handoff_failed)
    assert tracker.counts[:, 0].sum().item() == 6


def test_resume_level_override_discards_old_window_without_relaxing_threshold():
    settings = dict(
        height_levels_m=[0.04, 0.0925, 0.145],
        curriculum_min_events=500,
        guidance_success_threshold=0.6,
        guidance_decay_iterations=2000,
        guidance_final_scale=0.0,
    )
    curriculum = JumpCurriculum(settings, "cpu", fresh_windows=True)
    curriculum.attempts.fill_(499)
    curriculum.successes.fill_(200)
    curriculum.latest_rate.fill_(0.4)
    curriculum.anneal_start.fill_(10)
    curriculum.restart(2)
    assert curriculum.maximum_level == 1
    assert not curriculum.attempts.any() and not curriculum.successes.any() and not curriculum.latest_rate.any()
    assert (curriculum.anneal_start == -1).all()
    assert curriculum.levels[1].item() == torch.tensor(0.0925).item()
    curriculum.record(torch.ones(500, dtype=torch.long), torch.arange(500) < 299, 100)
    assert curriculum.maximum_level == 1
    curriculum.record(torch.ones(500, dtype=torch.long), torch.arange(500) < 300, 101)
    assert curriculum.maximum_level == 2
