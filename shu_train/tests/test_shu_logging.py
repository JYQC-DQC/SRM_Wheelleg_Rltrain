"""Real SHU events, raw CPU sensor samples, and the rollout/runner inference-mode boundary."""

import math

import pytest
import torch

from shu_train.wheelleg.shu_landing import ShuLanding
from shu_train.wheelleg.shu_logging import ShuLandingLog


class Run:
    def __init__(self, air, preset, band):
        n = len(band)
        self.band = torch.tensor(band)
        cfg = dict(
            contact_force_n=3.0,
            wheel_contact_force_n=2.0,
            support_force_n=20.0,
            termination_force_n=4.0,
            termination_tilt_rad=0.7,
            termination_duration_s=0.4,
            termination_decay_s=2.0,
            release_s=0.01,
        )
        self.event = ShuLanding(n, [1, 2], [3], [], [0, 3], [0, 3], 4, cfg, "cpu")
        self.tick = 0
        self.event.reset(torch.arange(n), torch.tensor(air), torch.tensor(preset), self.tick)
        self.force = torch.zeros(n, 4, 3)
        self.vz = torch.zeros(n, 1)
        self.length = torch.full((n, 2), 0.3)
        self.spring = torch.full((n, 2), 0.02)
        self.angle = torch.full((n, 2), -0.4)
        self.state = dict(
            roll=torch.zeros(n),
            pitch=torch.zeros(n),
            angular_velocity=torch.zeros(n, 3),
            velocity_w=torch.zeros(n, 3),
            height_error=torch.zeros(n),
            position_xy_w=torch.zeros(n, 2),
        )
        self.physical, self.timeout, self.numerical = (torch.zeros(n, dtype=torch.bool) for _ in range(3))
        self.log = ShuLandingLog()

    def step(self, *, missed=()):
        e = self.event
        e.begin_step()
        for substep in range(5):
            self.tick += 1
            fresh = torch.ones_like(self.physical)
            if substep == 2:
                fresh[list(missed)] = False
            e.sample(
                self.tick,
                self.force,
                self.vz,
                self.length,
                self.angle,
                spring_compression_m=self.spring,
                fresh_mask=fresh,
            )
        e.update(self.tick, self.state, self.physical, self.timeout, self.numerical)
        self.log.add(e, self.band)


def test_take_outside_real_inference_mode_drains_only_totals_not_birth_deduplication():
    r = Run([True], [False], [3])
    log = r.log
    assert log.take() == {}
    r.physical.fill_(True)
    with torch.inference_mode():
        r.step()
        log.add(r.event, r.band)  # duplicate deciding pulse, as opposed to the next policy step
    got = log.take()  # runner.log runs outside the rollout inference context
    assert got["Landing/all/resolved_count"] == got["Landing/top_band/resolved_count"] == 1
    assert got["Landing/all/left/event_peak_n/valid_count"] == 0
    assert got["Landing/all/left/event_peak_n/missing_count"] == 1
    assert "Landing/all/left/event_peak_n/mean" not in got
    assert log.take() == {}
    log.add(r.event, r.band)  # still the same pulse, even across take() and context change
    assert log.take() == {}
    r.event.reset(torch.tensor([0]), torch.tensor([True]), torch.tensor([False]), r.tick)
    r.band.fill_(1)
    r.step()
    got = log.take()
    assert got["Landing/all/resolved_count"] == 1 and not any("top_band" in k for k in got)


def test_air_event_weighting_true_top_band_clean_vs_light_and_missing_channel_denominators():
    # Top clean catch; lower band light-brush catch; top hard guide; simultaneous hard body and guide;
    # pre-touch physical failure; pure truncation; numerical anomaly; ordinary drive.
    r = Run([True] * 7 + [False], [False] * 8, [3, 0, 3, 1, 2, 3, 3, -1])
    r.vz[:, 0] = -0.6
    r.vz[2:4, 0] = -2
    r.step()
    assert r.log.take() == {}
    r.force[0, 1:, 2] = torch.tensor([30.0, 60.0, 0.0])
    r.force[1, 1:, 2] = torch.tensor([40.0, 50.0, 8.0])
    r.force[2, 1:, 2] = torch.tensor([90.0, 0.0, 8.0])
    r.force[3, 0, 2] = r.force[3, 3, 2] = 10
    r.physical[4] = True
    r.timeout[5] = True
    r.numerical[6] = True
    r.spring[:] = torch.tensor([0.04, 0.06])
    r.spring[0, 1] = torch.nan
    r.length[:] = torch.tensor([0.25, 0.28])
    r.step()
    r.physical.zero_()
    r.timeout.zero_()
    r.numerical.zero_()
    r.force[1, 3, 2] = 0.0
    for _ in range(50):
        r.step()
    got = r.log.take()
    a = "Landing/all/"
    top = "Landing/top_band/"
    assert all(type(v) in (float, int) and math.isfinite(v) for v in got.values())
    assert got[a + "ended_count"] == 7 and got[a + "resolved_count"] == 5
    assert got[a + "allow_light_catch_rate"] == pytest.approx(2 / 5) and got[a + "clean_rate"] == pytest.approx(2 / 5)
    assert (
        got[a + "hard_rate"] == pytest.approx(2 / 5)
        and got[a + "hard_guide_count"] == 2
        and got[a + "body_collision_count"] == 1
    )
    assert got[a + "truncated_count"] == got[a + "numerical_count"] == 1
    assert (
        got[top + "ended_count"] == 4
        and got[top + "resolved_count"] == 2
        and got[top + "allow_light_catch_rate"] == 0.5
    )
    assert got[a + "left/first_peak_n/mean"] == pytest.approx((30 + 40 + 90) / 3)
    assert got[a + "left/event_peak_n/max"] == 90
    assert got[a + "right/first_peak_n/valid_count"] == 2 and got[a + "right/first_peak_n/missing_count"] == 3
    assert got[a + "first_touch_gap_s/valid_count"] == 2 and got[a + "first_touch_gap_s/mean"] == 0
    assert got[a + "guide_peak_speed_m_s/mean"] == pytest.approx((0.6 + 2 + 2) / 3)
    assert got[a + "right/spring_peak_compression_m/missing_count"] == 2
    assert got[a + "left/leg_compression_m/max"] == pytest.approx(0.05) and got[
        a + "right/spring_compression_stroke_m/max"
    ] == pytest.approx(0.04)
    assert got[a + "left/touch_leg_angle_rad/max"] == pytest.approx(
        -0.4
    )  # invalid or non-event rows cannot force max to zero
    assert got[a + "catch_time_s/valid_count"] == 2 and got[a + "confirm_mean_rad/mean"] == 0
    assert not any(k.startswith("Rise/") for k in got)
    r.step()
    assert r.log.take() == {}  # late handoffs or latched hard flags must not reopen an observation


def test_first_patch_missing_due_to_sensor_gap_not_used_as_zero_or_as_whole_event_peak():
    r = Run([True], [False], [3])
    r.step()
    r.force[:, 1, 2] = 30
    r.physical.fill_(True)
    r.step(missed=(0,))
    got = r.log.take()
    a = "Landing/all/left/"
    for name in ("first_peak_n", "first_impulse_ns"):
        assert (
            got[a + name + "/valid_count"] == 0
            and got[a + name + "/missing_count"] == 1
            and a + name + "/max" not in got
        )
    assert got[a + "event_peak_n/max"] == 30 and got[a + "event_peak_n/valid_count"] == 1


def test_rise_success_timeout_physical_release_and_drift_are_not_air_denominators():
    r = Run([False] * 5, [True] * 4 + [False], [-1] * 5)
    r.physical[2] = True
    r.timeout[3] = True
    r.step()
    r.physical.zero_()
    r.timeout.zero_()
    r.force[0, 1:3, 2] = 30
    r.state["position_xy_w"][0, :] = torch.tensor([0.3, 0.4])
    r.state["position_xy_w"][1, 1] = 0.8
    for _ in range(500):
        r.step()
    got = r.log.take()
    g = "Rise/all/"
    assert not any(k.startswith("Landing/") for k in got)
    assert (
        got[g + "ended_count"] == 4
        and got[g + "resolved_count"] == 3
        and got[g + "success_rate"] == pytest.approx(1 / 3)
    )
    assert got[g + "physical_failure_count"] == got[g + "rise_timeout_count"] == got[g + "truncated_count"] == 1
    assert got[g + "rise_success_time_s/mean"] == pytest.approx(0.5)
    assert (
        got[g + "rise_failure_time_s/mean"] == pytest.approx(5.0) and got[g + "rise_failure_time_s/missing_count"] == 1
    )
    assert got[g + "rise_max_drift_m/max"] == pytest.approx(0.8) and got[g + "rise_max_drift_m/mean"] == pytest.approx(
        0.65
    )
    assert got[g + "rise_max_drift_m/valid_count"] == 2 and got[g + "rise_max_drift_m/missing_count"] == 1
