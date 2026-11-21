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

from wheelleg.observation import POLICY_OBS_DIM
from wheelleg.shu_terrain import mixed_columns, stair_lip_dimensions
from wheelleg.tasks import TASKS
from wheelleg.training import TrainingConfig, mutable

from .events import randomize_inertia
from .terrain import MixedTerrainCfg, MixedTerrainGenerator


@configclass
class WheelLegEnvCfg(DirectRLEnvCfg):
    action_space = 6
    observation_space = POLICY_OBS_DIM
    state_space = POLICY_OBS_DIM + 46
    training: TrainingConfig = None
    flat_transfer: dict | None = None
    evaluation: bool = False
    simulate_jump_button: bool = False
    robot: ArticulationCfg = None
    terrain: TerrainImporterCfg = None
    contact_sensor: ContactSensorCfg = None
    height_scanner: RayCasterCfg = None
    obstacle_contact_sensors: dict[str, ContactSensorCfg] = {}


def make_env_cfg(
    t: TrainingConfig,
    num_envs: int,
    device: str,
    *,
    evaluation: bool = False,
    flat_transfer: dict | None = None,
    simulate_jump_button: bool = False,
) -> WheelLegEnvCfg:
    if simulate_jump_button and (evaluation or t.task not in ("p3-jump", "p3-tunnel")):
        raise ValueError("synthetic jump button is only available for P3 training")
    t.require_ready(evaluation=evaluation, simulate_jump_button=simulate_jump_button)
    asset, physics = t.asset, t.shared
    names = list(asset["active_joint_names"])
    # The explicit motor envelope and randomized PD run every physics step in _apply_action.
    active = IdealPDActuatorCfg(
        joint_names_expr=names,
        stiffness=0.0,
        damping=0.0,
        effort_limit={
            n: max(t.policy.torque_limit_nm[i], physics["saturation_torque_nm"][i])
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
    terrain = TerrainImporterCfg(
        prim_path="/World/ground",
        terrain_type="plane",
        num_envs=num_envs,
        env_spacing=physics["env_spacing_m"],
        physics_material=sim_utils.RigidBodyMaterialCfg(**mutable(physics["ground_material"])),
    )
    terrain.max_init_terrain_level = 0 if not evaluation else None
    scanner = None
    if t.task == "p1-stairs":
        s = t.stage["terrain"]
        columns = mixed_columns(s, production=True)
        lip = stair_lip_dimensions(s)
        terrain.terrain_type = "generator"
        rough = mutable(s["profiles"]["rough"]["geometry"])
        # TerrainGenerator propagates these three atlas parameters to every height-field sub-config.
        terrain.terrain_generator = TerrainGeneratorCfg(
            horizontal_scale=rough["horizontal_scale"],
            vertical_scale=rough["vertical_scale"],
            slope_threshold=rough["slope_threshold"],
            class_type=MixedTerrainGenerator,
            seed=t.settings["seed"],
            size=tuple(s["tile_size_m"]),
            border_width=s["border_width_m"],
            num_rows=s["rows"],
            num_cols=len(columns),
            curriculum=True,
            sub_terrains={
                (name + ("_lip" if raised else "")): HfRandomUniformTerrainCfg(proportion=1.0, **rough)
                if name == "rough"
                else MixedTerrainCfg(
                    proportion=1.0,
                    profile=name,
                    parameters={
                        **mutable(s["profiles"]["slope" if name == "slope_inverted" else name]["geometry"]),
                        "seed": t.settings["seed"],
                    },
                    stair_lip=lip if raised else None,
                )
                for name, raised, _ in columns
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
        simulate_jump_button=simulate_jump_button,
        flat_transfer=flat_transfer,
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
        state_space=POLICY_OBS_DIM + 46 + (77 if scanner else 0),
    )
    if t.task == "p3-tunnel":
        # contact_sensor_cfg.py:63-68: one sensing body per environment, not Robot/.*.
        cfg.obstacle_contact_sensors = {
            name: ContactSensorCfg(
                prim_path=f"/World/envs/env_.*/Robot/{name}",
                update_period=0.0,
                history_length=0,
                filter_prim_paths_expr=["/World/envs/env_.*/TunnelBeam"],
            )
            for name in asset["collision_body_names"]
        }
    if not evaluation:
        r = physics["randomization"]
        base = SceneEntityCfg("robot", body_names=[asset["base_body_name"]])
        p1 = TASKS[t.task].policy == "p1"
        wheels = SceneEntityCfg("robot", body_names=list(asset["wheel_body_names"]))
        if p1:
            limb_names = [*asset["mass_randomized_leg_body_names"], *asset["wheel_body_names"]]
        else:
            limb_names = [f"(?!{asset['base_body_name']}$).*"]
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
                    "asset_cfg": SceneEntityCfg("robot", body_names=limb_names),
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
        )
        materials = [("material", wheels, r["static_friction"], r["dynamic_friction"], (0.0, 0.0))]
        if p1:
            guide = SceneEntityCfg("robot", body_names=list(asset["guide_body_names"]))
            for group_name, entity in (("base", base), ("guide", guide)):
                material = r["p1_materials"][group_name]
                materials.append(
                    (
                        f"{group_name}_material",
                        entity,
                        material["static_friction"],
                        material["dynamic_friction"],
                        material["restitution"],
                    )
                )
        for name, entity, static_friction, dynamic_friction, restitution in materials:
            setattr(
                cfg.events,
                name,
                EventTermCfg(
                    func=mdp.randomize_rigid_body_material,
                    mode="startup",
                    params={
                        "asset_cfg": entity,
                        "static_friction_range": tuple(static_friction),
                        "dynamic_friction_range": tuple(dynamic_friction),
                        "restitution_range": tuple(restitution),
                        "num_buckets": 64,
                        "make_consistent": True,
                    },
                ),
            )
    return cfg
