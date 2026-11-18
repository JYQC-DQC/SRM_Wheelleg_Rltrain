import itertools
from types import SimpleNamespace

import numpy as np
import pytest
import torch

from wheelleg.jump_geometry import box_bottom_z, cylinder_bottom_z, sagittal_leg_angle, usd_collision_frames


def test_box_support_matches_lowest_vertex_for_tilted_box():
    axes_z = torch.tensor([[0.06, -0.08, 0.09], [-0.16, -0.01, 0.04]])
    center_z = torch.tensor([0.34, 0.52])
    signs = torch.tensor(list(itertools.product((-1.0, 1.0), repeat=3)))
    expected = (center_z[:, None] + axes_z @ signs.T).amin(-1)
    torch.testing.assert_close(box_bottom_z(center_z, axes_z), expected)


def test_leg_angle_uses_gravity_and_ignores_lateral_offset_at_any_yaw():
    legs = torch.tensor([[[0.1, 0.2, -0.2], [-0.1, -0.2, -0.2]], [[-0.2, 0.1, -0.2], [0.2, -0.1, -0.2]]])
    angles = sagittal_leg_angle(legs, torch.tensor([0, torch.pi / 2]))
    expected = torch.atan(torch.tensor([[0.5, -0.5], [0.5, -0.5]]))
    torch.testing.assert_close(angles, expected)


def test_usd_collision_frames_compose_transform_and_exclude_visuals_and_nested_bodies():
    pytest.importorskip("pxr")
    from pxr import Gf, Usd, UsdGeom, UsdPhysics

    stage = Usd.Stage.CreateInMemory()
    UsdGeom.SetStageMetersPerUnit(stage, 1)
    UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.z)
    chassis = UsdGeom.Xform.Define(stage, "/chassis")
    chassis.AddTranslateOp().Set(Gf.Vec3d(0, 0, 0.7))
    UsdPhysics.RigidBodyAPI.Apply(chassis.GetPrim())
    offset = UsdGeom.Xform.Define(stage, "/chassis/offset")
    offset.AddTranslateOp().Set(Gf.Vec3d(0, 0, -0.1))
    offset.AddRotateYOp().Set(90)
    collider = UsdGeom.Cube.Define(stage, "/chassis/offset/box")
    collider.AddScaleOp().Set(Gf.Vec3f(0.4, 0.2, 0.1))
    collider.GetSizeAttr().Set(1)
    UsdPhysics.CollisionAPI.Apply(collider.GetPrim())
    UsdGeom.Cube.Define(stage, "/chassis/visual")
    disabled = UsdGeom.Cube.Define(stage, "/chassis/disabled")
    UsdPhysics.CollisionAPI.Apply(disabled.GetPrim()).GetCollisionEnabledAttr().Set(False)
    wheel = UsdGeom.Xform.Define(stage, "/chassis/wheel")
    UsdPhysics.RigidBodyAPI.Apply(wheel.GetPrim())
    cylinder = UsdGeom.Cylinder.Define(stage, "/chassis/wheel/cylinder")
    cylinder.GetAxisAttr().Set(UsdGeom.Tokens.y)
    cylinder.GetRadiusAttr().Set(0.06)
    cylinder.GetHeightAttr().Set(0.025)
    UsdPhysics.CollisionAPI.Apply(cylinder.GetPrim())

    boxes = torch.from_numpy(usd_collision_frames(chassis.GetPrim(), "box"))
    assert boxes.shape == (1, 4, 3)
    assert box_bottom_z(boxes[0, 3, 2], boxes[0, :3, 2]).item() == pytest.approx(-0.30)
    wheels = torch.from_numpy(usd_collision_frames(wheel.GetPrim(), "cylinder"))
    assert cylinder_bottom_z(wheels[0, 3, 2], wheels[0, :3, 2]).item() == pytest.approx(-0.06)
    assert cylinder_bottom_z(wheels[0, 3, 1], wheels[0, :3, 1]).item() == pytest.approx(-0.0125)


def test_mujoco_reads_compiled_offset_and_rotated_colliders_from_current_qpos():
    mujoco = pytest.importorskip("mujoco")
    pytest.importorskip("glfw")
    from tools.play_jump import JumpSim

    model = mujoco.MjModel.from_xml_string("""
    <mujoco>
      <worldbody>
        <geom name="ground" type="plane" size="0 0 0.1" pos="0 0 0.1"/>
        <body name="base" pos="0 0 0.5">
          <freejoint/>
          <geom name="box" type="box" size="0.2 0.1 0.05" pos="0 0 -0.05" euler="0 90 0"/>
          <body name="left" pos="0 0.2 -0.3">
            <joint name="l"/>
            <geom name="wheel_l" type="cylinder" size="0.06 0.015" euler="60 0 0"/>
          </body>
          <body name="right" pos="0 -0.2 -0.3">
            <joint name="r"/>
            <geom name="wheel_r" type="cylinder" size="0.07 0.02" euler="90 0 0"/>
          </body>
        </body>
      </worldbody>
    </mujoco>
    """)
    data = mujoco.MjData(model)
    data.qpos[2] += 0.05
    sim = SimpleNamespace(
        model=model,
        data=data,
        ground=model.geom("ground").id,
        base=model.body("base").id,
        wheel_ids=np.array([model.body(name).id for name in ("left", "right")]),
        jump_boxes=np.array([model.geom("box").id]),
        jump_cylinders=np.array([model.geom(name).id for name in ("wheel_l", "wheel_r")]),
        jump_hip_joints=np.array([[model.joint("l").id] * 2, [model.joint("r").id] * 2]),
    )
    body, wheels, _ = JumpSim._jump_geometry(sim)
    assert body == pytest.approx(0.20)
    assert wheels == pytest.approx([0.15 - 0.06 * np.sqrt(3) / 2 - 0.015 / 2, 0.15 - 0.07])
