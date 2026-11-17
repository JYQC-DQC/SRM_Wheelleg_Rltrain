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
    length, width = settings["beam_length_m"], settings["lane_width_m"]
    center_x = settings["beam_offset_from_entrance_m"] + length / 2
    ET.SubElement(
        world,
        "geom",
        name="TunnelBeam",
        type="box",
        pos=f"{center_x} 0 {top / 2}",
        size=f"{length / 2} {width / 2} {top / 2}",
        rgba="0.8 0.45 0.12 1",
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


if __name__ == "__main__":
    main()
