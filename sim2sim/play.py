"""Interactive MuJoCo viewer: air-spawned wheel-leg robot driven from the numeric keypad.

Same control loop as sim2sim.py (500 Hz physics/PD/spring, 100 Hz policy, training delays). Air spawns follow the
p1-landing training reset: random leg length/angle, roll/pitch, lateral speed and body rates, forward speed equal
to the command (driving off a ledge), and the command limits for the first seconds after the birth.

All controls are on the numeric keypad, which MuJoCo's viewer does not use (its own keys - Space, arrows,
letters, 0-5, Tab, [ ], F1-F5, Backspace, mouse - keep working as usual). Keep NumLock on.

    KP8 / KP2   forward speed  +/- 0.25 m/s        KP0        respawn in the air
    KP4 / KP6   yaw rate (left/right) 0.5 rad/s    KP .       respawn on the ground (folded legs)
    KP9 / KP3   height command +/- 0.02 m          KP+ / KP-  air spawn height +/- 0.05 m
    KP5         stop (vx = wz = 0)                 KP*        air spawn: random legs/tilt on/off
    KP7         slow motion 1 / 0.5 / 0.25 / 0.1   KP/        pause / resume
    KP1         tracking camera on/off             KP Enter   respawn in the air, straight drop

Without a keypad, add --panel for a small control window that takes W/S A/D R/F Space 1/2 etc. instead.
Mouse pushes work as in MuJoCo: double-click a body, then Ctrl + right-drag.

    python play.py --run checkpoints/landing_r5b2ffae_cmd40
"""

import argparse
import math
import threading
import time
from pathlib import Path

import mujoco
import mujoco.viewer
import numpy as np

from sim2sim import HERE, NumpyActor, RunConfig, Spawn, WheelLegSim, euler_xyz

KP = {name: 320 + i for i, name in enumerate("0123456789")}
KP_DECIMAL, KP_DIVIDE, KP_MULTIPLY, KP_SUBTRACT, KP_ADD, KP_ENTER = range(330, 336)
SLOW_MOTION = (1.0, 0.5, 0.25, 0.1)


class Player:
    def __init__(self, sim: WheelLegSim, spawn_height: float, seed: int):
        self.sim, self.cfg = sim, sim.cfg
        self.c = self.cfg.commands
        self.stage = self.cfg.policy["stages"].get("landing") or self.cfg.policy["stages"]["stairs"]
        self.rng = np.random.default_rng(seed)
        self.dt = 1.0 / self.cfg.policy_hz
        self.lock = threading.Lock()
        self.target = np.zeros(3)  # vx, vy, wz targets set by the keys
        self.height_target = self.cfg.evaluation["height_m"]
        self.spawn_height = spawn_height
        self.random_spawn = True
        self.slow = 0
        self.paused = False
        self.tracking = True
        self.request = ("air", True)
        self.value = np.zeros(3)
        self.height = self.height_target
        self.limit_remaining = 0.0
        self.budget = 0.0
        self.last = None
        self.info = None
        self.landing = ""
        self.spawn_desc = ""
        self.touch_time = None
        self.held = 0.0
        self.peak_force = 0.0

    # ----- input -----
    def key(self, code: int) -> None:
        c = self.c
        with self.lock:
            if code == KP["8"]:
                self.target[0] = min(self.target[0] + 0.25, c["vx_range_m_s"][1])
            elif code == KP["2"]:
                self.target[0] = max(self.target[0] - 0.25, c["vx_range_m_s"][0])
            elif code == KP["4"]:
                self.target[2] = min(self.target[2] + 0.5, c["wz_range_rad_s"][1])
            elif code == KP["6"]:
                self.target[2] = max(self.target[2] - 0.5, c["wz_range_rad_s"][0])
            elif code == KP["9"]:
                self.height_target = min(round(self.height_target + 0.02, 3), c["height_range_m"][1])
            elif code == KP["3"]:
                self.height_target = max(round(self.height_target - 0.02, 3), c["height_range_m"][0])
            elif code == KP["5"]:
                self.target[:] = 0.0
            elif code == KP["7"]:
                self.slow = (self.slow + 1) % len(SLOW_MOTION)
            elif code == KP["1"]:
                self.tracking = not self.tracking
            elif code == KP["0"]:
                self.request = ("air", self.random_spawn)
            elif code == KP_ENTER:
                self.request = ("air", False)
            elif code == KP_DECIMAL:
                self.request = ("ground", False)
            elif code == KP_ADD:
                self.spawn_height = min(round(self.spawn_height + 0.05, 3), 1.0)
            elif code == KP_SUBTRACT:
                self.spawn_height = max(round(self.spawn_height - 0.05, 3), 0.0)
            elif code == KP_MULTIPLY:
                self.random_spawn = not self.random_spawn
            elif code == KP_DIVIDE:
                self.paused = not self.paused

    # ----- simulation -----
    def _respawn(self, kind: str, random_pose: bool) -> None:
        sim, s, rng = self.sim, self.stage, self.rng
        x, y = sim.data.qpos[0], sim.data.qpos[1]
        _, _, yaw = euler_xyz(sim.data.qpos[3:7])
        self.value[:] = self.target
        self.height = self.height_target
        if kind == "ground":
            spawn = Spawn(x_m=x, y_m=y, yaw_rad=yaw)
            self.limit_remaining = 0.0
            self.spawn_desc = "ground, folded legs"
        else:
            limit = np.array([s["air_command_vx_limit_m_s"], np.inf, s["air_command_wz_limit_rad_s"]])
            self.value = np.clip(self.value, -limit, limit)
            self.limit_remaining = s["air_command_limit_s"]
            vx = self.value[0]
            spawn = Spawn(self.spawn_height, vx, x_m=x, y_m=y, yaw_rad=yaw)
            if random_pose:
                tilt = np.array(s["air_tilt_rad"])
                spawn.leg_length_m = float(rng.uniform(*s["air_leg_length_range_m"]))
                spawn.leg_angle_rad = float(rng.uniform(*s["air_leg_angle_range_rad"]))
                spawn.roll_rad, spawn.pitch_rad = rng.uniform(-1, 1, 2) * tilt
                spawn.vy_m_s = float(rng.uniform(*s["air_vy_range_m_s"]))
                spawn.rate_b = tuple(rng.uniform(-1, 1, 3) * np.array(s["air_angular_velocity_rad_s"]))
                if "air_vx_command_noise_m_s" in s and rng.random() < s["air_vx_command_probability"]:
                    vx += s["air_vx_command_noise_m_s"] * rng.standard_normal()
                else:
                    vx = rng.uniform(*s["air_vx_range_m_s"])
                spawn.vx_m_s = float(np.clip(vx, *s["air_vx_range_m_s"]))
            leg = "folded" if spawn.leg_length_m is None else f"leg {spawn.leg_length_m:.2f} m {spawn.leg_angle_rad:+.2f} rad"
            self.spawn_desc = (
                f"air +{spawn.height_offset_m:.2f} m, vx {spawn.vx_m_s:+.2f}, vy {spawn.vy_m_s:+.2f}, {leg}, "
                f"roll {spawn.roll_rad:+.2f} pitch {spawn.pitch_rad:+.2f}"
            )
        sim.reset(spawn)
        self.landing = "in flight" if kind == "air" else ""
        self.touch_time = None
        self.held = 0.0
        self.peak_force = 0.0

    def _command(self) -> np.ndarray:
        c, dt = self.c, self.dt
        rates = np.array([c["linear_slew_m_s2"], c["linear_slew_m_s2"], c["angular_slew_rad_s2"]]) * dt
        self.value += np.clip(self.target - self.value, -rates, rates)
        step = c["height_slew_m_s"] * dt
        self.height += float(np.clip(self.height_target - self.height, -step, step))
        if self.limit_remaining > 0:
            s = self.stage
            limit = np.array([s["air_command_vx_limit_m_s"], np.inf, s["air_command_wz_limit_rad_s"]])
            self.value = np.clip(self.value, -limit, limit)
            self.limit_remaining = max(self.limit_remaining - dt, 0.0)
        return np.array([self.value[0], 0.0, self.value[2]])

    def _track_landing(self, info: dict) -> None:
        p = self.cfg.landing
        if not self.landing or p is None or self.landing.startswith(("OK", "FAIL")):
            return
        touched = (info["wheel_force"] > p["contact_force_n"]).any() or info["nonwheel_contact"]
        if self.touch_time is None and touched:
            self.touch_time = info["time"]
        if self.touch_time is None:
            return
        since = info["time"] - self.touch_time
        if since < 0.5:
            self.peak_force = max(self.peak_force, float(info["wheel_force"].max()))
        if info["nonwheel_contact"] or info["terminated"]:
            self.landing = f"FAIL body contact at +{since:.2f} s"
            return
        stable = (info["wheel_force"] > p["support_force_n"]).all()
        stable &= max(abs(info["roll"]), abs(info["pitch"])) <= p["tilt_rad"]
        stable &= info["angular_xy"] <= p["angular_xy_rad_s"] and abs(info["vz"]) <= p["vertical_velocity_m_s"]
        stable &= abs(info["errors"][2]) <= p["height_error_m"]
        self.held = self.held + self.dt if stable else 0.0
        if self.held >= p["stable_s"] - 1e-6:
            self.landing = f"OK stable {since:.2f} s after touchdown, peak wheel force {self.peak_force:.0f} N"
        elif since >= p["window_s"]:
            self.landing = "FAIL not stable within window"
        else:
            self.landing = f"touchdown +{since:.2f} s"

    def tick(self, viewer) -> None:
        now = time.perf_counter()
        wall = 0.0 if self.last is None else now - self.last
        self.last = now
        with self.lock:
            request, self.request = self.request, None
            paused, scale = self.paused, SLOW_MOTION[self.slow]
        with viewer.lock():
            if request is not None:
                self._respawn(*request)
                self.budget = 0.0
            if not paused:
                self.budget = min(self.budget + wall * scale, 0.1)
                while self.budget >= self.dt:
                    with self.lock:
                        command = self._command()
                    self.info = self.sim.step(command, self.height)
                    self._track_landing(self.info)
                    self.budget -= self.dt
            viewer.cam.type = mujoco.mjtCamera.mjCAMERA_TRACKING if self.tracking else mujoco.mjtCamera.mjCAMERA_FREE
            viewer.cam.trackbodyid = self.sim.base
            viewer.set_texts(self._texts())
        viewer.sync()

    def _texts(self):
        i = self.info
        top = mujoco.mjtGridPos.mjGRID_TOPLEFT
        bottom = mujoco.mjtGridPos.mjGRID_BOTTOMLEFT
        font = mujoco.mjtFontScale.mjFONTSCALE_150
        if i is None:
            return [(font, top, "starting", "")]
        state = "FELL (KP0 respawn)" if i["terminated"] else "airborne" if i["airborne"] else "ground"
        if self.paused:
            state += "  [PAUSED]"
        names = [
            "time",
            "command vx / wz / h",
            "actual  vx / wz / h",
            "roll / pitch",
            "wheel force L / R",
            "state",
            "landing",
            "spawn",
            "next air spawn",
            "speed",
        ]
        values = [
            f"{i['time']:.2f} s",
            f"{self.value[0]:+.2f} m/s  {self.value[2]:+.2f} rad/s  {self.height:.2f} m"
            + (f"  (limited {self.limit_remaining:.1f} s)" if self.limit_remaining > 0 else ""),
            f"{i['heading_vx']:+.2f} m/s  {i['wz']:+.2f} rad/s  {i['base_height']:.2f} m",
            f"{math.degrees(i['roll']):+.1f} deg  {math.degrees(i['pitch']):+.1f} deg",
            f"{i['wheel_force'][0]:.0f} N  {i['wheel_force'][1]:.0f} N",
            state,
            self.landing or "-",
            self.spawn_desc,
            f"+{self.spawn_height:.2f} m, {'random legs/tilt' if self.random_spawn else 'folded, level'}",
            f"x{SLOW_MOTION[self.slow]}",
        ]
        help_left = "KP8/2 vx   KP4/6 yaw   KP9/3 height   KP5 stop\nKP0 air spawn   KP Enter straight drop   KP. ground"
        help_right = "KP+/- spawn height   KP* random pose\nKP7 slow motion   KP/ pause   KP1 camera"
        return [(font, top, "\n".join(names), "\n".join(values)), (font, bottom, help_left, help_right)]


def run_panel(player: Player, viewer) -> None:
    """Optional Tk control window for keyboards without a keypad; it has its own focus, so no MuJoCo conflicts."""
    import tkinter as tk

    root = tk.Tk()
    root.title("wheel-leg control")
    root.attributes("-topmost", True)
    mapping = {
        "w": KP["8"], "s": KP["2"], "a": KP["4"], "d": KP["6"], "r": KP["9"], "f": KP["3"],
        "space": KP["5"], "1": KP["0"], "2": KP_ENTER, "3": KP_DECIMAL, "equal": KP_ADD, "plus": KP_ADD,
        "minus": KP_SUBTRACT, "x": KP_MULTIPLY, "z": KP["7"], "p": KP_DIVIDE, "c": KP["1"],
    }  # fmt: skip
    text = (
        "Click here, then:\n"
        "W/S  forward speed    A/D  yaw rate    R/F  height    Space  stop\n"
        "1  air spawn    2  straight drop    3  ground spawn\n"
        "+/-  spawn height    X  random pose    Z  slow motion    P  pause    C  camera"
    )
    tk.Label(root, text=text, justify="left", font=("Consolas", 11), padx=10, pady=10).pack()
    root.bind("<KeyPress>", lambda e: player.key(mapping[e.keysym.lower()]) if e.keysym.lower() in mapping else None)

    def loop():
        if not viewer.is_running():
            root.destroy()
            return
        player.tick(viewer)
        root.after(2, loop)

    root.after(2, loop)
    root.mainloop()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run", type=Path, required=True, help="folder with model_*.pt and params/")
    parser.add_argument("--checkpoint", type=Path, help="default: highest model_*.pt in --run")
    parser.add_argument("--model", type=Path, default=HERE / "assets" / "scut_v14_2_flat.xml")
    parser.add_argument("--obs-delay", type=int, help="physics ticks; default training.evaluation")
    parser.add_argument("--act-delay", type=int, help="physics ticks; default training.evaluation")
    parser.add_argument("--noise", action="store_true", help="add the training observation noise")
    parser.add_argument("--wheel-friction", type=float, help="override the MJCF wheel friction (training 0.4-1.2)")
    parser.add_argument(
        "--spawn-height", type=float, default=0.25, help="air spawn offset above ground birth, m (training reached 0.28)"
    )
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--panel", action="store_true", help="extra Tk control window (no keypad needed)")
    args = parser.parse_args()

    cfg = RunConfig(args.run)
    checkpoint = args.checkpoint or max(args.run.glob("model_*.pt"), key=lambda p: int(p.stem.split("_")[1]))
    actor = NumpyActor(checkpoint, cfg.policy["hidden_dims"])
    obs_delay = cfg.evaluation["observation_delay_steps"] if args.obs_delay is None else args.obs_delay
    act_delay = cfg.evaluation["action_delay_steps"] if args.act_delay is None else args.act_delay
    sim = WheelLegSim(cfg, actor, args.model, obs_delay, act_delay, args.noise, args.wheel_friction)
    player = Player(sim, args.spawn_height, args.seed)
    print(__doc__)
    print(f"checkpoint {checkpoint} (iter {actor.iteration}); delays obs {obs_delay} / act {act_delay} ticks")
    with mujoco.viewer.launch_passive(
        sim.model, sim.data, key_callback=player.key, show_left_ui=False, show_right_ui=False
    ) as viewer:
        viewer.cam.distance, viewer.cam.elevation, viewer.cam.azimuth = 2.5, -15, 135
        if args.panel:
            run_panel(player, viewer)
        else:
            while viewer.is_running():
                player.tick(viewer)
                time.sleep(0.002)


if __name__ == "__main__":
    main()
