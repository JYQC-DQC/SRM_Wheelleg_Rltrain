"""CPU regression tests for per-environment stair difficulty."""

import pytest
import torch

from wheelleg.stair_rows import StairRowCurriculum


@pytest.mark.parametrize("rows", [1, 4, 6, 9])
def test_initial_draw_includes_both_ends_from_the_initial_range(rows):
    curriculum = StairRowCurriculum(512, rows, 2.0, "cpu", generator=torch.Generator().manual_seed(77))

    assert curriculum.levels.unique().tolist() == list(range(min(6, rows)))


def test_update_has_strict_thresholds_promotion_priority_bottom_clamp_and_id_order():
    curriculum = StairRowCurriculum(8, 8, 2.0, "cpu")
    curriculum.levels[:] = torch.tensor([2, 0, 2, 2, 2, 2, 6, 7])

    new_rows = curriculum.update(
        torch.tensor([6, 4, 1, 3, 5, 2]),
        torch.tensor([1.01, 0.0, 0.0, 1.01, 1.0, 1.0]),
        torch.tensor([0.0, 0.1, 0.1, 0.1, 0.39, 0.4]),
    )

    assert new_rows.tolist() == [7, 1, 0, 3, 1, 2]
    assert curriculum.levels.tolist() == [2, 0, 2, 3, 1, 1, 7, 7]


def test_only_promoted_top_envs_replay_across_all_rows_without_changing_other_envs():
    curriculum = StairRowCurriculum(1024, 9, 2.0, "cpu", generator=torch.Generator().manual_seed(99))
    curriculum.levels.fill_(8)
    ids = torch.arange(0, 1024, 2)
    zeros = torch.zeros_like(ids, dtype=torch.float32)

    replayed = curriculum.update(ids, zeros + 1.1, zeros)

    assert replayed.unique().tolist() == list(range(9))
    assert torch.equal(curriculum.levels[ids], replayed)
    assert (curriculum.levels[1::2] == 8).all()

    demoted = curriculum.update(ids, zeros, zeros)
    assert torch.equal(demoted, (replayed - 1).clamp_min(0))


def test_checkpoint_round_trip_and_empty_update_keep_per_env_state():
    source = StairRowCurriculum(3, 4, 2.0, "cpu")
    source.levels[:] = torch.tensor([0, 2, 3])
    state = source.state_dict()
    source.levels.fill_(1)

    restored = StairRowCurriculum(3, 4, 2.0, "cpu")
    restored.load_state_dict(state)
    state["levels"].zero_()
    result = restored.update(torch.empty(0, dtype=torch.long), torch.empty(0), torch.empty(0))

    assert result.numel() == 0
    assert restored.levels.tolist() == [0, 2, 3]
