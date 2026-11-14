from dataclasses import MISSING

import numpy as np
import trimesh
from isaaclab.terrains import SubTerrainBaseCfg
from isaaclab.utils import configclass

from wheelleg.stairs import grid_layout, step_layout


def steps_terrain(difficulty: float, cfg) -> tuple[list, np.ndarray]:
    """Flat / single / double step, with ascent and descent on each patch."""
    sx, sy = cfg.size
    mesh = trimesh.creation.box((sx, sy, 0.1))
    mesh.apply_translation((sx / 2, sy / 2, -0.05))
    meshes = [mesh]
    height = cfg.step_height_range[0] + difficulty * (cfg.step_height_range[1] - cfg.step_height_range[0])
    for level in range(cfg.step_count):  # Mesh construction, never a loop over simulation environments.
        width = (2 * (cfg.step_count - level) + 1) * cfg.step_width
        step = trimesh.creation.box((width, sy, height))
        step.apply_translation((sx / 2, sy / 2, (level + 0.5) * height))
        meshes.append(step)
    # Recovery still uses this legacy geometry. Spawn midway through its clear approach, never on a riser.
    if cfg.step_count == 0:
        return meshes, np.array((sx / 4, sy / 2, 0.0))
    edge = sx / 2 - (2 * cfg.step_count + 1) * cfg.step_width / 2
    return meshes, np.array((max(edge, 0.0) / 2, sy / 2, 0.0))


@configclass
class StepsCfg(SubTerrainBaseCfg):
    function = steps_terrain
    step_count: int = 1
    step_height_range: tuple[float, float] = MISSING
    step_width: float = MISSING


def slope_terrain(difficulty: float, cfg) -> tuple[list, np.ndarray]:
    sx, sy = cfg.size
    angle = cfg.angle_range[0] + difficulty * (cfg.angle_range[1] - cfg.angle_range[0])
    xs = np.array([0.0, sx / 4, sx / 2, 3 * sx / 4, sx])
    zs = np.array([0.0, 0.0, np.tan(angle) * sx / 4, 0.0, 0.0])
    vertices = np.array([(x, y, z) for x, z in zip(xs, zs, strict=True) for y in (0.0, sy)])
    faces = []
    for i in range(4):
        faces.extend(((2 * i, 2 * i + 2, 2 * i + 1), (2 * i + 1, 2 * i + 2, 2 * i + 3)))
    return [trimesh.Trimesh(vertices=vertices, faces=np.array(faces), process=False)], np.array((sx / 8, sy / 2, 0.0))


@configclass
class SlopeCfg(SubTerrainBaseCfg):
    function = slope_terrain
    angle_range: tuple[float, float] = MISSING


def spin_slope_terrain(difficulty: float, cfg) -> tuple[list, np.ndarray]:
    """Spawn on the slope: a stationary spinning policy must actually experience it."""
    meshes, _ = slope_terrain(difficulty, cfg)
    sx, sy = cfg.size
    angle = cfg.angle_range[0] + difficulty * (cfg.angle_range[1] - cfg.angle_range[0])
    return meshes, np.array((3 * sx / 8, sy / 2, np.tan(angle) * sx / 8))


@configclass
class SpinSlopeCfg(SlopeCfg):
    function = spin_slope_terrain


def bumps_terrain(difficulty: float, cfg) -> tuple[list, np.ndarray]:
    sx, sy = cfg.size
    ground = trimesh.creation.box((sx, sy, 0.1))
    ground.apply_translation((sx / 2, sy / 2, -0.05))
    meshes = [ground]
    height = cfg.height_range[0] + difficulty * (cfg.height_range[1] - cfg.height_range[0])
    for x in np.arange(sx / 3, 2 * sx / 3, cfg.spacing):
        bump = trimesh.creation.box((cfg.width, sy, height))
        bump.apply_translation((x, sy / 2, height / 2))
        meshes.append(bump)
    return meshes, np.array((sx / 8, sy / 2, 0.0))


@configclass
class BumpsCfg(SubTerrainBaseCfg):
    function = bumps_terrain
    height_range: tuple[float, float] = MISSING
    spacing: float = MISSING
    width: float = MISSING


def course_terrain(difficulty: float, cfg) -> tuple[list, np.ndarray]:
    """One-way traversal tiles with flat spawn/exit pads; all coordinates are tile-local metres."""
    p, profile = cfg.parameters, cfg.profile
    sx, sy = cfg.size
    meshes = []

    def box(x0, x1, y0, y1, z0, z1):
        mesh = trimesh.creation.box((x1 - x0, y1 - y0, z1 - z0))
        mesh.apply_translation(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
        meshes.append(mesh)

    kind = profile["kind"]
    if kind in ("up", "down", "mixed"):
        edges, heights = step_layout(p, profile, difficulty)
        boundaries = [0.0, *edges, sx]
        for start, end, height in zip(boundaries[:-1], boundaries[1:], heights, strict=True):
            box(start, end, 0, sy, -p["ground_thickness_m"], height)
        spawn_height = heights[0]
    elif kind in ("slope", "rough"):
        resolution = p["surface_resolution_m"]
        xs = np.linspace(0, sx, round(sx / resolution) + 1)
        ys = np.linspace(0, sy, round(sy / resolution) + 1)
        z = np.zeros((len(xs), len(ys)))
        surface_start, surface_end = p["surface_x_range_m"]
        inside = (xs >= surface_start) & (xs <= surface_end)
        if kind == "slope":
            angle = p["slope_angle_range_rad"][0] + difficulty * np.ptp(p["slope_angle_range_rad"])
            # Widen coverage without raising the peak at an unchanged difficulty row.
            rise_run = np.minimum(xs - surface_start, surface_end - xs).clip(0, (p["exit_x_m"] - p["entry_x_m"]) / 2)
            z[:] = (rise_run * np.tan(angle))[:, None]
        else:
            # Small uniform surface noise, clear approach and exit pads; no unsupported ray API needed.
            rng = np.random.default_rng(np.random.SeedSequence([p["seed"], round(difficulty * 1000000)]))
            amplitude = p["rough_noise_range_m"][0] + difficulty * np.ptp(p["rough_noise_range_m"])
            z[inside] = rng.uniform(-amplitude, amplitude, (inside.sum(), len(ys)))
        vertices = np.array([(x, y, z[i, j]) for i, x in enumerate(xs) for j, y in enumerate(ys)])
        faces = []
        for i in range(len(xs) - 1):
            for j in range(len(ys) - 1):
                a = i * len(ys) + j
                faces.extend(((a, a + len(ys), a + 1), (a + 1, a + len(ys), a + len(ys) + 1)))
        meshes.append(trimesh.Trimesh(vertices=vertices, faces=np.array(faces), process=False))
        spawn_height = 0.0
    else:
        box(0, sx, 0, sy, -p["ground_thickness_m"], 0)
        spawn_height = 0.0
        if kind == "grid":
            # Shared geometry keeps the training and sim2sim obstacle coverage identical.
            rectangles, height = grid_layout(p, difficulty)
            for x0, x1, y0, y1 in rectangles:
                box(x0, x1, y0, y1, 0, height)
    spawn_x = sx / 2 if profile["command_mode"] == "motion" else p["spawn_x_m"]
    return meshes, np.array((spawn_x, sy / 2, spawn_height))


@configclass
class CourseTerrainCfg(SubTerrainBaseCfg):
    function = course_terrain
    parameters: dict = MISSING
    profile: dict = MISSING
