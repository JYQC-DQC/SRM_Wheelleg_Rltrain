import importlib.util
import re
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def make_env_cfg(monkeypatch):
    # Read the real startup event configuration without launching Isaac Sim.
    def entity(name, **kwargs):
        return SimpleNamespace(name=name, **kwargs)

    def articulation(**kwargs):
        return SimpleNamespace(**kwargs)

    def ray_caster(**kwargs):
        return SimpleNamespace(**kwargs)

    articulation.InitialStateCfg = SimpleNamespace
    ray_caster.OffsetCfg = SimpleNamespace
    modules = {
        "isaaclab": {},
        "isaaclab.sim": dict.fromkeys(
            ("UsdFileCfg", "ArticulationRootPropertiesCfg", "RigidBodyMaterialCfg", "SimulationCfg"), SimpleNamespace
        ),
        "isaaclab.actuators": {"IdealPDActuatorCfg": SimpleNamespace},
        "isaaclab.assets": {"ArticulationCfg": articulation},
        "isaaclab.envs": {"DirectRLEnvCfg": SimpleNamespace},
        "isaaclab.envs.mdp": dict.fromkeys(
            ("randomize_rigid_body_mass", "randomize_rigid_body_com", "randomize_rigid_body_material"), object()
        ),
        "isaaclab.managers": {"EventTermCfg": SimpleNamespace, "SceneEntityCfg": entity},
        "isaaclab.scene": {"InteractiveSceneCfg": SimpleNamespace},
        "isaaclab.sensors": {
            "ContactSensorCfg": SimpleNamespace,
            "RayCasterCfg": ray_caster,
            "patterns": SimpleNamespace(GridPatternCfg=SimpleNamespace),
        },
        "isaaclab.terrains": dict.fromkeys(
            ("HfRandomUniformTerrainCfg", "TerrainGeneratorCfg", "TerrainImporterCfg"), SimpleNamespace
        ),
        "isaaclab.utils": {"configclass": lambda cls: cls},
        "isaac.wheelleg_tasks.terrain": {"MixedTerrainCfg": SimpleNamespace, "MixedTerrainGenerator": object()},
    }
    for name, entries in modules.items():
        module = ModuleType(name)
        vars(module).update(entries)
        monkeypatch.setitem(sys.modules, name, module)
    spec = importlib.util.spec_from_file_location(
        "isaac.wheelleg_tasks._test_env_cfg", ROOT / "isaac/wheelleg_tasks/env_cfg.py"
    )
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded.make_env_cfg


@pytest.mark.parametrize(
    "task,evaluation",
    [("p1-flat", False), ("p1-landing", False), ("p1-stairs", False), ("p2-spin", False), ("p1-flat", True)],
)
def test_startup_mass_and_material_targets(make_env_cfg, task, evaluation):
    data = yaml.safe_load((ROOT / "config/robot.yaml").read_text(encoding="utf8"))
    asset, shared = data["asset"], data["training"]
    asset.update(
        base_body_name="chassis",
        wheel_body_names=["wheel_l", "wheel_r"],
        mass_randomized_leg_body_names=["upper_leg", "spring_link"],
        leg_body_names=["upper_leg", "lower_leg"],
        guide_body_names=["guide_l", "guide_r"],
        active_joint_names=data["joint_order"],
        spring_joint_names=["spring_l", "spring_r"],
    )
    shared["saturation_torque_nm"] = [1] * 6
    shared["spring"]["force_limit_n"] = [1, 1]
    stage = {}
    if task == "p1-stairs":
        p1 = yaml.safe_load((ROOT / "config/policies/p1/policy_meta.yaml").read_text(encoding="utf8"))
        stage = p1["stages"]["stairs"]
    t = SimpleNamespace(
        task=task,
        asset=asset,
        shared=shared,
        settings={"seed": 1, "episode_length_s": 20},
        stage=stage,
        policy=SimpleNamespace(torque_limit_nm=[1] * 6),
        robot=SimpleNamespace(control_hz=500, decimation=5, leg_indices=data["leg_indices"]),
        require_ready=lambda **_: None,
    )
    cfg = make_env_cfg(t, 1, "cpu", evaluation=evaluation)
    if evaluation:
        assert "events" not in vars(cfg)
        return
    events = cfg.events
    assert events.base_mass.params["asset_cfg"].body_names == ["chassis"]
    assert events.base_mass.params["mass_distribution_params"] == (0.9, 1.3)
    assert events.limb_mass.params["mass_distribution_params"] == (0.9, 1.1)
    assert events.inertia.params == {"scale_range": (0.9, 1.1)}
    assert events.com.params["com_range"] == {"x": (-0.04, 0.04), "y": (-0.02, 0.02), "z": (-0.02, 0.02)}
    pn = events.limb_mass.params["asset_cfg"].body_names
    bodies = ["chassis", "upper_leg", "lower_leg", "spring_link", "wheel_l", "wheel_r", "guide_l", "guide_r", "misc"]
    matched = {body for body in bodies if any(re.fullmatch(pattern, body) for pattern in pn)}
    expected_materials = {"material": (asset["wheel_body_names"], (0.5, 1.2), (0.4, 1.0), (0.0, 0.0))}
    if task.startswith("p1-"):
        assert matched == {"upper_leg", "spring_link", "wheel_l", "wheel_r"}
        expected_materials.update(
            base_material=(["chassis"], (0.01, 0.1), (0.01, 0.1), (0.02, 0.20)),
            guide_material=(asset["guide_body_names"], (0.10, 0.70), (0.10, 0.70), (0.01, 0.10)),
        )
    else:
        assert matched == set(bodies) - {"chassis"}
    assert {name for name in vars(events) if name.endswith("material")} == set(expected_materials)
    for name, (names, static, dynamic, restitution) in expected_materials.items():
        term = getattr(events, name)
        assert term.mode == "startup"
        assert term.params["asset_cfg"].body_names == names
        assert term.params["static_friction_range"] == static
        assert term.params["dynamic_friction_range"] == dynamic
        assert term.params["restitution_range"] == restitution
        assert term.params["make_consistent"] is True
        assert term.params["num_buckets"] == (8 if name == "guide_material" else 64)
