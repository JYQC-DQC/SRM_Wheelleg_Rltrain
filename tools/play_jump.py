"""Manual P3 MuJoCo replay: Space jumps; F1..F12 teleport to twelve test sites."""

import argparse
import json
import math
import re
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import glfw
import mujoco
import numpy as np
import torch
import yaml

from wheelleg.jump import JumpEvent, TunnelTraversal, jump_height_error, landing_rates_ok, tunnel_landing

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "sim2sim"))
from build_model import build  # noqa: E402

from sim2sim import NumpyActor, RunConfig, Spawn, WheelLegSim  # noqa: E402


def build_arena(flat: Path, output: Path, course: dict, friction: float) -> list[dict]:
    tree = ET.parse(flat)
    world = tree.getroot().find("worldbody")
    world.find("geom[@name='ground']").set("group", "3")
    sites = [dict(name="Flat", kind="flat", height_m=0.0, spawn_xy_m=course["flat_spawn_xy_m"])]

    def box(name: str, position: tuple, size: tuple, color: str) -> None:
        ET.SubElement(
            world,
            "geom",
            name=name,
            type="box",
            group="3",
            pos=" ".join(map(str, position)),
            size=" ".join(map(str, size)),
            rgba=color,
            friction=f"{friction} 0.01 0.001",
        )

    spacing, approach = course["lane_spacing_m"], course["approach_distance_m"]
    for kind, x in (("tunnel", 0.0), ("step", course["column_spacing_m"])):
        for index, height in enumerate(course["heights_m"]):
            y = (index - (len(course["heights_m"]) - 1) / 2) * spacing
            name = f"{kind}_{round(height * 100)}cm"
            if kind == "tunnel":
                length, width, wall = (
                    course[k] for k in ("tunnel_length_m", "tunnel_outer_width_m", "tunnel_wall_thickness_m")
                )
                if height <= wall or width <= 2 * wall:
                    raise ValueError("Tunnel outer height/width must exceed its wall thickness")
                # Outer top is height; the cavity reaches the ground and is open at both ends.
                box(
                    name + "_roof",
                    (x + length / 2, y, height - wall / 2),
                    (length / 2, width / 2, wall / 2),
                    "0.90 0.55 0.12 1",
                )
                for side in (-1, 1):
                    box(
                        name + f"_wall_{side}",
                        (x + length / 2, y + side * (width - wall) / 2, (height - wall) / 2),
                        (length / 2, wall / 2, (height - wall) / 2),
                        "0.78 0.40 0.10 1",
                    )
            else:
                length, width = course["step_length_m"], course["step_width_m"]
                box(name, (x + length / 2, y, height / 2), (length / 2, width / 2, height / 2), "0.22 0.53 0.75 1")
            sites.append(
                dict(
                    name=name,
                    kind=kind,
                    height_m=height,
                    start_x_m=x,
                    end_x_m=x + length,
                    center_y_m=y,
                    width_m=width,
                    spawn_xy_m=[x - approach, y],
                )
            )
    x, y = course["column_spacing_m"], -3 * spacing
    rise, first, second, width = (
        course[k]
        for k in ("double_step_rise_m", "double_step_first_tread_m", "double_step_second_tread_m", "step_width_m")
    )
    box(
        "double_step_lower",
        (x + (first + second) / 2, y, rise / 2),
        ((first + second) / 2, width / 2, rise / 2),
        "0.22 0.65 0.45 1",
    )
    box(
        "double_step_upper",
        (x + first + second / 2, y, 1.5 * rise),
        (second / 2, width / 2, rise / 2),
        "0.16 0.48 0.32 1",
    )
    sites.append(
        dict(
            name="double_step_20_40cm",
            kind="double_step",
            height_m=rise,
            start_x_m=x,
            end_x_m=x + first + second,
            center_y_m=y,
            width_m=width,
            spawn_xy_m=[x - approach, y],
        )
    )
    for index, site in enumerate(sites):
        sx, sy = site["spawn_xy_m"]
        ET.SubElement(
            world,
            "site",
            name=f"spawn_{index}",
            pos=f"{sx} {sy} 0.005",
            type="cylinder",
            size="0.18 0.004",
            rgba="0.2 0.9 0.5 0.6",
        )
    ET.indent(tree)
    tree.write(output, encoding="utf-8", xml_declaration=True)
    return sites


class JumpSim(WheelLegSim):
    def __init__(self, cfg: RunConfig, actor: NumpyActor, model: Path):
        if cfg.run.get("task") != "p3-jump" or cfg.policy["policy_family"] != "p3":
            raise ValueError("Use a p3-jump checkpoint with its matching saved params/")
        self.stage = cfg.policy["stages"]["jump"]
        self.jump = JumpEvent(self.stage, 1, "cpu")
        self.traversal = TunnelTraversal(1, "cpu")
        self.test_site = None
        self.ids = torch.tensor([0])
        self.estopped = False
        self.jump_result = "ready"
        super().__init__(
            cfg, actor, model, cfg.evaluation["observation_delay_steps"], cfg.evaluation["action_delay_steps"], False
        )
        patterns = cfg.robot["asset"]["termination_contact_body_names"]
        names = [self.model.body(i).name for i in range(self.model.nbody)]
        self.bad_bodies = np.array([i for i, n in enumerate(names) if any(re.fullmatch(p, n) for p in patterns)])
        self.missing_contact_patterns = [p for p in patterns if not any(re.fullmatch(p, n) for n in names)]

    def reset(self, spawn: Spawn) -> None:
        super().reset(spawn)
        self.jump.reset(self.ids)
        self.traversal.reset(self.ids)
        self.jump.remaining.zero_()  # An event starts only on a manual press.
        self.estopped = False
        self.jump_result = "ready"
        self.takeoff_speed_ok = True
        self.peak_rise_m = 0.0

    def observation_mode(self) -> np.ndarray:
        # Commands.mode for p3-jump: first four slots stay zero even on obstacle test sites.
        mode = np.zeros(7)
        active = bool(self.jump.active[0])
        mode[4:] = [
            float(active),
            float(self.jump.height[0]) * self.cfg.scales["height"] * active,
            float(self.jump.phase[0]) * active,
        ]
        return mode

    def press_jump(self, height_m: float) -> bool:
        if self.estopped or bool(self.jump.active[0]):
            return False
        self.jump.reset(self.ids)
        self.traversal.reset(self.ids)
        self.jump.remaining[:] = 1
        self.jump.trigger(
            self.jump.elapsed.new_tensor([self.time]),
            self.jump.elapsed.new_tensor([self.data.qpos[2]]),
            torch.tensor([True]),
            target_height=self.jump.elapsed.new_tensor([height_m]),
            require_trigger_time=False,
        )
        self.takeoff_speed_ok = True
        self.peak_rise_m = 0.0
        self.jump_result = "requested"
        if self.test_site is not None and self.test_site["kind"] == "tunnel":
            self.traversal.approached[:] = bool(self.data.xpos[self.robot_body, 0].max() < self.test_site["start_x_m"])
        return True

    def emergency_stop(self) -> None:
        self.estopped = True
        self.jump.active.zero_()
        self.jump.remaining.zero_()
        self.raw_action[:] = 0
        self.torque[:] = 0
        self.act_line.reset(np.zeros(6))
        self.data.ctrl[self.ctrl_active] = 0
        self.jump_result = "E-STOP: reset required"

    def surface_height(self, xy: np.ndarray, z: float) -> float:
        origin = np.array([xy[0], xy[1], z])
        distance = mujoco.mj_ray(
            self.model,
            self.data,
            origin,
            np.array([0.0, 0.0, -1.0]),
            np.array([0, 0, 0, 1, 0, 0], dtype=np.uint8),
            True,
            -1,
            None,
        )
        return z - distance if distance >= 0 else 0.0

    def _measure(self, command, height, peaks, saturated, inference_s, bad_action) -> dict:
        previous = self.termination_steps
        info = super()._measure(command, height, peaks, saturated, inference_s, bad_action)
        wheel_z = self.data.xpos[self.wheel_ids, 2]
        ground = np.array([self.surface_height(xy, z) for xy, z in zip(self.data.xpos[self.wheel_ids, :2], wheel_z)])
        body_hit = bool((peaks[self.bad_bodies] > self.cfg.termination["contact_force_n"]).any())
        limit = self.cfg.termination["airborne_tilt_rad"] if info["airborne"] else self.cfg.termination["tilt_rad"]
        physical = body_hit or max(abs(info["roll"]), abs(info["pitch"])) > limit
        physical &= self.time >= self.cfg.leg_reset["settle_s"]
        t = self.cfg.termination
        self.termination_steps = previous + 1 if physical else max(previous - t["duration_s"] / t["release_s"], 0)
        safety = self.cfg.shared["numerical_safety"]
        numerical = not (np.isfinite(self.data.qpos).all() and np.isfinite(self.data.qvel).all())
        numerical |= np.abs(self.data.qvel[self.v_adr]).max() > safety["joint_velocity_abs_max"]
        numerical |= np.abs(self.data.qvel[:3]).max() > safety["base_linear_velocity_abs_max"]
        numerical |= np.abs(self.data.qvel[3:6]).max() > safety["base_angular_velocity_abs_max"]
        info.update(
            nonwheel_contact=body_hit,
            numerical=bool(numerical or bad_action),
            terminated=bool(
                numerical or bad_action or self.termination_steps >= round(t["duration_s"] * self.cfg.policy_hz)
            ),
            wheel_clearance=wheel_z - ground - self.cfg.shared["wheel_radius_m"],
            support_z=float(ground.mean()),
        )
        return info

    def step(self, command: np.ndarray, height: float) -> dict:
        if self.estopped:
            peaks = np.zeros(self.model.nbody)
            for _ in range(self.cfg.decimation):
                self.data.ctrl[self.ctrl_active] = 0
                self.data.ctrl[self.ctrl_spring] = self._spring_force()
                mujoco.mj_step(self.model, self.data)
                self.delayed_sensor = self.obs_line.push(self.sensors())
                peaks = np.maximum(peaks, self._contact_forces())
            self.time += 1 / self.cfg.policy_hz
            return self._measure(command, height, peaks, np.zeros(6), 0.0, False)
        info = super().step(command, height)
        took_off = bool(self.jump.took_off[0])
        stable = max(abs(info["roll"]), abs(info["pitch"])) < self.stage["landing_tilt_rad"]
        stable &= not info["terminated"] and not info["nonwheel_contact"]
        if self.jump.clearance_training is not None:
            stable &= bool(
                landing_rates_ok(
                    torch.tensor([info["vz"]]),
                    torch.tensor([[info["angular_xy"]]]),
                    self.jump.clearance_training,
                )[0]
            )
        valid, obstacle_hit = torch.tensor([True]), torch.tensor([False])
        site = self.test_site
        if site is not None and site["kind"] == "tunnel" and bool(self.jump.active[0]):
            wheels = torch.tensor(self.data.xpos[self.wheel_ids][None], dtype=torch.float32)
            bodies = torch.tensor(self.data.xpos[self.robot_body][None], dtype=torch.float32)
            scalar = lambda value: torch.tensor([value], dtype=torch.float32)  # noqa: E731
            p = self.cfg.policy["stages"]["tunnel"]["tunnel"]
            flight = took_off and not bool(self.jump.landed[0]) and not info["wheel_contact"].any()
            self.traversal.update(
                wheels,
                self.cfg.shared["wheel_radius_m"],
                bodies,
                scalar(site["start_x_m"]),
                scalar(site["end_x_m"]),
                scalar(site["height_m"]),
                scalar(site["center_y_m"]),
                site["width_m"] / 2,
                p["landing_margin_m"],
                p["clearance_margin_m"],
                torch.tensor([flight]),
                torch.tensor([True]),
            )
            valid = tunnel_landing(
                wheels,
                self.cfg.shared["wheel_radius_m"],
                bodies,
                scalar(site["end_x_m"]),
                scalar(0.0),
                p["landing_margin_m"],
                p["clearance_margin_m"],
                scalar(site["center_y_m"]),
                site["width_m"] / 2,
                contact=torch.tensor(info["wheel_contact"][None]),
            )
            valid &= self.traversal.cleared & ~self.traversal.invalid
            obstacle_hit = self.traversal.invalid
        self.jump.update(
            1 / self.cfg.policy_hz,
            torch.tensor([self.time]),
            self.jump.elapsed.new_tensor([self.data.qpos[2]]),
            self.jump.elapsed.new_tensor([info["vz"]]),
            torch.tensor(info["wheel_contact"][None]),
            torch.tensor([stable]),
            valid,
            obstacle_hit,
            wheel_clearance=torch.tensor(info["wheel_clearance"][None]),
            failed=torch.tensor([info["terminated"]]),
            require_height=torch.tensor([False]) if "moving_probability" in self.stage else None,
        )
        if bool(self.jump.took_off[0]) and not took_off:
            self.takeoff_speed_ok = command[0] <= 0 or info["heading_vx"] >= (
                self.stage.get("moving_takeoff_min_fraction", 0.0) * command[0]
            )
        self.peak_rise_m = float(self.jump.apex_z[0] - self.jump.start_z[0])
        if bool(self.jump.failure_pulse[0]):
            self.jump_result = "failed: takeoff/settle deadline or physical termination"
        elif bool(self.jump.landing_pulse[0]):
            height_ok = float(jump_height_error(self.jump.scored_height, self.jump.height, self.stage)[0]) <= 1e-6
            self.jump_result = "success" if height_ok and self.takeoff_speed_ok else "landed: height/speed below target"
            if site is not None and site["kind"] == "tunnel" and self.jump_result == "success":
                self.jump_result = "cleared tunnel and landed beyond"
        elif bool(self.jump.active[0]):
            self.jump_result = (
                "settling" if bool(self.jump.first_touch[0]) else "flight" if bool(self.jump.took_off[0]) else "takeoff"
            )
        info["jump_result"] = self.jump_result
        return info


class JumpPlayer:
    def __init__(self, sim: JumpSim, sites: list[dict], settings: dict):
        self.sim, self.sites, self.settings = sim, sites, settings
        self.target = np.zeros(3)
        self.command = np.zeros(3)
        self.height_m = settings["jump_height_range_m"][0]
        self.body_height_m = sim.cfg.evaluation["height_m"]
        self.selected = 0
        self.paused = self.failed = False
        self.slow = 1.0
        self.info = None
        self.teleport(0)

    def set_targets(self, height_m: float, vx_m_s: float, wz_rad_s: float) -> None:
        values = [height_m, vx_m_s, wz_rad_s]
        bounds = [self.settings[k] for k in ("jump_height_range_m", "vx_range_m_s", "wz_range_rad_s")]
        if any(not math.isfinite(v) or not low <= v <= high for v, (low, high) in zip(values, bounds)):
            raise ValueError(f"Targets must be finite and inside {bounds}")
        self.height_m = height_m
        if not self.sim.estopped:
            self.target[:] = [vx_m_s, 0.0, wz_rad_s]

    def teleport(self, index: int) -> None:
        self.selected = index
        self.sim.test_site = self.sites[index]
        self.sim.reset(Spawn(x_m=self.sites[index]["spawn_xy_m"][0], y_m=self.sites[index]["spawn_xy_m"][1]))
        self.target[:] = self.command[:] = 0
        self.failed = self.paused = False
        self.info = None

    def stop(self) -> None:
        self.target[:] = self.command[:] = 0
        self.sim.emergency_stop()

    def key(self, key: int) -> None:
        p = self.settings
        if glfw.KEY_F1 <= key <= glfw.KEY_F12:
            self.teleport(key - glfw.KEY_F1)
        elif key == glfw.KEY_R:
            self.teleport(self.selected)
        elif key == glfw.KEY_X:
            self.stop()
        elif key == glfw.KEY_SPACE and not self.failed and not self.paused:
            self.sim.press_jump(self.height_m)
        elif key == glfw.KEY_P:
            self.paused = not self.paused
        elif key == glfw.KEY_Z:
            self.slow = {1.0: 0.5, 0.5: 0.25, 0.25: 1.0}[self.slow]
        elif key == glfw.KEY_C:
            self.target[:] = 0
        elif not self.sim.estopped:
            if key in (glfw.KEY_W, glfw.KEY_S):
                sign = 1 if key == glfw.KEY_W else -1
                self.target[0] = np.clip(self.target[0] + sign * p["vx_step_m_s"], *p["vx_range_m_s"])
            elif key in (glfw.KEY_A, glfw.KEY_D):
                sign = 1 if key == glfw.KEY_A else -1
                self.target[2] = np.clip(self.target[2] + sign * p["wz_step_rad_s"], *p["wz_range_rad_s"])
            elif key in (glfw.KEY_Q, glfw.KEY_E):
                sign = 1 if key == glfw.KEY_E else -1
                self.height_m = float(
                    np.clip(round(self.height_m + sign * p["jump_height_step_m"], 4), *p["jump_height_range_m"])
                )

    def step(self) -> None:
        if self.paused or (self.failed and not self.sim.estopped):
            return
        c, dt = self.sim.cfg.commands, 1 / self.sim.cfg.policy_hz
        limit = np.array([c["linear_slew_m_s2"], c["linear_slew_m_s2"], c["angular_slew_rad_s2"]]) * dt
        self.command += np.clip(self.target - self.command, -limit, limit)
        self.info = self.sim.step(self.command, self.body_height_m)
        self.failed |= self.info["terminated"]

    def status(self) -> str:
        state = (
            "E-STOP (R resets)"
            if self.sim.estopped
            else "FAILED (R resets)"
            if self.failed
            else "PAUSED"
            if self.paused
            else "RUNNING"
        )
        actual = (
            "" if self.info is None else f"actual vx {self.info['heading_vx']:+.2f}, body wz {self.info['wz']:+.2f}\n"
        )
        return (
            f"{self.sites[self.selected]['name']} | {state} | x{self.slow}\n"
            f"target jump {self.height_m * 100:.1f} cm | vx {self.target[0]:+.2f} m/s "
            f"| wz {self.target[2]:+.2f} rad/s\n"
            f"{actual}jump: {self.sim.jump_result} | "
            + (
                f"peak wheel clearance {self.sim.jump.scored_height[0] * 100:.1f} cm | "
                if self.sim.jump.clearance_training is not None
                else ""
            )
            + f"peak base rise {self.sim.peak_rise_m * 100:.1f} cm"
        )


def control_panel(player: JumpPlayer):
    import tkinter as tk
    from tkinter import ttk

    root = tk.Tk()
    root.title("P3 sim2sim 跳跃控制")
    status, message = tk.StringVar(), tk.StringVar()
    entries = [tk.StringVar(value=v) for v in (player.height_m * 100, 0.0, 0.0)]
    frame = ttk.Frame(root, padding=12)
    frame.pack(fill="both", expand=True)
    for row, (label, value) in enumerate(zip(("跳跃高度 cm", "前后速度 m/s", "自身偏航角速度 rad/s"), entries)):
        ttk.Label(frame, text=label).grid(row=row, column=0, sticky="w")
        ttk.Entry(frame, textvariable=value, width=12).grid(row=row, column=1)

    def apply():
        try:
            player.set_targets(float(entries[0].get()) / 100, float(entries[1].get()), float(entries[2].get()))
            message.set("指令已应用")
        except ValueError as error:
            message.set(str(error))

    ttk.Button(frame, text="应用设定", command=apply).grid(row=3, column=0)
    ttk.Button(frame, text="空格 跳跃", command=lambda: player.key(glfw.KEY_SPACE)).grid(row=3, column=1)
    ttk.Button(frame, text="X 紧急停机（锁存）", command=player.stop).grid(row=4, column=0)
    ttk.Button(frame, text="R 复位到当前出生点", command=lambda: player.teleport(player.selected)).grid(row=4, column=1)
    ttk.Button(frame, text="C 速度归零（保持控制）", command=lambda: player.key(glfw.KEY_C)).grid(row=5, column=0)
    ttk.Button(frame, text="P 暂停 / 继续", command=lambda: player.key(glfw.KEY_P)).grid(row=5, column=1)
    for index, site in enumerate(player.sites):
        ttk.Button(frame, text=f"F{index + 1} {site['name']}", command=lambda i=index: player.teleport(i)).grid(
            row=6 + index // 2, column=index % 2, sticky="ew"
        )
    ttk.Label(frame, textvariable=status, wraplength=580).grid(row=12, column=0, columnspan=2, pady=10)
    ttk.Label(frame, textvariable=message, wraplength=580).grid(row=13, column=0, columnspan=2)
    ttk.Label(
        frame,
        text="W/S 前后速度  A/D 偏航  Q/E 跳高减/增  Space 跳跃\n"
        "X 停机  R 复位  C 停车  P 暂停  Z 慢放  F1-F12 场地\n"
        "输入框内可编辑数值，空格始终只触发跳跃。",
    ).grid(row=14, column=0, columnspan=2)
    mapping = {"space": glfw.KEY_SPACE, "Escape": glfw.KEY_X, "x": glfw.KEY_X, "X": glfw.KEY_X}
    mapping.update({f"F{i + 1}": glfw.KEY_F1 + i for i in range(12)})

    def key(event):
        code = mapping.get(event.keysym)
        if code is None and event.keysym.lower() in "wsadqexrcpz" and len(event.keysym) == 1:
            if isinstance(event.widget, ttk.Entry):
                return None
            code = ord(event.keysym.upper())
        if code is not None:
            player.key(code)
            return "break"
        return None

    root.bind_class("JumpInput", "<KeyPress>", key)
    widgets = [root]
    while widgets:
        widget = widgets.pop()
        widget.bindtags(("JumpInput", *widget.bindtags()))
        widgets.extend(widget.winfo_children())
    root.protocol("WM_DELETE_WINDOW", root.withdraw)
    return root, status


def run_viewer(player: JumpPlayer, panel: bool) -> None:
    # Own GLFW key handling: the passive viewer consumes Space as pause before key_callback.
    if not glfw.init():
        raise RuntimeError("GLFW initialization failed")
    window = glfw.create_window(1280, 800, "P3 jump sim2sim - Space jumps", None, None)
    if not window:
        glfw.terminate()
        raise RuntimeError("Could not create MuJoCo window")
    glfw.make_context_current(window)
    glfw.swap_interval(1)
    sim = player.sim
    scene, camera, option = mujoco.MjvScene(sim.model, maxgeom=10000), mujoco.MjvCamera(), mujoco.MjvOption()
    context = mujoco.MjrContext(sim.model, mujoco.mjtFontScale.mjFONTSCALE_150)
    option.geomgroup[3] = 1
    camera.distance, camera.azimuth, camera.elevation = 3.5, 135, -22
    mouse = [0.0, 0.0]

    def key_callback(win, key, scancode, action, mods):
        if action == glfw.PRESS:
            if key == glfw.KEY_ESCAPE:
                player.stop()
            else:
                player.key(key)

    def cursor(win, x, y):
        dx, dy = x - mouse[0], y - mouse[1]
        mouse[:] = x, y
        left = glfw.get_mouse_button(win, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS
        right = glfw.get_mouse_button(win, glfw.MOUSE_BUTTON_RIGHT) == glfw.PRESS
        if left or right:
            action = mujoco.mjtMouse.mjMOUSE_MOVE_V if right else mujoco.mjtMouse.mjMOUSE_ROTATE_V
            height = max(glfw.get_window_size(win)[1], 1)
            mujoco.mjv_moveCamera(sim.model, action, dx / height, dy / height, scene, camera)

    def scroll(win, xoffset, yoffset):
        mujoco.mjv_moveCamera(sim.model, mujoco.mjtMouse.mjMOUSE_ZOOM, 0, -0.05 * yoffset, scene, camera)

    glfw.set_key_callback(window, key_callback)
    glfw.set_cursor_pos_callback(window, cursor)
    glfw.set_scroll_callback(window, scroll)
    controls = control_panel(player) if panel else None
    last, budget = time.perf_counter(), 0.0
    try:
        while not glfw.window_should_close(window):
            now = time.perf_counter()
            budget = min(budget + (now - last) * player.slow, 0.1)
            last = now
            glfw.poll_events()
            if controls:
                controls[1].set(player.status())
                controls[0].update()
            while budget >= 1 / sim.cfg.policy_hz:
                player.step()
                budget -= 1 / sim.cfg.policy_hz
            camera.lookat[:] = sim.data.qpos[:3]
            mujoco.mjv_updateScene(sim.model, sim.data, option, None, camera, mujoco.mjtCatBit.mjCAT_ALL, scene)
            viewport = mujoco.MjrRect(0, 0, *glfw.get_framebuffer_size(window))
            mujoco.mjr_render(viewport, scene, context)
            mujoco.mjr_overlay(
                mujoco.mjtFont.mjFONT_NORMAL, mujoco.mjtGridPos.mjGRID_TOPLEFT, viewport, player.status(), "", context
            )
            mujoco.mjr_overlay(
                mujoco.mjtFont.mjFONT_NORMAL,
                mujoco.mjtGridPos.mjGRID_BOTTOMLEFT,
                viewport,
                "SPACE jump | W/S vx | A/D yaw | Q/E jump height | X E-stop | R reset\n"
                "C zero speed | P pause | Z slow | F1 flat | F2-F6 tunnels | F7-F11 steps | F12 double",
                "",
                context,
            )
            glfw.swap_buffers(window)
    finally:
        if controls:
            controls[0].destroy()
        context.free()
        glfw.destroy_window(window)
        glfw.terminate()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, default=ROOT / "sim2sim/checkpoints/jump_latest")
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--source", type=Path, default=ROOT / "runs/scut_experience/scene.xml")
    parser.add_argument("--site", type=int, default=1, choices=range(1, 13), help="F-key site number")
    parser.add_argument("--height", type=float, help="jump target in metres")
    parser.add_argument("--vx", type=float, default=0.0)
    parser.add_argument("--wz", type=float, default=0.0, help="body yaw rate command, rad/s")
    parser.add_argument("--no-panel", action="store_true")
    parser.add_argument("--headless", type=float, metavar="SECONDS", help="CPU smoke run without a window")
    args = parser.parse_args()
    torch.set_num_threads(1)
    run = args.run.resolve()
    cfg = RunConfig(run)
    settings = yaml.safe_load((ROOT / "config/policies/p3/policy_meta.yaml").read_text(encoding="utf-8"))["sim2sim"]
    checkpoints = list(run.glob("model_*.pt"))
    if not checkpoints and args.checkpoint is None:
        parser.error(f"No checkpoint found in {run}; supply a saved cloud run with params/")
    checkpoint = args.checkpoint or max(checkpoints, key=lambda p: int(p.stem.split("_")[1]))
    output = ROOT / "runs/jump_viewer"
    output.mkdir(parents=True, exist_ok=True)
    flat, arena = output / "robot_flat.xml", output / "arena.xml"
    build(args.source.resolve(), run / "params/robot.yaml", flat, settings["wheel_friction"])
    sites = build_arena(flat, arena, settings["course"], cfg.shared["ground_material"]["dynamic_friction"])
    actor = NumpyActor(checkpoint, cfg.policy["hidden_dims"])
    sim = JumpSim(cfg, actor, arena)
    player = JumpPlayer(sim, sites, settings["controls"])
    player.teleport(args.site - 1)
    player.set_targets(player.height_m if args.height is None else args.height, args.vx, args.wz)
    launch = dict(
        checkpoint=str(checkpoint),
        source_commit=cfg.run.get("git_commit"),
        model=str(arena),
        sites=sites,
        missing_contact_patterns=sim.missing_contact_patterns,
        control_hz=cfg.control_hz,
        policy_hz=cfg.policy_hz,
    )
    (output / "last_launch.json").write_text(json.dumps(launch, indent=2), encoding="utf-8")
    print(json.dumps(launch, ensure_ascii=False), flush=True)
    print(
        "Backward and nonzero yaw are manual test inputs outside the current flat-P3 training distribution.", flush=True
    )
    if args.headless is not None:
        if not math.isfinite(args.headless) or args.headless <= 0:
            parser.error("--headless must be a finite positive duration")
        player.key(glfw.KEY_SPACE)
        for _ in range(math.ceil(args.headless * cfg.policy_hz)):
            player.step()
        print(player.status(), flush=True)
        print(f"finite={np.isfinite(sim.data.qpos).all() and np.isfinite(sim.data.qvel).all()}", flush=True)
    else:
        run_viewer(player, not args.no_panel)


if __name__ == "__main__":
    main()
