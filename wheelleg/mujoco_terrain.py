"""MuJoCo counterparts of the training course; no Isaac imports or robot edits."""

import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np

from wheelleg.stairs import step_layout


def build_course(flat_model: Path, output: Path, terrain: dict, friction: float) -> list[dict]:
    """One selectable tile per profile and difficulty row. Coordinates and dimensions are metres."""
    tree = ET.parse(flat_model)
    root = tree.getroot()
    compiler = root.find("compiler")
    compiler.set("meshdir", str((flat_model.parent / compiler.get("meshdir")).resolve()))
    world, asset = root.find("worldbody"), root.find("asset")
    floor = world.find("geom[@name='ground']")
    # The floor is below the tiles so it cannot hide the negative troughs of the rough heightfields.
    floor.set("pos", f"0 0 {-terrain['ground_thickness_m']}")
    floor.set("group", "3")
    sx, sy = terrain["tile_size_m"]
    gap = 2 * terrain["boundary_margin_m"]
    tiles = []

    def box(name, bounds, offset, color):
        x0, x1, y0, y1, z0, z1 = bounds
        position = ((x0 + x1) / 2 + offset[0], (y0 + y1) / 2 + offset[1], (z0 + z1) / 2)
        ET.SubElement(
            world,
            "geom",
            name=name,
            type="box",
            group="3",
            contype="1",
            conaffinity="1",
            pos=" ".join(map(str, position)),
            size=f"{(x1 - x0) / 2} {(y1 - y0) / 2} {(z1 - z0) / 2}",
            rgba=color,
            friction=f"{friction} 0.01 0.001",
        )

    for column, (name, profile) in enumerate(terrain["profiles"].items()):
        for row in range(terrain["rows"]):
            # Midpoint of the same difficulty band Isaac samples as (row+uniform)/rows.
            difficulty = (row + 0.5) / terrain["rows"]
            offset = (row * (sx + gap), column * (sy + gap))
            tag = f"course_{name}_{row}"
            color = "0.45 0.57 0.68 1" if column % 2 else "0.63 0.55 0.39 1"
            kind = profile["kind"]
            spawn_z = 0.0
            if kind in ("up", "down", "mixed"):
                edges, heights = step_layout(terrain, profile, difficulty)
                boundaries = [0.0, *edges, sx]
                for i, (a, b, h) in enumerate(zip(boundaries[:-1], boundaries[1:], heights, strict=True)):
                    box(f"{tag}_{i}", (a, b, 0, sy, -terrain["ground_thickness_m"], h), offset, color)
                spawn_z = heights[0]
            elif kind in ("slope", "rough"):
                res = terrain["surface_resolution_m"]
                xs = np.linspace(0, sx, round(sx / res) + 1)
                ys = np.linspace(0, sy, round(sy / res) + 1)
                z = np.zeros((len(xs), len(ys)))
                if kind == "slope":
                    angle = terrain["slope_angle_range_rad"][0] + difficulty * np.ptp(terrain["slope_angle_range_rad"])
                    z[:] = (np.minimum(xs - terrain["entry_x_m"], terrain["exit_x_m"] - xs).clip(0) * np.tan(angle))[
                        :, None
                    ]
                else:
                    rng = np.random.default_rng(np.random.SeedSequence([terrain["seed"], round(difficulty * 1000000)]))
                    amplitude = terrain["rough_noise_range_m"][0] + difficulty * np.ptp(terrain["rough_noise_range_m"])
                    inside = (xs >= terrain["entry_x_m"]) & (xs <= terrain["exit_x_m"])
                    z[inside] = rng.uniform(-amplitude, amplitude, (inside.sum(), len(ys)))
                low, span = float(z.min()), float(np.ptp(z))
                if span == 0:
                    box(tag, (0, sx, 0, sy, -terrain["ground_thickness_m"], 0), offset, color)
                else:
                    # MuJoCo columns are x, rows are y; transpose the training z[x,y] array.
                    ET.SubElement(
                        asset,
                        "hfield",
                        name=tag,
                        nrow=str(len(ys)),
                        ncol=str(len(xs)),
                        size=f"{sx / 2} {sy / 2} {span} {terrain['ground_thickness_m']}",
                        elevation=" ".join(f"{v:.8f}" for v in ((z - low) / span).T.ravel()),
                    )
                    ET.SubElement(
                        world,
                        "geom",
                        name=tag,
                        type="hfield",
                        hfield=tag,
                        group="3",
                        contype="1",
                        conaffinity="1",
                        pos=f"{offset[0] + sx / 2} {offset[1] + sy / 2} {low}",
                        rgba=color,
                        friction=f"{friction} 0.01 0.001",
                    )
            else:
                box(tag, (0, sx, 0, sy, -terrain["ground_thickness_m"], 0), offset, color)
                if kind == "grid":
                    # Same randomization/split intersections as isaac/wheelleg_tasks/terrain.py.
                    rng = np.random.default_rng(np.random.SeedSequence([terrain["seed"], round(difficulty * 1000000)]))
                    g = terrain["grid"]
                    width = rng.uniform(*g["width_range_m"])
                    height = (
                        g["height_range_m"][0] + difficulty * np.ptp(g["height_range_m"])
                        if "command_mode" in profile
                        else rng.uniform(*g["height_range_m"])
                    )
                    spacing_x, spacing_y = rng.uniform(*g["spacing_range_m"], size=2)
                    cx, cy = (terrain["entry_x_m"] + terrain["exit_x_m"]) / 2, sy / 2
                    vertical = [
                        (cx + s * spacing_x / 2 - width / 2, cx + s * spacing_x / 2 + width / 2) for s in (-1, 1)
                    ]
                    for i, (a, b) in enumerate(vertical):
                        box(
                            f"{tag}_v{i}",
                            (a, b, cy - g["half_span_m"], cy + g["half_span_m"], 0, height),
                            offset,
                            color,
                        )
                    for j, y in enumerate((cy - spacing_y / 2, cy + spacing_y / 2)):
                        start = terrain["entry_x_m"]
                        for i, (a, b) in enumerate([*vertical, (terrain["exit_x_m"], terrain["exit_x_m"])]):
                            box(f"{tag}_h{j}_{i}", (start, a, y - width / 2, y + width / 2, 0, height), offset, color)
                            start = b
            tiles.append(
                dict(
                    profile=name,
                    row=row,
                    difficulty=difficulty,
                    offset=offset,
                    spawn=(
                        offset[0] + (sx / 2 if profile.get("command_mode") == "motion" else terrain["spawn_x_m"]),
                        offset[1] + sy / 2,
                        spawn_z,
                    ),
                )
            )
    ET.indent(root)
    tree.write(output, encoding="utf-8", xml_declaration=True)
    return tiles
