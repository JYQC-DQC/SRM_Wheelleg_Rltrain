"""Prepare a simulation-only SCUT profile for the latest P1 framework; never imports policy weights."""

import argparse
import hashlib
import json
import re
from math import acos, radians
from pathlib import Path

import numpy as np
import yaml

from wheelleg.spawn import scut_spawn_height, spring_extension_height


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reference-package",
        type=Path,
        required=True,
        help="SCUT source/agent_world directory containing agent_world/",
    )
    parser.add_argument("--output", type=Path, default=Path("runs/scut_latest"))
    from isaaclab.app import AppLauncher

    AppLauncher.add_app_launcher_args(parser)
    args = parser.parse_args()
    package = args.reference_package.resolve()
    usd = package / "agent_world/assets/usd_files/wheelbipeV14_2_1/wheelbipeV14_2.usd"
    asset_py = package / "agent_world/assets/wheelbipe_V14_2.py"
    for file in (usd, asset_py):
        if not file.is_file():
            raise FileNotFoundError(file)
    app = AppLauncher(args).app
    try:
        from pxr import Usd, UsdGeom, UsdPhysics

        root = Path(__file__).resolve().parents[1]
        robot = yaml.safe_load((root / "config/reference/scut_robot.template.yaml").read_text(encoding="utf-8"))
        stage = Usd.Stage.Open(str(usd))
        if UsdGeom.GetStageMetersPerUnit(stage) != 1.0:
            raise ValueError("Expected SCUT meter-based USD")
        joints = {p.GetName(): p for p in stage.Traverse() if p.IsA(UsdPhysics.Joint)}
        bodies = [p.GetName() for p in stage.Traverse() if p.HasAPI(UsdPhysics.RigidBodyAPI)]
        if len(bodies) != len(set(bodies)):
            raise ValueError("USD body names must be unique")
        asset = robot["asset"]
        if any(value != 0.0 for value in asset["initial_joint_positions_rad"].values()):
            raise ValueError("SCUT zero-pose height preparation requires zero initial joint positions")
        body_prims = {p.GetName(): p for p in stage.Traverse() if p.HasAPI(UsdPhysics.RigidBodyAPI)}
        transform_cache = UsdGeom.XformCache(Usd.TimeCode.Default())
        base_position = list(
            transform_cache.GetLocalToWorldTransform(body_prims[asset["base_body_name"]]).ExtractTranslation()
        )
        wheel_positions = [
            list(transform_cache.GetLocalToWorldTransform(body_prims[name]).ExtractTranslation())
            for name in asset["wheel_body_names"]
        ]
        spawn_height = scut_spawn_height(
            base_position, wheel_positions, robot["training"]["wheel_radius_m"], robot["training"]["spawn_clearance_m"]
        )
        asset["initial_root_position_m"][2] = spawn_height
        leg_reset_joints = robot["training"]["leg_reset"]["joint_names"]
        for name in asset["active_joint_names"] + asset["spring_joint_names"] + leg_reset_joints:
            if name not in joints:
                raise ValueError(f"USD missing joint {name}")
        # 模板里的接触名单是正则（SCUT V14/env.py:118-139）。Isaac 的 find_bodies 遇到匹配不到的正则会报错，
        # 所以这里按 USD 实际刚体展开成精确名字，并把没匹配到的正则写进报告，由人确认。
        unmatched_contact_patterns = {}
        for key in ("undesired_contact_body_names", "termination_contact_body_names"):
            patterns = asset[key]
            asset[key] = [body for body in bodies if any(re.fullmatch(p, body) for p in patterns)]
            unmatched_contact_patterns[key] = [p for p in patterns if not any(re.fullmatch(p, body) for body in bodies)]
            if asset["base_body_name"] not in asset[key]:
                raise ValueError(f"asset.{key} must include {asset['base_body_name']}")
        print("UNMATCHED_CONTACT_PATTERNS", json.dumps(unmatched_contact_patterns), flush=True)
        pivots = []
        for side in ("left", "right"):
            anchors = []
            for part in ("front", "rear"):
                joint = UsdPhysics.Joint(joints[f"{side}_{part}1_joint"])
                if [p.name for p in joint.GetBody0Rel().GetTargets()] != ["base_link"]:
                    raise ValueError("Hip anchor parent is not base_link")
                anchors.append(list(joint.GetLocalPos0Attr().Get()))
            pivots.append([(a + b) / 2 for a, b in zip(*anchors, strict=True)])
        spans = []
        for name in asset["spring_joint_names"]:
            joint = UsdPhysics.PrismaticJoint(joints[name])
            spans.append(float(joint.GetUpperLimitAttr().Get() - joint.GetLowerLimitAttr().Get()))
        if min(spans) <= 0 or abs(spans[0] - spans[1]) > 1e-6:
            raise ValueError("Unexpected spring stroke")
        robot["spring_stroke_m"] = spans[0]
        # USD attributes/frames follow supermimic_wheelbipe/tools/usd2mjcf.py:181-216.
        # Use actual spring endpoints and slide limits, not the spring's nominal force or stroke alone.
        extension_heights = []
        passive_limits = {}
        for side, spring_name in zip(("left", "right"), asset["spring_joint_names"], strict=True):
            rear1, rear2 = f"{side}_rear1_link", f"{side}_rear2_link"
            spring2 = joints[spring_name].GetRelationship("physics:body1").GetTargets()[0].name
            closures = [
                p
                for p in joints.values()
                if {q.name for key in ("physics:body0", "physics:body1") for q in p.GetRelationship(key).GetTargets()}
                == {rear2, spring2}
            ]
            if len(closures) != 1:
                raise ValueError(f"{side}: expected one spring-to-rear2 closure joint")
            closure = closures[0]
            pin = {}
            for index in (0, 1):
                body = closure.GetRelationship(f"physics:body{index}").GetTargets()[0].name
                pin[body] = np.asarray(closure.GetAttribute(f"physics:localPos{index}").Get(), dtype=float)
            matrices = {
                name: np.asarray(transform_cache.GetLocalToWorldTransform(body_prims[name]), dtype=float)
                for name in (
                    asset["base_body_name"],
                    rear1,
                    rear2,
                    spring2,
                    f"{side}_spring1_link",
                    f"{side}_wheel_link",
                )
            }
            rear_frame = np.linalg.inv(matrices[rear1])
            base_frame = np.linalg.inv(matrices[asset["base_body_name"]])
            if not np.allclose((matrices[rear2] @ rear_frame)[:3, :3], np.eye(3), atol=1e-5) or not np.allclose(
                (matrices[rear1] @ base_frame)[:3, :3], np.eye(3), atol=1e-5
            ):
                raise ValueError(f"{side}: spring height solver requires aligned zero-pose rear-link frames")
            slider = joints[spring_name]
            parent = slider.GetRelationship("physics:body0").GetTargets()[0].name
            quat = slider.GetAttribute("physics:localRot0").Get()
            w, v = float(quat.GetReal()), np.asarray(quat.GetImaginary(), dtype=float)
            axis = np.eye(3)["XYZ".index(str(slider.GetAttribute("physics:axis").Get()))]
            axis = axis + 2 * (w * np.cross(v, axis) + np.cross(v, np.cross(v, axis)))
            axis = np.r_[axis, 0.0] @ matrices[parent] @ rear_frame
            hinge = joints[f"{side}_spring1_joint"]
            pivot = np.asarray(hinge.GetAttribute("physics:localPos0").Get(), dtype=float)
            if hinge.GetRelationship("physics:body0").GetTargets()[0].name != rear1:
                raise ValueError(f"{side}: spring hinge parent must be rear1")
            tip = np.r_[pin[spring2], 1.0] @ matrices[spring2] @ rear_frame
            maximum = tip[:3] + float(slider.GetAttribute("physics:upperLimit").Get()) * axis[:3] - pivot
            lr = robot["training"]["leg_reset"]
            height, leg_length = spring_extension_height(
                lr["link_lengths_m"],
                lr["angle_offsets_rad"],
                float((matrices[rear1] @ base_frame)[3, 2]),
                (matrices[rear2] @ rear_frame)[3, :3],
                pivot,
                pin[rear2],
                (matrices[f"{side}_wheel_link"] @ np.linalg.inv(matrices[rear2]))[3, :3],
                float(np.linalg.norm(maximum[[0, 2]])),
                robot["training"]["wheel_radius_m"],
            )
            extension_heights.append(height)
            l0, l1, l2 = lr["link_lengths_m"]
            knee = acos((l0**2 + l1**2 - l0**2 * leg_length**2 / l2**2) / (2 * l0 * l1))
            # Only widen the passive hinges that otherwise stop extension before the gas spring.
            # User authorization is simulation-only; never edit source USD or real SRM limits.
            for part, angle in (
                ("front2", lr["angle_offsets_rad"][2] - knee),
                ("front4", lr["angle_offsets_rad"][4] - knee),
                ("rear2", knee - lr["angle_offsets_rad"][5]),
            ):
                name = f"{side}_{part}_joint"
                lower = radians(float(joints[name].GetAttribute("physics:lowerLimit").Get()))
                upper = radians(float(joints[name].GetAttribute("physics:upperLimit").Get()))
                if angle < lower or angle > upper:
                    passive_limits[name] = [min(lower, angle), max(upper, angle)]
        if abs(extension_heights[0] - extension_heights[1]) > 0.001:
            raise ValueError(f"Spring-limited standing heights differ by >1 mm: {extension_heights}")
        robot["training"]["spring_extension_height_m"] = min(extension_heights)
        robot["training"]["stairs_passive_joint_limits_rad"] = passive_limits
        robot["training"]["hip_pivot_positions_b_m"] = pivots
        asset.update(usd_path=str(usd), reference_package=str(package), collision_body_names=bodies)
        report = {
            "target": "SCUT reference simulation only; NOT SRM calibration",
            "files_sha256": {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in (usd, asset_py)},
            "body_names": bodies,
            "undesired_contact_body_names": asset["undesired_contact_body_names"],
            "termination_contact_body_names": asset["termination_contact_body_names"],
            "unmatched_contact_patterns": unmatched_contact_patterns,
            "spring_stroke_m": spans,
            "spring_extension_height_m": extension_heights,
            "stairs_passive_joint_limits_rad": passive_limits,
            "hip_pivots_b_m": pivots,
            "zero_pose_base_position_w_m": base_position,
            "zero_pose_wheel_positions_w_m": wheel_positions,
            "initial_root_height_m": spawn_height,
            "initialization": "random network; no old checkpoint or teacher",
        }
        args.output.mkdir(parents=True, exist_ok=False)
        (args.output / "robot.yaml").write_text(yaml.safe_dump(robot, sort_keys=False), encoding="utf-8")
        policy = yaml.safe_load((root / "config/reference/scut_p1.yaml").read_text(encoding="utf-8"))
        stairs = policy["stages"]["stairs"]
        stairs["terrain"]["profiles"]["flat"]["height_range_m"][1] = (
            robot["training"]["spring_extension_height_m"] - stairs["step_height_margin_m"]
        )
        (args.output / "policy_meta.yaml").write_text(yaml.safe_dump(policy, sort_keys=False), encoding="utf-8")
        (args.output / "policy_p2.yaml").write_bytes((root / "config/reference/scut_p2.yaml").read_bytes())
        (args.output / "reference_manifest.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        from wheelleg.training import load_training

        cfg = load_training("p1-flat", args.output / "robot.yaml", args.output / "policy_meta.yaml")
        cfg.require_ready()
        load_training("p2-spin", args.output / "robot.yaml", args.output / "policy_p2.yaml").require_ready()
        print("SCUT_PROFILE_READY", str(args.output.resolve()), flush=True)
    except Exception:
        import traceback

        traceback.print_exc()
        raise
    finally:
        app.close()


if __name__ == "__main__":
    main()
