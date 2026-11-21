"""CPU-only SHU event and contact contracts. Body IDs deliberately differ from actuator order."""

import math

import pytest
import torch

from shu_train.wheelleg.shu_landing import AIR, CATCH, DRIVE, RELEASE, RISE, ShuLanding

# Synthetic sensor thresholds; these are not calibrations for SHU's chassis.
CFG = dict(
    contact_force_n=3.0,
    wheel_contact_force_n=2.0,
    support_force_n=20.0,
    termination_force_n=4.0,
    termination_tilt_rad=0.7,
    termination_duration_s=0.4,
    termination_decay_s=2.0,
    release_s=0.02,
)
WHEELS, GUIDES, LINKS, UNDESIRED = [4, 1], [5, 3], [2], [0, 2, 3, 5]
BASE, LINK = 0, 2


class Batch:
    def __init__(self, births=(AIR,), **settings):
        n = len(births)
        births = torch.tensor(births)
        self.event = ShuLanding(n, WHEELS, GUIDES, LINKS, UNDESIRED, UNDESIRED, 6, CFG | settings, "cpu")
        self.event.reset(torch.arange(n), births == AIR, births == RELEASE, 0)
        self.f = torch.zeros(n, 6, 3)
        self.guide_vz = torch.zeros(n, 2)
        self.legs = torch.full((n, 2), 0.3)
        self.angles = torch.zeros_like(self.legs)
        self.spring = torch.zeros_like(self.legs)
        self.tick = 0
        self.state = {k: torch.zeros(n) for k in ["roll", "pitch", "height_error"]}
        self.state.update(
            angular_velocity=torch.zeros(n, 3), velocity_w=torch.zeros(n, 3), position_xy_w=torch.zeros(n, 2)
        )
        self.physical, self.timeout, self.numerical = (torch.zeros(n, dtype=torch.bool) for _ in range(3))

    def sample(self, **kwargs):
        self.event.sample(
            self.tick, self.f, self.guide_vz, self.legs, self.angles, spring_compression_m=self.spring, **kwargs
        )

    def finish(self):
        self.event.update(self.tick, self.state, self.physical, self.timeout, self.numerical)

    def step(self, count=1):
        for _ in range(count):
            self.event.begin_step()
            for _ in range(5):
                self.tick += 1
                self.sample()
            self.finish()

    def support(self):
        self.f[:, WHEELS, 2] = 30


def test_first_touch_raw_norm_vs_vertical_support_phase_and_wheel_filter():
    b = Batch((AIR, RELEASE, DRIVE))
    e = b.event
    assert e.phase.tolist() == [AIR, RELEASE, DRIVE]
    b.f[0, WHEELS, 0] = 80  # lateral forces are contact, never vertical support
    b.step()
    assert e.phase.tolist() == [CATCH, RELEASE, DRIVE]
    assert not e.wheel_contact.any() and e.best[0] == 0
    b.f.zero_()
    b.support()
    b.step()
    assert e.phase.tolist() == [CATCH, RISE, DRIVE] and e.reward_phase[1] == RELEASE
    assert e.wheel_contact.all() and e.held_steps[0] == 1
    b.f.zero_()
    b.step()
    assert e.wheel_contact.all() and e.held_steps[0] == 0
    b.step()
    assert not e.wheel_contact.any() and e.touch_tick.tolist() == [1, -1, -1]
    assert e.reward_phase.tolist() == [CATCH, RISE, DRIVE]


def test_confirmation_budget_angle_mean_and_no_second_payout_or_flight():
    b = Batch()
    e = b.event
    b.state["height_error"].fill_(0.7)  # not a catch gate
    b.state["velocity_w"][:, 0] = -2.4  # neither stopping nor following the command is required
    b.support()
    b.state["roll"].fill_(math.radians(5))
    b.step()
    q = math.exp(-(0.5**2) / 3)
    assert e.best.item() == pytest.approx(q)
    assert e.event_terms["landing_progress"].item() == pytest.approx(0.75 * q)
    b.state["roll"].neg_()
    b.step(25)
    assert e.event_terms["landing_progress"] == 0 and not e.resolved
    b.state["roll"].zero_()
    b.step()
    assert e.event_terms["landing_progress"].item() == pytest.approx(0.75 * (1 - q))
    b.step(23)
    assert e.held_steps == 49 and not e.succeeded
    b.step()
    assert e.succeeded and e.handoff and e.phase == DRIVE and e.clean
    elapsed = (b.tick - 1) * 0.002
    assert e.catch_time_s.item() == pytest.approx(elapsed)
    assert e.confirm_mean_rad.item() == pytest.approx(math.radians(2.5))
    assert e.event_terms["landing_outcome"].item() == pytest.approx(1.5 * (0.7 * math.exp(-elapsed + 0.5) + 0.3 * 0.75))
    recorded = e.impact.first_impulse_ns.clone()
    b.f.zero_()
    b.step()
    b.f[:, BASE, 2] = 9
    b.step()
    assert e.phase == DRIVE and not e.resolved and not e.handoff and e.clean
    assert all((v == 0).all() for v in e.event_terms.values())
    torch.testing.assert_close(e.impact.first_impulse_ns, recorded)


def test_impact_edges_peak_impulse_rebound_and_physical_stroke_masks():
    b = Batch((AIR, AIR))
    e = b.event
    b.event.begin_step()
    b.tick = 1
    b.angles.fill_(0.61)
    b.spring.fill_(0.01)
    b.sample()
    # Stale reset tick and repeated sensor hook must not contribute another sample or overwrite pre-impact state.
    b.tick = 2
    b.f[:, WHEELS[0], 2] = 40
    b.legs[:, 0] = 0.28
    b.angles.zero_()
    b.spring[:, 0] = 0.02
    b.sample()
    b.f[:, WHEELS[0], 2] = 4000
    b.sample()
    b.tick = 3
    b.f[:, WHEELS[0], 2] = 60
    b.f[0, WHEELS[1], 2] = 25
    b.legs[:, 0] = 0.25
    b.spring[:, 0] = 0.06
    b.sample()
    b.tick = 4
    b.f[:, WHEELS[0], 2] = 0
    b.sample()
    b.tick = 5
    b.f[:, WHEELS[0], 2] = 90
    b.sample()
    b.finish()
    m = e.metrics()
    torch.testing.assert_close(m["first_peak_n"], torch.tensor([[60.0, 25.0], [60.0, 0.0]]))
    torch.testing.assert_close(m["event_peak_n"][:, 0], torch.full((2,), 90.0))
    torch.testing.assert_close(m["first_impulse_ns"], torch.tensor([[0.2, 0.15], [0.2, 0.0]]))
    assert m["first_touch_gap_s"][0].item() == pytest.approx(0.002) and m["first_touch_gap_s"][1].isnan()
    assert m["wheel_touched"].tolist() == [[True, True], [True, False]]
    assert m["leg_compression_m"][0, 0].item() == pytest.approx(0.05)
    assert m["spring_peak_compression_m"][0, 0].item() == pytest.approx(0.06)
    assert m["spring_compression_stroke_m"][0, 0].item() == pytest.approx(0.05)
    torch.testing.assert_close(m["touch_leg_length_m"], torch.full((2, 2), 0.3))
    torch.testing.assert_close(m["touch_leg_angle_rad"], torch.full((2, 2), 0.61))
    # Only one row is reset. Its next real tick is masked out by the environment's stale-sensor guard.
    e.reset(torch.tensor([0]), torch.tensor([True]), torch.tensor([False]), b.tick)
    b.sample()
    b.tick += 1
    b.sample(fresh_mask=torch.tensor([False, True]))
    assert e.touch_tick.tolist() == [-1, 2] and e.last_tick.tolist() == [5, 6]
    assert not e.impact.first_peak_n[0].any() and e.impact.first_tick[1, 0] == 2


def test_guide_edges_use_own_previous_world_speed_multi_hit_priority_and_unknown():
    b = Batch((AIR,) * 5)
    e = b.event
    b.guide_vz[:] = torch.tensor([[-0.3, -1.2], [-2.0, -0.1], [2.0, -1.5], [-3.0, -1.8], [-1.0, 0.0]])
    b.step()
    b.f[:, GUIDES, 2] = 12
    b.f[1, GUIDES[0], 2] = 0
    b.f[3, BASE, 1] = 10
    b.guide_vz.zero_()
    b.step()
    torch.testing.assert_close(
        e.event_terms["landing_guide_contact"], torch.tensor([-0.56, -0.7 * 0.1 / 1.5, 0.0, 0.0, -0.7 / 1.5])
    )
    assert e.resolved.tolist() == [False, False, True, True, False] and not e.succeeded.any()
    assert e.hard_guide.tolist() == [False, False, True, True, False] and e.body_collision.tolist() == [
        False,
        False,
        False,
        True,
        False,
    ]
    assert e.first_nonwheel_bodies[3, [BASE, *GUIDES]].all()
    assert not e.clean.any() and not e.physical_failure.any()
    b.step()
    assert not e.event_terms["landing_guide_contact"].any()
    b.f.zero_()
    b.support()
    b.step(50)
    assert e.succeeded.tolist() == [True, True, False, False, True] and e.handoff.all() and not e.clean.any()
    only = Batch()
    only.f[:, GUIDES[0], 2] = 50
    only.step()
    assert only.event.unknown_guide and not only.event.resolved and not only.event.succeeded
    assert only.event.guide_peak_speed_m_s.isnan() and not only.event.event_terms["landing_guide_contact"]


def test_failure_priority_vs_confirmation_and_pure_truncation_or_numerical():
    b = Batch((AIR,) * 6)
    e = b.event
    b.support()
    b.step(50)
    b.f[0, LINK, 0] = 8
    b.timeout[:3] = True
    b.physical[1] = True
    b.state["roll"][3] = float("nan")
    b.f[4, BASE, 2] = float("nan")
    b.step()
    assert e.resolved.tolist() == [True, True, False, False, False, True]
    assert e.succeeded.tolist() == [False, False, False, False, False, True]
    assert e.truncated.tolist() == [False, False, True, False, False, False]
    assert e.numerical_failure.tolist() == [False, False, False, True, True, False]
    assert e.event_terms["landing_outcome"][:5].tolist() == [-1.0, -1.0, 0.0, 0.0, 0.0]
    assert e.event_terms["landing_progress"][:5].eq(0).all()
    assert all(v.isfinite().all() for v in e.event_terms.values())
    assert e.clean.tolist() == [False, True, True, True, True, True]
    m = e.metrics()
    assert m["clean_count"] == 2 and m["resolved_count"] == 3 and m["success_count"] == 1
    assert m["clean_rate"].item() == pytest.approx(2 / 3)


def test_two_second_failure_no_physical_reset_late_handoff_no_new_rewards_or_deadline_before_touch():
    b = Batch((AIR, AIR))
    e = b.event
    b.f[0, WHEELS[1], 2] = 30
    b.step(200)
    assert not e.air_timeout.any() and e.touch_tick.tolist() == [1, -1]
    b.step()
    assert e.air_timeout.tolist() == [True, False] and e.resolved.tolist() == [True, False]
    assert e.event_terms["landing_outcome"].tolist() == [-1.0, 0.0] and not e.physical_failure.any()
    assert e.phase.tolist() == [CATCH, AIR] and not e.rise_timeout.any()
    b.f[0, WHEELS[0], 2] = 30
    b.step(50)
    assert e.handoff.tolist() == [True, False] and e.phase.tolist() == [DRIVE, AIR]
    assert not e.resolved.any() and not e.succeeded.any() and not e.event_terms["landing_progress"].any()
    assert not e.event_terms["landing_outcome"].any()
    b.timeout[1] = True
    b.step()
    assert e.truncated[1] and not e.resolved.any()


def test_ground_release_takeover_height_baseline_support_budget_and_handoff():
    b = Batch((RELEASE,))
    e = b.event
    b.f[:, LINK, 2] = 12
    b.state["height_error"].fill_(0.2)
    b.step(2)
    assert e.phase == RISE and e.reward_phase == RELEASE and e.takeover_tick == 10
    assert e.best.item() == pytest.approx(math.exp(-(0.2**2) / 0.025)) and not e.event_terms["rise_progress"]
    b.state["height_error"].fill_(0.1)
    b.state["position_xy_w"][:] = torch.tensor([0.3, 0.4])
    b.step()
    gain = 0.75 * (math.exp(-(0.1**2) / 0.025) - math.exp(-(0.2**2) / 0.025))
    assert e.event_terms["rise_progress"].item() == pytest.approx(gain) and e.rise_max_drift_m.item() == pytest.approx(
        0.5
    )
    b.state["height_error"].zero_()
    b.f.zero_()
    b.step()
    assert not e.event_terms["rise_progress"]
    b.f[:, GUIDES[0], 2] = 12
    b.step()
    assert e.event_terms["rise_progress"].item() == pytest.approx(0.75 * (1 - math.exp(-(0.1**2) / 0.025)))
    assert not e.held_steps and not e.hard_guide and e.fall_steps == 0
    b.state["height_error"].fill_(0.2)
    b.f.zero_()
    b.support()
    b.step(50)
    assert not e.handoff
    b.state["height_error"].fill_(0.05)
    b.step(50)
    assert e.rise_succeeded and e.handoff and not e.rise_failed and e.phase == DRIVE
    assert not e.resolved and all(v.eq(0).all() for v in e.event_terms.values())


def test_five_seconds_from_takeover_only_true_physics_or_numerical_protection_is_separate():
    b = Batch((RELEASE,) * 3)
    e = b.event
    b.step(2)
    b.step(499)
    assert not e.rise_timeout.any() and not e.physical_failure.any()
    b.physical[1] = True
    b.numerical[2] = True
    b.step()
    assert e.rise_timeout.tolist() == [True, False, False] and e.rise_failed.tolist() == [True, True, False]
    assert e.physical_failure.tolist() == [False, True, False] and e.numerical_failure.tolist() == [False, False, True]
    assert not e.truncated.any() and not e.resolved.any() and not e.event_terms["landing_outcome"].any()


def test_slow_leak_shared_mechanism_not_shared_exemption_and_release_has_independent_safety():
    b = Batch((RELEASE, RELEASE, DRIVE, DRIVE))
    e = b.event
    b.f[0, GUIDES[0], 2] = 8
    b.f[1, BASE, 2] = 8
    b.f[2, LINK, 2] = 8
    b.state["pitch"][3] = 0.8
    b.step(20)
    assert e.fall_steps.tolist() == [0, 18, 20, 20]
    f = b.f.clone()
    b.f.zero_()
    b.state["pitch"].zero_()
    b.step(5)
    torch.testing.assert_close(e.fall_steps, torch.tensor([0.0, 17.0, 19.0, 19.0]))
    b.f.copy_(f)
    b.state["pitch"][3] = 0.8
    b.step(21)
    assert e.physical_failure.tolist() == [False, False, True, True]
    b.step(2)
    assert e.physical_failure[1] and e.rise_failed[1] and not e.rise_timeout.any()
    x = Batch((RELEASE, RELEASE))
    x.physical[0] = True
    x.numerical[1] = True
    x.step()
    assert x.event.physical_failure[0] and x.event.numerical_failure[1] and not x.event.resolved.any()


def test_invalid_birth_is_not_in_curriculum_and_main_wheels_cannot_be_penalized():
    b = Batch()
    e = b.event
    e.reset(torch.tensor([0]), torch.tensor([True]), torch.tensor([False]), 0, birth_contact=torch.tensor([True]))
    b.f[:, BASE, 0] = 100
    b.step()
    assert e.invalid_birth and not e.resolved and not e.succeeded and not e.event_terms["landing_outcome"]
    with pytest.raises(ValueError, match="contact body lists"):
        ShuLanding(1, WHEELS, GUIDES, LINKS, UNDESIRED + [WHEELS[0]], UNDESIRED, 6, CFG, "cpu")


def test_confirmed_on_deadline_wins_but_first_confirmed_after_it_cannot_retroactively_succeed():
    b = Batch((AIR, AIR))
    e = b.event
    e.begin_step()
    for tick in range(1, 6):
        b.tick = tick
        if tick == 4:
            b.f[1, WHEELS[0], 2] = 30
        if tick == 5:
            b.f[0, WHEELS[0], 2] = 30
        b.sample()
    b.finish()
    b.step(150)
    b.support()
    b.step(50)
    assert (b.tick - e.touch_tick).tolist() == [1000, 1001]
    assert e.resolved.all() and e.succeeded.tolist() == [True, False]
    assert e.air_timeout.tolist() == [False, True] and e.handoff.all()
    assert e.event_terms["landing_outcome"][1].item() == -1


def test_reset_and_duplicate_callbacks_do_not_pay_twice_for_two_separate_guide_edges():
    b = Batch()
    e = b.event
    b.guide_vz.fill_(-0.3)
    b.step()
    e.begin_step()
    for j in range(5):
        b.tick += 1
        b.f[:, GUIDES, 1] = 9 if j in (0, 2) else 0
        b.sample()
        b.sample()
    b.finish()
    assert e.event_terms["landing_guide_contact"].item() == pytest.approx(2 * -0.7 * 0.3 / 1.5)
    assert e.leg_or_guide_contact and not e.other_undesired_contact and not e.clean
    assert not e.resolved and e.touch_tick == 6


def test_last_rise_tick_external_cut_does_not_turn_observed_confirmation_into_failure():
    b = Batch((RELEASE,) * 5)
    e = b.event
    b.step(2 + 450)
    b.f[:, WHEELS, 2] = 30
    b.f[1, WHEELS[1], 2] = 0  # genuine failure at five seconds, even if the episode clock also expires
    b.step(49)
    b.timeout[:3] = True
    b.physical[2] = True
    b.numerical[3] = True
    b.step()
    assert e.truncated.tolist() == [True, False, False, False, False]
    assert e.rise_timeout.tolist() == [False, True, False, False, False]
    assert e.physical_failure.tolist() == [False, False, True, False, False]
    assert e.rise_succeeded.tolist() == [False, False, False, False, True]
    assert e.rise_failed.tolist() == [False, True, True, False, False]
    assert e.metrics()["rise_time_s"][1].item() == pytest.approx(5.0)


def test_policy_endpoint_missing_is_not_current_support_or_the_5s_clock():
    b = Batch((RELEASE,))
    e = b.event
    b.state["height_error"].fill_(0.3)
    b.step(2)
    b.state["height_error"].zero_()
    e.begin_step()
    for j in range(5):
        b.tick += 1
        b.f[:, LINK, 2] = 8 if j == 3 else 0
        b.sample(fresh_mask=torch.tensor([j != 4]))
    b.finish()
    assert e.leg_or_guide_contact and not e.event_terms["rise_progress"]
    # Time of decision follows the policy's real physics tick, not the timestamp of the last contact reading.
    b.tick = e.takeover_tick.item() + 2500
    e.begin_step()
    b.finish()
    assert e.rise_timeout and not e.physical_failure and e.metrics()["rise_time_s"].item() == pytest.approx(5.0)


def test_single_substep_pulse_is_visible_to_wheel_filter_but_not_continuous_support():
    b = Batch()
    e = b.event
    e.begin_step()
    for j in range(5):
        b.tick += 1
        b.f[:, WHEELS[0], 2] = 30 if j == 1 else 0
        b.sample()
    b.finish()
    assert e.wheel_contact.tolist() == [[True, False]] and not e.held_steps and not e.best
    b.step()
    assert e.wheel_contact.tolist() == [[True, False]]
    b.step()
    assert not e.wheel_contact.any() and not e.resolved


def test_capture_only_adjacent_preimpact_readings_and_do_not_bridge_contact_patches_across_gap():
    b = Batch((AIR, AIR))
    e = b.event
    e.begin_step()
    b.tick = 1
    b.legs.fill_(0.40)
    b.angles.fill_(0.5)
    b.spring.fill_(0.02)
    b.sample()
    b.tick = 2
    b.f[1, WHEELS[0], 2] = 30
    b.sample(fresh_mask=torch.tensor([False, True]))
    b.tick = 3
    b.f[0, WHEELS[0], 2] = 40
    b.legs.fill_(0.30)
    b.spring.fill_(0.08)
    b.sample(fresh_mask=torch.tensor([True, False]))
    b.tick = 4
    b.f[1, WHEELS[0], 2] = 90
    b.sample()
    m = e.metrics()
    assert m["touch_leg_length_m"][0].isnan().all() and m["touch_leg_angle_rad"][0].isnan().all()
    assert m["leg_compression_m"][0].eq(0).all() and m["spring_compression_stroke_m"][0].eq(0).all()
    assert m["first_impulse_ns"][1, 0].isnan() and m["first_peak_n"][1, 0].isnan()
    assert m["event_peak_n"][1, 0] == 90 and m["wheel_touched"][1, 0]


def test_optional_diagnostic_missing_or_nonfinite_is_never_stale_or_infinite_or_an_event_input():
    b = Batch((AIR, AIR))
    e = b.event
    e.begin_step()
    b.tick = 1
    b.angles[:] = torch.tensor([[0.4, 0.5], [0.2, 0.3]])
    b.spring.fill_(0.02)
    b.sample()
    b.tick = 2
    e.sample(b.tick, b.f, b.guide_vz, b.legs)  # no optional sensors at this tick
    b.tick = 3
    b.f[0, WHEELS[0], 2] = 40
    b.angles[1, 0] = float("inf")
    b.spring[1, 0] = -float("inf")
    b.sample()
    b.tick = 4
    b.f[1, WHEELS[0], 2] = 50
    b.angles.fill_(0.3)
    b.spring.fill_(0.05)
    b.sample()
    b.tick = 5
    b.sample()
    b.finish()
    m = e.metrics()
    assert m["touch_leg_angle_rad"][0].isnan().all() and m["touch_leg_angle_rad"][1, 0].isnan()
    assert m["touch_leg_angle_rad"][1, 1].item() == pytest.approx(0.3)
    assert m["spring_compression_stroke_m"][1, 0] == 0 and not e.numerical_failure.any()
    b.f.zero_()
    b.support()
    b.step(50)
    assert e.succeeded.all() and e.clean.all()


def test_any_nonfinite_root_velocity_component_cannot_receive_an_event_result():
    b = Batch((AIR, AIR))
    e = b.event
    b.support()
    b.step(50)
    b.state["velocity_w"][0, 0] = torch.nan
    b.state["angular_velocity"][1, 2] = torch.inf
    b.step()
    assert e.numerical_failure.all() and not e.resolved.any() and not e.handoff.any()
    assert all(v.eq(0).all() for v in e.event_terms.values())
