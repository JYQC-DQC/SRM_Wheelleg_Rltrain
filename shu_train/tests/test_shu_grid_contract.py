from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
import yaml
from test_shu_mixed_variants import terrain_module as terrain_module

from shu_train.wheelleg.shu_terrain import mixed_columns


@pytest.fixture
def grid_config():
    path = Path(__file__).resolve().parents[1] / "config/policies/p1/policy_meta.yaml"
    terrain = yaml.safe_load(path.read_text(encoding="utf-8"))["stages"]["stairs"]["terrain"]
    grid = terrain["profiles"]["grid"]
    assert tuple(terrain["tile_size_m"]) == (12.0, 12.0)
    assert terrain["groups"]["grid"] == 0.10
    assert grid["command_mode"] == "free"
    assert grid["row_range"] == [0, terrain["rows"] - 1] == [0, 9]
    assert [c for c in mixed_columns(terrain, production=True) if c[0] == "grid"] == [("grid", False, False)]
    return SimpleNamespace(size=tuple(terrain["tile_size_m"]), profile="grid", parameters=grid["geometry"])


@pytest.mark.parametrize(("seed", "nh", "nv"), [(1, 4, 4), (2, 4, 2), (5, 2, 4), (11, 2, 2)])
def test_one_grid_row_matches_frozen_mesh_contract(terrain_module, grid_config, monkeypatch, seed, nh, nv):  # noqa: F811 (shared fixture)
    rng = np.random.RandomState(seed)
    width = 0.05 + 0.15 * np.random.RandomState(seed).uniform(size=3)[2]
    monkeypatch.setattr(np.random, "uniform", rng.uniform)
    generator = terrain_module.MixedTerrainGenerator()
    generator.cfg = SimpleNamespace(num_rows=1, difficulty_range=(0.0, 1.0), sub_terrains={"grid": grid_config})
    generator.np_rng = np.random.default_rng(42)
    height = 0.01 + 0.02 * np.random.default_rng(42).uniform()
    generator._get_terrain_mesh = terrain_module.mixed_terrain
    generated = {}
    generator._add_sub_terrain = lambda meshes, origin, row, col, cfg: generated.update({(row, col): (meshes, origin)})
    generator._generate_curriculum_terrains()

    assert set(generated) == {(0, 0)}
    meshes, origin = generated[0, 0]
    np.testing.assert_allclose(origin, (6.0, 6.0, height))
    np.testing.assert_allclose(meshes[0].bounds, ((0.0, 0.0, -0.05), (12.0, 12.0, 0.0)))
    bars = np.array([mesh.bounds for mesh in meshes[1:]])
    lower, upper = bars.transpose(1, 0, 2)
    np.testing.assert_allclose(lower[:, 2], 0.0, atol=1e-12)
    np.testing.assert_allclose(upper[:, 2], height)
    vertical = np.isclose(upper[:, 1] - lower[:, 1], 11.4)
    assert vertical.sum() == nv
    assert (~vertical).sum() == nh * (nv + 1)
    np.testing.assert_allclose(lower[vertical, 1], 0.30)
    np.testing.assert_allclose(upper[vertical, 1], 11.70)
    for intervals, count in ((bars[vertical, :, 0], nv), (bars[~vertical, :, 1], nh)):
        spans = np.unique(intervals.round(10), axis=0)
        assert len(spans) == count
        np.testing.assert_allclose(spans[:, 1] - spans[:, 0], width)
        gaps = np.r_[spans[0, 0], spans[1:, 0] - spans[:-1, 1], 12.0 - spans[-1, 1]]
        np.testing.assert_allclose(gaps, (12.0 - count * width) / (count + 1), atol=1.5e-6, rtol=0)
        assert not ((spans[:, 0] <= 6.0) & (6.0 <= spans[:, 1])).any()

    # Each horizontal line fills the uncovered intervals of its 11.4 m span, right up to each vertical bar.
    cuts = bars[vertical, :, 0][np.argsort(lower[vertical, 0])]
    expected = np.column_stack((np.r_[0.30, cuts[:, 1]], np.r_[cuts[:, 0], 11.70]))
    for y in np.unique(lower[~vertical, 1].round(10)):
        intervals = bars[(~vertical) & np.isclose(lower[:, 1], y), :, 0]
        np.testing.assert_allclose(intervals[np.argsort(intervals[:, 0])], expected)


@pytest.mark.parametrize(("draws", "nv"), [((0.2499, 0.2501, 0.01), 4), ((0.2501, 0.2499, 0.99), 2)])
def test_grid_evenization_and_width_do_not_use_height_difficulty(terrain_module, grid_config, monkeypatch, draws, nv):  # noqa: F811 (shared fixture)
    monkeypatch.setattr(np.random, "uniform", lambda *args, **kwargs: draws)
    low, low_origin = terrain_module.mixed_terrain(0.0, grid_config)
    high, high_origin = terrain_module.mixed_terrain(1.0, grid_config)
    low_bars, high_bars = (np.array([mesh.bounds for mesh in meshes[1:]]) for meshes in (low, high))
    np.testing.assert_array_equal(low_bars[:, :, :2], high_bars[:, :, :2])
    vertical = np.isclose(low_bars[:, 1, 1] - low_bars[:, 0, 1], 11.4)
    assert vertical.sum() == nv
    assert (~vertical).sum() == (6 - nv) * (nv + 1)
    np.testing.assert_allclose(low_bars[vertical, 1, 0] - low_bars[vertical, 0, 0], 0.05 + 0.15 * draws[2])
    np.testing.assert_allclose(low_bars[:, 1, 2], 0.01)
    np.testing.assert_allclose(high_bars[:, 1, 2], 0.03)
    np.testing.assert_allclose((low_origin[2], high_origin[2]), (0.01, 0.03))
