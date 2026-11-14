"""Keyboard/mouse MuJoCo course viewer, reusing the existing sibling sim2sim controller.

python -m tools.play_stairs --run runs/stairs_viewer/checkpoint
"""

import argparse
import json
import math
import re
import sys
import threading
import time
from pathlib import Path

import mujoco
import mujoco.viewer
import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
SIM2SIM = ROOT.parent / "sim2sim"
sys.path.insert(0, str(SIM2SIM))
from build_model import build  # noqa: E402
from play import KP, KP_ADD, KP_DECIMAL, KP_DIVIDE, KP_ENTER, KP_MULTIPLY, KP_SUBTRACT, SLOW_MOTION  # noqa: E402
from sim2sim import OBS_FIELDS, NumpyActor, RunConfig, Spawn, WheelLegSim, euler_xyz  # noqa: E402

from wheelleg.mujoco_terrain import build_course  # noqa: E402
from wheelleg.stairs import advance_height_assist, scan_course  # noqa: E402


class TerrainSim(WheelLegSim):
    def __init__(self, cfg, actor, model_path):
        self.stage = cfg.policy["stages"]["stairs"]
        # Replay existing checkpoints with their saved height contract; never upgrade old snapshots silently.
        self.spring_assist = "step_height_margin_m" in self.stage
        self.legacy_course = "step_height_max_m" not in self.stage and not self.spring_assist
        self.course = self.stage["course"]
        p = self.course
        x = np.linspace(
            -p["scan_half_length_m"],
            p["scan_half_length_m"],
            round(2 * p["scan_half_length_m"] / p["scan_resolution_m"]) + 1,
        )
        y = np.linspace(
            -p["scan_half_width_m"],
            p["scan_half_width_m"],
            round(2 * p["scan_half_width_m"] / p["scan_resolution_m"]) + 1,
        )
        self.scan_xy = np.array(np.meshgrid(x, y, indexing="ij")).reshape(2, -1).T
        self.ray_group = np.array([0, 0, 0, 1, 0, 0], dtype=np.uint8)
        self.ray_down = np.array([0.0, 0.0, -1.0])
        self.ray_id = np.zeros(1, dtype=np.int32)
        self.ground_z = self.signal_remaining = self.boost_remaining = 0.0
        self.boost_target = 0.0
        self.boost_triggered = False
        self.up = self.down = math.inf
        self.travel_sign = 1.0
        super().__init__(
            cfg,
            actor,
            model_path,
            cfg.evaluation["observation_delay_steps"],
            cfg.evaluation["action_delay_steps"],
            False,
        )
        if self.spring_assist:
            limits = cfg.shared["stairs_passive_joint_limits_rad"]
            if limits and (
                cfg.robot["variant"] != "reference_simulation_only"
                or cfg.robot["asset"].get("reference_preset") != "scut_v14_2"
            ):
                raise ValueError("Passive limit widening is authorized only for SCUT reference simulation")
            for name, bounds in limits.items():
                joint = self.model.joint(name).id
                self.model.jnt_range[joint] = bounds
                self.model.jnt_limited[joint] = 1
        body_names = {self.model.body(i).name: i for i in range(self.model.nbody)}
        requested = cfg.robot["asset"]["termination_contact_body_names"]
        missing = [n for n in requested if n not in body_names]
        if any(not re.fullmatch(p["guide_body_regex"], n) for n in missing):
            raise ValueError(f"MJCF is missing required termination bodies: {missing}")
        # The existing sim2sim robot omits independent guide bodies. Report this asset limitation explicitly.
        self.missing_guides = missing
        self.bad_bodies = np.array([body_names[n] for n in requested if n in body_names], dtype=int)
        if missing:
            print(
                f"MODEL_LIMITATION: {len(missing)} guide bodies absent; guide-support behaviour is not validated",
                flush=True,
            )
        self.guides = np.array(
            [i for i in range(self.model.nbody) if re.fullmatch(p["guide_body_regex"], self.model.body(i).name)],
            dtype=int,
        )
        self.stair_index = sum(width for name, width in OBS_FIELDS if name != "mode") + 1

    def terrain_heights(self, xy: np.ndarray) -> np.ndarray:
        heights = np.full(len(xy), np.nan)
        # The z offset follows the Isaac scanner; only static terrain group 3 is queried.
        for i, point in enumerate(xy):
            origin = np.array([point[0], point[1], self.data.qpos[2] + 20.0])
            distance = mujoco.mj_ray(
                self.model, self.data, origin, self.ray_down, self.ray_group, True, -1, self.ray_id
            )
            if distance >= 0:
                heights[i] = origin[2] - distance
        return heights

    def observation(self, command: np.ndarray, height: float) -> np.ndarray:
        yaw = euler_xyz(self.data.qpos[3:7])[2]
        rot = np.array([[math.cos(yaw), -math.sin(yaw)], [math.sin(yaw), math.cos(yaw)]])
        xy = self.scan_xy @ rot.T + self.data.qpos[:2]
        hits = np.column_stack((xy, self.terrain_heights(xy)))
        if abs(command[0]) >= self.cfg.training["reward_parameters"]["stand_deadzone"]:
            self.travel_sign = float(np.sign(command[0]))
        with torch.inference_mode():
            ground, up, down, rise = scan_course(
                torch.tensor(hits[None], dtype=torch.float32),
                torch.tensor(self.data.qpos[None, :3].copy(), dtype=torch.float32),
                torch.tensor([yaw]),
                torch.tensor(self.data.xpos[None, self.wheel_ids].copy(), dtype=torch.float32),
                torch.tensor([self.travel_sign]),
                torch.tensor([self.ground_z]),
                self.course,
            )
        self.ground_z, self.up, self.down = ground.item(), up.item(), down.item()
        dt = 1 / self.cfg.policy_hz
        detected = math.isfinite(self.up) or math.isfinite(self.down)
        self.signal_remaining = self.course["detection_hold_s"] if detected else max(0.0, self.signal_remaining - dt)
        if self.legacy_course:
            self.boost_remaining = (
                self.stage["step_height_hold_s"]
                if self.up <= self.course["trigger_distance_m"]
                else max(0.0, self.boost_remaining - dt)
            )
            self.effective_height = min(
                height + self.stage["step_height_boost_m"] * (self.boost_remaining > 0),
                self.course["height_range_m"][1],
            )
        elif self.spring_assist and "step_height_clearance_range_m" in self.stage:
            remaining, target, triggered = advance_height_assist(
                torch.tensor(self.up <= self.course["trigger_distance_m"]),
                torch.tensor(False),
                torch.tensor(self.boost_remaining),
                torch.tensor(self.boost_target),
                torch.tensor(self.boost_triggered),
                self.stage,
                dt,
                self.cfg.shared["spring_extension_height_m"] - self.stage["step_height_margin_m"],
                torch.tensor(height),
                rise.squeeze(0),
                False,
            )
            self.boost_remaining, self.boost_target, self.boost_triggered = (
                remaining.item(),
                target.item(),
                triggered.item(),
            )
            self.effective_height = self.boost_target if self.boost_remaining > 0 else height
        elif self.spring_assist:
            # Revision 3 snapshots retain their fixed spring-ceiling assistance.
            trigger = self.up <= self.course["trigger_distance_m"]
            entered = trigger and not self.boost_triggered and self.boost_remaining <= 0
            if entered:
                self.boost_target = self.cfg.shared["spring_extension_height_m"] - self.stage["step_height_margin_m"]
            self.boost_remaining = (
                self.stage["step_height_hold_s"]
                if trigger and (entered or self.boost_remaining > 0)
                else max(0.0, self.boost_remaining - dt)
            )
            self.boost_triggered = trigger
            self.effective_height = self.boost_target if self.boost_remaining > 0 else height
        else:
            # Revision 2 checkpoints retain their original latch and ceiling during replay.
            trigger = self.up <= self.course["trigger_distance_m"]
            entered = trigger and not self.boost_triggered
            if entered:
                self.boost_target = min(height + self.stage["step_height_boost_m"], self.stage["step_height_max_m"])
            self.boost_remaining = self.stage["step_height_hold_s"] if entered else max(0.0, self.boost_remaining - dt)
            self.boost_triggered = trigger
            self.effective_height = self.boost_target if self.boost_remaining > 0 else height
        obs = super().observation(command, self.effective_height)
        obs[self.stair_index] = float(self.signal_remaining > 0)
        return obs

    def _measure(self, command, height, peaks, saturated, inference_s, bad_action) -> dict:
        # Use local wheel support height, not world z=0, for height/airborne/termination diagnostics.
        c, d, dt = self.cfg, self.data, 1 / self.cfg.policy_hz
        roll, pitch, yaw = euler_xyz(d.qpos[3:7])
        ground = self.terrain_heights(d.xpos[self.wheel_ids, :2])
        self.ground_z = float(np.where(np.isfinite(ground), ground, self.ground_z).mean())
        base_height = d.qpos[2] - self.ground_z
        force = peaks[self.wheel_ids]
        contact = force > c.airborne["contact_force_n"]
        clearance = d.xpos[self.wheel_ids, 2] - self.ground_z - c.shared["wheel_radius_m"]
        a = c.airborne
        candidate = not contact.any() and clearance.min() > a["wheel_clearance_m"] and base_height > a["base_height_m"]
        self.air_enter = self.air_enter + dt if candidate else 0.0
        self.air_exit = self.air_exit + dt if contact.any() else 0.0
        self.is_airborne |= self.air_enter >= a["enter_duration_s"]
        self.air_elapsed = self.air_elapsed + dt if self.is_airborne else 0.0
        self.is_airborne &= self.air_exit < a["exit_duration_s"] and self.air_elapsed < a["max_duration_s"]
        tilt = c.termination["airborne_tilt_rad"] if self.is_airborne else c.termination["tilt_rad"]
        body_hit = bool((peaks[self.bad_bodies] > c.termination["contact_force_n"]).any())
        physical = (max(abs(roll), abs(pitch)) > tilt or body_hit) and self.time >= c.leg_reset["settle_s"]
        self.termination_steps = (
            self.termination_steps + 1
            if physical
            else max(0.0, self.termination_steps - c.termination["duration_s"] / c.termination["release_s"])
        )
        safety = c.shared["numerical_safety"]
        numerical = not (np.isfinite(d.qpos).all() and np.isfinite(d.qvel).all())
        numerical |= np.abs(d.qvel[self.v_adr]).max() > safety["joint_velocity_abs_max"]
        numerical |= np.abs(d.qvel[:3]).max() > safety["base_linear_velocity_abs_max"]
        numerical |= np.abs(d.qvel[3:6]).max() > safety["base_angular_velocity_abs_max"]
        vx = math.cos(yaw) * d.qvel[0] + math.sin(yaw) * d.qvel[1]
        return dict(
            time=self.time,
            heading_vx=vx,
            wz=d.qvel[5],
            base_height=base_height,
            roll=roll,
            pitch=pitch,
            wheel_force=force,
            guide_force=float(peaks[self.guides].max(initial=0)),
            terminated=bool(
                bad_action or numerical or self.termination_steps >= round(c.termination["duration_s"] * c.policy_hz)
            ),
            numerical=bool(numerical or bad_action),
            action_max=float(np.abs(self.raw_action).max()),
            saturation=float(saturated.mean()),
            position=d.qpos[:3].copy(),
        )


class CoursePlayer:
    def __init__(self, sim: TerrainSim, tiles: list[dict], profile: str, row: int):
        self.sim, self.tiles = sim, tiles
        self.names = list(sim.stage["terrain"]["profiles"])
        self.profile, self.row, self.reverse = profile, row, False
        self.lock = threading.Lock()
        self.target, self.value = np.zeros(3), np.zeros(3)
        self.height = self.height_target = float(np.mean(self.height_bounds()))
        self.request, self.paused, self.tracking, self.slow = True, False, True, 0
        self.camera_request = True
        self.last, self.budget, self.info = None, 0.0, None
        self.failed = False

    def height_bounds(self) -> list:
        return (
            self.sim.course["height_range_m"]
            if self.sim.legacy_course
            else self.sim.stage["terrain"]["profiles"][self.profile]["height_range_m"]
        )

    def key(self, code: int) -> None:
        # The passive viewer keeps its native shortcuts. Never bind letters, arrows, Space or top-row digits here.
        if code not in (*KP.values(), KP_DECIMAL, KP_DIVIDE, KP_ENTER, KP_ADD, KP_SUBTRACT, KP_MULTIPLY):
            return
        with self.lock:
            if code == KP["8"]:
                self.target[0] += 0.25
            elif code == KP["2"]:
                self.target[0] -= 0.25
            elif code == KP["4"]:
                self.target[2] += 0.5
            elif code == KP["6"]:
                self.target[2] -= 0.5
            elif code == KP["9"]:
                self.height_target += 0.02
            elif code == KP["3"]:
                self.height_target -= 0.02
            elif code == KP["5"]:
                self.target[:] = 0
            elif code == KP["7"]:
                self.slow = (self.slow + 1) % len(SLOW_MOTION)
            elif code == KP["1"]:
                self.tracking = not self.tracking
                self.camera_request = True
            elif code in (KP["0"], KP_DECIMAL):
                self.request = True
            elif code in (KP_ENTER, KP_MULTIPLY):
                self.reverse = not self.reverse
                self.request = True
            elif code in (KP_ADD, KP_SUBTRACT):
                self.profile = self.names[
                    (self.names.index(self.profile) + (1 if code == KP_ADD else -1)) % len(self.names)
                ]
                self.request = True
            elif code == KP_DIVIDE:
                self.paused = not self.paused
            maximum = self.sim.stage["terrain"]["profiles"][self.profile]["speed_range_m_s"][1]
            self.target[0] = np.clip(self.target[0], -maximum, maximum)
            self.target[2] = np.clip(self.target[2], *self.sim.cfg.commands["wz_range_rad_s"])
            self.height_target = float(np.clip(self.height_target, *self.height_bounds()))

    def respawn(self) -> None:
        self.height_target = float(np.clip(self.height_target, *self.height_bounds()))
        self.tile = next(t for t in self.tiles if t["profile"] == self.profile and t["row"] == self.row)
        x, y, z = self.tile["spawn"]
        self.sim.reset(Spawn(x_m=x, y_m=y, height_offset_m=z, yaw_rad=math.pi if self.reverse else 0.0))
        self.sim.ground_z = z
        self.sim.signal_remaining = self.sim.boost_remaining = 0.0
        self.sim.boost_target, self.sim.boost_triggered = 0.0, False
        self.sim.travel_sign = -1.0 if self.reverse else 1.0
        self.target[:] = self.value[:] = 0.0
        self.height = self.height_target
        self.info, self.failed, self.paused = None, False, False
        self.budget = 0.0
        self.request = False

    def tick(self, viewer) -> None:
        now = time.perf_counter()
        elapsed = 0 if self.last is None else now - self.last
        self.last = now
        dt = 1 / self.sim.cfg.policy_hz
        with viewer.lock(), self.lock:
            if self.request:
                self.respawn()
                viewer.cam.lookat[:] = self.sim.data.qpos[:3]
            if not self.paused and not self.failed:
                self.budget = min(self.budget + elapsed * SLOW_MOTION[self.slow], 0.1)
                c = self.sim.cfg.commands
                while self.budget >= dt:
                    rates = np.array([c["linear_slew_m_s2"], c["linear_slew_m_s2"], c["angular_slew_rad_s2"]]) * dt
                    self.value += np.clip(self.target - self.value, -rates, rates)
                    self.height += float(
                        np.clip(self.height_target - self.height, -c["height_slew_m_s"] * dt, c["height_slew_m_s"] * dt)
                    )
                    self.info = self.sim.step(self.value, self.height)
                    self.budget -= dt
                    self.failed = self.info["terminated"]
                    if self.failed:
                        break
            if self.camera_request:
                viewer.cam.type = (
                    mujoco.mjtCamera.mjCAMERA_TRACKING if self.tracking else mujoco.mjtCamera.mjCAMERA_FREE
                )
                viewer.cam.trackbodyid = self.sim.base
                self.camera_request = False
            # Respect native Esc / Ctrl-right-double-click changes instead of overwriting the camera every frame.
            self.tracking = viewer.cam.type == mujoco.mjtCamera.mjCAMERA_TRACKING
            viewer.set_texts(self.texts())
        viewer.sync()

    def texts(self) -> list:
        p, sim, i = self.sim.course, self.sim, self.info
        turn_limit = (
            p["yaw_rate_limit_rad_s"]
            if sim.legacy_course
            else max(abs(v) for v in sim.stage["terrain"]["profiles"][self.profile]["yaw_range_rad_s"])
        )
        color_note = "manual turning outside sampled yaw range" if abs(self.value[2]) > turn_limit else ""
        heading = (
            f"{self.tile['profile']} | row {self.tile['row'] + 1}/{sim.stage['terrain']['rows']}"
            f" | actor {sim.actor.iteration}"
        )
        state = "FAILED - KP0 / Respawn" if self.failed else "PAUSED" if self.paused else "RUNNING"
        values = f"{state} | speed x{SLOW_MOTION[self.slow]}\n"
        values += f"command vx {self.value[0]:+.2f} / wz {self.value[2]:+.2f} / height {self.height:.2f}\n"
        values += f"stair {int(sim.signal_remaining > 0)} / boost {sim.boost_remaining:.2f}s / {color_note}\n"
        if i:
            values += (
                f"actual vx {i['heading_vx']:+.2f} / height {i['base_height']:.3f}"
                f" / roll,pitch {math.degrees(i['roll']):+.1f},{math.degrees(i['pitch']):+.1f} deg\n"
            )
            guide = "N/A (model has no guides)" if sim.missing_guides else f"{i['guide_force']:.0f} N"
            values += (
                f"wheels {i['wheel_force'][0]:.0f}/{i['wheel_force'][1]:.0f} N"
                f" | guide {guide} | raw action {i['action_max']:.1f}\n"
            )
            values += (
                f"route x {i['position'][0] - self.tile['offset'][0]:.2f} m"
                f" / finish {sim.stage['terrain']['finish_x_m']:.2f} m"
            )
        return [
            (mujoco.mjtFontScale.mjFONTSCALE_150, mujoco.mjtGridPos.mjGRID_TOPLEFT, heading, values),
            (
                mujoco.mjtFontScale.mjFONTSCALE_100,
                mujoco.mjtGridPos.mjGRID_BOTTOMLEFT,
                "KP8/2 speed | KP4/6 yaw | KP9/3 height | KP5 stop\n"
                "KP0 reset | KP+/- terrain | KP Enter reverse\nKP/ pause | KP7 slow | KP1 camera",
                "NUMPAD ONLY (NumLock on). Top-row digits are MuJoCo display groups.\n"
                "Terrain: top-row 3 toggles visibility. D toggles static bodies.",
            ),
        ]


def run_panel(player: CoursePlayer, viewer, keyboard: bool) -> None:
    import tkinter as tk
    from tkinter import ttk

    root = tk.Tk()
    root.title(f"台阶 sim2sim · model_{player.sim.actor.iteration}")
    root.geometry("650x540")
    profile, row = tk.StringVar(value=player.profile), tk.IntVar(value=player.row + 1)
    reverse = tk.BooleanVar(value=False)
    instructions = (
        "字母驾驶键仅在此面板生效；MuJoCo窗口使用小键盘（NumLock开启）"
        if keyboard
        else "沿用旧sim2sim：点击MuJoCo窗口，用小键盘驾驶（NumLock开启）。此面板用鼠标。"
    )
    ttk.Label(root, text=instructions, padding=10, wraplength=610).pack()
    controls = ttk.Frame(root, padding=10)
    controls.pack(fill="x")
    ttk.Label(controls, text="地形").grid(row=0, column=0)
    ttk.Combobox(controls, textvariable=profile, values=player.names, state="readonly", width=18).grid(row=0, column=1)
    ttk.Label(controls, text="难度行").grid(row=0, column=2)
    ttk.Combobox(
        controls,
        textvariable=row,
        values=list(range(1, player.sim.stage["terrain"]["rows"] + 1)),
        state="readonly",
        width=4,
    ).grid(row=0, column=3)
    ttk.Checkbutton(controls, text="倒车接近", variable=reverse).grid(row=1, column=1)

    def spawn():
        with player.lock:
            player.profile, player.row, player.reverse = profile.get(), row.get() - 1, reverse.get()
            player.request = True

    ttk.Button(controls, text="到所选地形出生点", command=spawn).grid(row=1, column=2, columnspan=2)
    letters = {
        "w": KP["8"],
        "s": KP["2"],
        "a": KP["4"],
        "d": KP["6"],
        "r": KP["9"],
        "f": KP["3"],
        "space": KP["5"],
        "p": KP_DIVIDE,
        "z": KP["7"],
        "c": KP["1"],
        "1": KP["0"],
        "2": KP_ENTER,
        "3": KP_DECIMAL,
        "equal": KP_ADD,
        "plus": KP_ADD,
        "minus": KP_SUBTRACT,
        "x": KP_MULTIPLY,
    }
    mapping = {f"kp_{n}": code for n, code in KP.items()}
    mapping.update(
        kp_decimal=KP_DECIMAL,
        kp_divide=KP_DIVIDE,
        kp_enter=KP_ENTER,
        kp_add=KP_ADD,
        kp_subtract=KP_SUBTRACT,
        kp_multiply=KP_MULTIPLY,
    )
    if keyboard:
        mapping.update(letters)

    def key(event):
        # Space while a button is focused must not also trigger the selected button.
        if event.keysym.lower() in mapping:
            player.key(mapping[event.keysym.lower()])
            return "break"

    # Install before Tk widget/class bindings: one press cannot both steer and activate a focused button.
    input_tag = "StairsPanelInput"
    root.bind_class(input_tag, "<KeyPress>", key)
    buttons = ttk.Frame(root, padding=10)
    buttons.pack()
    for n, (label, code) in enumerate(
        [
            ("小键盘8 前进 +0.25", KP["8"]),
            ("小键盘2 后退 -0.25", KP["2"]),
            ("小键盘4 左转 +0.5", KP["4"]),
            ("小键盘6 右转 -0.5", KP["6"]),
            ("小键盘9 抬高 +0.02", KP["9"]),
            ("小键盘3 降低 -0.02", KP["3"]),
            ("小键盘5 停车", KP["5"]),
            ("小键盘/ 暂停", KP_DIVIDE),
            ("小键盘7 慢放", KP["7"]),
            ("小键盘1 跟随相机", KP["1"]),
        ]
    ):
        ttk.Button(buttons, text=label, command=lambda k=code: player.key(k), width=23).grid(
            row=n // 2, column=n % 2, padx=4, pady=4
        )
    status = tk.StringVar()
    ttk.Label(root, textvariable=status, wraplength=560, padding=10).pack()

    def show_map():
        with viewer.lock():
            viewer.opt.geomgroup[3] = 1
            viewer.opt.flags[mujoco.mjtVisFlag.mjVIS_STATIC] = 1
        viewer.sync()

    ttk.Button(root, text="恢复地图显示", command=show_map).pack()
    ttk.Label(
        root,
        text=(
            "MuJoCo窗口：鼠标拖动旋转/平移，滚轮缩放；双击刚体后 Ctrl+右键拖动施力。\n"
            "速度为累加指令，不是松键自动停车；小键盘5停车。失败后冻结，按重新出生。\n"
            "沿用旧sim2sim简化模型：缺少独立导轮，不能据此验收导轮支撑收腿。"
        ),
        wraplength=560,
    ).pack()
    root.protocol("WM_DELETE_WINDOW", lambda: (viewer.close(), root.destroy()))
    widgets = [root]
    while widgets:
        widget = widgets.pop()
        widget.bindtags((input_tag, *widget.bindtags()))
        widgets.extend(widget.winfo_children())

    def loop():
        if not viewer.is_running():
            root.destroy()
            return
        player.tick(viewer)
        state = "失败，需重新出生" if player.failed else "暂停" if player.paused else "运行"
        status.set(
            f"{player.profile} · 第{player.row + 1}行 · {state}\n"
            f"目标速度 {player.target[0]:+.2f} m/s / 转向 {player.target[2]:+.2f} rad/s"
            f" / 高度 {player.height_target:.2f}m\n"
            "按所载快照构造高度与提示；窗口为手动驾驶，转向范围参考HUD及该地形配置。"
        )
        root.after(5, loop)

    root.after(5, loop)
    root.mainloop()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, default=ROOT / "runs/stairs_viewer/checkpoint")
    parser.add_argument("--profile", default="up_one")
    parser.add_argument("--row", type=int, default=2, help="difficulty row, 1..8")
    parser.add_argument(
        "--panel", action="store_true", help="enable old W/S A/D letter keys ONLY in the separate panel"
    )
    parser.add_argument(
        "--build-only", action="store_true", help="compile the model and inspect spawn/sensors, no viewer"
    )
    args = parser.parse_args()
    torch.set_num_threads(1)
    run = args.run.resolve()
    cfg = RunConfig(run)
    if cfg.run.get("task") != "p1-stairs":
        raise ValueError("Use a p1-stairs checkpoint and its matching params/run.json")
    checkpoints = list(run.glob("model_*.pt"))
    if not checkpoints:
        raise ValueError(f"No downloaded checkpoint in {run}")
    checkpoint = max(checkpoints, key=lambda p: int(p.stem.split("_")[1]))
    terrain = cfg.policy["stages"]["stairs"]["terrain"]
    if args.profile not in terrain["profiles"] or not 1 <= args.row <= terrain["rows"]:
        parser.error("Unknown terrain profile or difficulty row")
    out = ROOT / "runs/stairs_viewer"
    out.mkdir(parents=True, exist_ok=True)
    # Rebuild the existing robot with this run's friction/damping and fixed randomization midpoints.
    flat = out / "robot_flat.xml"
    build(ROOT / "runs/scut_experience/scene.xml", run / "params/robot.yaml", flat, 0.8)
    model_path = out / "course.xml"
    tiles = build_course(flat, model_path, terrain, cfg.shared["ground_material"]["dynamic_friction"])
    (out / "map.json").write_text(json.dumps(tiles, indent=2), encoding="utf-8")
    actor = NumpyActor(checkpoint, cfg.policy["hidden_dims"])
    sim = TerrainSim(cfg, actor, model_path)
    player = CoursePlayer(sim, tiles, args.profile, args.row - 1)
    player.respawn()
    obs = sim.observation(np.zeros(3), player.height)
    print(
        f"MODEL_READY actor={checkpoint} tiles={len(tiles)} geoms={sim.model.ngeom}"
        f" obs={obs.shape} delays={sim.obs_line.lag}/{sim.act_line.lag}",
        flush=True,
    )
    (out / "last_launch.json").write_text(
        json.dumps(
            dict(checkpoint=str(checkpoint), model=str(model_path), profile=args.profile, row=args.row), indent=2
        ),
        encoding="utf-8",
    )
    if args.build_only:
        print(f"SPAWN ground_z={sim.ground_z:.4f} actor_finite={bool(np.isfinite(actor(obs)).all())}", flush=True)
        return
    with mujoco.viewer.launch_passive(
        sim.model, sim.data, key_callback=player.key, show_left_ui=False, show_right_ui=False
    ) as viewer:
        viewer.cam.distance, viewer.cam.elevation, viewer.cam.azimuth = 3.0, -20.0, 135.0
        # MuJoCo defaults to geom groups [1,1,1,0,0,0]; our terrain-only raycast group must also be visible.
        with viewer.lock():
            viewer.opt.geomgroup[3] = 1
            viewer.opt.flags[mujoco.mjtVisFlag.mjVIS_STATIC] = 1
        viewer.sync()
        run_panel(player, viewer, keyboard=args.panel)


if __name__ == "__main__":
    main()
