from pathlib import Path

import pytest
import yaml

from wheelleg.config import load_policy
from wheelleg.tasks import TASKS
from wheelleg.training import load_training, runner_config

ROOT = Path(__file__).resolve().parents[1]
ROBOT = ROOT / "config/robot.yaml"


def read(path):
    return yaml.safe_load(path.read_text(encoding="utf8"))


def write(path, values):
    path.write_text(yaml.safe_dump(values), encoding="utf8")
    return path


def policy(family):
    return ROOT / "config/policies" / family / "policy_meta.yaml"


@pytest.mark.parametrize("family", ["p1", "p2", "p3"])
@pytest.mark.parametrize(
    "key,bad",
    [("obs_version", 3), ("obs_version", 4.0), ("hidden_dims", [256, 128, 64]), ("hidden_dims", [128.0, 64, 32])],
)
def test_network_contract(tmp_path, family, key, bad):
    data = read(policy(family))
    data.update(obs_version=4, hidden_dims=[128, 64, 32])
    data[key] = bad
    with pytest.raises(ValueError, match=key):
        load_policy(write(tmp_path / "p.yaml", data))


def test_shu_stage_scope(tmp_path):
    r = read(ROBOT)
    r["asset"].update(
        shu_leg_reset_joint_names=[None] * 12,
        guide_body_names=None,
        leg_body_names=None,
        termination_contact_body_names=None,
    )
    r["training"].update(shu_spawn={"min_root_height_m": None}, wheel_rim_sign=[None, None])
    robot = write(tmp_path / "robot.yaml", r)
    p = read(policy("p1"))
    p.update(obs_version=4, hidden_dims=[128, 64, 32])
    p["stages"].pop("recovery", None)
    for key in ("air_rewards", "reward_parameters", "rewards", "command_curriculum"):
        p["training"].pop(key, None)
    p["training"].pop("transition_reset", None)
    p["stages"]["flat"]["min_segments"] = None
    p["stages"]["landing"]["height_edges_m"] = [None] * 4 + [0.45]
    path = write(tmp_path / "p1.yaml", p)
    for task in ("p1-flat", "p1-landing", "p1-stairs"):
        cfg = load_training(task, robot, path)
        missing = set(cfg.missing())
        assert runner_config(cfg)["obs_groups"] == {"policy": ["policy"], "critic": ["critic"]}
        assert {
            "robot.asset.usd_path",
            "robot.asset.leg_body_names",
            "robot.asset.guide_body_names",
            "robot.asset.termination_contact_body_names",
            "robot.training.wheel_rim_sign[0]",
        } <= missing
        assert "robot.training.shu_spawn.min_root_height_m" in missing
        assert "robot.asset.shu_leg_reset_joint_names[0]" in missing
        assert ("policy.stages.flat.min_segments" in missing) == (task == "p1-flat")
        assert ("policy.stages.landing.height_edges_m[0]" in missing) == (task == "p1-landing")
        for key in ("air_wheel_height_bias_m", "air_wheel_height_max_m"):
            assert (f"policy.stages.landing.{key}" in missing) == (task == "p1-landing")
        assert not any("states_npz" in key or ".evaluation." in key for key in missing)
        with pytest.raises(ValueError, match="Training is not ready"):
            cfg.require_ready()
    with pytest.raises(ValueError, match="Unknown task"):
        load_training("p1-recovery", robot, path)


@pytest.mark.parametrize(
    "task,required",
    [("p2-spin", "spin_rates_rad_s"), ("p3-jump", "event_duration_s"), ("p3-tunnel", "tunnel.collision_bounds_m")],
)
def test_real_p2_p3_templates_block_unmeasured(task, required):
    spec = TASKS[task]
    cfg = load_training(task, ROBOT, policy(spec.policy))
    missing = cfg.missing()
    assert "robot.asset.usd_path" in missing
    assert f"policy.stages.{spec.stage}.{required}" in missing
    assert not any("shu_spawn" in field for field in missing)
    assert "policy.training.commands.vx_range_m_s" not in missing
    assert ("robot.asset.collision_body_names" in missing) == (task == "p3-tunnel")
    with pytest.raises(ValueError, match="Training is not ready"):
        cfg.require_ready()


@pytest.mark.parametrize(
    "task,key,bad",
    [
        ("p1-flat", "min_segments", 0),
        ("p1-flat", "error_floor", [0, 1]),
        ("p1-landing", "height_edges_m", [0, None, 0.4, 0.3, 0.45]),
        ("p1-landing", "air_wheel_height_bias_m", -0.1),
        ("p1-landing", "air_wheel_height_max_m", 0),
        ("p2-spin", "spin_rates_rad_s", [-19, 19]),
    ],
)
def test_reject_invalid_stage_calibration(tmp_path, task, key, bad):
    spec = TASKS[task]
    p = read(policy(spec.policy))
    p["stages"][spec.stage][key] = bad
    with pytest.raises(ValueError, match=key):
        load_training(task, ROBOT, write(tmp_path / "p.yaml", p))


def test_mixed_requires_flat_spawn_calibration(tmp_path):
    r = read(ROBOT)
    r["asset"].pop("shu_leg_reset_joint_names")
    for key in ("shu_spawn", "shu_reset_map"):
        r["training"].pop(key)
    robot = write(tmp_path / "r.yaml", r)
    cfg = load_training("p1-stairs", robot, policy("p1"))
    missing = set(cfg.missing())
    assert {
        "robot.training.shu_contact.support_force_n",
        "robot.asset.shu_leg_reset_joint_names",
        "robot.training.shu_spawn.min_root_height_m",
        "robot.training.shu_reset_map.mode",
    } <= missing
    assert any(k.startswith("policy.stages.stairs.terrain.") for k in missing)

    r["asset"]["shu_leg_reset_joint_names"] = ["invalid count for closed-chain resets"]
    with pytest.raises(ValueError, match="shu_leg_reset_joint_names"):
        load_training("p1-stairs", write(robot, r), policy("p1"))
    r["asset"].pop("shu_leg_reset_joint_names")
    r["training"]["shu_reset_map"] = {"mode": "invalid"}
    with pytest.raises(ValueError, match="shu_reset_map.mode"):
        load_training("p1-stairs", write(robot, r), policy("p1"))


def test_mixed_inherits_only_flat_recovery_probability(tmp_path):
    p = read(policy("p1"))
    path = tmp_path / "p1.yaml"
    p["stages"]["stairs"]["recovery_probability"] = 0.9  # not the flat replay source
    p["stages"]["flat"].update(recovery_probability=0.27, initial_fraction=None, min_segments=None)
    cfg = load_training("p1-stairs", ROBOT, write(path, p))
    assert cfg.flat_recovery_probability == 0.27
    assert not any(k.startswith("policy.stages.flat.") for k in cfg.missing())

    del p["stages"]["flat"]["recovery_probability"]
    cfg = load_training("p1-stairs", ROBOT, write(path, p))
    assert "policy.stages.flat.recovery_probability" in cfg.missing()
    for bad in (-0.1, 1.1, True):
        p["stages"]["flat"]["recovery_probability"] = bad
        with pytest.raises(ValueError, match="flat.recovery_probability"):
            load_training("p1-stairs", ROBOT, write(path, p))


def test_p2_partial_calibration_is_not_hardware_signoff(tmp_path):
    p = read(policy("p2"))
    p["stages"]["spin"].update(
        spin_rates_rad_s=[-18, None], spin_probabilities=[0.5, 0.5], hardware_spin_limit_rad_s=None
    )
    cfg = load_training("p2-spin", ROBOT, write(tmp_path / "p.yaml", p))
    for evaluation in (False, True):
        missing = cfg.missing(evaluation=evaluation)
        assert "policy.stages.spin.spin_rates_rad_s[1]" in missing
        assert "policy.stages.spin.spin_rates_rad_s[0]" not in missing
        assert "policy.stages.spin.hardware_spin_limit_rad_s" not in missing
        assert "robot.asset.termination_contact_body_names" in missing
        with pytest.raises(ValueError, match=r"spin_rates_rad_s\[1\]"):
            cfg.require_ready(evaluation=evaluation)


@pytest.mark.parametrize(
    "key,bad",
    [
        ("wheel_body_names", ["wheel_left", "wheel_.*"]),
        ("base_body_name", "base|chassis"),
        ("termination_contact_body_names", ["base", "base"]),
        ("undesired_contact_body_names", []),
    ],
)
def test_literal_asset_names(tmp_path, key, bad):
    r = read(ROBOT)
    r["asset"][key] = bad
    with pytest.raises(ValueError, match=key):
        load_training("p2-spin", write(tmp_path / "r.yaml", r), policy("p2"))


@pytest.mark.parametrize("task", list(TASKS))
def test_pending_p1_randomization_only_blocks_p1_training(task):
    family = TASKS[task].policy
    cfg = load_training(task, ROBOT, policy(family))
    expected = {"robot.asset.mass_randomized_leg_body_names"} | {
        f"robot.training.randomization.p1_materials.{group}.{field}"
        for group in ("base", "guide")
        for field in ("static_friction", "dynamic_friction", "restitution")
    }
    assert expected.intersection(cfg.missing()) == (expected if family == "p1" else set())
    assert not expected.intersection(cfg.missing(evaluation=True))


def test_p1_missing_material_entries_are_not_defaulted(tmp_path):
    r = read(ROBOT)
    del r["asset"]["mass_randomized_leg_body_names"]
    del r["training"]["randomization"]["p1_materials"]
    cfg = load_training("p1-flat", write(tmp_path / "r.yaml", r), policy("p1"))
    with pytest.raises(ValueError, match=r"p1_materials\.guide\.restitution"):
        cfg.require_ready()
    assert "robot.asset.mass_randomized_leg_body_names" in cfg.missing()


@pytest.mark.parametrize(
    "names",
    [["chassis"], ["wheel_l"], ["guide_l"], ["leg_a", "leg_a"], ["leg_.*"]],
)
def test_p1_mass_leg_names_must_be_literal_and_distinct_from_other_groups(tmp_path, names):
    r = read(ROBOT)
    r["asset"].update(
        base_body_name="chassis",
        wheel_body_names=["wheel_l", "wheel_r"],
        guide_body_names=["guide_l"],
        mass_randomized_leg_body_names=names,
    )
    with pytest.raises(ValueError, match="mass_randomized_leg_body_names"):
        load_training("p1-landing", write(tmp_path / "r.yaml", r), policy("p1"))


@pytest.mark.parametrize(
    "key,value",
    [
        ("static_friction", [-0.1, 1.0]),
        ("static_friction", [0.8, 0.4]),
        ("dynamic_friction", [0.5, 0.9]),
        ("restitution", [0.0, 1.1]),
    ],
)
def test_p1_material_ranges_are_validated_before_event_setup(tmp_path, key, value):
    r = read(ROBOT)
    r["training"]["randomization"]["p1_materials"]["guide"] = {
        "static_friction": [0.4, 1.0],
        "dynamic_friction": [0.1, 0.8],
        "restitution": [0.0, 0.05],
        key: value,
    }
    with pytest.raises(ValueError, match=rf"p1_materials\.guide\.{key}"):
        load_training("p1-stairs", write(tmp_path / "r.yaml", r), policy("p1"))


def test_partial_evidence_and_body_bounds(tmp_path):
    r = read(ROBOT)
    r["asset"]["collision_body_names"] = ["base", "wheel_left"]
    r["pending_measurements"].pop("imu_mounting_rotation")
    r["pending_measurements"]["motor_ids_and_protocol_readback"] = {"left": [1, None]}
    p = read(policy("p3"))
    p["stages"]["tunnel"]["tunnel"]["collision_bounds_m"] = {"base": [[0, None, 0], [1, 1, 1]]}
    cfg = load_training("p3-tunnel", write(tmp_path / "r.yaml", r), write(tmp_path / "p.yaml", p))
    missing = cfg.missing()
    assert "imu_mounting_rotation" in missing and "motor_ids_and_protocol_readback.left[1]" in missing
    assert "policy.stages.tunnel.tunnel.collision_bounds_m.wheel_left" in missing
    assert "policy.stages.tunnel.tunnel.collision_bounds_m.base[0][1]" in missing
    with pytest.raises(ValueError, match="collision_bounds_m.wheel_left"):
        cfg.require_ready()


def test_old_reset_library_cannot_enable_spawn(tmp_path):
    p = read(policy("p2"))
    p["training"]["transition_reset"] = {"probability": 1, "states_npz": "unknown.npz"}
    with pytest.raises(ValueError, match="transition_reset"):
        load_training("p2-spin", ROBOT, write(tmp_path / "p.yaml", p))


@pytest.mark.parametrize("task", list(TASKS))
def test_reset_map_only_in_spawn_stages(tmp_path, task):
    r = read(ROBOT)
    r["training"]["shu_spawn"]["ik_branch"] = None
    r["training"]["shu_reset_map"] = {
        "fixed_pin_xz_m": [[0, None], None],
        "auxiliary_joint_names": [],
        "hinge_zero_xz_rad": [],
        "hinge_asset_sign": [],
    }
    cfg = load_training(task, write(tmp_path / "r.yaml", r), policy(TASKS[task].policy))
    m = cfg.missing()
    spawn = TASKS[task].policy == "p1"
    assert ("robot.training.shu_spawn.ik_branch" in m) == spawn
    assert ("robot.training.shu_reset_map.mode" in m) == spawn
    assert ("robot.training.shu_reset_map.fixed_pin_xz_m[0][1]" in m) == spawn
    assert not any("shu_reset_map.hinge_" in k for k in m)
    if spawn:
        with pytest.raises(ValueError, match="shu_reset_map.mode"):
            cfg.require_ready()
    else:
        assert not any("shu_reset_map" in k for k in m)


@pytest.mark.parametrize(
    "section,key,value",
    [
        ("shu_spawn", "ik_branch", "reference"),
        ("shu_reset_map", "mode", "other"),
        ("shu_reset_map", "canonical_to_asset_sign", [1] * 13 + [0]),
        ("shu_reset_map", "knee_pivot_xz_m", [[1, None, 3], None]),
        ("shu_reset_map", "hinge_asset_sign", [1, -1]),
        ("shu_reset_map", "slider_safe_range_m", [[1, 0], None]),
    ],
)
def test_reject_invalid_partial_reset_map(tmp_path, section, key, value):
    r = read(ROBOT)
    r["training"]["shu_reset_map"] = {"auxiliary_joint_names": []}
    r["training"][section][key] = value
    with pytest.raises(ValueError, match=key):
        load_training("p1-landing", write(tmp_path / "r.yaml", r), policy("p1"))


def test_shu_p3_inherits_ground_recipe_without_inventing_jump_parameters():
    data = read(policy("p3"))
    training, stages = data["training"], data["stages"]
    assert set(stages) == {"jump", "tunnel"}
    assert all(value is None for value in stages["jump"].values())
    assert all(value is None for key, value in stages["tunnel"].items() if key != "tunnel")
    fixed_geometry = {k: v for k, v in stages["tunnel"]["tunnel"].items() if v is not None}
    assert fixed_geometry == {
        "beam_bottom_m": 0.25,
        "beam_height_m": 0.27,
        "lane_width_m": 0.8,
        "beam_offset_from_entrance_m": 1.35,
        "beam_length_m": 0.35,
    }
    flat = read(policy("p1"))["training"]
    for family in ("p2", "p3"):
        cfg = read(policy(family))["training"]
        for key in (
            "vx_tol_max",
            "vx_tol_knee",
            "wz_tol_max",
            "wz_tol_knee",
            "vx_error_sigma",
            "wz_error_sigma",
            "height_gate_shape",
        ):
            assert cfg["reward_parameters"][key] == flat["shu_rewards"][key]
        for key in ("height_duration_s", "linear_slew_m_s2", "angular_slew_rad_s2"):
            assert cfg["commands"][key] == flat["commands"][key]
        assert "height_slew_m_s" not in cfg["commands"] and cfg["reward_clip"] == 1.0
    assert training["commands"]["vx_range_m_s"] == flat["commands"]["vx_range_m_s"]
    assert training["rewards"]["jump_landing"] is None and training["rewards"]["tunnel_crossing"] is None
    assert "disturbance" not in training  # no automatic external push on P3


@pytest.mark.parametrize("task", ["p3-jump", "p3-tunnel"])
def test_pending_p3_tuning_is_reported_not_defaulted(task):
    cfg = load_training(task, ROBOT, policy("p3"))
    prefix = f"policy.stages.{TASKS[task].stage}."
    missing = set(cfg.missing(simulate_jump_button=True))
    assert {
        prefix + k for k in ("flight_tracking_scale", "landing_stable_s", "no_press_probability", "press_time_range_s")
    } <= missing
    with pytest.raises(ValueError, match="Training is not ready"):
        cfg.require_ready(simulate_jump_button=True)
