from pathlib import Path

import pytest
import torch
import yaml

from wheelleg.jump import JumpEvent, TunnelTraversal, jump_height_error, tunnel_landing
from wheelleg.rewards import jump_apex


@pytest.fixture
def jump():
    config = yaml.safe_load(
        (Path(__file__).resolve().parents[1] / "config/reference/scut_p3.yaml").read_text(encoding="utf-8")
    )
    settings = dict(config["stages"]["tunnel"], landing_stable_s=0.03)
    event = JumpEvent(settings, 1, "cpu")
    event.reset(torch.tensor([0]))
    event.trigger(
        torch.tensor([3.0]),
        torch.tensor([0.3]),
        torch.tensor([True]),
        torch.tensor([0.04]),
        require_trigger_time=False,
    )
    return event, config["training"]["air_rewards"]


def update(event, *, z=0.35, vz=0.4, clearance=0.03, contact=False, stable=False, hit=False, failed=False, dt=0.01):
    event.update(
        dt,
        torch.tensor([3.0]),
        torch.tensor([z]),
        torch.tensor([vz]),
        torch.tensor([[contact, contact]]),
        torch.tensor([stable]),
        torch.tensor([True]),
        torch.tensor([hit]),
        wheel_clearance=torch.full((1, 2), clearance),
        failed=torch.tensor([failed]),
    )


def prepare_takeoff(event):
    update(event, dt=0.25, z=0.3, vz=0, clearance=0, contact=True)
    for z in (0.33, 0.34, 0.35):
        update(event, z=z)
    assert event.took_off.item()
    assert event.features().shape == (1, 16)


@pytest.mark.parametrize("clearance,vz", [(0.03, 0.0), (0.0, 0.4)])
def test_no_fake_takeoff_or_apex(jump, clearance, vz):
    event, _ = jump
    update(event, dt=0.25, contact=True, z=0.3, clearance=0)
    for _ in range(5):
        update(event, clearance=clearance, vz=vz)
    assert not event.took_off.item()
    assert jump_apex({"jump": event}, {}).item() == 0


def test_single_contact_dropout_does_not_confirm_takeoff(jump):
    event, _ = jump
    update(event, dt=0.25, contact=True, z=0.3, clearance=0)
    update(event)
    update(event, contact=True, clearance=0)
    assert not event.took_off.item()
    assert event.takeoff_time.item() == 0


def test_success_bonuses_wait_for_settlement_and_pay_only_once(jump):
    event, parameters = jump
    prepare_takeoff(event)
    zeros = torch.zeros(1, 2)
    assert event.sample_air_quality(zeros, zeros, parameters, 0.01).sum().item() == 0
    update(event, vz=-0.1)
    assert jump_apex({"jump": event}, {}).item() == 0
    event.sample_air_quality(zeros, zeros, parameters, 0.01)
    for _ in range(2):
        update(event, z=0.3, vz=0, clearance=0, contact=True, stable=True)
        assert not event.landing_pulse.item()
        assert jump_apex({"jump": event}, {}).item() == 0
    update(event, z=0.3, vz=0, clearance=0, contact=True, stable=True)
    assert event.landing_pulse.item()
    assert jump_apex({"jump": event}, {}).item() == pytest.approx(1.0)
    score = event.sample_air_quality(zeros, zeros, parameters, 0.01)
    assert score.tolist() == [[1.0, 1.0]]
    weights = torch.tensor([parameters["wheel_torque"], parameters["wheel_center"]])
    # Quality can be perfect while the current policy deliberately disables these old airborne bounties.
    assert weights.tolist() == [0.0, 0.0]
    assert (score * weights).sum().item() == 0
    assert event.sample_air_quality(zeros, zeros, parameters, 0.01).sum().item() == 0
    for _ in range(5):
        update(event, z=0.3, vz=0, clearance=0, contact=True, stable=True)
        assert event.sample_air_quality(zeros, zeros, parameters, 0.01).sum().item() == 0
        assert jump_apex({"jump": event}, {}).item() == 0
        assert not event.failure_pulse.item()


def test_longer_airtime_cannot_increase_success_bonus(jump):
    event, parameters = jump
    prepare_takeoff(event)
    zeros = torch.zeros(1, 2)
    for _ in range(20):
        update(event, vz=0.0)
        assert event.sample_air_quality(zeros, zeros, parameters, 0.01).sum().item() == 0
    for _ in range(3):
        update(event, z=0.3, vz=0, clearance=0, contact=True, stable=True)
    assert event.sample_air_quality(zeros, zeros, parameters, 0.01).sum().item() == pytest.approx(2)


@pytest.mark.parametrize("reason", ["contact", "physical", "expiry"])
def test_event_failure_is_once_and_does_not_pay_success_bonus(jump, reason):
    event, parameters = jump
    prepare_takeoff(event)
    update(event, hit=reason == "contact", failed=reason == "physical", dt=2.0 if reason == "expiry" else 0.01)
    assert event.failure_pulse.item()
    assert not event.active.item()
    zeros = torch.zeros(1, 2)
    assert event.sample_air_quality(zeros, zeros, parameters, 0.01).sum().item() == 0
    assert jump_apex({"jump": event}, {}).item() == 0
    update(event)
    assert not event.failure_pulse.item()


def test_height_tolerance_is_asymmetric_and_large_overshoot_cannot_succeed(jump):
    event, _ = jump
    actual = torch.tensor([0.029, 0.030, 0.040, 0.070, 0.071])
    error = jump_height_error(actual, torch.full_like(actual, 0.04), event.settings)
    torch.testing.assert_close(error, torch.tensor([0.001, 0, 0, 0, 0.001]))
    prepare_takeoff(event)
    update(event, z=0.5, vz=-0.1)
    assert jump_apex({"jump": event}, {}).item() < 0.01
    for _ in range(5):
        update(event, z=0.3, vz=0, clearance=0, contact=True, stable=True)
    assert not event.landing_paid.item()


def test_timeout_at_apex_cannot_collect_apex_reward(jump):
    event, _ = jump
    prepare_takeoff(event)
    update(event, dt=2.0, vz=-0.1)
    assert event.failure_pulse.item()
    assert jump_apex({"jump": event}, {}).item() == 0


def test_pending_failure_and_no_jump_time_limit_are_distinct(jump):
    event, _ = jump
    event.reset(torch.tensor([0]))
    event.fail_pending(torch.tensor([True]))
    assert event.failure_pulse.item()
    assert event.remaining.item() == 0
    update(event, contact=True, clearance=0)
    event.fail_pending(torch.tensor([True]))
    assert not event.failure_pulse.item()
    event.reset(torch.tensor([0]))
    event.remaining.zero_()
    event.fail_pending(torch.tensor([True]))
    assert not event.failure_pulse.item()


def path_step(path, x, *, y=0, height=0.4, flight=True):
    wheels = torch.tensor([[[x, y - 0.1, height], [x, y + 0.1, height]]])
    bodies = torch.tensor([[[x, y, max(height, 0.3)]]])
    path.update(
        wheels,
        0.06,
        bodies,
        torch.tensor([1.0]),
        torch.tensor([1.35]),
        torch.tensor([0.27]),
        torch.tensor([0.0]),
        0.8,
        0.05,
        0.03,
        torch.tensor([flight]),
        torch.tensor([True]),
    )
    return wheels, bodies


def test_corridor_requires_real_overflight_and_both_faces():
    path = TunnelTraversal(1, "cpu")
    path_step(path, 0.0, height=0.06, flight=False)
    path_step(path, 0.99)
    assert path.entered.item()
    assert not path.cleared.item()
    path_step(path, 1.2)
    wheels, bodies = path_step(path, 1.5, height=0.06, flight=False)
    assert path.cleared.item()
    assert not path.invalid.item()
    assert tunnel_landing(
        wheels, 0.06, bodies, torch.tensor([1.35]), torch.tensor([0.0]), 0.05, 0.03, torch.tensor([0.0]), 0.8
    ).item()
    path.reset(torch.tensor([0]))
    assert not path.features().any()


@pytest.mark.parametrize("mode", ["side", "under", "teleport"])
def test_tunnel_bypass_stays_invalid(mode):
    path = TunnelTraversal(1, "cpu")
    if mode != "teleport":
        path_step(path, 0.0, height=0.06, flight=False)
    if mode == "side":
        path_step(path, 0.99, y=1.0)
    elif mode == "under":
        path_step(path, 0.99, height=0.06, flight=False)
    else:
        path_step(path, 2.0)
    assert path.invalid.item()
    path_step(path, 1.5)
    assert not path.cleared.item()
    wheels = torch.tensor([[[1.5, 10.0, 0.06], [1.5, 10.2, 0.06]]])
    bodies = torch.tensor([[[1.5, 10.0, 0.3]]])
    assert not tunnel_landing(
        wheels, 0.06, bodies, torch.tensor([1.35]), torch.tensor([0.0]), 0.05, 0.03, torch.tensor([0.0]), 0.8
    ).item()
