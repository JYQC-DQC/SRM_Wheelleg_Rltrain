"""Training-only diagnostics for the first landing of an air-reset episode.

No reward, termination, curriculum, or actor input depends on these buffers.
"""

import torch


class FirstLanding:
    def __init__(self, count: int, body_names: list[str], wheels: list[int], settings: dict, device: str):
        self.settings, self.body_names, self.wheels = settings, body_names, wheels
        self.nonwheel = torch.ones(len(body_names), dtype=torch.bool, device=device)
        self.nonwheel[wheels] = False
        self.active = torch.zeros(count, dtype=torch.bool, device=device)
        self.start_tick = torch.zeros(count, dtype=torch.long, device=device)
        self.last_tick = torch.full_like(self.start_tick, -1)
        self.first_time = torch.full((count,), -1.0, device=device)
        self.wheel_time = torch.full((count, 2), -1.0, device=device)
        self.first_bodies = torch.zeros(count, len(body_names), dtype=torch.bool, device=device)
        self.collided = self.active.clone()
        self.invalid = self.active.clone()
        self.latest_wheels = torch.zeros(count, 2, dtype=torch.bool, device=device)
        self.step_both = self.active.clone()
        self.step_nonwheel = self.active.clone()
        self.stable_time = torch.zeros(count, device=device)
        self.recovery_time = torch.full_like(self.stable_time, -1)
        self.wheel_peak = torch.zeros(count, 2, device=device)
        self.nonwheel_peak = torch.zeros(count, device=device)
        self.torque_peak = torch.zeros(count, device=device)
        self.tilt_peak = torch.zeros(count, device=device)
        self.stats = {}

    def _add(self, name: str, value: torch.Tensor) -> None:
        if name not in self.stats:
            self.stats[name] = value.detach().clone()
        else:
            self.stats[name] += value.detach()

    def reset(self, ids: torch.Tensor, air: torch.Tensor, tick: int) -> None:
        # Explicit external reset is an interrupted event, never a silent disappearance.
        interrupted = torch.zeros_like(self.active)
        interrupted[ids] = self.active[ids]
        self._finish(interrupted, interrupted)
        self.active[ids] = air
        self.start_tick[ids] = tick
        self.last_tick[ids] = tick
        for value in (self.first_time, self.wheel_time, self.recovery_time):
            value[ids] = -1
        for value in (
            self.first_bodies,
            self.collided,
            self.invalid,
            self.latest_wheels,
            self.step_both,
            self.step_nonwheel,
            self.stable_time,
            self.wheel_peak,
            self.nonwheel_peak,
            self.torque_peak,
            self.tilt_peak,
        ):
            value[ids] = 0
        self._add("air_births", air.sum())

    def begin_step(self) -> None:
        self.step_both.copy_(self.latest_wheels.all(-1))
        self.step_nonwheel.zero_()

    def sample_contacts(self, tick: int, physics_dt: float, forces: torch.Tensor, torque: torch.Tensor) -> None:
        # env calls before the next physics step and once after the last substep. Deduplicate ticks.
        selected = self.active & (tick > self.last_tick) & (tick > self.start_tick)
        self.last_tick[selected] = tick
        age = (tick - self.start_tick) * physics_dt
        finite = torch.isfinite(forces).all(-1) & torch.isfinite(torque).all(-1)
        self.invalid |= selected & ~finite
        selected &= finite
        contact = forces > self.settings["first_contact_force_n"]
        first = selected & (self.first_time < 0) & contact.any(-1)
        self.first_time[first] = age[first]
        self.first_bodies[first] = contact[first]
        wheel_touch = contact[:, self.wheels]
        new_wheel = selected[:, None] & wheel_touch & (self.wheel_time < 0)
        self.wheel_time = torch.where(new_wheel, age[:, None], self.wheel_time)
        bad = contact[:, self.nonwheel].any(-1)
        self.collided |= selected & bad
        self.step_nonwheel |= selected & bad
        wheels = forces[:, self.wheels] > self.settings["support_force_n"]
        self.latest_wheels[selected] = wheels[selected]
        self.step_both &= ~selected | wheels.all(-1)
        self.wheel_peak = torch.where(
            selected[:, None], torch.maximum(self.wheel_peak, forces[:, self.wheels]), self.wheel_peak
        )
        self.nonwheel_peak = torch.where(
            selected, torch.maximum(self.nonwheel_peak, forces[:, self.nonwheel].amax(-1)), self.nonwheel_peak
        )
        self.torque_peak = torch.where(
            selected, torch.maximum(self.torque_peak, torque.abs().amax(-1)), self.torque_peak
        )

    def update(
        self,
        tick: int,
        physics_dt: float,
        dt: float,
        state: dict,
        terminated: torch.Tensor,
        timeout: torch.Tensor,
        numerical: torch.Tensor,
    ) -> None:
        done = terminated | timeout
        age = (tick - self.start_tick) * physics_dt
        contacted = self.first_time >= 0
        tilt = torch.stack((state["roll"].abs(), state["pitch"].abs()), -1).amax(-1)
        finite = torch.isfinite(tilt) & torch.isfinite(state["height_error"])
        finite &= torch.isfinite(state["angular_velocity"]).all(-1) & torch.isfinite(state["velocity_w"]).all(-1)
        self.invalid |= self.active & (~finite | numerical)
        self.tilt_peak = torch.where(
            self.active & contacted & finite, torch.maximum(self.tilt_peak, tilt), self.tilt_peak
        )
        p = self.settings
        stable = self.active & contacted & finite & self.step_both & ~self.step_nonwheel & ~done & ~self.invalid
        stable &= tilt <= p["tilt_rad"]
        stable &= state["angular_velocity"][:, :2].abs().amax(-1) <= p["angular_xy_rad_s"]
        stable &= state["velocity_w"][:, 2].abs() <= p["vertical_velocity_m_s"]
        stable &= state["height_error"].abs() <= p["height_error_m"]
        self.stable_time = torch.where(stable, self.stable_time + dt, 0.0)
        held = self.stable_time >= p["stable_duration_s"]
        first_recovery = self.active & held & (self.recovery_time < 0)
        # Time to completion of the first continuous stable interval, relative to first contact.
        self.recovery_time[first_recovery] = (age - self.first_time)[first_recovery]
        no_touch_deadline = ~contacted & (age >= p["first_contact_timeout_s"])
        window_end = contacted & (age - self.first_time >= p["observation_window_s"])
        finished = self.active & (done | self.invalid | no_touch_deadline | window_end)
        self._add("early_timeout", (finished & timeout & ~terminated & ~self.invalid).sum())
        self._add("physical_termination", (finished & terminated & ~self.invalid).sum())
        self._finish(finished, done | self.invalid, held)

    def _finish(self, mask: torch.Tensor, interrupted: torch.Tensor, held: torch.Tensor | None = None) -> None:
        if not bool(mask.any()):
            return
        if held is None:
            held = torch.zeros_like(mask)
        contacted = self.first_time >= 0
        both_touched = (self.wheel_time >= 0).all(-1)
        gap = (self.wheel_time[:, 0] - self.wheel_time[:, 1]).abs()
        symmetric = both_touched & (gap <= self.settings["touchdown_difference_s"])
        stable = held & ~interrupted
        outcomes = {
            "aborted": interrupted,
            "no_contact": ~interrupted & ~contacted,
            "unstable": ~interrupted & contacted & ~stable,
            "collision_recovered": stable & self.collided,
            "asymmetric_recovered": stable & ~self.collided & ~symmetric,
            "clean_success": stable & ~self.collided & symmetric,
        }
        self._add("resolved", mask.sum())
        for name, condition in outcomes.items():
            self._add(name, (mask & condition).sum())
        for name, condition in {
            "nonwheel_contact": self.collided,
            "both_wheels_touched": both_touched,
            "recovered_once": self.recovery_time >= 0,
            "numerical_invalid": self.invalid,
        }.items():
            self._add(name, (mask & condition).sum())
        self._add("first_contact_events", (mask & contacted).sum())
        for i, name in enumerate(self.body_names):
            self._add(f"first_body/{name}", (mask & self.first_bodies[:, i]).sum())
        for name, values, valid in (
            ("touchdown_difference_s", gap, both_touched),
            ("recovery_s", self.recovery_time, self.recovery_time >= 0),
            ("first_contact_s", self.first_time, contacted),
            ("left_wheel_peak_n", self.wheel_peak[:, 0], contacted),
            ("right_wheel_peak_n", self.wheel_peak[:, 1], contacted),
            ("nonwheel_peak_n", self.nonwheel_peak, contacted),
            ("hip_torque_peak_nm", self.torque_peak, contacted),
            ("postcontact_tilt_peak_rad", self.tilt_peak, contacted),
        ):
            use = mask & valid
            self._add(f"{name}/sum", torch.where(use, values, 0.0).sum())
            self._add(f"{name}/count", use.sum())
            maximum = torch.where(use, values, 0.0).amax()
            key = f"{name}/max"
            self.stats[key] = torch.maximum(self.stats[key], maximum) if key in self.stats else maximum.clone()
        self.active[mask] = False

    def take_log(self) -> dict[str, float]:
        values = {key: float(value.item()) for key, value in self.stats.items()}
        self.stats = {}
        result = {f"Landing/{k}": v for k, v in values.items() if not k.endswith(("/sum", "/max"))}
        result["Landing/pending"] = float(self.active.sum().item())
        resolved = values.get("resolved", 0.0)
        if resolved:
            result["Landing/clean_success_rate"] = values["clean_success"] / resolved
            result["Landing/failure_rate"] = 1 - values["clean_success"] / resolved
            result["Landing/nonwheel_contact_rate"] = values["nonwheel_contact"] / resolved
            result["Landing/collision_recovered_rate"] = values["collision_recovered"] / resolved
        for key, value in values.items():
            if key.endswith("/max") and values[key.removesuffix("/max") + "/count"]:
                result["Landing/" + key] = value
            if key.endswith("/sum") and values[key.removesuffix("/sum") + "/count"]:
                result["Landing/" + key.removesuffix("/sum") + "/mean"] = (
                    value / values[key.removesuffix("/sum") + "/count"]
                )
        return result
