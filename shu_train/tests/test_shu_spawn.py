"""CPU synthetic five-bar, no parameter in this fixture describes the SHU chassis."""

from dataclasses import replace
from math import pi

import pytest
import torch

from shu_train.wheelleg.shu_spawn import (
    AIR,
    LEG_JOINT_ORDER,
    ORDINARY,
    RECOVERY,
    SpawnConfig,
    five_bar_joint_angles,
    sample_spawn,
    sample_spawn_kinds,
)

CFG = SpawnConfig(
    ik_branch="symmetric_five_bar_v1",
    link_lengths_m=(0.12, 0.12, 0.2),
    angle_offsets_rad=(0.1, -0.2, 0.3, -0.4, 0.5, -0.6),
    hip_pivot_positions_b_m=((0.02, 0.11, -0.025), (0.02, -0.11, -0.025)),
    wheel_radius_m=0.04,
    min_root_height_m=0.14,
    spawn_clearance_m=0.01,
    ordinary_length_m=(0.12, 0.20),
    ordinary_angle_rad=(-0.4, 0.5),
    ordinary_tilt_rad=0.25,
    air_length_m=(0.11, 0.35),
    recovery_length_m=(0.13, 0.24),
    recovery_forward_leg_height_m=(-0.07, -0.02),
    recovery_rear_leg_height_m=(-0.02, 0.04),
    recovery_root_height_m=0.19,
    wheel_angle_rad=(-2, 2),
    wheel_speed_rad_s=(-5, 5),
    leg_speed_rad_s=(-1, 1),
)


def test_distribution_per_birth_and_no_flat_default():
    torch.manual_seed(783)
    k = sample_spawn_kinds("p1-landing", 30000, "cpu")
    assert torch.bincount(k).div(len(k)).tolist() == pytest.approx([0.2, 0.4, 0.4], abs=0.012)
    k = sample_spawn_kinds("p1-flat", 17000, "cpu", flat_recovery_probability=0.28)
    assert k.max() == RECOVERY and (k == RECOVERY).float().mean().item() == pytest.approx(0.28, abs=0.016)
    with pytest.raises(ValueError, match="flat_recovery_probability"):
        sample_spawn_kinds("p1-flat", 1, "cpu")


def test_analytic_branch_offsets_sign_and_interleaved_joint_order():
    # Equilateral triangle: d=l0=l1, hence half=knee=pi/3, close=2pi/3.
    L = torch.full((1, 2), 0.2, dtype=torch.float64)
    a = torch.tensor([[0.45, -0.32]], dtype=L.dtype)
    o = CFG.angle_offsets_rad
    q = five_bar_joint_angles(L, a, CFG.link_lengths_m, o).reshape(1, 6, 2)
    assert LEG_JOINT_ORDER[0:4] == ("left_front1", "right_front1", "left_rear1", "right_rear1")
    expected = torch.stack(
        (
            a + pi / 6 - o[0],
            a + 5 * pi / 6 - o[1],
            torch.full_like(a, o[2] - pi / 3),
            torch.full_like(a, o[3] - 2 * pi / 3),
            torch.full_like(a, o[4] - pi / 3),
            torch.full_like(a, pi / 3 - o[5]),
        ),
        dim=1,
    )
    torch.testing.assert_close(q, expected)
    for bad in (0, 0.4, 0.42):
        with pytest.raises(ValueError, match="singular|unreachable"):
            five_bar_joint_angles(torch.full_like(L, bad), a, CFG.link_lengths_m, o)


def test_recovery_signed_geometry_splits_fixed_root_and_residual_velocities():
    torch.manual_seed(199)
    n = 6000
    s = sample_spawn(torch.full((n,), RECOVERY), torch.zeros(n), CFG)
    assert (s.root_state[:, :2] == 0).all() and (s.root_state[:, 2] == CFG.recovery_root_height_m).all()
    assert (s.root_state[:, 3] == 1).all() and (s.root_state[:, 4:] == 0).all()
    forward = s.angle_rad < 0
    pair = (2 * forward[:, 0].long() + forward[:, 1]).long()
    assert torch.bincount(pair).div(n).tolist() == pytest.approx([4 / 9, 2 / 9, 2 / 9, 1 / 9], abs=0.022)
    h = s.angle_rad.cos() * s.length_m
    for mask, bounds in ((forward, CFG.recovery_forward_leg_height_m), (~forward, CFG.recovery_rear_leg_height_m)):
        assert h[mask].min() >= bounds[0] - 1e-6 and h[mask].max() <= bounds[1] + 1e-6
    q = s.leg_q
    qd = s.leg_qd
    torch.testing.assert_close(s.drive_q[:, [0, 1, 3, 4]], q[:, [0, 2, 1, 3]])
    torch.testing.assert_close(s.drive_qd[:, [0, 1, 3, 4]], qd[:, [0, 2, 1, 3]])
    assert ((s.drive_qd[:, [2, 5]].abs() <= 5) & (s.drive_qd[:, [2, 5]] != 0)).all()
    assert s.drive_q[:, [2, 5]].abs().max() <= 2


def test_passive_velocity_matches_finite_difference_of_ik():
    torch.manual_seed(73)
    s = sample_spawn(torch.full((31,), ORDINARY), torch.zeros(31, dtype=torch.float64), CFG)
    length, ang = s.length_m, s.angle_rad
    eps = 1e-6

    def ik(lengths, a):
        return five_bar_joint_angles(lengths, a, CFG.link_lengths_m, CFG.angle_offsets_rad).reshape(-1, 6, 2)

    jac_l = (ik(length + eps, ang) - ik(length - eps, ang)) / (2 * eps)
    jac_a = (ik(length, ang + eps) - ik(length, ang - eps)) / (2 * eps)
    qd = s.leg_qd.reshape(-1, 6, 2)
    rates = torch.linalg.solve(
        torch.stack((jac_l[:, :2], jac_a[:, :2]), dim=-1).transpose(1, 2), qd[:, :2].transpose(1, 2).unsqueeze(-1)
    ).squeeze(-1)
    torch.testing.assert_close(qd, jac_l * rates[:, None, :, 0] + jac_a * rates[:, None, :, 1], rtol=1e-8, atol=1e-8)


def test_air_root_clearance_rotated_both_wheels_world_velocity_and_ordinary_bounds():
    torch.manual_seed(199)
    k = torch.arange(4500) % 2
    k[k == 1] = AIR
    air = k == AIR
    off = torch.where(air, 0.123, 0.0)
    s = sample_spawn(k, off, CFG)
    q = s.root_state[:, 3:7]
    w, x, y, z = q.unbind(1)
    yaw = torch.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))
    lin = s.root_state[:, 7:10]
    vx = lin[:, 0] * yaw.cos() + lin[:, 1] * yaw.sin()
    vy = -lin[:, 0] * yaw.sin() + lin[:, 1] * yaw.cos()
    assert (lin[:, 2] == 0).all() and (lin[~air] == 0).all()
    for v, lim in ((vx[air], 2.5), (vy[air], 0.5)):
        assert -lim - 1e-6 <= v.min() < -0.97 * lim and 0.97 * lim < v.max() <= lim + 1e-6
    v = s.root_state[:, 10:]
    u = -q[:, 1:]
    cross = torch.linalg.cross(u, v)
    omega = v + 2 * (w[:, None] * cross + torch.linalg.cross(u, cross))
    a = omega[air].abs().amax(0)
    limits = torch.tensor([0.05, 0.1, 0.5])
    assert (a <= limits + 1e-6).all() and (a > 0.97 * limits).all()
    pitch = (2 * (w * y - z * x)).clamp(-1, 1).asin()
    roll = torch.atan2(2 * (w * x + y * z), 1 - 2 * (x * x + y * y))
    for axis, limit in ((roll, 0.1), (pitch, 0.2)):
        assert axis[air].abs().max() <= limit + 1e-6 and axis[~air].abs().max() <= CFG.ordinary_tilt_rad + 1e-6
    assert s.angle_rad[air].abs().max() <= pi / 4 and (
        s.angle_rad[air].prod(1) < 0
    ).float().mean().item() == pytest.approx(0.5, abs=0.04)
    assert s.angle_rad[~air].min() >= -0.4 and s.angle_rad[~air].max() <= 0.5
    assert s.length_m[~air].min() >= 0.12 and s.length_m[~air].max() <= 0.20
    wheel = torch.tensor(CFG.hip_pivot_positions_b_m).repeat(len(k), 1, 1)
    wheel[:, :, 0] -= s.length_m * s.angle_rad.sin()
    wheel[:, :, 2] -= s.length_m * s.angle_rad.cos()
    row_z = torch.stack((2 * (x * z - w * y), 2 * (w * x + y * z), 1 - 2 * (x * x + y * y)), dim=1)
    bottom = (row_z[:, None] * wheel).sum(-1).min(1).values - CFG.wheel_radius_m
    torch.testing.assert_close(
        s.root_state[:, 2] - off,
        torch.maximum(-bottom + CFG.spawn_clearance_m, torch.full_like(off, CFG.min_root_height_m)),
    )


def test_unsafe_height_or_impossible_signed_drop_rejected_not_clamped():
    with pytest.raises(ValueError, match="height"):
        replace(CFG, recovery_forward_leg_height_m=(-0.25, -0.05))
    cfg = replace(CFG, min_root_height_m=0.05, recovery_root_height_m=0.06)
    torch.manual_seed(1)
    with pytest.raises(ValueError, match="release geometry"):
        sample_spawn(torch.full((128,), RECOVERY), torch.zeros(128), cfg)
    with pytest.raises(ValueError, match="non-air"):
        sample_spawn(torch.tensor([ORDINARY]), torch.tensor([0.1]), CFG)


def test_calibrated_mirror_and_zero_map_resolves_all_active_passive_and_slider_axes_once():
    from shu_train.wheelleg.shu_spawn import SpawnJointMap

    torch.manual_seed(6)
    sample = sample_spawn(torch.full((3,), RECOVERY), torch.zeros(3), CFG)
    leg = [4, 1, 0, 6, 17, 9, 7, 8, 5, 16, 3, 10]
    wheels = [14, 2]
    springs = [11, 13]
    aux = [15, 12]
    m = SpawnJointMap(18, leg, [4, 0, 14, 1, 6, 2], springs, aux, [1, -1] * 7, [i * 0.05 for i in range(14)])
    pin_q = torch.tensor([[0.03, -0.07], [0.02, -0.02], [0.051, -0.039]])
    pin_qd = pin_q * 0.28
    hinge_q = torch.tensor([[0.21, -0.32], [0.33, -0.42], [0.54, 0.12]])
    hinge_qd = hinge_q * 0.3
    limits = torch.tensor([[-10.0, 10.0]]).repeat(18, 1)
    limits[springs] = torch.tensor([-0.08, 0.08])
    kwargs = dict(
        spring_q_m=pin_q, spring_qd_m_s=pin_qd, auxiliary_q=hinge_q, auxiliary_qd=hinge_qd, asset_position_limits=limits
    )
    q, qd = m.assemble(sample, **kwargs)
    sign = torch.tensor([1, -1] * 7)
    zero = torch.arange(14) * 0.05
    for i, idx in enumerate(leg + wheels):
        cq = sample.leg_q[:, i] if i < 12 else sample.drive_q[:, (2, 5)[i - 12]]
        cv = sample.leg_qd[:, i] if i < 12 else sample.drive_qd[:, (2, 5)[i - 12]]
        torch.testing.assert_close(q[:, idx], zero[i] + sign[i] * cq)
        torch.testing.assert_close(qd[:, idx], sign[i] * cv)
    torch.testing.assert_close(q[:, springs], pin_q)
    torch.testing.assert_close(qd[:, springs], pin_qd)
    torch.testing.assert_close(q[:, aux], hinge_q)
    torch.testing.assert_close(qd[:, aux], hinge_qd)
    with pytest.raises(ValueError, match="active joint IDs"):
        replace(m, drive_ids=[4, 6, 14, 1, 0, 2])
    with pytest.raises(ValueError, match="every asset DOF"):
        replace(m, auxiliary_ids=[])
    with pytest.raises(ValueError, match="every asset DOF"):
        replace(m, spring_ids=wheels)
    with pytest.raises(ValueError, match="axis sign"):
        replace(m, canonical_to_asset_sign=[1] * 13 + [0])
    with pytest.raises(ValueError, match="auxiliary"):
        m.assemble(sample, **dict(kwargs, auxiliary_qd=torch.zeros(3, 0)))
    with pytest.raises(ValueError, match="stroke"):
        m.assemble(sample, **dict(kwargs, spring_q_m=pin_q + 0.18))


def test_slider_uses_pin_distance_and_velocity_projection_not_default_or_tangential_speed():
    from shu_train.wheelleg.shu_spawn import spring_slider_state

    p = torch.tensor([[[0.3, 0.0, 0.4], [0.0, -0.6, 0.0]]], dtype=torch.float64)
    v = torch.tensor([[[0.2, 3.0, -0.1], [0.3, 0.1, -0.8]]], dtype=p.dtype)
    args = dict(zero_pin_distance_m=p.new_tensor([0.46, 0.56]), extension_sign=p.new_tensor([1, -1]))
    q, qd = spring_slider_state(p, v, **args)
    torch.testing.assert_close(q, p.new_tensor([[0.04, -0.04]]))
    torch.testing.assert_close(qd, p.new_tensor([[0.04, 0.1]]))
    eps = 1e-6
    plus, _ = spring_slider_state(p + eps * v, v, **args)
    minus, _ = spring_slider_state(p - eps * v, v, **args)
    torch.testing.assert_close(qd, (plus - minus) / (2 * eps), atol=1e-9, rtol=1e-8)
    with pytest.raises(ValueError, match="degenerate"):
        spring_slider_state(p * 0, v, **args)
    with pytest.raises(ValueError, match="extension signs"):
        spring_slider_state(p, v, **dict(args, extension_sign=p.new_tensor([0, 1])))


def test_unknown_unreviewed_topology_is_not_assumed_to_match_reference_fivebar():
    for name in (None, "unknown_asymmetric"):
        with pytest.raises(ValueError, match="ik_branch.*CAD/FK"):
            replace(CFG, ik_branch=name)


def test_resolved_swivel_and_slider_drive_one_loop_and_differentiate_together():
    from shu_train.wheelleg.shu_spawn import CalibratedResetModel, SpawnJointMap

    model = CalibratedResetModel(
        mode="planar_rear_knee_coaxial_v1",
        canonical_to_asset_sign=[1] * 14,
        canonical_zero_in_asset_rad=[0.0] * 14,
        auxiliary_joint_names=["Lhinge", "Rhinge"],
        fixed_pin_xz_m=[[-0.09, 0.03], [-0.12, 0.014]],
        knee_pivot_xz_m=[[0.05, 0.023], [0.021, 0.03]],
        moving_pin_knee0_xz_m=[[0.025, 0.017], [0.035, -0.014]],
        knee_rotation_sign=[-1, 1],
        zero_pin_distance_m=[0.12, 0.11],
        extension_sign=[1, -1],
        slider_safe_range_m=[[-0.2, 0.2], [-0.2, 0.2]],
        hinge_zero_xz_rad=[0.1, -0.07],
        hinge_asset_sign=[1, -1],
    )
    mapping = SpawnJointMap(
        18,
        list(range(12)),
        [0, 2, 12, 1, 3, 13],
        [14, 15],
        [16, 17],
        model.canonical_to_asset_sign,
        model.canonical_zero_in_asset_rad,
    )
    torch.manual_seed(649)
    sample = sample_spawn(torch.full((20,), RECOVERY), torch.zeros(20, dtype=torch.float64), CFG)
    q = sample.leg_q
    limits = q.new_tensor([-20.0, 20.0]).expand(18, 2)
    pos, vel = model.resolve(sample, mapping, limits)
    # Reconstruct distal eye via proximal eye, slider distance and hinge angle. Must equal rear-link FK.
    bearing = pos[:, -2:] * q.new_tensor(model.hinge_asset_sign) + q.new_tensor(model.hinge_zero_xz_rad)
    length = pos[:, 14:16] * q.new_tensor(model.extension_sign) + q.new_tensor(model.zero_pin_distance_m)
    tip = q.new_tensor(model.fixed_pin_xz_m) + length[:, :, None] * torch.stack((bearing.cos(), bearing.sin()), -1)
    angle = q[:, -2:] * q.new_tensor(model.knee_rotation_sign)
    anchor = q.new_tensor(model.moving_pin_knee0_xz_m)
    # Independent FK using a complex number rotation (x + iz).
    rotated = torch.view_as_real(torch.view_as_complex(anchor) * torch.exp(1j * angle))
    torch.testing.assert_close(tip, q.new_tensor(model.knee_pivot_xz_m) + rotated)
    eps = 1e-6
    plus, _ = model.resolve(replace(sample, leg_q=q + eps * sample.leg_qd), mapping, limits)
    minus, _ = model.resolve(replace(sample, leg_q=q - eps * sample.leg_qd), mapping, limits)
    torch.testing.assert_close(vel[:, 14:], (plus - minus)[:, 14:] / (2 * eps), rtol=1e-7, atol=1e-9)
    with pytest.raises(ValueError, match="CAD safe stroke"):
        replace(model, slider_safe_range_m=[[1.0, 2.0], [-0.2, 0.2]]).resolve(sample, mapping, limits)
    with pytest.raises(ValueError, match="unsupported topology"):
        replace(model, mode="nonplanar")
    with pytest.raises(ValueError, match="auxiliary_joint_names"):
        replace(model, auxiliary_joint_names=["one"])
