import json
import struct
import zlib
from pathlib import Path

import mujoco
import numpy as np

folder = Path(__file__).resolve().parent
model = mujoco.MjModel.from_xml_path(str(folder / "scene.xml"))
data = mujoco.MjData(model)
mujoco.mj_forward(model, data)


def png(path, rgb):
    height, width, _ = rgb.shape
    def chunk(kind, payload):
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload))
    raw = b"".join(b"\x00" + row.tobytes() for row in rgb)
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
                     + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


with mujoco.Renderer(model, height=1000, width=1600) as renderer:
    camera = mujoco.MjvCamera()
    camera.lookat[:] = [12.5, 4.5, 0]
    camera.distance = 41
    camera.azimuth = 115
    camera.elevation = -62
    renderer.update_scene(data, camera)
    png(folder / "overview.png", renderer.render())
    camera.lookat[:] = [-3.8, 0, 0.4]
    camera.distance = 2.7
    camera.azimuth = 135
    camera.elevation = -22
    renderer.update_scene(data, camera)
    png(folder / "robot.png", renderer.render())

for _ in range(1000):
    mujoco.mj_step(model, data)
report = {
    "mujoco_version": mujoco.__version__, "bodies": model.nbody, "geoms": model.ngeom,
    "heightfields": model.nhfield, "actuators": model.nu,
    "physics_timestep_s": model.opt.timestep, "simulated_seconds": data.time,
    "finite_state": bool(np.isfinite(data.qpos).all() and np.isfinite(data.qvel).all()),
    "warning_counts": data.warning.number.tolist(),
    "controller": "none; passive fall only, not balance or policy validation",
}
(folder / "validation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report))
