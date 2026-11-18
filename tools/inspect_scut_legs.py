"""Manual suspended SCUT V14_2 leg bench (no policy or hardware connection)."""

import json
import time
import xml.etree.ElementTree as ET
from queue import Empty, SimpleQueue

import mujoco.viewer
import numpy as np

from tools.play_jump import ROOT, RunConfig
from sim2sim import five_bar_joint_angles


def main():
    launch = json.loads((ROOT / "runs/jump_viewer/last_launch.json").read_text())
    cfg = RunConfig((ROOT / launch["checkpoint"]).parent)
    path = ROOT / "runs/jump_viewer/robot_flat.xml"
    xml = ET.parse(path).getroot()
    compiler = xml.find("compiler")
    compiler.set("meshdir", str((path.parent / compiler.get("meshdir")).resolve()))
    base = xml.find(".//body[@name='base_link']")
    base.remove(base.find("freejoint"))
    base.set("pos", "0 0 0.7")
    for side in ("left", "right"):
        xml.find(f".//joint[@name='{side}_rear2_joint']").set("range", "-0.02 1.2")
    m = mujoco.MjModel.from_xml_string(ET.tostring(xml, encoding="unicode"))
    d = mujoco.MjData(m)
    bid = m.body("base_link").id
    wheels = [m.body(n).id for n in cfg.wheel_bodies]
    pivots = np.asarray(cfg.shared["hip_pivot_positions_b_m"])
    names = [cfg.active_joints[i] for i in cfg.legs]
    hips = [m.joint(n).id for n in names]
    acts = [m.actuator(n + "_ctrl").id for n in names]
    slides = [m.joint(n).id for n in cfg.spring_joints]
    valves = [m.actuator(n + "_ctrl").id for n in cfg.spring_joints]
    passive = [m.joint(f"{side}_{part}_joint").id for side in ("left", "right")
               for part in ("front2", "front3", "front4", "rear2", "spring1")]
    lr, spring = cfg.leg_reset, cfg.spring
    direction = np.asarray(spring["direction"])
    keys = SimpleQueue()
    target = .20
    ref = .125
    with mujoco.viewer.launch_passive(m, d, key_callback=keys.put, show_left_ui=False, show_right_ui=False) as view:
        view.cam.lookat[:] = [0, 0, .57]
        view.cam.distance, view.cam.azimuth, view.cam.elevation = 1.2, 83, -9
        while view.is_running():
            start = time.perf_counter()
            try:
                while True:
                    key = keys.get_nowait()
                    if key in (ord('['), ord(']')):
                        target = np.clip(target + (.005 if key == ord(']') else -.005), .06, .40)
                    elif key == ord('0'):
                        target = .20
            except Empty:
                pass
            with view.lock():
                for _ in range(5):
                    ref += np.clip(target - ref, -.04*m.opt.timestep, .04*m.opt.timestep)
                    qa = five_bar_joint_angles(ref, 0, lr['link_lengths_m'], lr['angle_offsets_rad'])[:2] * 2
                    torque = cfg.kp[cfg.legs] * (qa - d.qpos[m.jnt_qposadr[hips]]) - cfg.kd[cfg.legs]*d.qvel[m.jnt_dofadr[hips]]
                    d.ctrl[acts] = np.clip(torque, -cfg.torque_limit[cfg.legs], cfg.torque_limit[cfg.legs])
                    q, qd = d.qpos[m.jnt_qposadr[slides]], d.qvel[m.jnt_dofadr[slides]]
                    compression = np.clip(direction*(q-spring['reference_q_m']), 0, cfg.spring_stroke)
                    force = -direction*(spring['f0_n'] + spring['stiffness_n_m']*compression) - spring['damping_n_s_m']*qd - spring['hysteresis_n']*np.sign(qd)
                    d.ctrl[valves] = np.clip(force, -np.asarray(spring['force_limit_n']), spring['force_limit_n'])
                    mujoco.mj_step(m, d)
                mujoco.mj_kinematics(m, d)
                vec = (d.xpos[wheels]-d.xpos[bid]) @ d.xmat[bid].reshape(3, 3) - pivots
                L, R = np.linalg.norm(vec[:, [0, 2]], axis=1)*100
                q = d.qpos[m.jnt_qposadr[slides]]
                sl, sr = 1000*(q - m.jnt_range[slides, 0])
                el, er = 1000*(m.jnt_range[slides, 1] - q)
                angles = d.qpos[m.jnt_qposadr[passive]]
                gaps = np.rad2deg(np.minimum(angles-m.jnt_range[passive,0], m.jnt_range[passive,1]-angles))
                idx = int(np.argmin(gaps))
                stats = (f'SCUT V14_2 | suspended\nTarget: {100*target:.1f} cm\nActual L / R: {L:.2f} / {R:.2f} cm\n'
                         f'Spring to compressed end L / R: {sl:.1f} / {sr:.1f} mm\nSpring to extended end L / R: {el:.1f} / {er:.1f} mm\n'
                         f'Nearest hinge: {m.joint(passive[idx]).name}  {gaps[idx]:+.2f} deg')
            view.set_texts((None, mujoco.mjtGridPos.mjGRID_TOPLEFT, stats, ''))
            view.sync()
            time.sleep(max(0, 5*m.opt.timestep-(time.perf_counter()-start)))


if __name__ == '__main__':
    main()
