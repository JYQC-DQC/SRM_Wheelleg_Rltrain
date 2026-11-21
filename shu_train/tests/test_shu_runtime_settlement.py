"""Exercise P1 settlement through the Isaac adapter with scripted CPU sensors."""

import test_shu_runtime as transport
import torch

from shu_train.wheelleg.shu_rewards import DRIVE, RISE

runtime = transport.runtime


def test_numeric_fault_on_last_flat_tick_is_only_an_interruption(runtime):
    e = transport.make_runtime(runtime, "p1-flat")
    transport.reset(e, 32)
    index = int((e.shu.event.phase == DRIVE).nonzero()[0])
    cmd, flat = e.commands, e.shu.flat
    cmd.remaining.fill_(2)
    cmd.remaining[index] = 1
    cmd._issued[index] = torch.tensor([0.0, 0.0, e._measure()["base_height"][index]])
    actions = torch.zeros_like(e.raw_action)
    actions[index, 0] = torch.nan
    before = flat.fraction.clone()
    e._pre_physics_step(actions)
    e._sim_step_counter += transport.SUBSTEPS
    terminated, timeout = e._get_dones()
    assert terminated[index] and not timeout[index]
    assert flat.interruptions.sum() == 1 and not flat.completed.any() and not flat.falls.any()
    torch.testing.assert_close(flat.fraction, before)


def test_rise_confirmation_pays_last_rise_progress_then_switches_next_action(runtime):
    e = transport.make_runtime(runtime, "p1-flat")
    transport.reset(e, 32)
    event = e.shu.event
    preset = event.preset_birth.clone()
    assert preset.any()
    event.phase[preset] = RISE
    event.takeover_tick[preset] = e._sim_step_counter
    event.held_steps[preset] = event._hold_steps - 1
    e.robot.root[preset, 2] = e.terrain.env_origins[preset, 2] + e.commands.height[preset, 0]
    e.robot.root[preset, 3] = 1
    e.robot.root[preset, 4:] = 0
    e.robot.refresh()
    e.shu.observe_commands(torch.zeros(e.num_envs))
    support = torch.ones(e.num_envs, dtype=torch.bool)
    transport.interval(e, support)
    assert event.rise_succeeded[preset].all() and (event.phase[preset] == DRIVE).all()
    assert (e.reward_sums["rise_progress"][preset] > 0).all()
    assert not e.reward_sums["track_height"][preset].any()
    transport.interval(e, support)
    assert (e.reward_sums["track_height"][preset] > 0).all()


def test_unknown_first_guide_touch_returns_truncation(runtime):
    flat = transport.make_runtime(runtime, "p1-flat")
    flat.shu.flat.fraction.fill_(1)
    e = transport.make_runtime(runtime, "p1-landing", flat.shu.commands.transfer_metadata())
    transport.reset(e, 17)
    event = e.shu.event
    index = int(event.air_birth.nonzero()[0])
    e._pre_physics_step(torch.zeros_like(e.raw_action))
    e._sim_step_counter += 1
    e.contact.data.net_forces_w[index, event.guides[0], 2] = 20
    e._record_contacts(e._sim_step_counter)
    e._sim_step_counter += transport.SUBSTEPS - 1
    terminated, timeout = e._get_dones()
    assert not terminated[index] and timeout[index]
    assert event.unknown_guide[index] and event.truncated[index]
    assert not event.resolved[index] and e.shu.drop.events == 0
    e._get_rewards()
    assert e.shu.log.take()["Landing/all/unknown_guide_count"] == 1


def test_p1_driving_error_does_not_charge_oblique_entry_pitch_or_vertical_motion(runtime):
    from math import cos, radians, sin

    e = transport.make_runtime(runtime, "p1-flat")
    transport.reset(e, 32)
    yaw, pitch = radians(25), radians(18)
    cy, sy, cp, sp = cos(yaw / 2), sin(yaw / 2), cos(pitch / 2), sin(pitch / 2)
    e.robot.root[:, 3:7] = torch.tensor([cy * cp, -sy * sp, cy * sp, sy * cp])
    for cmd in (-1.0, 1.0):
        e.commands.value[:, 0] = cmd
        e.robot.root[:, 7:10] = torch.tensor([cmd * cos(yaw), cmd * sin(yaw), 2.0])
        e.robot.refresh()
        s = e._measure()
        torch.testing.assert_close(s["linear_error"], torch.zeros_like(s["linear_error"]), atol=1e-6, rtol=0)
        assert (s["velocity"][:, 0] - cmd).abs().min() > 0.1  # independent body-vx diagnostic remains distinct
        e.robot.root[:, 7:9].neg_()
        e.robot.refresh()
        torch.testing.assert_close(e._measure()["linear_error"], torch.full_like(s["linear_error"], -2 * cmd))
