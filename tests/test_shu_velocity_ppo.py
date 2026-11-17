import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
import yaml

from wheelleg.config import load_policy
from wheelleg.history import HISTORY_DIM

torch = pytest.importorskip("torch")

from wheelleg.actor import DeployedPolicy, policy_contract  # noqa: E402
from wheelleg.checkpoints import initialize_actor, load_actor, load_landing_transfer  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
P1 = ROOT / "config/policies/p1/policy_meta.yaml"
ROBOT = ROOT / "config/robot.yaml"
COMMANDS = {"height_range_m": [0.2, 0.4]}


class Env:
    num_envs = 4
    num_actions = 6

    def __init__(self, policy, task):
        self.unwrapped = self
        self.training = SimpleNamespace(
            task=task, policy=policy, shared={"observation_clip": {}, "critic_torque_scale": 0.05}
        )
        self.fractions = [1.0] * 6
        self.shu = SimpleNamespace(
            curriculum_state_dict=lambda: {
                "flat": {"fraction": torch.tensor(self.fractions)},
                "flat_transfer": dict(
                    stage="p1-flat",
                    all_full=all(v == 1 for v in self.fractions),
                    fractions=self.fractions,
                    commands=COMMANDS,
                ),
            },
            load_curriculum_state_dict=lambda state: setattr(self, "restored", state),
        )
        self.jump_curriculum = None
        self.mixed_curriculum = None
        from tensordict import TensorDict

        self.obs = TensorDict(
            {
                "policy": torch.randn(4, 35),
                "history": torch.randn(4, 175),
                "estimator_target": torch.full((4, 3), 5.0),
                "critic": torch.randn(4, 8),
            },
            batch_size=[4],
        )
        self.obs["history"][:, -35:] = self.obs["policy"]

    def get_observations(self):
        return self.obs


def make_runner(policy, task):
    pytest.importorskip("rsl_rl.runners")
    from isaac.wheelleg_tasks.runner import WheelLegRunner

    runner = WheelLegRunner(
        Env(policy, task),
        {
            "num_steps_per_env": 2,
            "save_interval": 1,
            "obs_groups": {"policy": ["policy"], "critic": ["critic"]},
            "policy": {
                "class_name": "ActorCritic",
                "actor_hidden_dims": [128, 64, 32],
                "critic_hidden_dims": [8],
                "actor_obs_normalization": False,
            },
            "algorithm": {"class_name": "PPO", "num_mini_batches": 2, "num_learning_epochs": 2},
        },
    )
    runner.logger_type = "tensorboard"
    return runner


def ppo_update(runner):
    alg, obs = runner.alg, runner.env.obs
    with torch.inference_mode():
        for step in range(2):
            saved_history = obs["history"].clone()
            saved_target = obs["estimator_target"].clone()
            alg.act(obs)
            obs["history"].add_(0.25)  # simulate mutable env tensors after act and before storage copy
            obs["estimator_target"].add_(0.25)
            alg.process_env_step(obs, torch.arange(4, dtype=torch.float), torch.zeros(4, dtype=torch.long), {})
            torch.testing.assert_close(alg.storage.observations["history"][step], saved_history)
            torch.testing.assert_close(alg.storage.observations["estimator_target"][step], saved_target, equal_nan=True)
        alg.compute_returns(obs)
    return alg.update()


def test_ppo_updates_and_checkpoint_resume(tmp_path, monkeypatch):
    policy = load_policy(P1)
    runner = make_runner(policy, "p1-flat")
    alg, obs = runner.alg, runner.env.obs
    net = alg.policy
    expected = net.act_inference(obs)
    obs["estimator_target"].mul_(2)
    torch.testing.assert_close(net.act_inference(obs), expected)
    expected.square().mean().backward()
    assert all(p.grad is None for p in net.encoder.parameters())
    encoder_param = next(net.encoder.parameters())
    assert all(p is not encoder_param for group in alg.optimizer.param_groups for p in group["params"])
    before_encoder = encoder_param.detach().clone()
    before_actor = next(net.actor.parameters()).detach().clone()
    before_critic = next(net.critic.parameters()).detach().clone()
    ppo_step = alg.optimizer.step

    def step():
        torch.testing.assert_close(encoder_param, before_encoder, atol=0, rtol=0)
        ppo_step()

    monkeypatch.setattr(alg.optimizer, "step", step)
    obs["estimator_target"][0, 0] = float("nan")
    assert np.isfinite(ppo_update(runner)["encoder_velocity_mse"])
    assert not torch.equal(encoder_param, before_encoder)
    assert not torch.equal(next(net.actor.parameters()), before_actor)
    assert not torch.equal(next(net.critic.parameters()), before_critic)
    runner.current_learning_iteration = 17
    path = tmp_path / "model_17.pt"
    runner.save(str(path))
    deployed = load_actor(path, policy)
    torch.testing.assert_close(deployed(obs["policy"], obs["history"]), net.act_inference(obs))
    resumed = make_runner(policy, "p1-flat")
    resumed.load(str(path))
    assert resumed.current_learning_iteration == 17
    assert resumed.alg.encoder_optimizer.state_dict()["state"]
    assert resumed.alg.optimizer.state_dict()["state"]
    torch.testing.assert_close(resumed.env.restored["flat"]["fraction"], torch.ones(6))
    torch.testing.assert_close(resumed.alg.policy.act_inference(obs), net.act_inference(obs))
    landing = make_runner(policy, "p1-landing")
    with pytest.raises(ValueError, match="--resume requires the same task"):
        landing.load(str(path))


def test_landing_transfer_requires_completed_source_and_only_copies_inference_weights(tmp_path):
    policy = load_policy(P1)
    source = make_runner(policy, "p1-flat")
    destination = make_runner(policy, "p1-landing")
    ppo_update(source)
    source.alg.policy.std.data.fill_(0.5)
    source.current_learning_iteration = 23
    path = tmp_path / "flat.pt"
    dest_policy = destination.alg.policy
    critic_before = next(dest_policy.critic.parameters()).detach().clone()
    source.env.fractions[-1] = 0.9
    source.save(str(path))
    with pytest.raises(ValueError, match="all flat command buckets"):
        load_landing_transfer(path, policy, source_task="p1-flat", commands=COMMANDS)
    source.env.fractions[-1] = 1.0
    source.save(str(path))
    weights_without_curriculum = torch.load(path, weights_only=True)
    del weights_without_curriculum["infos"]["shu_curriculum"]
    no_proof = tmp_path / "flat_without_curriculum.pt"
    torch.save(weights_without_curriculum, no_proof)
    with pytest.raises(ValueError, match="all flat command buckets"):
        load_landing_transfer(no_proof, policy, source_task="p1-flat", commands=COMMANDS)
    with pytest.raises(ValueError, match="requires a p1-landing checkpoint"):
        load_landing_transfer(path, policy, source_task="p1-landing", commands=COMMANDS)
    with pytest.raises(ValueError, match="matching commands"):
        load_landing_transfer(path, policy, source_task="p1-flat", commands={"height_range_m": [0.2, 0.5]})
    transfer = load_landing_transfer(path, policy, source_task="p1-flat", commands=COMMANDS)
    assert transfer["fractions"] == [1.0] * 6
    initialize_actor(destination, path)
    obs = destination.env.obs
    torch.testing.assert_close(dest_policy.act_inference(obs), source.alg.policy.act_inference(obs))
    torch.testing.assert_close(next(dest_policy.critic.parameters()), critic_before, atol=0, rtol=0)
    torch.testing.assert_close(dest_policy.std, torch.ones(6))
    assert not destination.alg.optimizer.state_dict()["state"]
    assert not destination.alg.encoder_optimizer.state_dict()["state"]
    assert destination.current_learning_iteration == 0
    assert not hasattr(destination.env, "restored")
    landing_path = tmp_path / "landing.pt"
    destination.save(str(landing_path))
    assert load_landing_transfer(landing_path, policy, source_task="p1-landing", commands=COMMANDS) == transfer
    with pytest.raises(ValueError, match="expected a p1-landing checkpoint"):
        load_actor(path, policy, source_task="p1-landing")
    torch.testing.assert_close(
        load_actor(landing_path, policy, source_task="p1-landing")(obs["policy"], obs["history"]),
        dest_policy.act_inference(obs),
    )


def test_incompatible_checkpoints_do_not_load(tmp_path):
    policy = load_policy(P1)
    model = DeployedPolicy(policy)
    package = {"model_state_dict": model.state_dict()}
    path = tmp_path / "invalid.pt"
    torch.save(package, path)
    with pytest.raises(ValueError, match="incompatible Actor/velocity encoder"):
        load_actor(path, policy)
    # Even a checkpoint with correct metadata cannot hide an old five-output head.
    package["infos"] = {"observation_contract": {"policy": policy_contract(policy)}}
    package["model_state_dict"]["encoder.4.weight"] = torch.zeros(5, 64)
    torch.save(package, path)
    with pytest.raises(RuntimeError, match="size mismatch for encoder.4.weight"):
        load_actor(path, policy)


def test_export_with_real_shape_and_onnx_parity(tmp_path):
    pytest.importorskip("onnx")
    pytest.importorskip("onnxruntime")
    from tools.export_policy import export_policy

    config = yaml.safe_load(P1.read_text(encoding="utf-8"))
    for key in ("kp", "kd", "torque_limit_nm"):
        config[key] = [1.0] * 6
    robot = yaml.safe_load(ROBOT.read_text(encoding="utf-8"))
    robot["pending_measurements"] = {k: "synthetic test only" for k in robot["pending_measurements"]}
    robot.update(q_default_rad=[0.0] * 6, q_zero_offset_rad=[0.0] * 6, motor_direction=[1] * 6)
    robot["training"].update(joint_lower_rad=[-1.0] * 6, joint_upper_rad=[1.0] * 6)
    policy_path, robot_path = tmp_path / "policy.yaml", tmp_path / "robot.yaml"
    policy_path.write_text(yaml.safe_dump(config), encoding="utf-8")
    robot_path.write_text(yaml.safe_dump(robot), encoding="utf-8")
    policy = load_policy(policy_path)
    model = DeployedPolicy(policy)
    path = tmp_path / "model.pt"
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "infos": {"observation_contract": {"policy": policy_contract(policy)}},
        },
        path,
    )
    (tmp_path / "params").mkdir()
    (tmp_path / "params/run.json").write_text(json.dumps({"git_commit": "test", "task": "p1-flat"}), encoding="utf-8")
    history = np.random.default_rng(5).normal(size=(121, HISTORY_DIM)).astype(np.float32)
    obs = history[:, -35:]
    rollout, output = tmp_path / "rollout.npz", tmp_path / "export"
    np.savez(rollout, observation=obs, obs_history=history[::-1])
    with pytest.raises(ValueError, match="newest frame"):
        export_policy(path, policy_path, robot_path, rollout, output)
    np.savez(rollout, observation=obs, obs_history=history)
    manifest = export_policy(path, policy_path, robot_path, rollout, output)
    assert manifest["onnx_max_absolute_error"] < 1e-5
    assert manifest["inference_contract"]["inputs"] == {"obs": [1, 35], "obs_history": [1, 175]}
    with np.load(output / "golden.npz") as vectors:
        assert vectors["actions"].shape == (100, 6)
        np.testing.assert_array_equal(vectors["obs_history"][:, -35:], vectors["observation"])
    assert "kGoldenObsHistory[100][175]" in (output / "golden.h").read_text(encoding="utf-8")
    assert "#define WL_OBS_HISTORY_DIM 175u" in (output / "gen_config.h").read_text(encoding="utf-8")
