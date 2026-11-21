"""Adapter between the Isaac articulation and the calibrated SHU P1 task kernels."""

from math import pi

import torch
from isaaclab.utils.math import euler_xyz_from_quat, quat_apply_inverse

from shu_train.wheelleg.shu_air_clearance import AirBirthClearance, retry_air_births
from shu_train.wheelleg.shu_commands import ShuCommands
from shu_train.wheelleg.shu_curriculum import AirHeightCurriculum, FlatCommandCurriculum
from shu_train.wheelleg.shu_landing import ShuLanding
from shu_train.wheelleg.shu_logging import ShuLandingLog, ShuRewardLog
from shu_train.wheelleg.shu_map import ShuFreeMap
from shu_train.wheelleg.shu_rewards import AIR, DRIVE, RELEASE, RISE, air_wheel_height_reward, shu_reward_terms
from shu_train.wheelleg.shu_spawn import AIR as AIR_BIRTH
from shu_train.wheelleg.shu_spawn import (
    ORDINARY,
    RECOVERY,
    CalibratedResetModel,
    SpawnConfig,
    SpawnJointMap,
    sample_spawn,
    sample_spawn_kinds,
)
from shu_train.wheelleg.shu_terrain import STAIR_PROFILES, mixed_columns

PLATFORM_SPAWN_JITTER_M = 1.0


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
        self.flat = self.drop = None
        self.flat_replay = torch.zeros(n, dtype=torch.bool, device=dev)
        self.free_map = None
        self.proof = proof
        self.log = ShuLandingLog()
        self.reward_log = ShuRewardLog()
        if t.task == "p1-flat":
            self.flat = FlatCommandCurriculum(t.stage["initial_fraction"], t.stage["min_segments"], dev)
            self.commands = ShuCommands(cp, n, dev, flat=self.flat)
            self.error_floor = torch.tensor(t.stage["error_floor"], device=dev)
            self.relative_error = torch.tensor(t.stage["relative_error"], device=dev)
        elif t.task == "p1-landing":
            self.commands = ShuCommands(cp, n, dev, landing_metadata=proof)
            self.drop = AirHeightCurriculum(t.stage["height_edges_m"], dev)
            self.air_debug = tuple(torch.zeros(n, device=dev) for _ in range(5))
        else:
            terrain = t.stage["terrain"]
            self.commands = ShuCommands.for_mixed(cp, n, dev, route=terrain["route"])
            route = terrain["route"]
            columns = mixed_columns(terrain)
            self.flat_columns = torch.tensor([name == "flat" for name, _, _ in columns], device=dev)
            self.slope_columns = torch.tensor(
                [name in ("slope", "slope_inverted") for name, _, _ in columns], device=dev
            )
            up, down = route["up_height_range_m"], route["down_height_range_m"]
            self.down_height_bounds = env.raw_action.new_tensor(down)
            self.oblique_birth = torch.zeros(n, dtype=torch.bool, device=dev)
            self.straight_spawn_probability = route["straight_spawn_probability"]
            self.max_spawn_yaw_offset_rad = route["max_spawn_yaw_offset_rad"]
            if not 0 <= self.straight_spawn_probability <= 1:
                raise ValueError("terrain.route.straight_spawn_probability must be in [0, 1]")
            if not 0 <= self.max_spawn_yaw_offset_rad <= pi:
                raise ValueError("terrain.route.max_spawn_yaw_offset_rad must be in [0, pi]")
            self.pyramid_columns = torch.tensor([pyramid for _, _, pyramid in columns], device=dev)
            if any(pyramid for _, _, pyramid in columns):
                clearance_m = route["clearance_m"]
                for name in STAIR_PROFILES:
                    half_width_m = terrain["profiles"][name]["geometry"]["platform_width_m"] / 2
                    if half_width_m - clearance_m < PLATFORM_SPAWN_JITTER_M:
                        raise ValueError(f"{name}: center XY jitter does not fit the platform after route clearance")
            # Center-out motion flips the direction implied by the outside-in pyramid names.
            # Only legacy straight ascent holds height; every pyramid keeps its resampling clock.
            self.hold_height_columns = torch.tensor(
                [not pyramid and name.endswith("_up") for name, _, pyramid in columns], device=dev
            )
            self.birth_height_bounds = env.raw_action.new_tensor(
                [
                    (up if name == "pyramid_down" else down)
                    if pyramid
                    else up
                    if name.endswith("_up")
                    else down
                    if name.endswith("_down")
                    else cp["height_range_m"]
                    for name, _, pyramid in columns
                ]
            )
            self.free_map = ShuFreeMap(env.cfg.terrain.terrain_generator, terrain.get("free_map") or {}, dev)
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
        self._air_clearance = None
        if self.drop is not None:
            self._air_clearance = AirBirthClearance(
                t.shared["shu_air_collision"],
                base=t.asset["base_body_name"],
                colliders=t.asset["collision_body_names"],
                body_names=env.robot.body_names,
                joint_names=env.robot.joint_names,
                like=env.raw_action,
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
        spawn_rows = slice(None)
        spawn_stage = self.stage
        if mix is None:
            self.commands.reset(ids)
        else:
            columns = env.terrain.terrain_types[ids]
            replay = self.flat_columns[columns]
            self.flat_replay[ids] = replay
            spawn_rows, spawn_stage = replay, "p1-flat"
            # Non-replay mixed starts have no seeded root or joint velocity.
            root[:, 7:13] = 0
            qd.zero_()
            traverse = mix.traverse[ids] & ~replay
            reverse = mix.reverse_descent[ids]
            bounds = torch.where(reverse[:, None], self.down_height_bounds, self.birth_height_bounds[columns])
            self.commands.reset(
                ids,
                route=traverse,
                reverse_descent=reverse,
                upstairs=self.hold_height_columns[columns] & ~reverse,
                birth_height_bounds=bounds,
            )
            # Write the route incidence angle into the actual upright root pose (wxyz).
            reverse_route = reverse[traverse]
            straight, offset = torch.rand((2, len(reverse_route)), device=root.device, dtype=root.dtype)
            offset = (2 * offset - 1) * self.max_spawn_yaw_offset_rad
            offset.masked_fill_(straight < self.straight_spawn_probability, 0.0)
            self.oblique_birth[ids] = False
            self.oblique_birth[ids[traverse]] = offset != 0
            half_yaw = (reverse_route.to(root.dtype) * pi + offset) / 2
            zeros = torch.zeros_like(half_yaw)
            root[traverse, 3:7] = torch.stack((half_yaw.cos(), zeros, zeros, half_yaw.sin()), dim=-1)
            # Anchor XY to the deck center, independent of the asset's default XY offset.
            # Root Z already includes the signed deck elevation from env_origins.
            center_birth = (traverse & self.pyramid_columns[columns]) | self.slope_columns[columns]
            center_xy = env.terrain.env_origins[ids[center_birth], :2]
            jitter = torch.rand_like(center_xy)
            root[center_birth, :2] = center_xy + (2 * jitter - 1) * PLATFORM_SPAWN_JITTER_M
        preset = torch.zeros(len(ids), dtype=torch.bool, device=env.device)
        air = torch.zeros_like(preset)
        spawn_ids = ids[spawn_rows]
        if spawn_ids.numel():
            probability = None
            if self.stage == "p1-flat":
                probability = env.training.stage["recovery_probability"]
            elif self.stage == "p1-stairs":
                probability = env.training.flat_recovery_probability
            kinds = sample_spawn_kinds(spawn_stage, len(spawn_ids), env.device, flat_recovery_probability=probability)
            if spawn_stage == "p1-flat" and env.cfg.evaluation:
                kinds.fill_(ORDINARY)  # no preset cohort in flat eval; still solve the whole articulation
            spawn_air = kinds == AIR_BIRTH
            preset[spawn_rows], air[spawn_rows] = kinds == RECOVERY, spawn_air
            offsets = root.new_zeros(len(spawn_ids))
            self.band[spawn_ids] = -1
            if self.drop is not None:
                if env.cfg.evaluation:
                    edges = self.drop.edges
                    offsets[spawn_air] = edges[0] + (edges[-1] - edges[0]) * torch.rand_like(offsets[spawn_air])
                    self.band[spawn_ids[spawn_air]] = torch.bucketize(offsets[spawn_air], edges[1:-1])
                else:
                    offsets[spawn_air], self.band[spawn_ids[spawn_air]] = self.drop.sample(int(spawn_air.sum()))
            spawn = sample_spawn(kinds, offsets, self.spawn_cfg)
            # Do not overwrite a subset of the default q/qd: a different leg pose also changes
            # pin orientation, slider extension and their velocities. Resolve all DOFs atomically.
            limits = env.robot.data.joint_pos_limits[spawn_ids]
            asset_q, asset_qd = self.reset_model.resolve(spawn, self.spawn_joints, limits)
            if self.drop is not None:
                retry_air_births(
                    spawn,
                    asset_q,
                    asset_qd,
                    rows=spawn_air.nonzero().flatten(),
                    band=self.band[spawn_ids],
                    edges_m=self.drop.edges,
                    spawn=self.spawn_cfg,
                    mapping=self.spawn_joints,
                    model=self.reset_model,
                    limits=limits,
                    clearance=self._air_clearance,
                )
            root[spawn_rows] = spawn.root_state
            root[spawn_rows, :3] += env.terrain.env_origins[spawn_ids]
            q[spawn_rows], qd[spawn_rows] = asset_q, asset_qd
            env.spawn_check_mask[spawn_ids] = False
            if spawn_stage == "p1-flat" and env.commands_fixed and env.fixed_command is not None:
                # Fixed evaluation commands, including height, are already in force at reset.
                self.commands.value[spawn_ids], self.commands.height[spawn_ids] = env.fixed_command
        self.event.reset(ids, air, preset, env._sim_step_counter)
        if self.stage == "p1-landing":
            angle_diff, birth_vx, first_cmd, rim_sq_sum, rim_ticks = self.air_debug
            # Read the accepted reset pose, including retries. The two active
            # coordinates in five_bar_joint_angles() bracket each virtual leg angle.
            axes = self.spawn_joints
            angle_q = q[:, list(axes.leg_ids[:4])]
            angle_q = (angle_q - q.new_tensor(axes.canonical_zero_in_asset_rad[:4])) * q.new_tensor(
                axes.canonical_to_asset_sign[:4]
            )
            angle_diff[ids] = (angle_q[:, 0::2] - angle_q[:, 1::2]).sum(-1).abs() / 2
            _, _, yaw = euler_xyz_from_quat(root[:, 3:7])
            birth_vx[ids] = root[:, 7] * yaw.cos() + root[:, 8] * yaw.sin()
            first_cmd[ids] = torch.nan
            rim_sq_sum[ids] = rim_ticks[ids] = 0
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
            limits = self.free_map.limits_at(e.robot.data.root_pos_w)
            c.free_limits = None if limits is None else limits.masked_fill(self.flat_replay[:, None], torch.inf)
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
            # Only free driving uses the external fixed command. Route gates, signed targets,
            # slew, and the independent route height clock stay authoritative in evaluation.
            if e.mixed_curriculum is not None:
                fixed_ids = torch.arange(len(yaw), device=yaw.device)[fixed_ids][~c.route[fixed_ids]]
            target, height = e.fixed_command
            raw = torch.as_tensor(target, device=e.device, dtype=c.value.dtype)
            cap = ev.air_birth[fixed_ids] & (age[fixed_ids] < 300)
            cmd = raw.expand(len(cap), 3).clone()
            cmd[:, 0] = torch.where(cap, raw[0].clamp(-2.5, 2.5), raw[0])
            cmd[:, 2] = torch.where(cap, raw[2].clamp(-torch.pi / 2, torch.pi / 2), raw[2])
            cmd[:, 1] = 0  # reserved command ABI, including fixed evaluation commands
            cmd.masked_fill_(recovering[fixed_ids, None], 0)
            c.clamp_free_motion(cmd, fixed_ids)
            c.value[fixed_ids] = cmd
            c.height[fixed_ids] = height
            c.height_rate[fixed_ids] = 0.0
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
        terminated = ev.physical_failure | ev.rise_timeout | ev.numerical_failure | ev.invalid_birth
        if not e.commands_fixed or e.mixed_curriculum is not None:
            yaw = s["yaw"]
            vw = s["velocity_w"]
            forward = vw[:, 0] * yaw.cos() + vw[:, 1] * yaw.sin()

            def criterion(kind, error, magnitude):
                return (error <= self.error_floor + self.relative_error * magnitude).all(-1)

            # The independent flat driver does not consume motion/height clocks with a fixed
            # command. Freeze those same clocks only for replay rows; the atlas still advances.
            fixed_replay = self.flat_replay.nonzero().flatten() if e.commands_fixed else None
            if fixed_replay is not None:
                clocks = (c.remaining, c.height_remaining, c.steps)
                before = tuple(clock[fixed_replay] for clock in clocks)
            c.finish(
                torch.stack((forward, s["angular_velocity"][:, 2], s["base_height"]), -1),
                ev.physical_failure,
                (timeout | terminated) & ~ev.physical_failure,
                criterion if self.flat is not None else None,
                invalid=ev.numerical_failure,
            )
            if fixed_replay is not None:
                for clock, previous in zip(clocks, before, strict=True):
                    clock[fixed_replay] = previous
        return terminated

    def rewards(self, s):
        e, ev, c = self.env, self.event, self.commands
        root_pos_w = e.robot.data.root_pos_w
        rel = s["wheel_position_w"] - root_pos_w[:, None]
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
        self.params["height_fraction"] = c.reward_height_fraction
        terrain_masks = None
        if self.free_map is not None:
            nonflat, pyramid = self.free_map.reward_masks_at(root_pos_w)
            terrain_masks = nonflat & ~self.flat_replay, pyramid & ~self.flat_replay
        diagnostics = None if e.cfg.evaluation else {}
        terms = shu_reward_terms(
            s, ev.reward_phase, self.params, e.step_dt, terrain_masks=terrain_masks, diagnostics=diagnostics
        )
        if diagnostics is not None:
            self.reward_log.add(diagnostics, ~(ev.numerical_failure | ev.invalid_birth | ev.unknown_guide))
        if self.stage == "p1-stairs":
            # Before autoreset, keep the scan-derived reference and error independently of the reward gates.
            e.extras["p1_mixed"] = {
                "ground_z_w_m": s["ground"].detach().clone(),
                "height_error_m": s["height_error"].detach().clone(),
            }
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
        if not e.cfg.evaluation:
            if self.stage == "p1-landing":
                _, _, first_cmd, rim_sq_sum, rim_ticks = self.air_debug
                first = ev.air_birth & (e._sim_step_counter - ev.born == e.training.robot.decimation)
                first_cmd.copy_(torch.where(first, s["vx_cmd"], first_cmd))
                vx, vy = s["velocity_w"][:, :2].unbind(-1)
                forward = vx * yaw.cos() + vy * yaw.sin()
                rim_sq = (s["wheel_rim_speed"] - forward[:, None]).square().mean(-1)
                use = (ev.reward_phase == AIR) & ~ev.numerical_failure & ~ev.invalid_birth & rim_sq.isfinite()
                rim_sq_sum.add_(torch.where(use, rim_sq, 0))
                rim_ticks.add_(use)
                self.log.add(ev, self.band, self.air_debug)
            else:
                self.log.add(ev, self.band)
        if self.stage == "p1-landing":
            # Raw observations for the collector must survive the vectorized autoreset on this same step.
            e.extras["landing"] = {k: v.detach().clone() for k, v in ev.metrics().items()}
            e.extras["landing"].update(
                air_birth=ev.air_birth.clone(), preset_birth=ev.preset_birth.clone(), birth_band=self.band.clone()
            )
        return terms
