from dataclasses import MISSING

import numpy as np
import trimesh
from isaaclab.terrains import SubTerrainBaseCfg, TerrainGenerator
from isaaclab.utils import configclass

from wheelleg.shu_terrain import (
    LEGACY_PROFILES,
    LEGACY_STEP_COUNTS,
    MIXED_PROFILES,
    STAIR_PROFILES,
    natural_pyramid_layout,
)


def _slope_mesh(
    difficulty: float, size, angle_range, *, platform_width_m: float, inverted: bool
) -> tuple[trimesh.Trimesh, np.ndarray]:
    sx, sy = size
    cx, cy = sx / 2, sy / 2
    if not 0 < platform_width_m < min(sx, sy):
        raise ValueError("slope: platform_width_m must be positive and leave room for four faces")
    half_platform_m = platform_width_m / 2
    run_m = min(cx, cy) - half_platform_m
    angle = angle_range[0] + difficulty * (angle_range[1] - angle_range[0])
    # Use the shorter run so even on a rectangular tile no face exceeds the selected angle.
    center_z = (-1 if inverted else 1) * run_m * np.tan(angle)
    vertices = [(0, 0, 0), (sx, 0, 0), (sx, sy, 0), (0, sy, 0)]
    vertices.extend(
        (cx + dx * half_platform_m, cy + dy * half_platform_m, center_z)
        for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))
    )
    faces = [(4, 5, 6), (4, 6, 7)]
    for a in range(4):
        b = (a + 1) % 4
        faces.extend(((a, b, b + 4), (a, b + 4, a + 4)))
    return trimesh.Trimesh(vertices=vertices, faces=faces, process=False), np.array((cx, cy, center_z))


def _closed_stair_mesh(edges, tops, bottom, width) -> trimesh.Trimesh:
    # Triangulate the XZ section in strips. Split the taller strip at each
    # shared edge so the extrusion caps have no T-junctions or internal faces.
    vertices = {}
    faces = []
    for i, (left, right, top) in enumerate(zip(edges[:-1], edges[1:], tops, strict=True)):
        outline = [(left, bottom), (right, bottom)]
        if i + 1 < len(tops) and tops[i + 1] < top:
            outline.append((right, tops[i + 1]))
        outline.extend(((right, top), (left, top)))
        if i > 0 and tops[i - 1] < top:
            outline.append((left, tops[i - 1]))
        center = vertices.setdefault(((left + right) / 2, (bottom + top) / 2), len(vertices))
        ring = [vertices.setdefault(point, len(vertices)) for point in outline]
        faces.extend((center, a, b) for a, b in zip(ring, ring[1:] + ring[:1], strict=True))
    mesh = trimesh.creation.extrude_triangulation(np.array(list(vertices)), np.array(faces), height=width)
    # Extrusion coordinates (x, z, depth) -> terrain (x, width - depth, z).
    mesh.apply_transform(np.array(((1, 0, 0, 0), (0, 0, -1, width), (0, 1, 0, 0), (0, 0, 0, 1))))
    return mesh


def _pyramid_mesh(size, layout, height, down, lip) -> tuple[trimesh.Trimesh, float]:
    """Terrain surface only: apron, risers, treads (with optional lips) and center deck."""
    sx, sy = size
    lift, depth = lip or (0.0, 0.0)
    if height <= lift:
        raise ValueError("pyramid lip must fit below the riser")
    # Inverted tiles start and end flush with their neighbours, center below ground.
    rings = [(sx / 2, sy / 2, 0.0)]
    z = 0.0
    risers = layout.riser_half_widths_m
    for i, half in enumerate(risers):
        if down and lip:
            rings.extend(((half + depth, half + depth, z), (half + depth, half + depth, z + lift)))
        crest = z + (lift if down else height)
        new_z = z + (-1 if down else 1) * (height - lift)
        rings.extend(((half, half, crest if down else z), (half, half, new_z if down else crest)))
        if lip and not down:
            inner = layout.platform_half_width_m if i == len(risers) - 1 else half - depth
            rings.extend(((inner, inner, crest), (inner, inner, new_z)))
        z = new_z
    vertices = [
        (sx / 2 + dx * x, sy / 2 + dy * y, z) for x, y, z in rings for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))
    ]
    faces = []
    for i in range(len(rings) - 1):
        for j in range(4):
            a, b = 4 * i + j, 4 * i + (j + 1) % 4
            faces.extend(((a, b, b + 4), (a, b + 4, a + 4)))
    t = len(vertices) - 4
    faces.extend(((t, t + 1, t + 2), (t, t + 2, t + 3)))
    return trimesh.Trimesh(vertices=vertices, faces=faces, process=False), z


def mixed_terrain(difficulty: float, cfg) -> tuple[list, np.ndarray]:
    """One tile with explicit geometry, independent of command mode or unlock state."""
    sx, sy = cfg.size
    p, kind = cfg.parameters, cfg.profile
    if kind in ("slope", "slope_inverted"):
        mesh, origin = _slope_mesh(
            difficulty,
            cfg.size,
            p["slope_angle_range_rad"],
            platform_width_m=p["platform_width_m"],
            inverted=kind == "slope_inverted",
        )
        return [mesh], origin
    if kind not in MIXED_PROFILES and kind not in LEGACY_PROFILES:
        raise ValueError(f"Unknown SHU mixed terrain profile: {kind}")
    if kind == "rough":
        raise ValueError("rough uses Isaac Lab HfRandomUniformTerrainCfg, not the custom mesh builder")
    if kind in STAIR_PROFILES:
        down = kind.endswith("_down")
        depth = cfg.stair_lip[1] if cfg.stair_lip else 0.0
        layout = natural_pyramid_layout(cfg.size, p, down=down, lip_width_m=depth)
        height = p["step_height_range_m"][0] + difficulty * np.ptp(p["step_height_range_m"])
        mesh, deck_z = _pyramid_mesh(cfg.size, layout, height, down, cfg.stair_lip)
        return [mesh], np.array((sx / 2, sy / 2, deck_z))

    ground = p["ground_thickness_m"]
    meshes = []

    def box(x0, x1, y0, y1, top, bottom=-ground):
        mesh = trimesh.creation.box((x1 - x0, y1 - y0, top - bottom))
        mesh.apply_translation(((x0 + x1) / 2, (y0 + y1) / 2, (top + bottom) / 2))
        meshes.append(mesh)

    if kind == "grid":
        # SCUT agent_world/terrains/height_field.py: mesh_grid_bars_terrain (frozen tiny_step_rot).
        # Count and width use separate random draws, not the row difficulty used for height.
        horizontal_draw, vertical_draw, width_draw = map(float, np.random.uniform(0.0, 1.0, size=3))
        count_min, count_max = p["grid_bar_count_range"]
        width_min, width_max = p["grid_width_range_m"]
        width = width_min + width_draw * (width_max - width_min)
        height_min, height_max = p["grid_height_range_m"]
        height = height_min + difficulty * (height_max - height_min)

        def bar_spans(axis_size, draw):
            count = int(np.rint(count_min + draw * (count_max - count_min)))
            # Prefer the larger valid even count: in [2, 4], 3 becomes 4, not 2.
            if count % 2:
                count += 1 if count < count_max else -1
            gap = (axis_size - count * width) / (count + 1)
            centers = gap + width / 2 + np.arange(count, dtype=np.float32) * (width + gap)
            return [(float(center) - width / 2, float(center) + width / 2) for center in centers]

        horizontal = bar_spans(sy, horizontal_draw)
        vertical = bar_spans(sx, vertical_draw)
        margin = (1.0 - p["grid_bar_length_ratio"]) / 2
        x0, x1 = sx * margin, sx - sx * margin
        y0, y1 = sy * margin, sy - sy * margin
        box(0, sx, 0, sy, 0)
        # Only the full-length vertical bar owns each intersection; split horizontal boxes around it.
        cuts = [(max(x0, left), min(x1, right)) for left, right in vertical if right > x0 and left < x1]
        starts = [x0, *(right for _, right in cuts)]
        ends = [*(left for left, _ in cuts), x1]
        for low, high in horizontal:
            for left, right in zip(starts, ends, strict=True):
                if right - left > 1.0e-6:
                    box(left, right, low, high, height, 0.0)
        for left, right in vertical:
            box(left, right, y0, y1, height, 0.0)
        return meshes, np.array((sx / 2, sy / 2, height))
    spawn_x = p["spawn_x_m"]
    if kind.endswith(("_up", "_down")):
        count = LEGACY_STEP_COUNTS[kind.split("_")[0]]
        down = kind.endswith("_down")
        start, width = p["first_edge_x_m"], p["step_width_m"]
        edges = [0, *(start + i * width for i in range(count)), sx]
        if not 0 <= spawn_x < start or not 0 < start <= edges[-2] < sx or width <= 0:
            raise ValueError(f"{kind}: need a clear approach, ordered risers and an exit within the tile")
        height = p["step_height_range_m"][0] + difficulty * np.ptp(p["step_height_range_m"])
        if cfg.stair_lip is None:
            levels = [height * (count - i if down else i) for i in range(count + 1)]
            for left, right, z in zip(edges[:-1], edges[1:], levels, strict=True):
                box(left, right, 0, sy, z)
        else:
            lip_height, lip_width = cfg.stair_lip
            if not lip_height < height:
                raise ValueError(f"{kind}: terrain.stair_lip.height_m must be less than the outer riser height")
            levels = [(height - lip_height) * (count - i if down else i) for i in range(count + 1)]
            section_x, section_z = [0], []
            for i, (left, right, z) in enumerate(zip(edges[:-1], edges[1:], levels, strict=True)):
                has_lip = i < count if down else i > 0
                if has_lip:
                    lip_edge = right - lip_width if down else left + lip_width
                    if not left < lip_edge < right or (down and i == 0 and spawn_x >= lip_edge):
                        raise ValueError(f"{kind}: terrain.stair_lip.width_m must fit the high tread and clear spawn")
                    section_x.append(lip_edge)
                    # The outside riser is height H, not H + lip_height.
                    crown = (levels[i + 1] if down else levels[i - 1]) + height
                    section_z.extend((z, crown) if down else (crown, z))
                else:
                    section_z.append(z)
                section_x.append(right)
            meshes.append(_closed_stair_mesh(section_x, section_z, -ground, sy))
        spawn_z = levels[0]
    else:
        box(0, sx, 0, sy, 0)
        spawn_z = 0.0
    return meshes, np.array((spawn_x, sy / 2, spawn_z))


class MixedTerrainGenerator(TerrainGenerator):
    def _generate_curriculum_terrains(self):
        # Isaac Lab 2.3.2 samples once per (column, row). Reuse that draw for
        # paired stair and slope columns so only geometry changes within a row.
        lower, upper = self.cfg.difficulty_range
        difficulties = {}
        for col, (name, cfg) in enumerate(self.cfg.sub_terrains.items()):
            profile = getattr(cfg, "profile", name)  # native rough config has no SHU profile field
            if profile == "slope_inverted":
                profile = "slope"
            for row in range(self.cfg.num_rows):
                key = (profile, row)
                if key not in difficulties:
                    fraction = (row + self.np_rng.uniform()) / self.cfg.num_rows
                    if profile == "slope" or profile.endswith(("_up", "_down")):
                        if row == self.cfg.num_rows - 1:
                            fraction = 1.0
                        elif row == 0:
                            fraction = 0.0
                    difficulties[key] = lower + (upper - lower) * fraction
                mesh, origin = self._get_terrain_mesh(difficulties[key], cfg)
                self._add_sub_terrain(mesh, origin, row, col, cfg)


@configclass
class MixedTerrainCfg(SubTerrainBaseCfg):
    function = mixed_terrain
    profile: str = MISSING
    parameters: dict = MISSING
    stair_lip: tuple[float, float] | None = None
