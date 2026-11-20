from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
import torch
import yaml
from test_shu_mixed_variants import terrain_module as terrain_module

from wheelleg.shu_terrain import STAIR_PROFILES, MixedTerrainRuntime, mixed_columns, stair_lip_dimensions


@pytest.fixture
def p1_terrain():
    path = Path(__file__).resolve().parents[1] / "config/policies/p1/policy_meta.yaml"
    settings = yaml.safe_load(path.read_text(encoding="utf-8"))["stages"]["stairs"]["terrain"]
    # Only supply unmeasured fields needed to build route bounds or meshes; keep the shipped mix and stair dimensions.
    settings["route"]["clearance_m"] = 0.25
    for name, profile in settings["profiles"].items():
        if profile["row_range"] is None:
            profile["row_range"] = [0, settings["rows"] - 1]
        if name in STAIR_PROFILES:
            profile["geometry"]["ground_thickness_m"] = 0.10
    return settings


def test_shipped_p1_mix_samples_both_variants_in_each_tower_task_and_direction(p1_terrain):
    columns = mixed_columns(p1_terrain)
    ids = torch.arange(16_000)
    zeros = torch.zeros_like(ids)
    terrain = SimpleNamespace(
        terrain_origins=torch.zeros(p1_terrain["rows"], len(columns), 3),
        terrain_types=zeros.clone(),
        terrain_levels=zeros.clone(),
        env_origins=torch.zeros(len(ids), 3),
    )
    with torch.random.fork_rng(devices=[]):
        torch.manual_seed(11)
        mix = MixedTerrainRuntime(p1_terrain, len(ids), "cpu")
        mix.reset(terrain, ids, zeros.bool(), zeros.bool(), evaluation=False)
    profile, lip, pyramid = torch.tensor(
        [
            (STAIR_PROFILES.index(name) if name in STAIR_PROFILES else -1, raised, tower)
            for name, raised, tower in columns
        ]
    )[terrain.terrain_types].unbind(-1)
    stair = profile >= 0
    assert torch.equal(stair, pyramid.bool())
    assert stair.float().mean().item() == pytest.approx(0.45, abs=0.02)
    raised = profile == STAIR_PROFILES.index("pyramid_up")
    assert not (mix.reverse_descent & ~raised).any()
    for task, share in ((stair & ~raised, 0.45), (raised & ~mix.reverse_descent, 0.45), (mix.reverse_descent, 0.10)):
        assert task.sum().item() / stair.sum().item() == pytest.approx(share, abs=0.02)
        assert lip[task].float().mean().item() == pytest.approx(0.50, abs=0.05)


def test_shipped_p1_tower_grid_keeps_every_raised_ring(terrain_module, p1_terrain):  # noqa: F811 (shared fixture)
    sx, sy = p1_terrain["tile_size_m"]
    lift, depth = stair_lip_dimensions(p1_terrain)
    assert (lift, depth) == pytest.approx((0.05, 0.10))
    generator = terrain_module.MixedTerrainGenerator()
    generator.cfg = SimpleNamespace(
        difficulty_range=(0, 1),
        num_rows=p1_terrain["rows"],
        sub_terrains={
            (name, raised): SimpleNamespace(
                size=(sx, sy),
                profile=name,
                parameters=p1_terrain["profiles"][name]["geometry"],
                stair_lip=(lift, depth) if raised else None,
                pyramid=True,
            )
            for name, raised, pyramid in mixed_columns(p1_terrain)
            if pyramid
        },
    )
    assert len(generator.cfg.sub_terrains) == 4
    assert generator.cfg.num_rows == 10
    generator.np_rng = np.random.default_rng(42)

    def get_mesh(difficulty, cfg):
        (mesh,), center_origin = terrain_module.mixed_terrain(difficulty, cfg)
        return mesh, (difficulty, center_origin)

    generator._get_terrain_mesh = get_mesh
    heights = {}

    def check_row(mesh, origin_and_difficulty, row, _col, cfg):
        difficulty, origin = origin_and_difficulty
        assert tuple(origin[:2]) == (sx / 2, sy / 2)
        np.testing.assert_array_equal(mesh.triangles[-2:, :, 2], origin[2])
        assert (origin[2] > 0) if cfg.profile == "pyramid_up" else (origin[2] < 0)
        top = mesh.face_normals[:, 2] > 0.999
        centers = mesh.triangles_center[top]
        z = centers[:, 2]
        xy = np.abs(centers[:, :2] - (sx / 2, sy / 2))
        area = mesh.area_faces[top]
        low, high = cfg.parameters["step_height_range_m"]
        assert (low, high) == pytest.approx((0.10, 0.23))
        height = low + difficulty * (high - low)
        if row in (0, generator.cfg.num_rows - 1):
            assert height == pytest.approx(low if row == 0 else high)
        key = (cfg.profile, row)
        assert height == heights.setdefault(key, height)
        direction = cfg.profile.split("_")[-1]
        tread = cfg.parameters["step_width_m"]
        assert tread == pytest.approx(0.30) and cfg.parameters["platform_width_m"] == pytest.approx(4.0)
        # Count vertical riser faces independently on a ray parallel to the X axis, facing +X.
        normals = mesh.face_normals
        wall = (
            (np.abs(normals[:, 0]) > 0.999)
            & (mesh.triangles_center[:, 0] > 0.001)
            & (mesh.triangles_center[:, 0] < sx / 2)
        )
        positions = np.unique(np.round(mesh.triangles_center[wall, 0], 8))
        expected_normal = -1 if direction == "up" else 1
        principal = np.unique(np.round(mesh.triangles_center[wall & (normals[:, 0] * expected_normal > 0.999), 0], 8))
        count = len(principal)
        assert cfg.parameters["first_edge_x_m"] == pytest.approx(0.60)
        assert count == 12
        outer_obstruction_x = principal[0] - (depth if cfg.stair_lip is not None and direction == "down" else 0)
        assert outer_obstruction_x == pytest.approx(0.60 if cfg.stair_lip is not None else 0.70)

        assert count >= 2 and len(positions) == count * (2 if cfg.stair_lip is not None else 1)
        np.testing.assert_allclose(np.diff(principal), tread, atol=1e-6)
        start = principal[0]
        assert start >= cfg.parameters["first_edge_x_m"] - 1e-6
        if cfg.stair_lip is None:
            sign = 1 if direction == "up" else -1
            assert np.unique(np.round(z, 8)) == pytest.approx(sorted(sign * height * i for i in range(count + 1)))
            return
        # Check the whole horizontal crest area, not just a cross-section that could miss gaps around the rim.
        for i in range(count):
            x = sx / 2 - start - i * tread
            y = min(sx, sy) / 2 - start - i * tread
            if direction == "up":
                crest = i * (height - lift) + height
                inner, outer = (x - depth, y - depth), (x, y)
            else:
                crest = -i * (height - lift) + lift
                inner, outer = (x, y), (x + depth, y + depth)
            # At the lowest row a neighbouring deck can share this Z; restrict to this ring's footprint.
            ring = (xy <= outer).all(axis=1) & (xy >= inner).any(axis=1)
            expected = 4 * (np.prod(outer) - np.prod(inner))
            assert area[ring & np.isclose(z, crest)].sum() == pytest.approx(expected), (cfg.profile, row, i)

    generator._add_sub_terrain = check_row
    generator._generate_curriculum_terrains()
    assert len(heights) == len(STAIR_PROFILES) * generator.cfg.num_rows
