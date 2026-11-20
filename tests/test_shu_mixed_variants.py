import importlib.util
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import numpy as np
import pytest
import torch

from wheelleg.shu_terrain import (
    MIXED_COLUMN_PROFILES,
    MIXED_PROFILES,
    STAIR_PROFILES,
    MixedTerrainRuntime,
    mixed_columns,
    natural_pyramid_layout,
)


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


def test_generator_pairs_stair_difficulties(terrain_module):
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
    for col in range(4, 6):
        for row in range(10):
            assert pairs[col, row] == pairs[col + 2, row]
            if row in (0, 9):
                assert pairs[col, row] == (1.0 if row == 9 else 0.0)
            else:
                assert row / 10 <= pairs[col, row] < (row + 1) / 10


@pytest.mark.parametrize(("name", "sign"), [("slope", 1), ("slope_inverted", -1)])
@pytest.mark.parametrize("angle_deg", [0, 25])
def test_four_sided_slope_geometry_and_spawn(terrain_module, name, sign, angle_deg):
    parameters = dict(platform_width_m=3.0, slope_angle_range_rad=np.deg2rad([0, 25]))
    cfg = SimpleNamespace(profile=name, size=(12, 12), parameters=parameters)
    (mesh,), origin = terrain_module.mixed_terrain(angle_deg / 25, cfg)
    center_z = sign * 4.5 * np.tan(np.deg2rad(angle_deg))
    assert origin == pytest.approx((6, 6, center_z))
    np.testing.assert_allclose(mesh.bounds, ((0, 0, min(0, center_z)), (12, 12, max(0, center_z))))
    assert (mesh.face_normals[:, 2] > 0).all()
    assert mesh.area_faces.sum() == pytest.approx(9 + (144 - 9) / np.cos(np.deg2rad(angle_deg)))

    if angle_deg == 0:
        np.testing.assert_allclose(mesh.vertices[:, 2], 0)
        return
    normals = mesh.face_normals
    flat = np.isclose(normals[:, 2], 1)
    deck_xy = mesh.triangles[flat, :, :2].reshape(-1, 2)
    np.testing.assert_allclose(deck_xy.min(axis=0), (4.5, 4.5))
    np.testing.assert_allclose(deck_xy.max(axis=0), (7.5, 7.5))
    np.testing.assert_allclose(mesh.triangles[flat, :, 2], origin[2])
    assert mesh.area_faces[flat].sum() == pytest.approx(9)
    pitch = np.arctan2(np.linalg.norm(normals[~flat, :2], axis=1), normals[~flat, 2])
    np.testing.assert_allclose(np.rad2deg(pitch), 25)
    directions = np.unique(np.round(normals[~flat, :2] / np.sin(pitch)[:, None]), axis=0)
    np.testing.assert_array_equal(directions, [(-1, 0), (0, -1), (0, 1), (1, 0)])
    perimeter = (np.isclose(mesh.vertices[:, :2], 0) | np.isclose(mesh.vertices[:, :2], 12)).any(axis=1)
    np.testing.assert_allclose(mesh.vertices[perimeter, 2], 0)


def test_generator_pairs_slope_difficulties_and_locks_endpoints(terrain_module):
    profiles = ("slope", "slope_inverted")
    parameters = dict(platform_width_m=3.0, slope_angle_range_rad=np.deg2rad([0, 25]))
    gen = terrain_module.MixedTerrainGenerator()
    gen.cfg = SimpleNamespace(
        difficulty_range=(0, 1),
        num_rows=10,
        sub_terrains={name: SimpleNamespace(profile=name, size=(12, 12), parameters=parameters) for name in profiles},
    )
    gen.np_rng = np.random.default_rng(5)
    gen._get_terrain_mesh = lambda difficulty, cfg: (difficulty, terrain_module.mixed_terrain(difficulty, cfg)[1])
    draws, heights = np.empty((10, 2)), np.empty((10, 2))

    def store(difficulty, origin, row, col, cfg):
        draws[row, col] = difficulty
        heights[row, col] = origin[2]

    gen._add_sub_terrain = store
    gen._generate_curriculum_terrains()
    np.testing.assert_array_equal(draws[:, 0], draws[:, 1])
    np.testing.assert_array_equal(draws[[0, -1]], ((0, 0), (1, 1)))
    assert (np.diff(draws[:, 0]) > 0).all()
    np.testing.assert_allclose(heights, np.tan(np.deg2rad(25 * draws)) * (4.5, -4.5))


def settings():
    return dict(
        rows=3,
        tile_size_m=(12.0, 12.0),
        route=dict(vx_range_m_s=(0.5, 1.0), clearance_m=0.2, reverse_descent_share_of_stairs=0.1),
        stair_lip=dict(height_m=0.05, width_m=0.10),
        groups=dict(rough=0.1, grid=0.1, slope=0.1, stairs=0.4),
        profiles={
            name: dict(
                row_range=[0, 2],
                command_mode="traverse" if name in STAIR_PROFILES else "free",
                geometry=dict(
                    ground_thickness_m=0.1,
                    first_edge_x_m=1.4,
                    step_width_m=0.30,
                    step_height_range_m=(0.10, 0.23),
                    platform_width_m=4.0,
                ),
            )
            for name in MIXED_PROFILES
        },
    )


def test_lip_coin_is_independent_of_curriculum_and_eval_does_not_advance_rows():
    torch.manual_seed(5)
    count = 12000
    cfg = settings()
    columns = mixed_columns(cfg, production=True)
    assert columns == [
        ("flat", False, False),
        ("rough", False, False),
        ("grid", False, False),
        ("slope", False, False),
        ("pyramid_up", False, True),
        ("pyramid_down", False, True),
        ("pyramid_up", True, True),
        ("pyramid_down", True, True),
        ("slope_inverted", False, False),
    ]
    mix = MixedTerrainRuntime(cfg, count, "cpu")
    rows, cols = 3, len(columns)
    terrain = SimpleNamespace(
        terrain_origins=torch.arange(rows * cols * 3, dtype=torch.float32).reshape(rows, cols, 3),
        terrain_levels=torch.zeros(count, dtype=torch.long),
        terrain_types=torch.zeros(count, dtype=torch.long),
        env_origins=torch.zeros(count, 3),
    )
    ids = torch.arange(count)
    no = torch.zeros(count, dtype=torch.bool)

    def check_draws():
        histogram = terrain.terrain_types.bincount(minlength=cols)
        assert histogram.sum() == count
        for col in range(4, 6):
            sharp, lip = histogram[col], histogram[col + 2]
            assert (lip / (sharp + lip)).item() == pytest.approx(0.5, abs=0.06)
        torch.testing.assert_close(
            terrain.env_origins, terrain.terrain_origins[terrain.terrain_levels, terrain.terrain_types]
        )
        torch.testing.assert_close(mix.traverse, (terrain.terrain_types >= 4) & (terrain.terrain_types <= 7))
        assert ((histogram[3] + histogram[8]) / count).item() == pytest.approx(0.10, abs=0.012)
        assert (histogram[8] / (histogram[3] + histogram[8])).item() == pytest.approx(0.50, abs=0.06)

    mix.reset(terrain, ids, no, no, evaluation=False)
    check_draws()
    torch.testing.assert_close(terrain.terrain_levels[mix.traverse], mix.stair_rows.levels[mix.traverse])
    before = mix.stair_rows.levels.clone()
    mix.reset(terrain, ids, ~no, no, evaluation=True)
    check_draws()
    torch.testing.assert_close(mix.stair_rows.levels, before)
    assert (terrain.terrain_levels == 2).all()


def test_unconfirmed_lip_depth_is_not_replaced_with_a_default():
    cfg = settings()
    cfg["stair_lip"]["width_m"] = None
    with pytest.raises(ValueError, match=r"terrain\.stair_lip.*width_m"):
        MixedTerrainRuntime(cfg, 1, "cpu")


@pytest.mark.parametrize("name", STAIR_PROFILES)
@pytest.mark.parametrize("lip", [None, (0.05, 0.10)])
@pytest.mark.parametrize("size,border,counts", [((12, 12), 2.0, (7, 7)), ((12, 8), 1.4, (3, 2))])
def test_natural_pyramid_has_exact_clear_center_and_full_riser_pitch(terrain_module, name, lip, size, border, counts):
    geometry = settings()["profiles"][name]["geometry"]
    geometry["first_edge_x_m"] = border
    cfg = SimpleNamespace(size=size, profile=name, parameters=geometry, stair_lip=lip)
    (mesh,), origin = terrain_module.mixed_terrain(1.0, cfg)
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0
    sx, sy = size
    down = name == "pyramid_down"
    count = counts[lip is not None]
    assert tuple(origin[:2]) == (sx / 2, sy / 2)

    # Measure both the actual top cap and the principal X risers, not just the layout inputs.
    cap = mesh.triangles[-2:].reshape(-1, 3)
    assert tuple(cap[:, :2].min(axis=0)) == (sx / 2 - 2.0, sy / 2 - 2.0)
    assert tuple(cap[:, :2].max(axis=0)) == (sx / 2 + 2.0, sy / 2 + 2.0)
    sign = -1 if down else 1
    assert cap[:, 2] == pytest.approx(np.full(6, sign * count * (0.18 if lip else 0.23)))
    np.testing.assert_array_equal(cap[:, 2], origin[2])
    centers, normals = mesh.triangles_center, mesh.face_normals
    internal_wall = (np.abs(normals[:, 0]) > 0.999) & (centers[:, 0] > 0) & (centers[:, 0] < sx)
    principal = internal_wall & (np.sign(normals[:, 0] * (centers[:, 0] - sx / 2)) == sign)
    edges = np.unique(np.round(centers[principal & (centers[:, 0] < sx / 2), 0], 8))
    assert len(edges) == count
    np.testing.assert_allclose(np.diff(edges), 0.30)
    for x in edges:
        assert np.ptp(mesh.triangles[principal & np.isclose(centers[:, 0], x), :, 2]) == pytest.approx(0.23)
    if lip:
        lip_edges = np.unique(np.round(centers[internal_wall & ~principal & (centers[:, 0] < sx / 2), 0], 8))
        assert lip_edges == pytest.approx(edges + sign * lip[1])

    first_obstruction_x = centers[internal_wall, 0].min()
    actual_apron_short_axis = first_obstruction_x - (sx - min(size)) / 2
    assert border - 1e-8 <= actual_apron_short_axis < border + 0.30


def test_pending_border_and_tile_with_no_room_for_riser_fail_clearly():
    geometry = settings()["profiles"]["pyramid_up"]["geometry"]
    geometry["first_edge_x_m"] = None
    with pytest.raises(ValueError, match="first_edge_x_m"):
        natural_pyramid_layout((12, 12), geometry, down=False, lip_width_m=0.1)
    geometry["first_edge_x_m"] = 3.95
    with pytest.raises(ValueError, match="cannot fit a riser"):
        natural_pyramid_layout((12, 12), geometry, down=False, lip_width_m=0.1)


def test_rough_shipped_config_and_native_heightfield_column(terrain_module):
    from pathlib import Path

    import yaml

    policy = Path(__file__).resolve().parents[1] / "config/policies/p1/policy_meta.yaml"
    rough = yaml.safe_load(policy.read_text(encoding="utf8"))["stages"]["stairs"]["terrain"]["profiles"]["rough"]
    assert rough["geometry"] == dict(
        noise_range=[0, 0.03],
        noise_step=0.005,
        downsampled_scale=0.20,
        border_width=1.0,
        horizontal_scale=0.10,
        vertical_scale=0.005,
        slope_threshold=0.5,
    )
    g = terrain_module.MixedTerrainGenerator()
    native = SimpleNamespace(proportion=1.0)  # native hf config has no .profile attribute
    g.cfg = SimpleNamespace(difficulty_range=(0, 1), num_rows=2, sub_terrains={"rough": native})
    g.np_rng = np.random.default_rng(12)
    calls = []
    g._get_terrain_mesh = lambda difficulty, cfg: (None, None)
    g._add_sub_terrain = lambda mesh, origin, row, col, cfg: calls.append((row, col, cfg))
    g._generate_curriculum_terrains()
    assert calls == [(0, 0, native), (1, 0, native)]
