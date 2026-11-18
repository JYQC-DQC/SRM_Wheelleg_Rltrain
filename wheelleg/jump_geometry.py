"""Collision support and gravity-relative leg measurements for flat jumps."""

import numpy as np
import torch

JUMP_GEOMETRY_COLUMNS = (
    "body_clearance_m",
    "left_leg_angle_rad",
    "right_leg_angle_rad",
    "start_body_clearance_m",
    "peak_joint_clearance_m",
    "peak_body_at_apex_m",
    "peak_wheel_at_apex_m",
    "peak_abs_leg_angle_at_apex_rad",
    "apex_pose_quality",
)


def box_bottom_z(center_z: torch.Tensor, half_axes_z: torch.Tensor) -> torch.Tensor:
    return center_z - half_axes_z.abs().sum(-1)


def cylinder_bottom_z(center_z: torch.Tensor, half_axes_z: torch.Tensor) -> torch.Tensor:
    # The first two vectors span the circular cap; the third points along the axis.
    return center_z - half_axes_z[..., :2].norm(dim=-1) - half_axes_z[..., 2].abs()


def sagittal_leg_angle(hip_to_wheel_w: torch.Tensor, yaw: torch.Tensor) -> torch.Tensor:
    """Signed angle from gravity down toward heading forward, one per leg."""
    forward = hip_to_wheel_w[..., 0] * yaw.cos()[..., None] + hip_to_wheel_w[..., 1] * yaw.sin()[..., None]
    return torch.atan2(forward, -hip_to_wheel_w[..., 2])


def usd_collision_frames(body, kind: str) -> np.ndarray:
    """Read enabled SCUT colliders as [shape, 4, 3]: three half axes, then center, in link frame."""
    from pxr import Usd, UsdGeom, UsdPhysics

    if not body or not body.HasAPI(UsdPhysics.RigidBodyAPI):
        raise ValueError(f"Expected a USD rigid body for jump collision geometry, got {body}")
    stage = body.GetStage()
    if UsdGeom.GetStageMetersPerUnit(stage) != 1.0 or UsdGeom.GetStageUpAxis(stage) != "Z":
        raise ValueError("Flat jump collision geometry requires a meter-based, Z-up USD stage")
    cache = UsdGeom.XformCache()
    world_to_body = cache.GetLocalToWorldTransform(body).GetInverse()
    frames = []
    prims = iter(Usd.PrimRange(body, Usd.TraverseInstanceProxies()))
    for prim in prims:
        if prim != body and prim.HasAPI(UsdPhysics.RigidBodyAPI):
            prims.PruneChildren()
            continue
        if not prim.HasAPI(UsdPhysics.CollisionAPI):
            continue
        if not UsdPhysics.CollisionAPI(prim).GetCollisionEnabledAttr().Get():
            continue
        frame = np.asarray(cache.GetLocalToWorldTransform(prim) * world_to_body).copy()[:, :3]
        if kind == "box" and prim.IsA(UsdGeom.Cube):
            frame[:3] *= 0.5 * UsdGeom.Cube(prim).GetSizeAttr().Get()
        elif kind == "cylinder" and prim.IsA(UsdGeom.Cylinder):
            cylinder = UsdGeom.Cylinder(prim)
            axis = "XYZ".index(cylinder.GetAxisAttr().Get())
            frame[:3] = np.roll(frame[:3], 2 - axis, axis=0)
            frame[:2] *= cylinder.GetRadiusAttr().Get()
            frame[2] *= 0.5 * cylinder.GetHeightAttr().Get()
        else:
            raise ValueError(f"Expected a {kind} collider at {prim.GetPath()}, got {prim.GetTypeName()}")
        frames.append(frame)
    if not frames or (kind == "cylinder" and len(frames) != 1):
        raise ValueError(f"Unexpected number of enabled {kind} colliders on {body.GetPath()}: {len(frames)}")
    return np.stack(frames)
