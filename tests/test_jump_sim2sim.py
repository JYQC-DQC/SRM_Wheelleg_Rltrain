from pathlib import Path
from types import SimpleNamespace

import glfw
import mujoco
import numpy as np
import pytest
import torch
import yaml

from tools.play_jump import JumpPlayer, JumpSim, NumpyActor, RunConfig, build, build_arena
from wheelleg.config import load_policy, load_robot
from wheelleg.tensor_ops import observation_tensor

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "sim2sim/checkpoints/jump_latest"


@pytest.fixture(scope="module")
def playground(tmp_path_factory):
    if not (RUN / "params/run.json").exists():
        pytest.skip("Cloud jump snapshot has not been downloaded")
    torch.set_num_threads(1)
    cfg = RunConfig(RUN)
    p = yaml.safe_load((ROOT / "config/policies/p3/policy_meta.yaml").read_text(encoding="utf-8"))["sim2sim"]
    output = tmp_path_factory.mktemp("jump_scene")
    flat, arena = output / "flat.xml", output / "arena.xml"
    build(ROOT / "runs/scut_experience/scene.xml", RUN / "params/robot.yaml", flat, p["wheel_friction"])
    sites = build_arena(flat, arena, p["course"], cfg.shared["ground_material"]["dynamic_friction"])
    checkpoint = max(RUN.glob("model_*.pt"), key=lambda f: int(f.stem.split("_")[1]))
    actor = NumpyActor(checkpoint, cfg.policy["hidden_dims"])
    return JumpSim(cfg, actor, arena), sites, p


def test_manual_keypad_and_space_before_settling():
    controls = yaml.safe_load((ROOT / "config/policies/p3/policy_meta.yaml").read_text(encoding="utf-8"))["sim2sim"][
        "controls"
    ]

    class Sim:
        cfg = SimpleNamespace(
            evaluation={"height_m": 0.22},
            commands={
                "height_range_m": (0.22, 0.30),
                "height_slew_m_s": 0.2,
                "linear_slew_m_s2": 2.0,
                "angular_slew_rad_s2": 10.0,
            },
            policy_hz=100,
        )
        jump = SimpleNamespace(active=np.array([False]))
        estopped = False
        presses = []

        def reset(self, _):
            self.time = 0.0
            self.jump.active.fill(False)

        def press_jump(self, target):
            if not self.jump.active[0]:
                self.presses.append((self.time, target))
                self.jump.active.fill(True)

        def step(self, command, height):
            self.time += 0.01
            return {"terminated": False}

    sim = Sim()
    player = JumpPlayer(sim, [{"spawn_xy_m": (0.0, 0.0)}], controls)
    player.key(glfw.KEY_KP_8)
    player.key(glfw.KEY_KP_4)
    player.key(glfw.KEY_KP_9)
    player.key(glfw.KEY_KP_ADD)
    np.testing.assert_allclose(player.target, [0.25, 0.0, 0.5])
    assert player.body_height_target_m == pytest.approx(0.24)
    assert player.height_m == pytest.approx(0.05)
    player.key(glfw.KEY_SPACE)
    assert sim.presses == [(0.0, 0.05)]  # No hold time, velocity threshold, or stable stance required.
    player.step()
    assert player.body_height_m == pytest.approx(0.22)
    sim.jump.active.fill(False)
    player.step()
    assert player.body_height_m == pytest.approx(0.222)
    player.key(glfw.KEY_KP_5)
    np.testing.assert_array_equal(player.target, 0)


def test_hollow_tunnels_and_step_dimensions(playground):
    sim, sites, p = playground
    assert len(sites) == 12
    m, d = sim.model, sim.data
    for site in sites:
        if site["kind"] == "flat":
            continue
        x, y = site["start_x_m"], site["center_y_m"]
        if site["kind"] == "tunnel":
            roof = m.geom(site["name"] + "_roof")
            h = site["height_m"]
            np.testing.assert_allclose(roof.size * 2, [0.35, 0.8, 0.02])
            assert roof.pos[2] + roof.size[2] == pytest.approx(h)
            assert sim.surface_height(np.array([x + 0.175, y]), 1.0) == pytest.approx(h)
            # A horizontal ray crosses the cavity without meeting a filled obstacle.
            distance = mujoco.mj_ray(
                m,
                d,
                np.array([x - 0.01, y, (h - 0.02) / 2]),
                np.array([1.0, 0.0, 0.0]),
                np.array([0, 0, 0, 1, 0, 0], dtype=np.uint8),
                True,
                -1,
                None,
            )
            assert distance < 0 or distance > 0.37
            assert sim.surface_height(np.array([x + 0.175, y]), h - 0.03) == pytest.approx(0.0)
        elif site["kind"] == "step":
            assert sim.surface_height(np.array([x + 0.1, y]), 1.0) == pytest.approx(site["height_m"])
        else:
            assert sim.surface_height(np.array([x + 0.79, y]), 1.0) == pytest.approx(0.2)
            assert sim.surface_height(np.array([x + 0.81, y]), 1.0) == pytest.approx(0.4)


def test_p3_observation_matches_training_tensor_and_actor(playground):
    sim, sites, p = playground
    player = JumpPlayer(sim, sites, p["controls"])
    player.set_targets(0.15, -0.5, 0.7)
    player.key(glfw.KEY_SPACE)
    sim.jump.elapsed[:] = 0.3
    sensor = np.linspace(-0.4, 0.8, 18)
    sim.delayed_sensor = sensor
    sim.raw_action = np.linspace(-1, 1, 6)
    command = np.array([-0.5, 0.0, 0.7])
    height = player.body_height_m
    mode = sim.observation_mode()
    np.testing.assert_allclose(mode[:4], [1, 0, 0, 0])
    np.testing.assert_allclose(mode[4:], [1, 0.15 * sim.cfg.scales["height"], 0.25])
    fields = dict(
        command=command,
        height=np.array([height]),
        angular_velocity=sensor[:3],
        gravity=sensor[3:6],
        joint_position=sensor[6:12],
        joint_velocity=sensor[12:18],
        previous_action=sim.raw_action,
        mode=mode,
    )
    fields = {k: torch.tensor(v[None], dtype=torch.float32) for k, v in fields.items()}
    expected = observation_tensor(
        load_robot(RUN / "params/robot.yaml"), load_policy(RUN / "params/policy_meta.yaml"), fields
    )
    obs = sim.observation(command, height)
    np.testing.assert_allclose(obs, expected[0].numpy(), atol=2e-7)
    x = expected
    for i, (w, b) in enumerate(sim.actor.layers):
        x = torch.nn.functional.linear(x, torch.from_numpy(w), torch.from_numpy(b))
        if i < len(sim.actor.layers) - 1:
            x = torch.nn.functional.elu(x)
    np.testing.assert_allclose(sim.actor(obs), x[0].numpy(), atol=2e-5)


def test_space_latches_height_estop_and_every_spawn_clear_state(playground):
    sim, sites, p = playground
    player = JumpPlayer(sim, sites, p["controls"])
    player.set_targets(0.15, -1.0, 0.5)
    player.key(glfw.KEY_SPACE)
    assert sim.jump.active.item() and not player.paused
    player.set_targets(0.3, -1.0, 0.5)
    player.key(glfw.KEY_SPACE)
    assert sim.jump.height.item() == pytest.approx(0.15)
    player.step()
    player.key(glfw.KEY_X)
    for _ in range(5):
        player.step()
        np.testing.assert_array_equal(sim.data.ctrl[sim.ctrl_active], 0)
        np.testing.assert_array_equal(sim.raw_action, 0)
    player.key(glfw.KEY_W)
    player.key(glfw.KEY_SPACE)
    np.testing.assert_array_equal(player.target, 0)
    assert not sim.jump.active.item()
    for index, site in enumerate(sites):
        player.key(glfw.KEY_F1 + index)
        np.testing.assert_allclose(sim.data.qpos[:2], site["spawn_xy_m"])
        np.testing.assert_array_equal(sim.data.qvel, 0)
        np.testing.assert_array_equal(player.command, 0)
        assert not sim.estopped and not sim.jump.active.item()
        assert sim.jump.elapsed.item() == 0 and sim.jump.remaining.item() == 0
        assert np.max(np.abs(sim.act_line.buffer[0])) == 0
    player.key(glfw.KEY_S)
    player.key(glfw.KEY_D)
    assert player.target[0] < 0 and player.target[2] < 0
    player.key(glfw.KEY_R)
    assert not player.failed


def test_snapshot_smoke_jump_and_latched_stop_are_finite(playground):
    sim, sites, p = playground
    player = JumpPlayer(sim, sites, p["controls"])
    # Let the folded ground birth settle before requesting the jump.
    for _ in range(sim.cfg.policy_hz * 2):
        player.step()
    player.key(glfw.KEY_SPACE)
    for _ in range(sim.cfg.policy_hz * 4):
        player.step()
    assert np.isfinite(sim.data.qpos).all() and np.isfinite(sim.data.qvel).all()
    assert sim.jump.took_off.item()
    assert sim.peak_rise_m > 0.02
    player.stop()
    for _ in range(10):
        player.step()
    np.testing.assert_array_equal(sim.data.ctrl[sim.ctrl_active], 0)


def test_tunnel_roof_cannot_be_reported_as_success(playground):
    sim, sites, p = playground
    player = JumpPlayer(sim, sites, p["controls"])
    player.teleport(3)  # 20 cm tunnel.
    player.key(glfw.KEY_SPACE)
    sim.jump.took_off[:] = True
    sim.data.qpos[0] = 0.175
    sim.data.qpos[2] += sites[3]["height_m"]
    mujoco.mj_forward(sim.model, sim.data)
    player.step()
    assert sim.traversal.invalid.item()
    assert not sim.jump.landing_paid.item()
    assert sim.jump_result.startswith("failed")


@pytest.mark.parametrize("values", [(float("nan"), 0.0, 0.0), (0.2, 3.01, 0.0), (0.2, 0.0, float("inf"))])
def test_invalid_operator_targets_fail_at_input_boundary(playground, values):
    sim, sites, p = playground
    player = JumpPlayer(sim, sites, p["controls"])
    player.set_targets(0.2, 3.0, 0.0)
    assert player.target[0] == 3.0
    with pytest.raises(ValueError):
        player.set_targets(*values)
