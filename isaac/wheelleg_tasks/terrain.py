from dataclasses import MISSING

import numpy as np
import trimesh
from isaaclab.terrains import SubTerrainBaseCfg
from isaaclab.utils import configclass

from wheelleg.shu_terrain import MIXED_PROFILES


def _slope_mesh(difficulty: float, size, angle_range) -> list:
    sx, sy = size
    angle = angle_range[0] + difficulty * (angle_range[1] - angle_range[0])
    xs = np.array([0.0, sx / 4, sx / 2, 3 * sx / 4, sx])
    zs = np.array([0.0, 0.0, np.tan(angle) * sx / 4, 0.0, 0.0])
    vertices = np.array([(x, y, z) for x, z in zip(xs, zs, strict=True) for y in (0.0, sy)])
    faces = []
    for i in range(4):
        faces.extend(((2 * i, 2 * i + 2, 2 * i + 1), (2 * i + 1, 2 * i + 2, 2 * i + 3)))
    return [trimesh.Trimesh(vertices=vertices, faces=np.array(faces), process=False)]


def mixed_terrain(difficulty: float, cfg) -> tuple[list, np.ndarray]:
    """One tile with explicit geometry, independent of command mode or unlock state."""
    sx, sy = cfg.size
    p, kind = cfg.parameters, cfg.profile
    if kind not in MIXED_PROFILES:
        raise ValueError(f"Unknown SHU mixed terrain profile: {kind}")
    spawn_x = p["spawn_x_m"]
    ground = p["ground_thickness_m"]
    meshes = []

    def box(x0, x1, y0, y1, top, bottom=-ground):
        mesh = trimesh.creation.box((x1 - x0, y1 - y0, top - bottom))
        mesh.apply_translation(((x0 + x1) / 2, (y0 + y1) / 2, (top + bottom) / 2))
        meshes.append(mesh)

    if kind.endswith(("_up", "_down")):
        count = {"single": 1, "double": 2, "triple": 3}[kind.split("_")[0]]
        down = kind.endswith("_down")
        start, width = p["first_edge_x_m"], p["step_width_m"]
        edges = [0, *(start + i * width for i in range(count)), sx]
        if not 0 <= spawn_x < start or not 0 < start <= edges[-2] < sx or width <= 0:
            raise ValueError(f"{kind}: need a clear approach, ordered risers and an exit within the tile")
        height = p["step_height_range_m"][0] + difficulty * np.ptp(p["step_height_range_m"])
        levels = [height * (count - i if down else i) for i in range(count + 1)]
        for left, right, z in zip(edges[:-1], edges[1:], levels, strict=True):
            box(left, right, 0, sy, z)
        spawn_z = levels[0]
    elif kind == "slope":
        meshes = _slope_mesh(difficulty, cfg.size, p["slope_angle_range_rad"])
        spawn_z = 0.0
    elif kind == "rough":
        start, end = p["surface_x_range_m"]
        resolution = p["surface_resolution_m"]
        interior = np.linspace(start, end, max(3, int(np.ceil((end - start) / resolution)) + 1))
        xs = np.r_[0.0, interior, sx]
        ys = np.linspace(0, sy, max(3, int(np.ceil(sy / resolution)) + 1))
        seed = np.random.SeedSequence([p["seed"], round(difficulty * 1e6)])
        rng = np.random.default_rng(seed)
        amplitude = p["rough_amplitude_range_m"][0] + difficulty * np.ptp(p["rough_amplitude_range_m"])
        heights = np.zeros((len(xs), len(ys)))
        heights[2:-2, 1:-1] = rng.uniform(-amplitude, amplitude, (len(xs) - 4, len(ys) - 2))
        vertices = np.column_stack((np.repeat(xs, len(ys)), np.tile(ys, len(xs)), heights.ravel()))
        a = (np.arange(len(xs) - 1)[:, None] * len(ys) + np.arange(len(ys) - 1)).ravel()
        b = a + len(ys)
        faces = np.concatenate((np.column_stack((a, b, a + 1)), np.column_stack((a + 1, b, b + 1))))
        meshes.append(trimesh.Trimesh(vertices=vertices, faces=faces, process=False))
        spawn_z = 0.0
    else:
        box(0, sx, 0, sy, 0)
        spawn_z = 0.0
        if kind == "grid":
            x0, x1 = p["surface_x_range_m"]
            y0, y1 = p["grid_y_range_m"]
            half = p["grid_width_m"] / 2
            height = p["grid_height_range_m"][0] + difficulty * np.ptp(p["grid_height_range_m"])
            # Build each crossing once; coincident vertical/horizontal top faces hurt collision queries.
            intervals = [(x - half, x + half) for x in p["grid_bar_x_m"]]
            for left, right in intervals:
                box(left, right, y0, y1, height, 0.0)
            starts = [x0, *(right for _, right in intervals)]
            ends = [*(left for left, _ in intervals), x1]
            for y in p["grid_bar_y_m"]:
                for left, right in zip(starts, ends, strict=True):
                    if right > left:
                        box(left, right, y - half, y + half, height, 0.0)
    return meshes, np.array((spawn_x, sy / 2, spawn_z))


@configclass
class MixedTerrainCfg(SubTerrainBaseCfg):
    function = mixed_terrain
    profile: str = MISSING
    parameters: dict = MISSING
