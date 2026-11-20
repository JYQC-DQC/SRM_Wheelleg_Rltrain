import importlib.util
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import numpy as np
import pytest
import torch

from wheelleg.shu_terrain import MIXED_COLUMN_PROFILES, MIXED_PROFILES, STAIR_PROFILES, MixedTerrainRuntime


@pytest.fixture
def terrain_module(monkeypatch):
    pytest.importorskip("trimesh")
    # Use real mesh operations without starting Isaac Sim or caching stub bindings.
    terrains = ModuleType("isaaclab.terrains")
    terrains.SubTerrainBaseCfg = terrains.TerrainGenerator = object
    utils = ModuleType("isaaclab.utils")
    utils.configclass = lambda cls: cls
    monkeypatch.setitem(sys.modules, "isaaclab.terrains", terrains)
    monkeypatch.setitem(sys.modules, "isaaclab.utils", utils)
    path = Path(__file__).resolve().parents[1] / "isaac/wheelleg_tasks/terrain.py"
    spec = importlib.util.spec_from_file_location("mixed_terrain_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(("name", "count"), [("single", 1), ("double", 2), ("triple", 3)])
def test_lip_is_closed_mirrored_and_keeps_the_outer_riser_height(terrain_module, name, count):
    sx, sy = 12, 12
    riser_height, lip_height, lip_depth = 0.20, 0.05, 0.10  # Synthetic depth, not a calibration.
    tread = 0.30
    first = (sx - (count - 1) * tread) / 2
    cfg = SimpleNamespace(
        profile=f"{name}_up",
        size=(sx, sy),
        parameters=dict(
            spawn_x_m=1.0,
            first_edge_x_m=first,
            ground_thickness_m=0.10,
            step_width_m=tread,
            step_height_range_m=(riser_height, riser_height),
        ),
        stair_lip=None,
    )
    sharp, _ = terrain_module.mixed_terrain(1.0, cfg)
    cfg.stair_lip = (lip_height, lip_depth)
    (up,), up_origin = terrain_module.mixed_terrain(1.0, cfg)
    cfg.profile = f"{name}_down"
    (down,), down_origin = terrain_module.mixed_terrain(1.0, cfg)
    for mesh in (up, down):
        assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0
        assert len(mesh.split()) == 1

    def face_height(mesh, x):
        at_x = np.isclose(mesh.triangles[:, :, 0], x).all(axis=1)
        axial = np.isclose(np.abs(mesh.face_normals[:, 0]), 1)
        return np.ptp(mesh.triangles[at_x & axial, :, 2])

    for i in range(count):
        x = first + i * tread
        sharp_height = sharp[i + 1].bounds[1, 2] - sharp[i].bounds[1, 2]
        assert face_height(up, x) == pytest.approx(sharp_height)
        assert face_height(up, x + lip_depth) == pytest.approx(lip_height)
        assert face_height(down, sx - x - lip_depth) == pytest.approx(lip_height)
        assert face_height(down, sx - x) == pytest.approx(sharp_height)
    mirrored_x = up.vertices.copy()
    mirrored_x[:, 0] = sx - mirrored_x[:, 0]
    unique_points = lambda points: set(map(tuple, np.round(points, 8)))  # noqa: E731
    assert unique_points(mirrored_x) == unique_points(down.vertices)
    assert up_origin[2] == 0.0
    assert down_origin[2] == pytest.approx(count * (riser_height - lip_height))


def test_generator_pairs_difficulties_and_slope_mesh_reaches_25_degrees(terrain_module):
    pairs = {}
    gen = terrain_module.MixedTerrainGenerator()
    gen.cfg = SimpleNamespace(
        difficulty_range=(0, 1),
        num_rows=10,
        sub_terrains={i: SimpleNamespace(profile=name) for i, name in enumerate(MIXED_COLUMN_PROFILES)},
    )
    gen.np_rng = np.random.default_rng(5)
    gen._get_terrain_mesh = lambda difficulty, cfg: (difficulty, None)
    gen._add_sub_terrain = lambda difficulty, _origin, row, col, _cfg: pairs.update({(col, row): difficulty})
    gen._generate_curriculum_terrains()
    for col in range(4, 10):
        for row in range(10):
            assert pairs[col, row] == pairs[col + 6, row]
            if row in (0, 9):
                assert pairs[col, row] == (1.0 if row == 9 else 0.0)
            else:
                assert row / 10 <= pairs[col, row] < (row + 1) / 10

    angles = np.deg2rad([0, 25])
    slope_col = MIXED_PROFILES.index("slope")
    (mesh,) = terrain_module._slope_mesh(pairs[slope_col, 9], (12, 12), angles)
    actual_angle = np.arctan2(np.abs(mesh.face_normals[:, 0]), mesh.face_normals[:, 2]).max()
    assert pairs[slope_col, 0] == 0.0
    assert np.rad2deg(actual_angle) == pytest.approx(25.0)


def settings():
    return dict(
        rows=3,
        tile_size_m=(12.0, 12.0),
        route=dict(
            vx_range_m_s=(0.5, 1.0), heading_kp=2.0, heading_max_wz_rad_s=1.0, corridor_width_m=2.0, clearance_m=0.2
        ),
        stair_lip=dict(height_m=0.05, width_m=0.10),
        groups=dict(rough=0.1, grid=0.1, slope=0.1, stairs=0.4),
        locked_stair_weights=dict(single=0.3, double=0.7),
        stair_weights={name: 0.6 if name.startswith("double") else 0.2 for name in STAIR_PROFILES},
        gates={name: dict(row=1, window=2, success_fraction=1.0) for name in STAIR_PROFILES[:4]},
        profiles={
            name: dict(
                row_range=[1, 2] if name in STAIR_PROFILES else [0, 2],
                command_mode="traverse" if name in STAIR_PROFILES else "free",
                exit_distance_m=3.0,
                geometry=dict(spawn_x_m=1.0, first_edge_x_m=2.0, step_width_m=0.30),
            )
            for name in MIXED_PROFILES
        },
    )


def test_reset_samples_variants_and_counts_both_in_the_same_gate():
    torch.manual_seed(5)
    count = 12000
    mix = MixedTerrainRuntime(settings(), count, "cpu")
    rows, cols = 3, len(MIXED_COLUMN_PROFILES)
    terrain = SimpleNamespace(
        terrain_origins=torch.arange(rows * cols * 3, dtype=torch.float32).reshape(rows, cols, 3),
        terrain_levels=torch.zeros(count, dtype=torch.long),
        terrain_types=torch.zeros(count, dtype=torch.long),
        env_origins=torch.zeros(count, 3),
    )
    ids = torch.arange(count)
    no = torch.zeros(count, dtype=torch.bool)

    def check_draws(active):
        histogram = terrain.terrain_types.bincount(minlength=cols)
        assert histogram.sum() == count
        for col in range(4, 10):
            sharp, lip = histogram[col], histogram[col + 6]
            if col in active:
                assert (lip / (sharp + lip)).item() == pytest.approx(0.5, abs=0.06)
            else:
                assert sharp + lip == 0
        torch.testing.assert_close(
            terrain.env_origins, terrain.terrain_origins[terrain.terrain_levels, terrain.terrain_types]
        )
        torch.testing.assert_close(mix.traverse, terrain.terrain_types >= 4)

    mix.reset(terrain, ids, no, no, evaluation=False)
    check_draws(range(4, 8))
    assert (terrain.terrain_levels[mix.traverse] >= 1).all()
    torch.testing.assert_close(mix.weights[4:], torch.tensor([0.06, 0.14, 0.06, 0.14, 0.0, 0.0]))

    # One sharp and one lip success at the required row for each ascent prerequisite.
    terrain.terrain_types[:4] = torch.tensor([4, 10, 5, 11])
    terrain.terrain_levels[:4] = 1
    terrain.env_origins[:4] = terrain.terrain_origins[1, terrain.terrain_types[:4]]
    mix.traverse[:4] = True
    mix.step(terrain, terrain.env_origins, terrain.env_origins + torch.tensor([3.1, 0, 0]), torch.ones(count), no)
    assert mix.crossed[:4].all()
    mix.reset(terrain, ids[:4], ~no, no, evaluation=False)
    assert mix.unlocked == {"triple_up": True, "triple_down": False}
    torch.testing.assert_close(mix.weights[:4], torch.tensor([0.30, 0.10, 0.10, 0.10]))
    torch.testing.assert_close(mix.weights[4:], torch.tensor([0.04, 0.12, 0.06, 0.14, 0.04, 0.0]))

    restored = MixedTerrainRuntime(settings(), count, "cpu")
    restored.load_state_dict(mix.state_dict())
    torch.testing.assert_close(restored.weights, mix.weights)
    mix = restored
    mix.reset(terrain, ids, no, no, evaluation=True)
    check_draws(range(4, 9))
    assert (terrain.terrain_levels == 2).all()


def test_unconfirmed_lip_depth_is_not_replaced_with_a_default():
    cfg = settings()
    cfg["stair_lip"]["width_m"] = None
    with pytest.raises(ValueError, match=r"terrain\.stair_lip.*width_m"):
        MixedTerrainRuntime(cfg, 1, "cpu")


@pytest.mark.parametrize("down", [False, True])
@pytest.mark.parametrize("lip", [None, (0.05, 0.15)])
def test_double_pyramid_crosses_four_main_risers(terrain_module, down, lip):
    mesh = terrain_module._pyramid_mesh((12, 12), 3, 0.30, 2, 0.23, down, 0.10, lip)
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0
    # Probe horizontal faces on the central traverse, slightly off triangulation diagonals.
    top = mesh.face_normals[:, 2] > 0.999

    def height(x):
        for tri in mesh.triangles[top]:
            a, b, c = tri[:, :2]
            uv = np.linalg.solve(np.stack((b - a, c - a), axis=1), np.array([x, 6.015]) - a)
            if min(uv) >= 0 and sum(uv) <= 1:
                return tri[0, 2]
        raise AssertionError(x)

    h = 0.18 if lip else 0.23
    sign = -1 if down else 1
    pos = 3.08 if down else 3.20  # outside lip on first tread
    assert [height(x) for x in (1, pos, 6, 12 - pos, 11)] == pytest.approx([0, sign * h, sign * 2 * h, sign * h, 0])
    assert height(6) == pytest.approx(sign * 2 * h)
    assert height(1) == height(11) == 0
    if lip:
        for edge in (3, 3.30, 8.70, 9):
            assert abs(height(edge - 0.001) - height(edge + 0.001)) == pytest.approx(0.23)


def test_mixed_pyramid_counts_far_exit_and_does_not_unlock_pure_gates():
    from wheelleg.shu_terrain import mixed_columns

    cfg = settings()
    cfg["pyramid"] = {"share_of_stairs": 1.0}
    # Extend far enough to cross the full geometric profile, not just the first flank.
    cfg["route"]["corridor_width_m"] = 1.0
    mix = MixedTerrainRuntime(cfg, 512, "cpu")
    cols = mixed_columns(cfg)
    t = SimpleNamespace(
        terrain_origins=torch.zeros(3, len(cols), 3),
        terrain_levels=torch.zeros(512, dtype=torch.long),
        terrain_types=torch.zeros(512, dtype=torch.long),
        env_origins=torch.zeros(512, 3),
    )
    ids = torch.arange(512)
    no = ids < 0
    mix.reset(t, ids, no, no, evaluation=True)
    assert (t.terrain_types[mix.traverse] >= 16).all()
    assert set(t.terrain_types[mix.traverse].tolist()) == {16, 17, 18, 19, 22, 23, 24, 25}
    x = mix.exit_distances[t.terrain_types]
    start = t.env_origins
    mid = start.clone()
    mid[:, 0] = x * 0.5
    mix.step(t, start, mid, torch.ones_like(x), no)
    assert not mix.crossed.any()
    end = start.clone()
    end[:, 0] = x + 0.01
    mix.step(t, mid, end, torch.ones_like(x), no)
    assert torch.equal(mix.traverse, mix.crossed)
    mix.reset(t, ids, ~no, no, evaluation=False)
    assert not any(mix.passed.values())
    assert list(mix.counts.values()) == [(0, 0)] * 4
    mix.unlocked["triple_up"] = True
    mix._update_weights()
    assert mix.weights[MIXED_PROFILES.index("triple_up")] == 0
    mix.reset(t, ids, no, no, evaluation=True)
    assert (t.terrain_types[mix.traverse] >= 16).all()
