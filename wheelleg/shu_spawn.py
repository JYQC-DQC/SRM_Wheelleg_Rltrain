"""Model-gated SHU reset generation on a flat plane. Values in this module are NOT a CAD calibration."""

from collections.abc import Sequence
from dataclasses import dataclass
from math import isfinite, pi

import torch

ORDINARY, RECOVERY, AIR = range(3)  # birth type, not reward phase
LEG_JOINT_ORDER = tuple(
    f"{side}_{name}"
    for name in ("front1", "rear1", "front2", "front3", "front4", "rear2")
    for side in ("left", "right")
)


@dataclass(frozen=True)
class SpawnConfig:
    """Reviewed SHU geometry/ranges, no fallback to reference-asset numbers.

    Applies to the documented symmetric five-bar branch ONLY. Map asset coordinates/axis signs to
    LEG_JOINT_ORDER before use. Calibrate ranges against joint stops, spring travel and interference
    over the joint left/right envelope, not just a marginal range of reachable lengths.
    min_root_height_m certifies safe height for all OTHER collision geometry in ALL allowed poses,
    including any tilted wheel tread not covered by the wheel-centre-minus-radius envelope.
    recovery_root_height_m is a separately audited fixed release height, never the target stand height.
    """

    link_lengths_m: Sequence[float]
    angle_offsets_rad: Sequence[float]
    hip_pivot_positions_b_m: Sequence[Sequence[float]]
    wheel_radius_m: float
    min_root_height_m: float
    spawn_clearance_m: float
    ordinary_length_m: Sequence[float]
    ordinary_angle_rad: Sequence[float]
    ordinary_tilt_rad: float
    air_length_m: Sequence[float]
    recovery_length_m: Sequence[float]
    recovery_forward_leg_height_m: Sequence[float]
    recovery_rear_leg_height_m: Sequence[float]
    recovery_root_height_m: float
    wheel_angle_rad: Sequence[float]
    wheel_speed_rad_s: Sequence[float]
    leg_speed_rad_s: Sequence[float]
    ik_branch: str | None = None  # None = CAD branch not approved, never assume the SCUT topology.

    def __post_init__(self) -> None:
        if self.ik_branch != "symmetric_five_bar_v1":
            raise ValueError(
                "shu_spawn.ik_branch: validate the symmetric_five_bar_v1 branch against CAD/FK first; "
                "a different mechanism needs its own calibrated IK"
            )
        for name in (
            "ordinary_length_m",
            "ordinary_angle_rad",
            "air_length_m",
            "recovery_length_m",
            "recovery_forward_leg_height_m",
            "recovery_rear_leg_height_m",
            "wheel_angle_rad",
            "wheel_speed_rad_s",
            "leg_speed_rad_s",
        ):
            lo, hi = getattr(self, name)
            if not (isfinite(lo) and isfinite(hi) and lo <= hi):
                raise ValueError(f"SpawnConfig: invalid {name} range")
        l0, l1, l2 = self.link_lengths_m
        if not all(
            isfinite(v) and v > 0
            for v in (l0, l1, l2, self.wheel_radius_m, self.min_root_height_m, self.recovery_root_height_m)
        ):
            raise ValueError("SpawnConfig: invalid link lengths, wheel radius or root-height bound")
        if not all(isfinite(v) and v >= 0 for v in (self.spawn_clearance_m, self.ordinary_tilt_rad)):
            raise ValueError("SpawnConfig: invalid spawn clearance or ordinary tilt bound")
        if len(self.angle_offsets_rad) != 6 or not all(map(isfinite, self.angle_offsets_rad)):
            raise ValueError("SpawnConfig: six calibrated offsets required in branch order")
        if len(self.hip_pivot_positions_b_m) != 2 or any(
            len(p) != 3 or not all(map(isfinite, p)) for p in self.hip_pivot_positions_b_m
        ):
            raise ValueError("SpawnConfig: left and right hip xyz in body frame required")
        for lo, hi in (self.ordinary_length_m, self.recovery_length_m, self.air_length_m):
            if not (abs(l0 - l1) * l2 / l0 < lo <= hi < (l0 + l1) * l2 / l0):
                raise ValueError("SpawnConfig: a length range reaches a singular or unreachable five-bar pose")
        for interval in (self.recovery_forward_leg_height_m, self.recovery_rear_leg_height_m):
            if max(abs(v) for v in interval) > self.recovery_length_m[0]:
                raise ValueError("SpawnConfig: recovery hip-wheel height exceeds shortest sampled leg")
        if self.recovery_root_height_m < self.min_root_height_m:
            raise ValueError("SpawnConfig: recovery release below whole-body safe floor")


@dataclass
class SpawnState:
    root_state: torch.Tensor  # (N,13) relative xyz, quat wxyz, world linear m/s and angular rad/s
    leg_q: torch.Tensor  # (N,12) rad, LEG_JOINT_ORDER, including the four passive pairs
    leg_qd: torch.Tensor  # (N,12) rad/s, velocities tangent to closed-chain manifold
    drive_q: torch.Tensor  # (N,6) LF, LR, LW, RF, RR, RW
    drive_qd: torch.Tensor
    length_m: torch.Tensor  # (N,2) left/right hip-to-wheel length; not root height
    angle_rad: torch.Tensor  # (N,2) relative to body -Z, positive swings wheel backward (-X)


def sample_spawn_kinds(
    stage: str, count: int, device: str, *, flat_recovery_probability: float | None = None
) -> torch.Tensor:
    """Sample once on true reset, never by physics time. Flat probability is not set by the landing decision."""
    draw = torch.rand(count, device=device)
    if stage == "p1-flat":
        if flat_recovery_probability is None or not 0 <= flat_recovery_probability <= 1:
            raise ValueError("p1-flat requires reviewed flat_recovery_probability")
        return torch.where(draw < flat_recovery_probability, RECOVERY, ORDINARY)
    if stage == "p1-landing":
        return torch.where(draw < 0.4, AIR, torch.where(draw < 0.8, RECOVERY, ORDINARY))
    raise ValueError(f"unknown SHU spawn stage: {stage}")


def five_bar_joint_angles(
    length: torch.Tensor, angle: torch.Tensor, links: Sequence[float], offsets: Sequence[float]
) -> torch.Tensor:
    """(N,2) m/rad -> (N,12) rad. Reference: 1a56b67 wheelleg/tensor_ops.py, V3 IK lines 5604-5631.

    One elbow branch, positive leg angle towards body -X. Reject singular/unreachable inputs;
    clipping cosines to repair an impossible pose would silently bias the distribution.
    """
    l0, l1, l2 = links
    d = length * (l0 / l2)
    ch = (d.square() + l0**2 - l1**2) / (2 * l0 * d)
    ck = (l0**2 + l1**2 - d.square()) / (2 * l0 * l1)
    if not ((d > 0) & (ch.abs() < 1) & (ck.abs() < 1) & torch.isfinite(angle)).all():
        raise ValueError("singular or unreachable five-bar reset pose")
    half, knee = ch.acos(), ck.acos()
    close = 2 * pi - 2 * (half + knee)
    return torch.stack(
        (
            angle + pi / 2 - half - offsets[0],
            angle + pi / 2 + half - offsets[1],
            offsets[2] - knee,
            offsets[3] - close,
            offsets[4] - knee,
            knee - offsets[5],
        ),
        dim=1,
    ).flatten(1)


def _rotate(q: torch.Tensor, v: torch.Tensor) -> torch.Tensor:
    """Apply wxyz quaternion to an xyz vector; works also on the (N,2,3) wheel-centre array."""
    uv = torch.linalg.cross(q[..., 1:], v)
    return v + 2 * (q[..., :1] * uv + torch.linalg.cross(q[..., 1:], uv))


def sample_spawn(kinds: torch.Tensor, offsets_m: torch.Tensor, cfg: SpawnConfig) -> SpawnState:
    """Generate pose and tangent velocity. Add the plane origin ONLY to root_state[:, :3] on integration.

    offsets_m (N,) are extra drop metres on top of the safe pose, zero for non-air. No command
    enters this function: the initial air speed is neither copied from, nor aligned to, a request.
    """
    n, device = len(kinds), kinds.device
    recovery, air = kinds == RECOVERY, kinds == AIR
    if not (
        ((kinds == ORDINARY) | air | recovery) & torch.isfinite(offsets_m) & (offsets_m >= 0) & (air | (offsets_m == 0))
    ).all():
        raise ValueError("invalid spawn kind/drop offset (non-air must be zero)")

    def draw(bounds: Sequence[float], width: int) -> torch.Tensor:
        lo, hi = bounds
        return lo + (hi - lo) * torch.rand((n, width), device=device, dtype=offsets_m.dtype)

    length = torch.where(
        air[:, None],
        draw(cfg.air_length_m, 2),
        torch.where(recovery[:, None], draw(cfg.recovery_length_m, 2), draw(cfg.ordinary_length_m, 2)),
    )
    forward = torch.rand_like(length) < 1 / 3
    hip_drop = torch.where(forward, draw(cfg.recovery_forward_leg_height_m, 2), draw(cfg.recovery_rear_leg_height_m, 2))
    # Only evaluate acos against the corresponding RECOVERY length (ordinary/air could be shorter).
    recovery_angle = torch.where(forward, -1.0, 1.0) * torch.where(recovery[:, None], hip_drop / length, 0.0).acos()
    angle = torch.where(
        recovery[:, None],
        recovery_angle,
        torch.where(air[:, None], draw((-pi / 4, pi / 4), 2), draw(cfg.ordinary_angle_rad, 2)),
    )
    q = five_bar_joint_angles(length, angle, cfg.link_lengths_m, cfg.angle_offsets_rad)
    angles = q.reshape(n, 6, 2)
    # Uniform independent active rates; differentiate closure rather than writing zero passive rates.
    front_rate, rear_rate = draw(cfg.leg_speed_rad_s, 4).reshape(n, 2, 2).unbind(1)
    half = (angles[:, 1] + cfg.angle_offsets_rad[1] - angles[:, 0] - cfg.angle_offsets_rad[0]) / 2
    knee = angles[:, 5] + cfg.angle_offsets_rad[5]
    # With side d=l0*L/l2, d^2-2*l0*cos(half)*d+l0^2-l1^2=0.
    # At the fold in active coordinates a finite arbitrary pair of hip rates is not a tangent.
    l0, l1, l2 = cfg.link_lengths_m
    d = length * (l0 / l2)
    denom = d - l0 * half.cos()
    if (denom.abs() <= torch.finfo(length.dtype).eps * max(l0, l1)).any():
        raise ValueError("singular active-velocity mapping at sampled five-bar pose")
    half_rate = (rear_rate - front_rate) / 2
    d_rate = -l0 * d * half.sin() * half_rate / denom
    knee_rate = d * d_rate / (l0 * l1 * knee.sin())
    qd = torch.stack(
        (front_rate, rear_rate, -knee_rate, 2 * (half_rate + knee_rate), -knee_rate, knee_rate), dim=1
    ).flatten(1)
    wheel_q, wheel_qd = draw(cfg.wheel_angle_rad, 2), draw(cfg.wheel_speed_rad_s, 2)
    drive_q = torch.stack((angles[:, 0], angles[:, 1], wheel_q), dim=-1).flatten(1)
    drive_qd = torch.stack((front_rate, rear_rate, wheel_qd), dim=-1).flatten(1)

    tilt = draw((-1, 1), 2) * torch.where(air[:, None], length.new_tensor([0.1, 0.2]), cfg.ordinary_tilt_rad)
    tilt[recovery] = 0
    yaw = torch.where(recovery, 0.0, draw((-pi, pi), 1)[:, 0])
    r, p, y = tilt[:, 0] / 2, tilt[:, 1] / 2, yaw / 2
    cr, cp, cy, sr, sp, sy = r.cos(), p.cos(), y.cos(), r.sin(), p.sin(), y.sin()
    quat = torch.stack(
        (
            cr * cp * cy + sr * sp * sy,
            sr * cp * cy - cr * sp * sy,
            cr * sp * cy + sr * cp * sy,
            cr * cp * sy - sr * sp * cy,
        ),
        dim=-1,
    )
    wheel_b = length.new_tensor(cfg.hip_pivot_positions_b_m).expand(n, 2, 3).clone()
    wheel_b[:, :, 0] -= length * angle.sin()
    wheel_b[:, :, 2] -= length * angle.cos()
    wheel_z = _rotate(quat[:, None, :], wheel_b)[:, :, 2]
    safe = (cfg.wheel_radius_m - wheel_z.amin(dim=1) + cfg.spawn_clearance_m).clamp_min(cfg.min_root_height_m)
    if (recovery & (cfg.recovery_root_height_m < safe)).any():
        raise ValueError("recovery_root_height_m would violate safe release geometry; review calibration")
    height = torch.where(recovery, cfg.recovery_root_height_m, safe + offsets_m)
    if (air & (height <= cfg.min_root_height_m) & (offsets_m == 0)).any() or (
        air & (height + wheel_z.amin(dim=1) <= cfg.wheel_radius_m)
    ).any():
        raise ValueError("air birth has no certified clearance; correct the drop limits or spawn geometry")
    root = length.new_zeros(n, 13)
    root[:, 2], root[:, 3:7] = height, quat
    vx, vy = draw((-2.5, 2.5), 1)[:, 0], draw((-0.5, 0.5), 1)[:, 0]
    root[:, 7] = torch.where(air, yaw.cos() * vx - yaw.sin() * vy, 0.0)
    root[:, 8] = torch.where(air, yaw.sin() * vx + yaw.cos() * vy, 0.0)
    omega_b = draw((-1, 1), 3) * length.new_tensor([0.05, 0.10, 0.50])
    root[:, 10:13] = torch.where(air[:, None], _rotate(quat, omega_b), 0.0)
    return SpawnState(root, q, qd, drive_q, drive_qd, length, angle)


def spring_slider_state(
    pin_delta: torch.Tensor,
    pin_relative_velocity: torch.Tensor,
    *,
    zero_pin_distance_m: torch.Tensor,
    extension_sign: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Map **coaxial** spring pin-to-pin motion to calibrated absolute USD prismatic q/qd (L,R).

    pin_delta, pin_relative_velocity: (N,2,3), B-A and vB-vA in the SAME frame [m, m/s].
    Obtain pins/velocities by FK/Jacobian at the sampled pose/rates, not from last frame's buffers.
    zero_pin_distance_m[2]: measured pin distance at slider asset q=0. extension_sign[2]: whether
    increasing asset q increases (+1) or decreases (-1) pin distance. Not a motor or force sign.
    NOT a solver for a spring rocker, offset attachment axis, or auxiliary pin hinge. For those,
    solve the actual asset constraints (including hinge angles AND rates) instead of using this formula.
    """
    if pin_delta.ndim != 3 or pin_delta.shape[1:] != (2, 3) or pin_relative_velocity.shape != pin_delta.shape:
        raise ValueError("spring pin displacement and velocity must have shape (N,2,3) in L/R order")
    distance = torch.linalg.vector_norm(pin_delta, dim=-1)
    if (
        zero_pin_distance_m.shape != (2,)
        or extension_sign.shape != (2,)
        or not (torch.isfinite(zero_pin_distance_m) & (zero_pin_distance_m >= 0) & (extension_sign.abs() == 1)).all()
    ):
        raise ValueError("supply calibrated left/right zero pin distances and extension signs")
    if not ((distance > 0) & torch.isfinite(distance) & torch.isfinite(pin_relative_velocity).all(-1)).all():
        raise ValueError("degenerate/nonfinite spring pin separation or velocity")
    rate = ((pin_delta / distance[:, :, None]) * pin_relative_velocity).sum(-1)
    return (distance - zero_pin_distance_m) * extension_sign, rate * extension_sign


@dataclass(frozen=True)
class SpawnJointMap:
    """Resolve asset IDs once; no implicit identity sign, zero offset, default-q or spring assumption.

    The adapter must first demonstrate this five-bar branch fits the actual CAD/axis convention.
    Canonical leg coordinates here already include SpawnConfig.angle_offsets_rad, once. For each
    of 12 leg axes followed by L/R wheels: asset_q = zero + sign*canonical_q, asset_qd = sign*qd.
    `canonical_zero_in_asset_rad` is the *asset reading at canonical zero*, NOT motor encoder zeros
    or neutral PD defaults. If the sampled angles are already asset coordinates, calibrate identity
    explicitly. auxiliary_ids must include every other moving DOF (e.g., spring pivot hinges).
    """

    joint_count: int
    leg_ids: Sequence[int]  # all 12 in LEG_JOINT_ORDER
    drive_ids: Sequence[int]  # LF, LR, LW, RF, RR, RW
    spring_ids: Sequence[int]  # left/right prismatic axes
    auxiliary_ids: Sequence[int]
    canonical_to_asset_sign: Sequence[int]  # 12 leg axes then 2 wheels
    canonical_zero_in_asset_rad: Sequence[float]  # same 14

    def __post_init__(self) -> None:
        if len(self.leg_ids) != 12 or len(self.drive_ids) != 6 or len(self.spring_ids) != 2:
            raise ValueError("resolve 12 leg, 6 drive and 2 spring joint IDs in the documented orders")
        if [self.drive_ids[i] for i in (0, 1, 3, 4)] != [self.leg_ids[i] for i in (0, 2, 1, 3)]:
            raise ValueError("active joint IDs do not agree between five-bar and six-drive orders")
        ids = (*self.leg_ids, self.drive_ids[2], self.drive_ids[5], *self.spring_ids, *self.auxiliary_ids)
        if any(type(i) is not int for i in ids) or sorted(ids) != list(range(self.joint_count)):
            raise ValueError("joint map must cover every asset DOF exactly once, including auxiliary hinge(s)")
        if len(self.canonical_to_asset_sign) != 14 or not all(v in (-1, 1) for v in self.canonical_to_asset_sign):
            raise ValueError("provide one calibrated +/- axis sign per canonical leg/wheel coordinate")
        if len(self.canonical_zero_in_asset_rad) != 14 or not all(map(isfinite, self.canonical_zero_in_asset_rad)):
            raise ValueError("provide 14 calibrated leg/wheel asset zero readings")

    def assemble(
        self,
        sample: SpawnState,
        *,
        spring_q_m: torch.Tensor,
        spring_qd_m_s: torch.Tensor,
        auxiliary_q: torch.Tensor,
        auxiliary_qd: torch.Tensor,
        asset_position_limits: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """Return FULL absolute (N,J) USD joint q/qd, not displacements from default pose.

        Spring inputs (N,2) in actual asset coordinates; auxiliary inputs (N,A), even if A=0.
        All solved at this very sampled pose. Required (J,2) or per-env (N,J,2) actual position bounds in
        asset units [rad, m], +/-inf only for unbounded DOFs (e.g. continuous wheels). Reject
        unsafe solutions, don't clip angles/stroke since independent clipping breaks closure.
        """
        n = sample.root_state.shape[0]
        for pos, vel, k, name in (
            (spring_q_m, spring_qd_m_s, 2, "spring"),
            (auxiliary_q, auxiliary_qd, len(self.auxiliary_ids), "auxiliary"),
        ):
            if pos.shape != (n, k) or vel.shape != (n, k):
                raise ValueError(f"{name} absolute q and consistent qd must both be supplied with shape {(n, k)}")
        if asset_position_limits.shape not in ((self.joint_count, 2), (n, self.joint_count, 2)):
            raise ValueError("expected (J,2) or (N,J,2) asset position limits in asset order")
        canonical_q = torch.cat((sample.leg_q, sample.drive_q[:, (2, 5)]), -1)
        canonical_qd = torch.cat((sample.leg_qd, sample.drive_qd[:, (2, 5)]), -1)
        sign = canonical_q.new_tensor(self.canonical_to_asset_sign)
        zeros = canonical_q.new_tensor(self.canonical_zero_in_asset_rad)
        rot_ids = [*self.leg_ids, self.drive_ids[2], self.drive_ids[5]]
        q = canonical_q.new_empty(n, self.joint_count)
        qd = torch.empty_like(q)
        q[:, rot_ids] = zeros + sign * canonical_q
        qd[:, rot_ids] = sign * canonical_qd
        q[:, list(self.spring_ids)], qd[:, list(self.spring_ids)] = spring_q_m, spring_qd_m_s
        q[:, list(self.auxiliary_ids)], qd[:, list(self.auxiliary_ids)] = auxiliary_q, auxiliary_qd
        low, high = asset_position_limits.unbind(-1)
        if not (torch.isfinite(q) & torch.isfinite(qd) & (q >= low) & (q <= high)).all():
            raise ValueError(
                "nonfinite or out-of-range absolute asset reset (joint/spring stroke); recheck calibration"
            )
        return q, qd


@dataclass(frozen=True)
class CalibratedResetModel:
    """One explicitly opt-in CAD topology; every parameter is per asset, never inferred from SCUT.

    In the rear proximal link's rigid X/Z frame: fixed_pin and knee_pivot are points;
    moving_pin_knee0 is the vector from knee pivot to distal spring eye when the canonical
    rear2 coordinate is zero (NOT the unoffset triangle knee angle). Positive planar rotation
    is +X towards +Z, corrected independently per side by knee_rotation_sign. Both eyes
    must be coplanar and the slider coaxial with their separation. Optional auxiliary axes
    are exactly L/R swivels at the fixed eyes, relative to this same link. hinge_zero_xz_rad
    is the pin-line bearing at asset hinge q=0; the reviewed branch must not wrap at +/-pi.
    Any other attachment, rocker or auxiliary DOF needs a different validated resolver.
    """

    mode: str
    canonical_to_asset_sign: Sequence[int]
    canonical_zero_in_asset_rad: Sequence[float]
    auxiliary_joint_names: Sequence[str]
    fixed_pin_xz_m: Sequence[Sequence[float]]
    knee_pivot_xz_m: Sequence[Sequence[float]]
    moving_pin_knee0_xz_m: Sequence[Sequence[float]]
    knee_rotation_sign: Sequence[int]
    zero_pin_distance_m: Sequence[float]
    extension_sign: Sequence[int]
    slider_safe_range_m: Sequence[Sequence[float]]
    hinge_zero_xz_rad: Sequence[float]
    hinge_asset_sign: Sequence[int]

    def __post_init__(self) -> None:
        if self.mode != "planar_rear_knee_coaxial_v1":
            raise ValueError("shu_reset_map.mode requires calibrated planar_rear_knee_coaxial_v1; unsupported topology")
        names = self.auxiliary_joint_names
        if (
            not isinstance(names, (list, tuple))
            or len(names) not in (0, 2)
            or any(not isinstance(x, str) or not x.strip() for x in names)
            or len(set(names)) != len(names)
        ):
            raise ValueError("shu_reset_map.auxiliary_joint_names must be [] or two distinct left/right hinge names")
        for key, width, sign in (
            ("canonical_to_asset_sign", 14, True),
            ("canonical_zero_in_asset_rad", 14, False),
            ("knee_rotation_sign", 2, True),
            ("extension_sign", 2, True),
            ("zero_pin_distance_m", 2, False),
            ("hinge_zero_xz_rad", len(names), False),
            ("hinge_asset_sign", len(names), True),
        ):
            a = getattr(self, key)
            if (
                not isinstance(a, (list, tuple))
                or len(a) != width
                or not all(type(v) in (int, float) and isfinite(v) and (not sign or v in (-1, 1)) for v in a)
            ):
                raise ValueError(f"shu_reset_map.{key}: expected {width} calibrated finite values or signs")
        if any(v < 0 for v in self.zero_pin_distance_m):
            raise ValueError("shu_reset_map.zero_pin_distance_m cannot be negative")
        for key in ("fixed_pin_xz_m", "knee_pivot_xz_m", "moving_pin_knee0_xz_m", "slider_safe_range_m"):
            r = getattr(self, key)
            if (
                not isinstance(r, (list, tuple))
                or len(r) != 2
                or any(
                    not isinstance(pair, (list, tuple))
                    or len(pair) != 2
                    or not all(type(v) in (int, float) and isfinite(v) for v in pair)
                    for pair in r
                )
            ):
                raise ValueError(f"shu_reset_map.{key}: expected calibrated left and right pairs")
        if any(lo >= hi for lo, hi in self.slider_safe_range_m):
            raise ValueError("shu_reset_map.slider_safe_range_m must contain strictly ordered asset stroke limits")
        if any(x == 0 and z == 0 for x, z in self.moving_pin_knee0_xz_m):
            raise ValueError("shu_reset_map.moving_pin_knee0_xz_m must not coincide with the knee pivot")

    def resolve(
        self, sample: SpawnState, mapping: SpawnJointMap, asset_position_limits: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """Solve pin positions AND velocities in one rotating frame; common rigid motion cancels here.

        Return whole-articulation absolute positions and velocities, only after both CAD safe
        stroke and per-env USD limits pass. No joint state from a preceding pose is retained.
        """
        knee, rate = sample.leg_q[:, 10:12], sample.leg_qd[:, 10:12]
        sign = knee.new_tensor(self.knee_rotation_sign)
        a = knee * sign
        c, s = a.cos(), a.sin()
        bx, bz = knee.new_tensor(self.moving_pin_knee0_xz_m).unbind(-1)
        rx, rz = c * bx - s * bz, s * bx + c * bz
        px, pz = (knee.new_tensor(self.knee_pivot_xz_m) - knee.new_tensor(self.fixed_pin_xz_m)).unbind(-1)
        dx, dz = px + rx, pz + rz
        vx, vz = -rz * rate * sign, rx * rate * sign
        zero = torch.zeros_like(dx)
        pos, vel = spring_slider_state(
            torch.stack((dx, zero, dz), -1),
            torch.stack((vx, zero, vz), -1),
            zero_pin_distance_m=knee.new_tensor(self.zero_pin_distance_m),
            extension_sign=knee.new_tensor(self.extension_sign),
        )
        lo, hi = knee.new_tensor(self.slider_safe_range_m).unbind(-1)
        if not ((pos >= lo) & (pos <= hi)).all():
            raise ValueError("spring slider outside calibrated CAD safe stroke; reject reset, do not clamp")
        if self.auxiliary_joint_names:
            bearing = torch.atan2(dz, dx) - knee.new_tensor(self.hinge_zero_xz_rad)
            hinge_sign = knee.new_tensor(self.hinge_asset_sign)
            hinge = (torch.remainder(bearing + pi, 2 * pi) - pi) * hinge_sign
            hinge_rate = ((dx * vz - dz * vx) / (dx.square() + dz.square())) * hinge_sign
        else:
            hinge = hinge_rate = knee[:, :0]
        return mapping.assemble(
            sample,
            spring_q_m=pos,
            spring_qd_m_s=vel,
            auxiliary_q=hinge,
            auxiliary_qd=hinge_rate,
            asset_position_limits=asset_position_limits,
        )
