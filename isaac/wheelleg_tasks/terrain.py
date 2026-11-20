from dataclasses import MISSING

import numpy as np
import trimesh
from isaaclab.terrains import SubTerrainBaseCfg, TerrainGenerator
from isaaclab.utils import configclass

from wheelleg.shu_terrain import MIXED_PROFILES, pyramid_extent


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


def _pyramid_mesh(size, start, tread, count, height, down, ground, lip):
    """Watertight rectangular rings, including an optional raised rim on each high tread."""
    sx, sy = size
    lift, depth = lip or (0.0, 0.0)
    hx, hy = pyramid_extent(size, start, tread, count, depth)
    if height <= lift or (lip and not 0 < depth < tread):
        raise ValueError("pyramid lip must fit below the riser and within the tread")
    # Inverted tiles start and end flush with their neighbours, center below ground.
    rings = [(sx / 2, sy / 2, 0.0)]
    z = 0.0
    for i in range(count):
        x, y = hx - i * tread, hy - i * tread
        if down and lip:
            rings.extend(((x + depth, y + depth, z), (x + depth, y + depth, z + lift)))
        crest = z + (lift if down else height)
        new_z = z + (-1 if down else 1) * (height - lift)
        rings.extend(((x, y, crest if down else z), (x, y, new_z if down else crest)))
        if lip and not down:
            rings.extend(((x - depth, y - depth, crest), (x - depth, y - depth, new_z)))
        z = new_z
    bottom = min(0.0, z) - ground
    rings.insert(0, (sx / 2, sy / 2, bottom))
    vertices = [
        (sx / 2 + dx * x, sy / 2 + dy * y, z) for x, y, z in rings for dx, dy in ((-1, -1), (1, -1), (1, 1), (-1, 1))
    ]
    faces = [(0, 2, 1), (0, 3, 2)]
    for i in range(len(rings) - 1):
        for j in range(4):
            a, b = 4 * i + j, 4 * i + (j + 1) % 4
            faces.extend(((a, b, b + 4), (a, b + 4, a + 4)))
    t = len(vertices) - 4
    faces.extend(((t, t + 1, t + 2), (t, t + 2, t + 3)))
    return trimesh.Trimesh(vertices=vertices, faces=faces, process=False)


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
        if getattr(cfg, "pyramid", False):
            if spawn_x >= start - (cfg.stair_lip[1] if down and cfg.stair_lip else 0):
                raise ValueError("pyramid spawn must precede the first edge")
            mesh = _pyramid_mesh(cfg.size, start, width, count, height, down, ground, cfg.stair_lip)
            return [mesh], np.array((spawn_x, sy / 2, 0.0))
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


class MixedTerrainGenerator(TerrainGenerator):
    def _generate_curriculum_terrains(self):
        # Isaac Lab 2.3.2 samples once per (column, row). Reuse that draw for
        # the paired lip column so only its geometry, not its difficulty, changes.
        lower, upper = self.cfg.difficulty_range
        difficulties = {}
        for col, cfg in enumerate(self.cfg.sub_terrains.values()):
            for row in range(self.cfg.num_rows):
                key = (cfg.profile, row)
                if key not in difficulties:
                    fraction = (row + self.np_rng.uniform()) / self.cfg.num_rows
                    if cfg.profile == "slope" or cfg.profile.endswith(("_up", "_down")):
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
    pyramid: bool = False
    stair_lip: tuple[float, float] | None = None
