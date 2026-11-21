"""Forward-kinematic clearance against the P1-landing plane before physics runs."""

from collections.abc import Mapping, Sequence
from dataclasses import fields
from math import isfinite

import torch

from .shu_spawn import AIR, CalibratedResetModel, SpawnConfig, SpawnJointMap, SpawnState, sample_spawn

_PATH = "robot.training.shu_air_collision"
_MAX_CANDIDATES = 32


def _vector(values: Sequence[float], width: int, path: str) -> None:
    if (
        not isinstance(values, (list, tuple))
        or len(values) != width
        or not all(type(v) in (float, int) and isfinite(v) for v in values)
    ):
        raise ValueError(f"{path}: expected {width} finite model coordinates")


def validate_air_collision(links: Mapping, base: str, colliders: Sequence[str]) -> None:
    """Validate a parent-first spanning tree using active USD joint coordinates and collision geometry."""
    if not isinstance(links, Mapping) or not links or next(iter(links)) != base:
        raise ValueError(f"{_PATH}: start with the articulation root {base!r}")
    if not colliders or base not in colliders:
        raise ValueError("robot.asset.collision_body_names: provide the USD collision owners including the base")
    seen, used_joints, covered = set(), set(), set()
    for name, link in links.items():
        path = f"{_PATH}.{name}"
        if not isinstance(link, Mapping):
            raise ValueError(f"{path}: expected a model link mapping")
        keys = {"vertices_m"}
        if name != base:
            keys |= {"parent", "motion", "zero_xyz_m", "zero_quat_wxyz"}
            motion = link.get("motion")
            if motion not in ("fixed", "revolute", "prismatic") or link.get("parent") not in seen:
                raise ValueError(f"{path}: expected fixed/revolute/prismatic motion and an earlier parent")
            _vector(link.get("zero_xyz_m"), 3, path + ".zero_xyz_m")
            quat = link.get("zero_quat_wxyz")
            _vector(quat, 4, path + ".zero_quat_wxyz")
            if abs(sum(x * x for x in quat) - 1) > 1e-5:
                raise ValueError(f"{path}.zero_quat_wxyz: expected a unit quaternion")
            if motion != "fixed":
                keys |= {"joint", "axis_parent"}
                joint = link.get("joint")
                if not isinstance(joint, str) or not joint or joint in used_joints:
                    raise ValueError(f"{path}.joint: expected a unique USD joint name")
                used_joints.add(joint)
                axis = link.get("axis_parent")
                _vector(axis, 3, path + ".axis_parent")
                if abs(sum(x * x for x in axis) - 1) > 1e-5:
                    raise ValueError(f"{path}.axis_parent: expected a unit axis in the parent frame")
            if motion == "revolute":
                keys.add("pivot_parent_m")
                _vector(link.get("pivot_parent_m"), 3, path + ".pivot_parent_m")
        if set(link) != keys:
            raise ValueError(f"{path}: expected fields {sorted(keys)}")
        points = link["vertices_m"]
        if not isinstance(points, (tuple, list)):
            raise ValueError(f"{path}.vertices_m: expected collision vertices or [] for a collisionless link")
        if points:
            covered.add(name)
            for point in points:
                _vector(point, 3, path + ".vertices_m")
        seen.add(name)
    if covered != set(colliders):
        raise ValueError(
            f"{_PATH}: vertices must cover exactly the USD collision owners; "
            f"missing {sorted(set(colliders) - covered)}, extra {sorted(covered - set(colliders))}"
        )


def _rotation(quat: torch.Tensor) -> torch.Tensor:
    w, x, y, z = quat.unbind(-1)
    return torch.stack(
        (
            1 - 2 * (y * y + z * z),
            2 * (x * y - w * z),
            2 * (x * z + w * y),
            2 * (x * y + w * z),
            1 - 2 * (x * x + z * z),
            2 * (y * z - w * x),
            2 * (x * z - w * y),
            2 * (y * z + w * x),
            1 - 2 * (x * x + y * y),
        ),
        dim=-1,
    ).unflatten(-1, (3, 3))


class AirBirthClearance:
    def __init__(self, links, *, base, colliders, body_names, joint_names, like):
        validate_air_collision(links, base, colliders)
        missing = set(body_names) - set(links)
        extra = set(links) - set(body_names)
        if not body_names or base != body_names[0] or missing or extra:
            raise ValueError(
                f"{_PATH}: FK tree does not match the launched articulation; "
                f"root {base!r}, missing links {sorted(missing)}, extra links {sorted(extra)}"
            )
        self.base = base
        self.points = {name: like.new_tensor(link["vertices_m"]) for name, link in links.items() if link["vertices_m"]}
        self.edges = []
        for name, spec in list(links.items())[1:]:
            motion = spec["motion"]
            joint = spec.get("joint")
            if joint is not None and joint_names.count(joint) != 1:
                raise ValueError(f"{_PATH}.{name}.joint: {joint!r} is not a unique launched USD DOF")
            xyz = like.new_tensor(spec["zero_xyz_m"])
            axis = like.new_tensor(spec["axis_parent"]) if joint is not None else None
            pivot = like.new_tensor(spec["pivot_parent_m"]) if motion == "revolute" else None
            self.edges.append(
                (
                    name,
                    spec["parent"],
                    motion,
                    joint_names.index(joint) if joint is not None else None,
                    xyz,
                    _rotation(like.new_tensor(spec["zero_quat_wxyz"])),
                    axis,
                    pivot,
                )
            )

    def minimum_z(self, root: torch.Tensor, asset_q: torch.Tensor) -> torch.Tensor:
        """Lowest collider point, relative to the plane origin. Root and q are the candidate to be written."""
        root_up = _rotation(root[:, 3:7])[:, 2]
        z = {self.base: root[:, 2]}
        up = {self.base: root_up}
        for name, parent, motion, idx, xyz, rotation, axis, pivot in self.edges:
            direction = up[parent]
            if motion == "revolute":
                # Rotate the plane normal by -q instead of rotating every collision vertex by q.
                a = asset_q[:, idx, None]
                c, s = a.cos(), a.sin()
                ax = axis.expand_as(direction)
                rotated = direction * c - torch.linalg.cross(ax, direction) * s
                rotated += ax * (ax * direction).sum(-1, keepdim=True) * (1 - c)
                z[name] = z[parent] + direction @ pivot + rotated @ (xyz - pivot)
                direction = rotated
            elif motion == "prismatic":
                z[name] = z[parent] + direction @ xyz + (direction @ axis) * asset_q[:, idx]
            else:
                z[name] = z[parent] + direction @ xyz
            up[name] = direction @ rotation
        return torch.stack(
            [z[name] + (up[name] @ points.T).amin(-1) for name, points in self.points.items()], dim=-1
        ).amin(-1)


def retry_air_births(
    state: SpawnState,
    q: torch.Tensor,
    qd: torch.Tensor,
    *,
    rows: torch.Tensor,
    band: torch.Tensor,
    edges_m: torch.Tensor,
    spawn: SpawnConfig,
    mapping: SpawnJointMap,
    model: CalibratedResetModel,
    limits: torch.Tensor,
    clearance: AirBirthClearance,
) -> None:
    """Repair only rejected air rows, at reset and before any articulation write or episode-state update."""
    for attempt in range(_MAX_CANDIDATES):
        minimum = clearance.minimum_z(state.root_state[rows], q[rows])
        # The wheel-derived margin is already in sample_spawn. Test against the plane itself so
        # a genuine first substep impact after a small positive gap remains an ordinary first touch.
        rows = rows[~(torch.isfinite(minimum) & (minimum > 0))]
        if not rows.numel():
            return
        selected = band[rows]
        if attempt + 1 == _MAX_CANDIDATES:
            raise ValueError(
                f"{_PATH}: no contact-free air candidate after {_MAX_CANDIDATES} draws; "
                f"height bands {selected.unique().tolist()}, rejected rows {rows.numel()}, "
                f"last minimum collision Z {minimum.min().item():.6g} m; check USD/FK and H0–H4"
            )
        low, high = edges_m[selected], edges_m[selected + 1]
        offset = low + torch.rand_like(low) * (high - low)
        # AirHeightCurriculum labels exact interior edges as the lower band. Keep the retry
        # in the selected band even if rand is exactly zero or rounds back to the lower endpoint.
        offset = torch.where(selected > 0, offset.maximum(torch.nextafter(low, high)), offset)
        candidate = sample_spawn(torch.full_like(rows, AIR), offset, spawn)
        q[rows], qd[rows] = model.resolve(candidate, mapping, limits[rows])
        for field in fields(SpawnState):
            getattr(state, field.name)[rows] = getattr(candidate, field.name)
