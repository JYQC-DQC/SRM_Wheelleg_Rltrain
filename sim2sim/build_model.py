"""Generate a flat-ground MuJoCo model of the SCUT V14.2 reference robot for sim2sim.

The robot body tree, closed-chain equalities and contact excludes come from the SCUT experience scene
(runs/scut_experience/scene.xml); the course terrain is dropped. Active-joint friction/damping use robot.yaml
nominal values plus the midpoints of training randomization; armature uses training.joint_armature, and the
wheel-ground friction is set explicitly (the scene's 5.5 is far above the trained 0.4-1.2 range).
Leg/wheel PD and the gas spring are computed in sim2sim.py, so the actuators here are plain unclamped motors.

    python build_model.py --robot checkpoints/<run>/params/robot.yaml
"""

import argparse
import os
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
DEFAULT_SOURCE = HERE.parent / "SRM_Wheelleg_Rltrain" / "runs" / "scut_experience" / "scene.xml"


def build(source: Path, robot_yaml: Path, output: Path, wheel_friction: float) -> None:
    robot = yaml.safe_load(robot_yaml.read_text(encoding="utf-8"))
    physics = robot["training"]
    active = robot["asset"]["active_joint_names"]
    springs = robot["asset"]["spring_joint_names"]

    src = ET.parse(source).getroot()
    model = ET.Element("mujoco", model="scut_v14_2_sim2sim")
    model.append(src.find("default"))
    ET.SubElement(model, "compiler", angle="radian", meshdir=os.path.relpath(source.parent, output.parent))
    ET.SubElement(
        model,
        "option",
        timestep=str(1.0 / robot["control_hz"]),
        integrator="implicitfast",
        gravity=f"0 0 {-physics['gravity_m_s2']}",
    )

    asset = ET.SubElement(model, "asset")
    for child in src.find("asset"):
        if child.tag == "material" and child.get("name") != "course_ground":
            asset.append(child)
        elif child.tag == "mesh" and child.get("file"):
            asset.append(child)
    ET.SubElement(
        asset, "texture", name="grid", type="2d", builtin="checker", width="512", height="512",
        rgb1="0.15 0.2 0.25", rgb2="0.25 0.3 0.35",
    )
    ET.SubElement(asset, "material", name="ground", texture="grid", texrepeat="2 2", texuniform="true")

    world = ET.SubElement(model, "worldbody")
    ET.SubElement(world, "light", pos="0 0 6", dir="0 0 -1", directional="true", diffuse="0.8 0.8 0.8")
    friction = physics["ground_material"]
    ET.SubElement(
        world, "geom", name="ground", type="plane", size="0 0 0.1", material="ground",
        friction=f"{friction['dynamic_friction']} 0.01 0.001",
    )
    base = src.find("worldbody/body[@name='base_link']")
    base.set("pos", " ".join(str(v) for v in robot["asset"]["initial_root_position_m"]))
    world.append(base)

    joints = {j.get("name"): j for j in base.iter("joint")}
    randomization = physics["randomization"]
    for i, name in enumerate(active):
        joint = joints[name]
        joint.set("armature", str(physics["joint_armature"][i]))
        dry_friction = physics["joint_coulomb_friction"][i]
        damping = physics["joint_viscous_friction"][i]
        if i in robot["leg_indices"]:
            dry_friction += sum(randomization["hip_static_friction_add"]) / 2
            damping += sum(randomization["hip_viscous_friction_add"]) / 2
        elif i in robot["wheel_indices"]:
            dry_friction += sum(randomization["wheel_static_friction_add"]) / 2
        # MuJoCo has one dry-friction effort, not separate static/dynamic coefficients.
        # Use the requested static-range midpoint as its numeric approximation, not an exact PhysX mapping.
        joint.set("frictionloss", str(dry_friction))
        joint.set("damping", str(damping))
        joint.attrib.pop("limited", None)
        joint.attrib.pop("range", None)  # SCUT +/-3.14 is a target clamp, not written to the USD
    for name in springs:
        joints[name].set("damping", "0")  # spring damping is part of the computed spring force
        joints[name].set("frictionloss", "0")
    for geom in base.iter("geom"):
        if geom.get("name", "").endswith("wheel_link_collision"):
            geom.set("friction", f"{wheel_friction} 0.01 0.001")

    actuator = ET.SubElement(model, "actuator")
    for name in [*active, *springs]:
        ET.SubElement(actuator, "motor", name=f"{name}_ctrl", joint=name, ctrllimited="false")
    model.append(src.find("equality"))
    model.append(src.find("contact"))
    sensor = ET.SubElement(model, "sensor")
    ET.SubElement(sensor, "framequat", name="imu_quat", objtype="site", objname="base_link_site")
    ET.SubElement(sensor, "gyro", name="imu_gyro", site="base_link_site")
    visual = ET.SubElement(model, "visual")
    ET.SubElement(visual, "global", offwidth="1280", offheight="720")

    ET.indent(model)
    output.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(model).write(output, encoding="utf-8", xml_declaration=True)
    print(f"wrote {output}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--robot", type=Path, required=True, help="robot.yaml snapshot of the training run")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=HERE / "assets" / "scut_v14_2_flat.xml")
    # Training: wheel static 0.5-1.2 / dynamic 0.4-1.0 times ground 1.0 (multiply); MuJoCo has one coefficient.
    parser.add_argument("--wheel-friction", type=float, default=0.8)
    args = parser.parse_args()
    build(args.source.resolve(), args.robot, args.output.resolve(), args.wheel_friction)


if __name__ == "__main__":
    main()
