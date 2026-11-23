from copy import deepcopy
from pathlib import Path

import pytest
import torch
import yaml

from wheelleg.jump import JumpEvent
from wheelleg.landing_guidance import LandingGuidance
from wheelleg.multi_actor import resume_contract_matches
from wheelleg.rewards import jump_reward_weight


def stage():
    return yaml.safe_load(Path("config/reference/scut_p3_multi_actor.yaml").read_text(encoding="utf-8"))["stages"][
        "jump"
    ]


def test_constant_deceleration_reference_and_first_arrest_are_not_retroactive():
    guide = LandingGuidance(stage()["clearance_jump"]["landing_guidance"], 1, "cpu")
    guide.begin(torch.tensor([0]), torch.full((1, 2), 0.20))
    active = torch.tensor([True])
    contact = torch.ones((1, 2), dtype=torch.bool)

    def update(length, vz):
        guide.update(
            0.01, active, active, active, contact, torch.full((1, 2), length), torch.tensor([vz]), torch.tensor([-2.0])
        )

    update(0.28, -2.0)
    assert guide.path_cost.item() == pytest.approx(0, abs=1e-7)
    update(0.22, -1.0)
    assert guide.path_cost.item() == pytest.approx(0, abs=1e-7)
    update(0.28, 0.0)  # Rigid arrest at long length cannot be repaired by squatting later.
    assert guide.stop_error.item() == pytest.approx(0.08)
    score = guide.stop_quality.clone()
    update(0.20, 0.0)
    assert torch.equal(score, guide.stop_quality) and score.item() < 0.001


def test_last_air_frames_not_maximum_and_normal_compression_is_good():
    cfg = stage()["clearance_jump"]["landing_guidance"]
    guide = LandingGuidance(cfg, 1, "cpu")
    guide.begin(torch.tensor([0]), torch.full((1, 2), 0.20))
    active = torch.tensor([True])
    air = torch.zeros((1, 2), dtype=torch.bool)
    for length in [0.28, 0.28, 0.28, 0.21, 0.21, 0.21]:
        guide.update(
            0.01, active, active, active, air, torch.full((1, 2), length), torch.tensor([-2.0]), torch.tensor([-2.0])
        )
    contact = ~air
    guide.update(
        0.01, active, active, active, contact, torch.full((1, 2), 0.28), torch.tensor([-2.0]), torch.tensor([-2.0])
    )
    assert guide.retained.item() < 0.4
    guide.update(
        0.01, active, active, active, contact, torch.full((1, 2), 0.20), torch.tensor([0.0]), torch.tensor([-2.0])
    )
    assert guide.stop_quality.item() == pytest.approx(1)
    guide.reset(torch.tensor([0]))
    assert not guide.touched.any() and not guide.stop_quality.any()


def test_launch_reference_depends_on_height_stroke_and_body_rise():
    settings = stage()
    event = JumpEvent(settings, 2, "cpu")
    event.height[:] = torch.tensor([0.04, 0.45])
    event.landing_guide.flat[:] = 0.21
    event.start_body_clearance[:] = 0.20
    v = event.references(torch.zeros(2), torch.zeros((2, 2)), 9.81)["takeoff_velocity"]
    assert v[0] < 2 < v[1]
    event.current_z[:] = 0.05
    higher = event.references(torch.zeros(2), torch.zeros((2, 2)), 9.81)["takeoff_velocity"]
    assert (higher <= v).all()


def test_migration_does_not_allow_other_stage_changes():
    settings = stage()
    old = deepcopy(settings)
    del old["clearance_jump"]["landing_guidance"]
    old["clearance_jump"]["reward_overrides"].update(jump_apex=2.0, jump_prepare=0.5, jump_landing=1.75)
    saved = dict(actor_bundle={"frozen": "hash"}, jump_event_stage=old)
    current = dict(actor_bundle={"frozen": "hash"}, jump_event_stage=settings)
    assert not resume_contract_matches(saved, current)
    assert resume_contract_matches(saved, current, landing_guidance_update=True)
    current["jump_event_stage"]["landing_stable_s"] = 0.1
    assert not resume_contract_matches(saved, current, landing_guidance_update=True)


def test_real_reward_path_separates_full_success_and_lazily_created_request_terms():
    import ast
    from types import SimpleNamespace

    source = Path("isaac/wheelleg_tasks/multi_actor.py").read_text(encoding="utf-8")
    cls = next(n for n in ast.parse(source).body if isinstance(n, ast.ClassDef))
    cls.body = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "_get_rewards"]

    class Base:
        def _get_rewards(self):
            self.reward_sums["base"] = torch.ones(2)
            return torch.ones(2)

    cls.bases = [ast.Name(id="Base", ctx=ast.Load())]
    namespace = {"Base": Base, "torch": torch, "jump_reward_weight": jump_reward_weight}
    exec(compile(ast.fix_missing_locations(ast.Module(body=[cls], type_ignores=[])), "reward", "exec"), namespace)
    env = namespace["MultiActorEnv"]()
    env.num_envs, env.device = 2, "cpu"
    env.step_dt = 0.01
    guide = LandingGuidance(stage()["clearance_jump"]["landing_guidance"], 2, "cpu")
    guide.retained[:] = guide.stop_quality[:] = 1
    guide.stopped[:] = guide.touched[:] = True
    env.jump = SimpleNamespace(
        settings=stage(),
        height=torch.tensor([0.04, 0.25]),
        landing_guide=guide,
        preload=None,
        landing_pulse=torch.ones(2, dtype=torch.bool),
        invalid=torch.zeros(2, dtype=torch.bool),
        failure_paid=torch.zeros(2, dtype=torch.bool),
        elapsed=torch.ones(2),
        first_touch=torch.ones(2, dtype=torch.bool),
        finished=torch.ones(2, dtype=torch.bool),
    )
    env.handoff_pulse = torch.ones(2, dtype=torch.bool)
    env.handoff_failed = torch.tensor([False, True])
    env.handoff_cost_pulse = torch.zeros(2, dtype=torch.bool)
    env.actor_bundle = {"handoff": {"failure_cost": 0.0}}
    env.state = {"body_clearance_m": torch.full((2,), 0.1), "wheel_force": torch.full((2, 2), 100.0)}
    env.reward_sums = {
        name: torch.zeros(2)
        for name in (
            "jump_buffer_path",
            "jump_buffer_clearance",
            "jump_retained_extension",
            "jump_stop_quality",
            "jump_full_success",
        )
    }
    env.request_terms = {name: torch.zeros(2) for name in env.reward_sums}
    env.iteration_request_terms = {name: torch.zeros(2) for name in env.reward_sums}
    env.specialist_return = torch.zeros(2)
    env.landing_force_peak = torch.zeros(2)
    env.landing_term_sums = torch.zeros((2, 5))
    env.landing_clearance_min = torch.full((2,), float("inf"))
    env.handoff_left = torch.zeros(2)
    env.iteration_handoff_cost_stats = torch.zeros(3)
    env.iteration_landing_stats = torch.zeros((2, 13))
    env.commands = SimpleNamespace(target=torch.zeros((2, 3)))
    env.extras = {"evaluation": {}}
    assert env._get_rewards().tolist() == pytest.approx([2.75, 1.25])
    assert env.request_terms["base"].tolist() == [1, 1]
