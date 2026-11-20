"""Adapter between the Isaac articulation and the calibrated SHU P1 task kernels."""

import torch
from isaaclab.utils.math import quat_apply_inverse

from wheelleg.shu_commands import ShuCommands
from wheelleg.shu_curriculum import AirHeightCurriculum, FlatCommandCurriculum
from wheelleg.shu_landing import ShuLanding
from wheelleg.shu_logging import ShuLandingLog
from wheelleg.shu_map import ShuFreeMap
from wheelleg.shu_rewards import DRIVE, RELEASE, RISE, air_wheel_height_reward, shu_reward_terms
from wheelleg.shu_spawn import AIR as AIR_BIRTH
from wheelleg.shu_spawn import (
    ORDINARY,
    RECOVERY,
    CalibratedResetModel,
    SpawnConfig,
    SpawnJointMap,
    sample_spawn,
    sample_spawn_kinds,
)


def _exact(finder, names):
    ids, resolved = finder(list(names), preserve_order=True)
    if list(resolved) != list(names) or len(set(ids)) != len(ids):
        raise ValueError(f"SHU USD name mapping mismatch: requested {list(names)}, resolved {resolved}")
    return list(ids)


class ShuP1:
    def __init__(self, env, proof):
        self.env = env
        t, n, dev = env.training, env.num_envs, env.device
        self.stage = t.task
        cp = t.settings["commands"]
        self.flat = self.drop = self.spawn_cfg = None
        self.free_map = None
        self.proof = proof
        self.log = ShuLandingLog()
        if t.task == "p1-flat":
            self.flat = FlatCommandCurriculum(t.stage["initial_fraction"], t.stage["min_segments"], dev)
            self.commands = ShuCommands(cp, n, dev, flat=self.flat)
            self.error_floor = torch.tensor(t.stage["error_floor"], device=dev)
            self.relative_error = torch.tensor(t.stage["relative_error"], device=dev)
        elif t.task == "p1-landing":
            self.commands = ShuCommands(cp, n, dev, landing_metadata=proof)
            self.drop = AirHeightCurriculum(t.stage["height_edges_m"], dev)
        else:
            terrain = t.stage["terrain"]
            self.commands = ShuCommands.for_mixed(cp, n, dev, route=terrain["route"])
            self.free_map = ShuFreeMap(env.cfg.terrain.terrain_generator, terrain.get("free_map") or {}, dev)
        if t.task != "p1-stairs":
            self.spawn_cfg = SpawnConfig(
                **dict(t.shared["shu_spawn"]),
                **{k: t.shared[k] for k in ("hip_pivot_positions_b_m", "wheel_radius_m", "spawn_clearance_m")},
            )
            model = t.shared.get("shu_reset_map")
            if not model or any(v is None for v in model.values()):
                raise ValueError("missing calibrated robot.training.shu_reset_map; refusing partial spring/leg reset")
            self.reset_model = CalibratedResetModel(**model)
            names = self.reset_model.auxiliary_joint_names
            self.spawn_joints = SpawnJointMap(
                len(env.robot.joint_names),
                _exact(env.robot.find_joints, t.asset["shu_leg_reset_joint_names"]),
                env.joints,
                env.springs,
                _exact(env.robot.find_joints, names) if names else [],
                self.reset_model.canonical_to_asset_sign,
                self.reset_model.canonical_zero_in_asset_rad,
            )
        gs = _exact(env.contact.find_bodies, t.asset["guide_body_names"])
        links = _exact(env.contact.find_bodies, t.asset["leg_body_names"])
        self.guide_bodies = _exact(env.robot.find_bodies, t.asset["guide_body_names"])
        term = t.shared["termination"]
        self.event = ShuLanding(
            n,
            env.contact_wheels,
            gs,
            links,
            env.contact_bad,
            env.contact_terminal,
            len(env.contact.body_names),
            dict(
                t.shared["shu_contact"],
                termination_force_n=term["contact_force_n"],
                termination_tilt_rad=term["tilt_rad"],
                termination_duration_s=term["duration_s"],
                termination_decay_s=term["decay_s"],
            ),
            dev,
        )
        self.band = torch.full((n,), -1, dtype=torch.long, device=dev)
        self.prev_qd = torch.zeros_like(env.raw_action)
        self.second_action = torch.zeros_like(env.raw_action)
        self.rim = env.raw_action.new_tensor(t.shared["wheel_rim_sign"]) * t.shared["wheel_radius_m"]
        self.hips = env.raw_action.new_tensor(t.shared["hip_pivot_positions_b_m"])
        self.params = dict(
            t.settings["shu_rewards"],
            leg_lower_rad=env.lower[env.legs],
            leg_upper_rad=env.upper[env.legs],
            heading_kp=cp["heading_kp"],
            heading_max_wz=cp["heading_max_wz"],
        )
        self.last_command_tick = -1
        self.reset_rows = torch.ones(n, dtype=torch.bool, device=dev)

    def curriculum_state_dict(self):
        if self.flat is not None:
            return {"flat": self.flat.state_dict(), "flat_transfer": self.commands.transfer_metadata()}
        if self.drop is not None:
            return {"drop": self.drop.state_dict(), "flat_transfer": self.proof}
        return {}

    def load_curriculum_state_dict(self, state):
        if self.flat is not None:
            self.flat.load_state_dict(state["flat"])
        if self.drop is not None:
            self.drop.load_state_dict(state["drop"])

    def reset(self, ids, root, q, qd):
        env = self.env
        mix = env.mixed_curriculum
        self.commands.reset(ids, route=None if mix is None else mix.traverse[ids])
        preset = air = torch.zeros(len(ids), dtype=torch.bool, device=env.device)
        if self.spawn_cfg is not None:
            kinds = sample_spawn_kinds(
                self.stage,
                len(ids),
                env.device,
                flat_recovery_probability=env.training.stage["recovery_probability"] if self.flat is not None else None,
            )
            if self.stage == "p1-flat" and env.cfg.evaluation:
                kinds.fill_(ORDINARY)  # no preset cohort in flat eval; still solve the whole articulation
            preset, air = kinds == RECOVERY, kinds == AIR_BIRTH
            offsets = root.new_zeros(len(ids))
            self.band[ids] = -1
            if self.drop is not None:
                if env.cfg.evaluation:
                    edges = self.drop.edges
                    offsets[air] = edges[0] + (edges[-1] - edges[0]) * torch.rand_like(offsets[air])
                    self.band[ids[air]] = torch.bucketize(offsets[air], edges[1:-1])
                else:
                    offsets[air], self.band[ids[air]] = self.drop.sample(int(air.sum()))
            spawn = sample_spawn(kinds, offsets, self.spawn_cfg)
            root.copy_(spawn.root_state)
            root[:, :3] += env.terrain.env_origins[ids]
            # Do not overwrite a subset of the default q/qd: a different leg pose also changes
            # pin orientation, slider extension and their velocities. Resolve all DOFs atomically.
            asset_q, asset_qd = self.reset_model.resolve(spawn, self.spawn_joints, env.robot.data.joint_pos_limits[ids])
            q.copy_(asset_q)
            qd.copy_(asset_qd)
            env.spawn_check_mask[ids] = False
        self.event.reset(ids, air, preset, env._sim_step_counter)
        self.second_action[ids] = 0
        self.prev_qd[ids] = qd[:, env.joints]
        self.reset_rows[ids] = True

    def observe_commands(self, yaw):
        e, c, ev = self.env, self.commands, self.event
        tick = e._sim_step_counter
        phase = ev.phase
        recovering = (phase == RELEASE) | (phase == RISE)
        age = (tick - ev.born) // e.training.robot.decimation
        args = (yaw, phase == DRIVE, recovering, ev.air_birth, age)
        route = None if e.mixed_curriculum is None else e.mixed_curriculum.route_open
        fixed_ids = slice(None)
        if self.free_map is not None:
            c.free_limits = self.free_map.limits_at(e.robot.data.root_pos_w)
        if tick != self.last_command_tick:
            c.prepare(*args, route_open=route)
            self.last_command_tick = tick
        else:
            ids = self.reset_rows.nonzero().flatten()
            if not len(ids):
                return
            c.prepare_reset_rows(ids, *args, route_open=route)
            if self.free_map is not None:
                fixed_ids = ids
        self.reset_rows.zero_()
        if e.commands_fixed and e.fixed_command is not None:
            target, height = e.fixed_command
            raw = torch.as_tensor(target, device=e.device, dtype=c.value.dtype)
            cap = ev.air_birth[fixed_ids] & (age[fixed_ids] < 300)
            cmd = raw.expand(len(cap), 3).clone()
            cmd[:, 0] = torch.where(cap, raw[0].clamp(-2.5, 2.5), raw[0])
            cmd[:, 2] = torch.where(cap, raw[2].clamp(-torch.pi / 2, torch.pi / 2), raw[2])
            cmd.masked_fill_(recovering[fixed_ids, None], 0)
            c.clamp_free_motion(cmd, fixed_ids)
            c.value[fixed_ids] = cmd
            c.height[fixed_ids] = height
            c.height_rate[fixed_ids] = 0
            c.vx_active[fixed_ids] = cmd[:, 0] != 0
            c.wz_active[fixed_ids] = cmd[:, 2] != 0
            c.heading_active[fixed_ids] = False

    def sample(self, tick):
        e, ev = self.env, self.event
        d = e.robot.data
        rel = d.body_pos_w[:, e.wheels] - d.root_pos_w[:, None]
        wb = quat_apply_inverse(d.root_quat_w[:, None].expand(-1, 2, -1).reshape(-1, 4), rel.reshape(-1, 3)).view(
            -1, 2, 3
        )
        leg = wb - self.hips
        spring = e.training.shared["spring"]
        coords = d.joint_pos[:, e.springs]
        compression = (
            (coords - coords.new_tensor(spring["reference_q_m"])) * coords.new_tensor(spring["direction"])
        ).clamp_min(0)
        ev.sample(
            tick,
            e.contact.data.net_forces_w,
            d.body_lin_vel_w[:, self.guide_bodies, 2],
            leg[:, :, (0, 2)].norm(dim=-1),
            torch.atan2(-leg[:, :, 0], -leg[:, :, 2]),
            spring_compression_m=compression,
        )

    def update(self, s, timeout):
        e, ev, c = self.env, self.event, self.commands
        s["position_xy_w"] = e.robot.data.root_pos_w[:, :2]
        ev.update(e._sim_step_counter, s, torch.zeros_like(timeout), timeout, e.numerical_bad | e.bad_action)
        e.airborne.copy_(~ev.wheel_contact.any(dim=1))
        s["wheel_contact"] = ev.wheel_contact
        if self.drop is not None and not e.cfg.evaluation:
            self.drop.record(self.band, ev.succeeded, ev.resolved)
        terminated = ev.physical_failure | ev.rise_timeout | ev.numerical_failure | ev.invalid_birth | ev.unknown_guide
        if not e.commands_fixed or e.mixed_curriculum is not None:
            yaw = s["yaw"]
            vw = s["velocity_w"]
            forward = vw[:, 0] * yaw.cos() + vw[:, 1] * yaw.sin()

            def criterion(kind, error, magnitude):
                return (error <= self.error_floor + self.relative_error * magnitude).all(-1)

            c.finish(
                torch.stack((forward, s["angular_velocity"][:, 2], s["base_height"]), -1),
                ev.physical_failure,
                (timeout | terminated) & ~ev.physical_failure,
                criterion if self.flat is not None else None,
            )
            c.handoff(ev.handoff, s["yaw"])
        return terminated

    def rewards(self, s):
        e, ev, c = self.env, self.event, self.commands
        rel = s["wheel_position_w"] - e.robot.data.root_pos_w[:, None]
        yaw = s["yaw"]
        q = e.robot.data.joint_pos[:, e.joints]
        qd = e.robot.data.joint_vel[:, e.joints]
        s.update(
            heading_ref=c.reference_yaw,
            vx_cmd=c.value[:, 0],
            wz_cmd=c.value[:, 2],
            heading_wz_cmd=c.value[:, 2],
            vx_active=c.vx_active,
            wz_active=c.wz_active,
            heading_active=c.heading_active,
            height_target_rate=c.height_rate,
            wheel_x_b=s["wheel_position_b"][:, :, 0],
            wheel_heading_x=rel[:, :, 0] * yaw.cos()[:, None] + rel[:, :, 1] * yaw.sin()[:, None],
            wheel_rim_speed=s["wheel_velocity"] * self.rim,
            fork_threshold_enabled=(
                ~(ev.air_birth | ev.preset_birth) if self.stage == "p1-landing" else torch.ones_like(ev.air_birth)
            ),
            leg_or_guide_contact=ev.leg_or_guide_contact,
            other_undesired_contact=ev.other_undesired_contact,
            joint_pos=q,
            joint_vel=qd,
            previous_joint_vel=self.prev_qd,
            previous_previous_action=self.second_action,
        )
        self.params["height_fraction"] = c.fraction
        terms = shu_reward_terms(s, ev.reward_phase, self.params, e.step_dt)
        if self.stage == "p1-landing":
            cfg = e.training
            terms["air_wheel_height"] = air_wheel_height_reward(
                rel[:, :, 2],
                cfg.shared["wheel_radius_m"],
                c.height[:, 0],
                cfg.stage["air_wheel_height_bias_m"],
                cfg.stage["air_wheel_height_max_m"],
                ev.reward_phase,
                e.step_dt,
            )
        terms.update(ev.event_terms)
        terms["termination"] = -4.0 * ev.physical_failure.float()
        self.prev_qd.copy_(qd)
        if self.stage == "p1-landing" and not e.cfg.evaluation:
            self.log.add(ev, self.band)
        if self.stage == "p1-landing":
            # Raw observations for the collector must survive the vectorized autoreset on this same step.
            e.extras["landing"] = {k: v.detach().clone() for k, v in ev.metrics().items()}
            e.extras["landing"].update(
                air_birth=ev.air_birth.clone(), preset_birth=ev.preset_birth.clone(), birth_band=self.band.clone()
            )
        return terms
