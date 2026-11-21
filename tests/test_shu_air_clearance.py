from math import pi, sqrt

import pytest
import torch

from wheelleg.shu_air_clearance import AirBirthClearance, retry_air_births, validate_air_collision
from wheelleg.shu_spawn import SpawnState


def model_links():
    # Model-only fixture: guide rotates on a displaced hinge and carries a translating child.
    return {
        "base": {"vertices_m": [(0, 0, -0.2)]},
        "guide": dict(
            parent="base",
            motion="revolute",
            joint="guide_hinge",
            axis_parent=[0, 1, 0],
            pivot_parent_m=[0.2, 0, 0],
            zero_xyz_m=[0.3, 0, 0],
            zero_quat_wxyz=[1, 0, 0, 0],
            vertices_m=[[0.2, 0, -0.05]],
        ),
        "foot": dict(
            parent="guide",
            motion="prismatic",
            joint="extension",
            axis_parent=[1, 0, 0],
            zero_xyz_m=[0, 0, 0],
            zero_quat_wxyz=[sqrt(0.5), 0, 0, sqrt(0.5)],
            vertices_m=[[0, -0.3, 0]],
        ),
    }


def make_clearance(links):
    return AirBirthClearance(
        links,
        base="base",
        colliders=("base", "guide", "foot"),
        body_names=("base", "foot", "guide"),
        joint_names=("extension", "guide_hinge"),
        like=torch.empty(0, dtype=torch.float64),
    )


def test_fk_takes_lowest_point_across_links_with_turn_tilt_and_asset_joint_order():
    clearance = make_clearance(model_links())
    root = torch.zeros(4, 13, dtype=torch.float64)
    root[:, 2:4] = torch.tensor([0.50, 1], dtype=root.dtype)
    root[3, 3:7] = torch.tensor([sqrt(0.5), 0, sqrt(0.5), 0], dtype=root.dtype)
    q = torch.tensor([[0, 0], [0, pi / 2], [0.2, pi / 2], [0, 0]], dtype=root.dtype)
    expected = root.new_tensor([0.3, 0.1, -0.1, -0.1])
    torch.testing.assert_close(clearance.minimum_z(root, q), expected, atol=1e-12, rtol=0)


def test_readiness_rejects_omitted_collider_and_runtime_rejects_unmapped_joint():
    links = model_links()
    with pytest.raises(ValueError, match="missing.*wheel"):
        validate_air_collision(links, "base", [*links, "wheel"])
    links["guide"]["joint"] = "absent"
    with pytest.raises(ValueError, match="not a unique launched USD DOF"):
        make_clearance(links)


def test_impossible_band_fails_without_advancing_physics(monkeypatch):
    from types import SimpleNamespace

    from wheelleg import shu_air_clearance

    root = torch.zeros(2, 13, dtype=torch.float64)
    root[:, 2:4] = root.new_tensor([0.1, 1])
    q = root.new_zeros(2, 2)
    state = SpawnState(root, *(q.clone() for _ in range(6)))
    draws = []

    def draw(kinds, offset, cfg):
        draws.append(offset)
        return SpawnState(root[:1].clone(), *(q[:1].clone() for _ in range(6)))

    monkeypatch.setattr(shu_air_clearance, "sample_spawn", draw)
    with pytest.raises(ValueError, match=r"height bands \[1\]"):
        retry_air_births(
            state,
            q,
            q.clone(),
            rows=torch.tensor([0]),
            band=torch.tensor([1, -1]),
            edges_m=root.new_tensor([0.05, 0.1, 0.2]),
            spawn=None,
            mapping=None,
            model=SimpleNamespace(resolve=lambda sample, mapping, limits: (q[:1].clone(), q[:1].clone())),
            limits=q,
            clearance=make_clearance(model_links()),
        )
    assert draws and all(0.1 < offset.item() <= 0.2 for offset in draws)
