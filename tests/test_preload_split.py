from pathlib import Path

import pytest
import torch
import yaml

from wheelleg.jump import JumpEvent
from wheelleg.preload import PreloadGuide


def stage():
    return yaml.safe_load(Path("config/reference/scut_p3_multi_actor.yaml").read_text(encoding="utf-8"))["stages"][
        "jump"
    ]


def test_split_budget_requires_real_stroke_and_confirmation_and_cannot_repeat():
    guide = PreloadGuide(stage()["clearance_jump"]["crouch_guidance"], 0.25, 1, "cpu")
    ids = torch.tensor([0])
    active = torch.tensor([True])
    contact = torch.ones((1, 2), dtype=torch.bool)
    start = torch.full((1, 2), 0.21)
    z = torch.tensor([0.30])
    height = torch.tensor([0.25])
    guide.begin(ids, start, z)
    for time, length, body in [(0.01, 0.21, 0.30), (0.02, 0.18, 0.27), (0.03, 0.21, 0.30)]:
        guide.update(
            0.01,
            active,
            torch.tensor([time]),
            height,
            contact,
            torch.full((1, 2), length),
            torch.tensor([body]),
            active,
        )
    assert not guide.takeoff_bonus(active, active).any()  # Still supported.
    contact[:] = False
    guide.update(0.01, active, torch.tensor([0.04]), height, contact, start, z + 0.01, active)
    assert not guide.takeoff_bonus(~active, active).any()
    first = guide.takeoff_bonus(active, active)
    assert first.item() == pytest.approx(0.08)
    assert not guide.takeoff_bonus(active, active).any()
    assert not guide.success_bonus(~active).any()  # A height-short attempt still keeps its small launch credit.
    last = guide.success_bonus(active)
    assert last.item() == pytest.approx(0.12)
    assert (first + last).item() == pytest.approx(0.20)
    assert not guide.success_bonus(active).any()
    guide.reset(ids)
    assert not guide.takeoff_paid.any() and not guide.paid.any()


def test_prepare_grace_is_reward_only_high_level_and_expires():
    event = JumpEvent(stage(), 2, "cpu")
    event.active[:] = True
    event.height[:] = torch.tensor([0.25, 0.1975])
    event.elapsed[:] = 0.05
    assert event.preload_preparing(torch.tensor([-0.3, -0.3])).tolist() == [True, False]
    refs = event.references(torch.tensor([-0.3, -0.3]), torch.zeros((2, 2)), 9.81)
    assert refs["push"].tolist() == [False, True]
    event.preload.best_score[0] = 0.3
    assert not event.preload_preparing(torch.tensor([0.2, -0.3])).any()
    event.preload.best_score.zero_()
    event.elapsed[:] = 0.16
    assert not event.preload_preparing(torch.zeros(2)).any()


def test_new_reward_fields_only_need_existing_crouch_migration():
    from copy import deepcopy
    from wheelleg.multi_actor import resume_contract_matches

    current = dict(actor_bundle={"frozen": "hash"}, jump_event_stage=stage())
    saved = deepcopy(current)
    guide = saved["jump_event_stage"]["clearance_jump"]["crouch_guidance"]
    del guide["takeoff_bonus"]
    del guide["prepare_window_s"]
    assert not resume_contract_matches(saved, current)
    assert resume_contract_matches(saved, current, crouch_guidance_update=True)
    bad = deepcopy(current)
    bad["jump_event_stage"]["landing_stable_s"] = 0.1
    assert not resume_contract_matches(saved, bad, crouch_guidance_update=True)
