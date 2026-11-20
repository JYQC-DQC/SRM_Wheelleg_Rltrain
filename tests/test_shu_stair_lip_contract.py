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
            profile["geometry"].update(spawn_x_m=1.0, first_edge_x_m=3.0, ground_thickness_m=0.10)
    return settings


def test_shipped_p1_mix_samples_both_variants_in_each_tower_task_and_step_count(p1_terrain):
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
    up = (
        (profile == STAIR_PROFILES.index("single_up"))
        | (profile == STAIR_PROFILES.index("double_up"))
        | (profile == STAIR_PROFILES.index("triple_up"))
    )
    for task, share, direction in (
        (up, 0.45, "up"),
        (stair & ~up & ~mix.reverse_descent, 0.45, "down"),
        (mix.reverse_descent, 0.10, "down"),
    ):
        assert task.sum().item() / stair.sum().item() == pytest.approx(share, abs=0.02)
        for steps, fraction in (("single", 0.20), ("double", 0.60), ("triple", 0.20)):
            subset = task & (profile == STAIR_PROFILES.index(f"{steps}_{direction}"))
            assert subset.sum().item() / task.sum().item() == pytest.approx(fraction, abs=0.06)
            assert lip[subset].float().mean().item() == pytest.approx(0.50, abs=0.10)


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
    assert len(generator.cfg.sub_terrains) == 12
    assert generator.cfg.num_rows == 10
    generator.np_rng = np.random.default_rng(42)
    generator._get_terrain_mesh = lambda difficulty, cfg: (
        terrain_module.mixed_terrain(difficulty, cfg)[0][0],
        difficulty,
    )
    heights = {}

    def check_row(mesh, difficulty, row, _col, cfg):
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
        steps, direction = cfg.profile.split("_")
        count = ("single", "double", "triple").index(steps) + 1
        tread = cfg.parameters["step_width_m"]
        start = cfg.parameters["first_edge_x_m"]
        assert tread == pytest.approx(0.30)
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
