from types import SimpleNamespace

import isaaclab.envs.mdp as mdp
import isaaclab.sim as sim_utils
from isaaclab.actuators import IdealPDActuatorCfg
from isaaclab.assets import ArticulationCfg
from isaaclab.envs import DirectRLEnvCfg
from isaaclab.managers import EventTermCfg, SceneEntityCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sensors import ContactSensorCfg, RayCasterCfg, patterns
from isaaclab.terrains import HfRandomUniformTerrainCfg, TerrainGeneratorCfg, TerrainImporterCfg
from isaaclab.utils import configclass

from wheelleg.training import TrainingConfig, mutable

from .events import randomize_inertia
from .terrain import BumpsCfg, SlopeCfg, StepsCfg


@configclass
class WheelLegEnvCfg(DirectRLEnvCfg):
    action_space = 6
    observation_space = 35
    state_space = 81
    training: TrainingConfig = None
    evaluation: bool = False
    robot: ArticulationCfg = None
    terrain: TerrainImporterCfg = None
    contact_sensor: ContactSensorCfg = None
    height_scanner: RayCasterCfg = None
    obstacle_contact_sensors: dict[str, ContactSensorCfg] = {}


def make_env_cfg(t: TrainingConfig, num_envs: int, device: str, *, evaluation: bool = False) -> WheelLegEnvCfg:
    t.require_ready(evaluation=evaluation)
    asset, physics = t.asset, t.shared
    names = list(asset["active_joint_names"])
    # The explicit motor envelope and randomized PD run every physics step in _apply_action.
    active = IdealPDActuatorCfg(
        joint_names_expr=names,
        stiffness=0.0,
        damping=0.0,
        effort_limit={
            n: (
                t.policy.torque_limit_nm[i]
                if asset.get("reference_preset") == "scut_v14_2"
                else max(t.policy.torque_limit_nm[i], physics["saturation_torque_nm"][i])
            )
            * physics["randomization"]["hip_torque_scale" if i in t.robot.leg_indices else "wheel_torque_scale"][1]
            for i, n in enumerate(names)
        },
        armature=dict(zip(names, physics["joint_armature"], strict=True)),
        friction=dict(zip(names, physics["joint_coulomb_friction"], strict=True)),
        dynamic_friction=dict(zip(names, physics["joint_dynamic_friction"], strict=True)),
        viscous_friction=dict(zip(names, physics["joint_viscous_friction"], strict=True)),
    )
    actuators = {
        "active": active,
        "spring": IdealPDActuatorCfg(
            joint_names_expr=list(asset["spring_joint_names"]),
            stiffness=0.0,
            damping=0.0,
            effort_limit=max(physics["spring"]["force_limit_n"]),
        ),
    }
    if asset["passive_joint_names"]:
        actuators["passive"] = IdealPDActuatorCfg(
            joint_names_expr=list(asset["passive_joint_names"]),
            stiffness=0.0,
            damping=physics["passive_damping"],
            effort_limit=physics["passive_effort_limit"],
        )
    robot = ArticulationCfg(
        prim_path="/World/envs/env_.*/Robot",
        spawn=sim_utils.UsdFileCfg(
            usd_path=asset["usd_path"],
            activate_contact_sensors=True,
            articulation_props=sim_utils.ArticulationRootPropertiesCfg(
                enabled_self_collisions=False,
                solver_position_iteration_count=physics["solver_position_iterations"],
                solver_velocity_iteration_count=physics["solver_velocity_iterations"],
            ),
        ),
        init_state=ArticulationCfg.InitialStateCfg(
            pos=tuple(asset["initial_root_position_m"]),
            joint_pos=mutable(asset["initial_joint_positions_rad"]),
            joint_vel={".*": 0.0},
        ),
        actuators=actuators,
    )
    if asset.get("reference_preset") == "scut_v14_2":
        # Preserve source passive/guide and gimbal actuators; replace only the six motors and springs.
        import sys

        sys.path.insert(0, asset["reference_package"])
        from agent_world.assets.wheelbipe_V14_2 import Wheelbipe_V14_2_CFG

        reference = Wheelbipe_V14_2_CFG.copy()
        reference.prim_path = robot.prim_path
        reference.spawn.usd_path = asset["usd_path"]
        reference.init_state = robot.init_state
        active.velocity_limit = {
            **reference.actuators["legs_act"].velocity_limit,
            ".*_wheel_joint": reference.actuators["wheel"].velocity_limit,
        }
        actuators["spring"].armature = reference.actuators["spring"].armature
        for name in ("legs_act", "wheel", "spring"):
            del reference.actuators[name]
        reference.actuators.update(actuators)
        robot = reference
    terrain = TerrainImporterCfg(
        prim_path="/World/ground",
        terrain_type="plane",
        num_envs=num_envs,
        env_spacing=physics["env_spacing_m"],
        physics_material=sim_utils.RigidBodyMaterialCfg(**mutable(physics["ground_material"])),
    )
    terrain.max_init_terrain_level = 0 if not evaluation else None
    scanner = None
    if t.task in ("p1-stairs", "p1-recovery"):
        s = t.stage["terrain"]
        terrain.terrain_type = "generator"
        step_proportion = (
            1 - s["flat_proportion"] - s["slope_proportion"] - s["bump_proportion"] - s["rough_proportion"]
        ) / 2
        terrain.terrain_generator = TerrainGeneratorCfg(
            seed=t.settings["seed"],
            size=tuple(s["tile_size_m"]),
            num_rows=s["rows"],
            num_cols=s["columns"],
            curriculum=not evaluation,
            sub_terrains={
                "flat": StepsCfg(
                    proportion=s["flat_proportion"],
                    step_count=0,
                    step_height_range=tuple(s["step_height_range_m"]),
                    step_width=s["step_width_m"],
                ),
                "one": StepsCfg(
                    proportion=step_proportion,
                    step_count=1,
                    step_height_range=tuple(s["step_height_range_m"]),
                    step_width=s["step_width_m"],
                ),
                "two": StepsCfg(
                    proportion=step_proportion,
                    step_count=2,
                    step_height_range=tuple(s["step_height_range_m"]),
                    step_width=s["step_width_m"],
                ),
                "slope": SlopeCfg(proportion=s["slope_proportion"], angle_range=tuple(s["slope_angle_range_rad"])),
                "bumps": BumpsCfg(
                    proportion=s["bump_proportion"],
                    height_range=tuple(s["bump_height_range_m"]),
                    spacing=s["bump_spacing_m"],
                    width=s["bump_width_m"],
                ),
                # 改自 SCUT manager/mdp/isaaclab/terrains.py:109-115 (RANDOM_UNIFORM_FOR_RM)。
                "rough": HfRandomUniformTerrainCfg(
                    proportion=s["rough_proportion"],
                    noise_range=tuple(s["rough_noise_range_m"]),
                    noise_step=s["rough_noise_step_m"],
                    downsampled_scale=s["rough_downsampled_scale_m"],
                    border_width=s["heightfield_border_width_m"],
                ),
            },
        )
        scanner = RayCasterCfg(
            prim_path=f"/World/envs/env_.*/Robot/{asset['base_body_name']}",
            offset=RayCasterCfg.OffsetCfg(pos=(0.0, 0.0, 20.0)),
            ray_alignment="yaw",
            pattern_cfg=patterns.GridPatternCfg(resolution=0.1, size=(1.0, 0.6)),
            mesh_prim_paths=["/World/ground"],
            debug_vis=False,
        )
    cfg = WheelLegEnvCfg(
        training=t,
        evaluation=evaluation,
        seed=t.settings["seed"],
        decimation=t.robot.decimation,
        episode_length_s=t.settings["episode_length_s"],
        sim=sim_utils.SimulationCfg(
            dt=1 / t.robot.control_hz,
            render_interval=t.robot.decimation,
            device=device,
            gravity=(0.0, 0.0, -physics["gravity_m_s2"]),
        ),
        scene=InteractiveSceneCfg(num_envs=num_envs, env_spacing=physics["env_spacing_m"], replicate_physics=True),
        robot=robot,
        terrain=terrain,
        contact_sensor=ContactSensorCfg(
            prim_path="/World/envs/env_.*/Robot/.*", history_length=3, update_period=0.0, track_air_time=True
        ),
        height_scanner=scanner,
        state_space=158 if scanner else 81,
    )
    if t.task == "p3-tunnel":
        # contact_sensor_cfg.py:63-68: one sensing body per environment, not Robot/.*.
        cfg.obstacle_contact_sensors = {
            name: ContactSensorCfg(
                prim_path=f"/World/envs/env_.*/Robot/{name}",
                update_period=0.0,
                history_length=0,
                filter_prim_paths_expr=[
                    f"/World/envs/env_.*/{target}" for target in ("TunnelBeam", "RailLeft", "RailRight")
                ],
            )
            for name in asset["collision_body_names"]
        }
    if not evaluation:
        r = physics["randomization"]
        base = SceneEntityCfg("robot", body_names=[asset["base_body_name"]])
        limb_pattern = f"(?!{asset['base_body_name']}$).*"
        cfg.events = SimpleNamespace(
            base_mass=EventTermCfg(
                func=mdp.randomize_rigid_body_mass,
                mode="startup",
                params={
                    "asset_cfg": base,
                    "mass_distribution_params": tuple(r["base_mass_scale"]),
                    "operation": "scale",
                },
            ),
            limb_mass=EventTermCfg(
                func=mdp.randomize_rigid_body_mass,
                mode="startup",
                params={
                    "asset_cfg": SceneEntityCfg("robot", body_names=[limb_pattern]),
                    "mass_distribution_params": tuple(r["limb_mass_scale"]),
                    "operation": "scale",
                },
            ),
            inertia=EventTermCfg(
                func=randomize_inertia, mode="startup", params={"scale_range": tuple(r["inertia_scale"])}
            ),
            com=EventTermCfg(
                func=mdp.randomize_rigid_body_com,
                mode="startup",
                params={
                    "asset_cfg": base,
                    "com_range": {k: (-v, v) for k, v in zip("xyz", r["com_offset_m"], strict=True)},
                },
            ),
            material=EventTermCfg(
                func=mdp.randomize_rigid_body_material,
                mode="startup",
                params={
                    "asset_cfg": SceneEntityCfg("robot", body_names=list(asset["wheel_body_names"])),
                    "static_friction_range": tuple(r["static_friction"]),
                    "dynamic_friction_range": tuple(r["dynamic_friction"]),
                    "restitution_range": tuple(r["restitution"]),
                    "num_buckets": 64,
                    "make_consistent": True,
                },
            ),
        )
        # 改自 SCUT V14/env_cfg.py:136-159: 机身、导轮等非轮子刚体的摩擦。按配置条目循环，不是按环境循环。
        for i, entry in enumerate(r["body_materials"]):
            setattr(
                cfg.events,
                f"body_material_{i}",
                EventTermCfg(
                    func=mdp.randomize_rigid_body_material,
                    mode="startup",
                    params={
                        "asset_cfg": SceneEntityCfg("robot", body_names=list(entry["body_names"])),
                        "static_friction_range": tuple(entry["static_friction"]),
                        "dynamic_friction_range": tuple(entry["dynamic_friction"]),
                        "restitution_range": tuple(entry["restitution"]),
                        "num_buckets": entry["buckets"],
                        "make_consistent": True,
                    },
                ),
            )
    return cfg
