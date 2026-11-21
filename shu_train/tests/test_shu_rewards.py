import math

import pytest
import torch

from shu_train.wheelleg.shu_rewards import AIR, CATCH, DRIVE, RELEASE, RISE, air_wheel_height_reward, shu_reward_terms

_DT = 0.01


def inputs(n, dtype=torch.float64):
    def zeros(*dims):
        return torch.zeros(n, *dims, dtype=dtype)

    state = {key: zeros() for key in ("yaw", "heading_ref", "vx_cmd", "wz_cmd", "height_error", "height_target_rate")}
    state.update({key: zeros(3) for key in ("velocity_w", "angular_velocity", "gravity")})
    state.update({key: zeros(2) for key in ("wheel_x_b", "wheel_heading_x", "wheel_rim_speed")})
    for key in (
        "joint_pos",
        "joint_vel",
        "previous_joint_vel",
        "torque",
        "action",
        "previous_action",
        "previous_previous_action",
    ):
        state[key] = zeros(6)
    for key in (
        "vx_active",
        "wz_active",
        "heading_active",
        "fork_threshold_enabled",
        "leg_or_guide_contact",
        "other_undesired_contact",
    ):
        state[key] = torch.zeros(n, dtype=torch.bool)
    state["gravity"][:, 2] = -1
    # Synthetic tuning and symmetric hard limits are fixtures, not vehicle defaults.
    parameters = {
        "leg_lower_rad": torch.full((4,), -1.0, dtype=dtype),
        "leg_upper_rad": torch.full((4,), 1.0, dtype=dtype),
        "height_fraction": 0.8,
        "height_wide_weight": 2.0,
        "height_gate_shape": 2.0,
        "vx_tol_max": 0.4,
        "vx_tol_knee": 0.5,
        "wz_tol_max": 0.6,
        "wz_tol_knee": 1.0,
        "vx_error_sigma": 2.5,
        "wz_error_sigma": 1.0,
        "heading_kp": 2.0,
        "heading_max_wz": 0.3,
    }
    return state, parameters


def assert_rates(terms, **rates):
    for key, values in rates.items():
        expected = torch.as_tensor(values, dtype=terms[key].dtype) * _DT
        torch.testing.assert_close(terms[key], expected, rtol=1e-10, atol=1e-12, msg=key)


def test_air_wheel_height_uses_higher_wheel_cap_and_stops_on_first_touch():
    phase = torch.tensor([AIR, AIR, AIR, CATCH, DRIVE, RELEASE, RISE])
    z = torch.tensor([[-0.25, -0.4], [-0.4, -0.25], [-0.20, -0.40]] + [[-0.25, -0.40]] * 4)
    cmd = torch.tensor([0.20, 0.45, 0.20] + [0.20] * 4)
    got = air_wheel_height_reward(z, 0.05, cmd, 0.10, 0.30, phase, _DT)
    expect = torch.tensor([1, 1, math.exp(-(0.05**2) / 0.001), 0, 0, 0, 0]) * _DT
    torch.testing.assert_close(got, expect)


def test_phase_switches_and_release():
    state, p = inputs(5)
    state["vx_active"].fill_(True)
    state["vx_cmd"].fill_(0.4)
    state["velocity_w"][:] = torch.tensor([0.4, 0.0, 0.5], dtype=torch.float64)
    state["height_target_rate"].fill_(0.2)
    state["gravity"][:, :2] = torch.tensor([0.3, 0.04], dtype=torch.float64)
    state["angular_velocity"][:, 0] = 0.5
    state["wheel_x_b"][:, 0] = 0.1
    state["wheel_heading_x"].fill_(1e3)
    state["wheel_rim_speed"].fill_(1e3)
    state["action"][:, 2] = 1
    terms = shu_reward_terms(state, torch.tensor([DRIVE, AIR, CATCH, RISE, RELEASE]), p, _DT)
    assert_rates(
        terms,
        track_lin_vel=[1, 0, 0, 0, 0],
        track_height=[1, 0, 0, 0, 0],
        vertical_velocity=[-0.09, -0.25, -0.25, 0, 0],
        angular_xy=[-0.05, -0.05, -0.05, -0.05, 0],
        orientation=[-1, -0.16, -1, -0.6, 0],
        no_fork_square=[-0.25, 0, -0.25, -0.25, 0],
        air_wheel_center=[0, -4, 0, 0, 0],
        air_wheel_speed=[0, -6, 0, 0, 0],
    )
    assert all(term.shape == (5,) and term.dtype == torch.float64 for term in terms.values())
    assert all(term[-1] == 0 for term in terms.values())
    assert not (terms.keys() & {"termination", "landing_progress", "landing_outcome", "height_error", "wheel_power"})


@pytest.mark.parametrize(
    ("phase", "rates"),
    [
        (DRIVE, [0, -2, -2, -2]),
        (AIR, [0, 0, 0, 0]),
        (CATCH, [0, -2, -2, -2]),
        (RISE, [0, -1, -2, -2]),
        (RELEASE, [0, 0, 0, 0]),
    ],
)
def test_contact_collapse_and_phase_caps(phase, rates):
    state, p = inputs(4)
    state["leg_or_guide_contact"][1::2] = True
    state["other_undesired_contact"][2:] = True
    assert_rates(shu_reward_terms(state, torch.full((4,), phase), p, _DT), undesired_contact=rates)


def test_fork_squared_is_full_range_and_binary_follows_birth_after_handoff():
    state, p = inputs(9)
    state["wheel_x_b"][:, 0] = torch.tensor([0.01, -0.05, -0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1], dtype=torch.float64)
    state["wheel_x_b"][3, 1] = 0.1  # same displacement of both wheels is not a fork
    state["fork_threshold_enabled"][:4] = True
    phase = torch.tensor([DRIVE, DRIVE, DRIVE, DRIVE, CATCH, DRIVE, RISE, DRIVE, RELEASE])
    assert_rates(
        shu_reward_terms(state, phase, p, _DT),
        no_fork_square=[-0.0025, -0.0625, -0.25, 0, -0.25, -0.25, -0.25, -0.25, 0],
        no_fork=[0, 0, -1, 0, 0, 0, 0, 0, 0],
    )


def test_soft_limits_sum_real_leg_angle_excess_and_clip_only_once():
    state, p = inputs(4)
    p["leg_lower_rad"][1] = -2.0
    state["joint_pos"][:, 2::3] = 100.0  # wheel position never participates
    state["joint_pos"][0, :2] = torch.tensor([0.97, -1.955], dtype=torch.float64)  # exactly at the boundary
    state["joint_pos"][1, :2] = torch.tensor([0.98, -1.975], dtype=torch.float64)
    state["joint_pos"][2:, 4] = 2.1
    assert_rates(
        shu_reward_terms(state, torch.tensor([DRIVE, AIR, RISE, RELEASE]), p, _DT), leg_soft_limits=[0, -0.03, -1, 0]
    )


def test_smoothness_phase_weights_channels_and_dt():
    state, p = inputs(5)
    state["joint_vel"][:, :3] = torch.tensor([10.0, 0.0, 100.0])
    state["previous_joint_vel"][:] = state["joint_vel"]
    state["previous_joint_vel"][:, 2] -= 2.0  # acceleration penalty includes wheels
    state["action"][:, :3] = torch.tensor([1.0, 0.0, 2.0])
    state["previous_previous_action"][:, 5] = 1e3  # wheel second difference is ignored
    state["torque"][:, 5] = 10.0
    phase = torch.tensor([DRIVE, AIR, CATCH, RISE, RELEASE])
    terms = shu_reward_terms(state, phase, p, _DT)
    assert_rates(
        terms,
        leg_joint_vel=[-0.005, -0.002, -0.002, -0.005, 0],
        joint_acc=[-0.01, -0.004, -0.004, -0.01, 0],
        action_rate=[-0.05, -0.02, -0.02, -0.05, 0],
        action_smoothness_leg=[-0.05, -0.02, -0.02, -0.05, 0],
        joint_torque=[-0.01, -0.01, -0.01, -0.01, 0],
    )
    half_dt = shu_reward_terms(state, phase, p, _DT / 2)
    for key in terms.keys() - {"joint_acc"}:
        torch.testing.assert_close(half_dt[key], terms[key] / 2)
    torch.testing.assert_close(half_dt["joint_acc"], terms["joint_acc"] * 2)  # derivative uses dt as well
    state["action"].fill_(1e3)
    assert_rates(shu_reward_terms(state, phase, p, _DT), action_rate=[-1, -1, -1, -1, 0])


def test_height_annealing_and_gate_affect_positive_motion_only():
    state, p = inputs(7)
    state["vx_active"].fill_(True)
    state["wz_active"].fill_(True)
    state["vx_cmd"].fill_(0.2)
    state["wz_cmd"].fill_(0.3)
    state["height_error"][:] = torch.tensor([0.02, -0.02, 0.02, 0.05, -0.08, 0.11, 0], dtype=torch.float64)
    p["height_fraction"] = torch.tensor([0.5, 0.7, 0.8, 0.9, 0.8, 0.8, 0], dtype=torch.float64)
    terms = shu_reward_terms(state, torch.full((7,), DRIVE), p, _DT)
    t, w = (math.exp(-(0.02**2) / sigma) for sigma in (0.001, 0.025))
    gate_mid = (math.exp(-0.5) - math.exp(-2)) / (1 - math.exp(-2))
    vx_pos = math.exp(-(((0.5 + 0.2) / 0.4) ** 2))
    wz_pos = math.exp(-(((1.0 + 0.3) / 0.6) ** 2))
    assert_rates(
        terms,
        track_height=[
            (t + 2 * w) / 3,
            (t + w) / 2,
            t,
            math.exp(-(0.05**2) / 0.001),
            math.exp(-(0.08**2) / 0.001),
            math.exp(-(0.11**2) / 0.001),
            1,
        ],
        track_lin_vel=[vx_pos] * 3 + [vx_pos * gate_mid, 0, 0, vx_pos],
        track_ang_vel=[wz_pos] * 3 + [wz_pos * gate_mid, 0, 0, wz_pos],
        lin_vel_error=[math.expm1(-(0.2**2) / 2.5)] * 7,
        ang_vel_error=[math.expm1(-(0.3**2))] * 7,
    )


def test_zero_axes_use_segment_masks_and_signed_tiny_commands():
    state, p = inputs(4, dtype=torch.float32)
    state["vx_active"][:2] = True
    state["vx_cmd"][:2] = -1e-9
    state["velocity_w"][:, 0] = torch.tensor([-1e-9, 1e-9, 0.3, 0.3])
    state["velocity_w"][:, 1] = 0.1
    state["wz_active"][2] = True
    state["wz_cmd"][2] = -1e-9
    state["angular_velocity"][2, 2] = -1e-9
    terms = shu_reward_terms(state, torch.full((4,), DRIVE), p, _DT)
    torch.testing.assert_close(terms["track_lin_vel"] / _DT, torch.tensor([1, math.exp(-(2.5**2)), 0, 0]))
    torch.testing.assert_close(terms["track_ang_vel"] / _DT, torch.tensor([0.0, 0.0, 1.0, 0.0]))
    torch.testing.assert_close(terms["stand_still"] / _DT, torch.tensor([0.0, 0.0, -0.4, -0.4]))
    assert torch.all(terms["ang_vel_error"] == 0)
    assert terms["lin_vel_error"][1] < 0
    assert "lateral_velocity" not in terms
    state["velocity_w"][:2, 1] = 1.0  # straight driving: sideways motion alone has no separate cost
    changed = shu_reward_terms(state, torch.full((4,), DRIVE), p, _DT)
    for name, value in terms.items():
        torch.testing.assert_close(changed[name][:2], value[:2])


def test_heading_wrap_clip_with_no_yaw_bonus():
    state, p = inputs(3)
    state["yaw"][:] = math.pi - 0.1
    state["heading_ref"][:] = -math.pi + 0.1
    state["heading_active"].fill_(True)
    state["vx_active"][:2] = True
    state["wz_active"][2] = True  # pure rotation ignores heading even if flag is stale
    state["wz_cmd"][2] = -0.3
    state["angular_velocity"][:, 2] = torch.tensor([0.3, 0, -0.3], dtype=torch.float64)
    state["velocity_w"][:, 0] = state["heading_ref"].cos()
    state["velocity_w"][:, 1] = state["heading_ref"].sin()
    state["vx_cmd"][:2] = math.cos(0.2)
    terms = shu_reward_terms(state, torch.full((3,), DRIVE), p, _DT)
    assert_rates(
        terms,
        track_lin_vel=[1, 1, 0],
        track_ang_vel=[0, 0, 1],
        ang_vel_error=[0, math.expm1(-0.09), 0],
        stand_still=[0, 0, -1],
    )


def test_rise_forces_zero_targets_and_halves_already_clipped_penalties():
    state, p = inputs(4)
    state["velocity_w"][:, 0] = torch.tensor([2.0, 2.0, 0.1, 0.1], dtype=torch.float64)
    state["velocity_w"][:, 1] = 0.2
    state["angular_velocity"][:, 2] = torch.tensor([100, 100, 0.4, 0.4], dtype=torch.float64)
    state["vx_active"][1::2] = state["wz_active"][1::2] = True  # stale even during takeover
    state["vx_cmd"][1::2] = 2.0
    state["wz_cmd"][1::2] = 0.4
    state["other_undesired_contact"].fill_(True)
    terms = shu_reward_terms(state, torch.tensor([DRIVE, RISE, DRIVE, RISE]), p, _DT)
    yaw_cost = math.expm1(-0.16)
    assert_rates(
        terms,
        stand_still=[-1, -0.5, -0.3, -0.15],
        ang_vel_error=[-1, -0.5, yaw_cost, yaw_cost / 2],
        track_lin_vel=[0] * 4,
        track_ang_vel=[0] * 4,
        track_height=[1, 0, 1, 0],
    )
    assert sum(terms.values())[0] < -2 * _DT  # no total clip or nonnegative clamp


def test_air_wheel_kernels_use_actual_heading_speed_and_each_wheel_offset():
    state, p = inputs(2)
    state["yaw"].fill_(math.pi / 2)
    state["velocity_w"][:, 1] = 2.0
    state["vx_cmd"].fill_(-2.0)  # deliberately opposite
    state["wheel_x_b"].fill_(99.0)  # air centering uses heading frame, not body X
    state["wheel_heading_x"][1, 0] = 0.2
    state["wheel_rim_speed"].fill_(2.0)
    state["wheel_rim_speed"][1, 0] = 3.0
    assert_rates(
        shu_reward_terms(state, torch.full((2,), AIR), p, _DT),
        air_wheel_center=[0, 2 * math.expm1(-2)],
        air_wheel_speed=[0, 6 * math.expm1(-0.5)],
    )
