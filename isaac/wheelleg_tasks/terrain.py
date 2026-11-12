from dataclasses import MISSING

import numpy as np
import trimesh
from isaaclab.terrains import SubTerrainBaseCfg
from isaaclab.utils import configclass


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
    return meshes, np.array((sx / 4, sy / 2, 0.0))


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
