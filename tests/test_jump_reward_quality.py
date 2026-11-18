from math import exp
from types import SimpleNamespace

import torch

from wheelleg.rewards import compute_rewards, jump_apex, jump_settle_response, jump_takeoff_response


def test_adaptive_lr_limit_applies_to_each_optimizer_step_and_scheduler_feedback():
    from wheelleg.adaptive_lr import install_adaptive_lr_limit

    param = torch.nn.Parameter(torch.ones(1))
    alg = SimpleNamespace(learning_rate=1e-4, optimizer=torch.optim.Adam([param], lr=1e-4))
    install_adaptive_lr_limit(alg, 1e-3, 1.2)
    for _ in range(30):
        previous = alg.learning_rate
        alg.learning_rate *= 1.5  # Proposal from rsl_rl when observed KL is small.
        alg.optimizer.param_groups[0]["lr"] = alg.learning_rate
        alg.optimizer.step()
        assert alg.optimizer.param_groups[0]["lr"] == alg.learning_rate == min(previous * 1.2, 1e-3)
    assert alg.iteration_peak_lr == 1e-3
    alg.learning_rate /= 1.5
    alg.optimizer.step()
    assert alg.optimizer.param_groups[0]["lr"] == 1e-3 / 1.5


def test_apex_combines_smooth_height_score_with_physical_cap_and_pose():
    event = SimpleNamespace(
        settings=dict(height_tolerance_m=0.01, height_is_minimum=True, apex_sigma=0.0025),
        height=torch.tensor([0.04, 0.04, 0.25, 0.04, 0.04, 0.04]),
        scored_height=torch.tensor([0.0, 0.015, 0.20, 0.05, 0.05, 0.05]),
        landing_pulse=torch.tensor([True, True, True, True, True, False]),
        invalid=torch.tensor([False, False, False, False, True, False]),
        failure_paid=torch.zeros(6, dtype=torch.bool),
    )
    state = {"jump": event}
    old_score = torch.tensor([exp(-0.36), exp(-0.09), exp(-0.64), 1.0, 0.0, 0.0])
    torch.testing.assert_close(jump_apex(state, {}), old_score)

    event.settings["body_wheel_jump"] = {"settle_response_scale_s": 0.6}
    event.apex_pose_quality = torch.tensor([1.0, 0.6, 1.0, 0.4, 1.0, 1.0])
    torch.testing.assert_close(jump_apex(state, {}), torch.tensor([0.0, 0.3, exp(-0.64), 0.4, 0.0, 0.0]))


def test_settle_bonus_is_for_clean_landing_independent_of_height_and_takeoff_speed():
    # The first three attempts succeed with progressively longer recoveries. The remaining attempts
    # miss the combined target, moving speed, clean landing, failure latch, or settlement pulse.
    event = SimpleNamespace(
        settings=dict(landing_stable_s=0.8, body_wheel_jump={"settle_response_scale_s": 1.4}),
        clearance_training={"takeoff_response_scale_s": 0.6},
        height=torch.full((8,), 0.04),
        target_reached=torch.tensor([True, True, True, False, True, True, True, True]),
        took_off=torch.ones(8, dtype=torch.bool),
        landing_pulse=torch.tensor([True, True, True, True, True, True, True, False]),
        first_touch=torch.ones(8, dtype=torch.bool),
        invalid=torch.tensor([False, False, False, False, False, True, False, False]),
        failure_paid=torch.tensor([False, False, False, False, False, False, True, False]),
        takeoff_latency_s=torch.full((8,), 0.2),
        time_since_first_touch=lambda: torch.tensor([0.80, 1.20, 2.00, 0.80, 0.80, 0.80, 0.80, 2.0]),
    )
    state = {"jump": event, "jump_vx_qualified": torch.tensor([True, True, True, True, False, True, True, True])}
    torch.testing.assert_close(
        jump_takeoff_response(state, {}), torch.tensor([exp(-((0.2 / 0.6) ** 2))] * 3 + [0.0] * 5)
    )

    weight = 0.35
    expected = weight * torch.tensor([exp(-((t / 1.4) ** 2)) for t in (0.80, 1.20, 2.00, 0.80, 0.80)] + [0.0] * 3)
    # Event rewards pay their full configured amount, independent of dt or the continuous-term clip.
    payout = compute_rewards(state, {}, {"jump_settle_response": weight}, 0.01, 0.001)
    torch.testing.assert_close(payout["jump_settle_response"], expected)
    event.landing_pulse.zero_()
    torch.testing.assert_close(jump_settle_response(state, {}), torch.zeros(8))


def test_legacy_stage_does_not_pay_settle_response():
    event = SimpleNamespace(settings={}, height=torch.tensor([0.04]))
    torch.testing.assert_close(jump_settle_response({"jump": event}, {}), torch.zeros(1))


def test_opt_in_can_disable_extra_air_leg_smoothness_without_disabling_action_rate():
    state = {"action": torch.ones(1, 6), "previous_action": torch.zeros(1, 6)}
    weights = {"jump_air_leg_smoothness": 0.0, "action_rate": -0.01}
    terms = compute_rewards(state, {}, weights, 0.01, 2.5)
    assert set(terms) == {"action_rate"}
    torch.testing.assert_close(terms["action_rate"], torch.tensor([-0.0006]))
