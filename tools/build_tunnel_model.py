"""Write standalone MuJoCo tunnel models from the training geometry."""

import argparse
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml


def build_tunnel(path: Path, settings: dict, top: float) -> None:
    root = ET.Element("mujoco", model="jump_tunnel")
    ET.SubElement(root, "compiler", angle="radian")
    ET.SubElement(root, "option", timestep="0.002", gravity="0 0 -9.81")
    world = ET.SubElement(root, "worldbody")
    ET.SubElement(world, "light", pos="0 0 3", dir="0 0 -1")
    ET.SubElement(world, "geom", name="ground", type="plane", size="3 3 0.1", rgba="0.22 0.25 0.3 1")
    length, width, thickness = (settings[k] for k in ("beam_length_m", "lane_width_m", "beam_thickness_m"))
    ET.SubElement(
        world,
        "geom",
        name="TunnelBeam",
        type="box",
        pos=f"{length / 2} 0 {top - thickness / 2}",
        size=f"{length / 2} {width / 2} {thickness / 2}",
        rgba="0.8 0.45 0.12 1",
    )
    for side, sign in (("Left", 1), ("Right", -1)):
        rail_width, rail_height = settings["rail_thickness_m"], settings["rail_height_m"]
        ET.SubElement(
            world,
            "geom",
            name=f"Rail{side}",
            type="box",
            pos=f"0 {sign * (width + rail_width) / 2} {rail_height / 2}",
            size=f"{settings['lane_length_m'] / 2} {rail_width / 2} {rail_height / 2}",
            rgba="0.4 0.45 0.5 1",
        )
    ET.SubElement(world, "camera", name="overview", pos="1.1 -1.6 0.9", xyaxes="0.8 0.6 0 -0.2 0.3 0.9")
    ET.indent(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", type=Path, default=Path("config/reference/scut_p3.yaml"))
    parser.add_argument("--output", type=Path, default=Path("assets/tunnel"))
    args = parser.parse_args()
    settings = yaml.safe_load(args.policy.read_text(encoding="utf-8"))["stages"]["tunnel"]["tunnel"]
    build_tunnel(args.output / "tunnel_standard.xml", settings, settings["beam_height_m"])
    for level, height in enumerate(settings["height_curriculum_m"], 1):
        path = args.output / f"tunnel_level{level}.xml"
        build_tunnel(path, settings, height)
        print(f"{path} top={height:.3f}m")


if __name__ == "__main__":
    main()
