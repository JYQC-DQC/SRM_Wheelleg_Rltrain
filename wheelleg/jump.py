import torch

from .commands import uniform


class JumpEvent:
    """Contact-driven phases; apex/landing pulses can only occur once per event."""

    def __init__(self, settings: dict, count: int, device: str):
        self.settings, self.device = settings, device
        self.active = torch.zeros(count, dtype=torch.bool, device=device)
        self.remaining = torch.zeros(count, dtype=torch.long, device=device)
        self.elapsed = torch.zeros(count, device=device)
        self.next_trigger = torch.zeros_like(self.elapsed)
        self.height = torch.zeros_like(self.elapsed)
        self.start_z = torch.zeros_like(self.elapsed)
        self.apex_z = torch.zeros_like(self.elapsed)
        self.air_time = torch.zeros_like(self.elapsed)
        self.stable_time = torch.zeros_like(self.elapsed)
        self.touchdown_time = torch.full((count, 2), -1.0, device=device)
        self.took_off = self.active.clone()
        self.landed = self.active.clone()
        self.apex_paid = self.active.clone()
        self.landing_paid = self.active.clone()
        self.invalid = self.active.clone()
        self.apex_pulse = self.active.clone()
        self.landing_pulse = self.active.clone()
        self.touchdown_pulse = self.active.clone()
        self.finished = self.active.clone()
        self.first_touch = self.active.clone()

    def reset(self, ids: torch.Tensor) -> None:
        for value in (
            self.active,
            self.took_off,
            self.landed,
            self.apex_paid,
            self.landing_paid,
            self.invalid,
            self.apex_pulse,
            self.landing_pulse,
            self.touchdown_pulse,
            self.finished,
            self.first_touch,
        ):
            value[ids] = False
        for value in (self.elapsed, self.height, self.air_time, self.stable_time, self.start_z, self.apex_z):
            value[ids] = 0
        self.touchdown_time[ids] = -1
        self.remaining[ids] = torch.multinomial(
            self.elapsed.new_tensor(self.settings["jump_count_probabilities"]), len(ids), replacement=True
        )
        self.next_trigger[ids] = uniform(self.settings["first_trigger_range_s"], (len(ids),), self.device)

    def trigger(
        self,
        age: torch.Tensor,
        z: torch.Tensor,
        allowed: torch.Tensor,
        target_height: torch.Tensor | None = None,
        *,
        require_trigger_time: bool = True,
    ) -> None:
        start = ~self.active & (self.remaining > 0) & allowed
        if require_trigger_time:
            start &= age >= self.next_trigger
        ids = start.nonzero().flatten()
        if not len(ids):
            return
        self.active[ids] = True
        self.remaining[ids] -= 1
        for value in (self.took_off, self.landed, self.apex_paid, self.landing_paid, self.invalid):
            value[ids] = False
        self.first_touch[ids] = False
        self.elapsed[ids] = 0
        self.air_time[ids] = 0
        self.stable_time[ids] = 0
        self.touchdown_time[ids] = -1
        self.height[ids] = (
            uniform(self.settings["height_range_m"], (len(ids),), self.device)
            if target_height is None
            else target_height[ids]
        )
        self.start_z[ids] = z[ids]
        self.apex_z[ids] = z[ids]

    def update(
        self,
        dt: float,
        age: torch.Tensor,
        z: torch.Tensor,
        vz: torch.Tensor,
        contact: torch.Tensor,
        stable: torch.Tensor,
        valid_landing: torch.Tensor,
        obstacle_contact: torch.Tensor,
    ) -> None:
        self.apex_pulse.zero_()
        self.landing_pulse.zero_()
        self.touchdown_pulse.zero_()
        self.finished.zero_()
        self.elapsed += dt * self.active
        no_contact = ~contact.any(-1)
        can_takeoff = self.active & ~self.landed & (self.elapsed >= self.settings["crouch_duration_s"])
        self.took_off |= can_takeoff & no_contact
        flight = self.active & self.took_off & ~self.landed
        self.air_time += dt * flight * no_contact
        self.apex_z = torch.where(flight, torch.maximum(self.apex_z, z), self.apex_z)
        self.apex_pulse = flight & (vz <= 0) & ~self.apex_paid
        self.apex_paid |= self.apex_pulse
        self.invalid |= self.active & obstacle_contact
        # Invalid first touchdown cannot become success by driving off the roof later.
        new_touch = flight & contact.all(-1) & ~self.first_touch
        self.invalid |= new_touch & ~valid_landing
        self.first_touch |= new_touch
        first_touch = flight[:, None] & contact & (self.touchdown_time < 0)
        self.touchdown_time = torch.where(first_touch, self.elapsed[:, None], self.touchdown_time)
        self.touchdown_pulse = flight & contact.all(-1)
        self.landed |= self.touchdown_pulse
        landing_ok = self.active & self.landed & contact.all(-1) & stable & valid_landing & ~self.invalid
        self.stable_time = torch.where(landing_ok, self.stable_time + dt, 0)
        self.landing_pulse = (self.stable_time >= self.settings["landing_stable_s"]) & ~self.landing_paid
        self.landing_paid |= self.landing_pulse
        # Keep the event alive through the required post-landing validation window.
        expired = self.elapsed >= self.settings["event_duration_s"] + self.settings["landing_stable_s"]
        finished = self.active & (expired | self.landing_pulse)
        self.finished = finished
        ids = finished.nonzero().flatten()
        self.next_trigger[ids] = age[ids] + uniform(self.settings["between_events_s"], (len(ids),), self.device)
        self.active[ids] = False

    @property
    def phase(self) -> torch.Tensor:
        return (self.elapsed / self.settings["event_duration_s"]).clamp(0, 1)

    def references(self, vz: torch.Tensor, wheel_clearance: torch.Tensor, gravity: float) -> dict[str, torch.Tensor]:
        flight = self.active & self.took_off & ~self.landed
        # Ballistic time remaining, evaluated only for the descending phase.
        time_to_ground = (vz + torch.sqrt(vz.square() + 2 * gravity * wheel_clearance.clamp_min(0))) / gravity
        prepare = flight & (vz < 0) & (time_to_ground < self.settings["landing_prepare_time_s"])
        return {
            "crouch": self.active & (self.elapsed < self.settings["crouch_duration_s"]),
            "push": self.active & ~self.took_off & (self.elapsed >= self.settings["crouch_duration_s"]),
            "flight": flight,
            "prepare": prepare,
            "tuck": flight & ~prepare,
            "takeoff_velocity": torch.sqrt(2 * gravity * self.height),
        }


def tunnel_landing(
    wheel_position: torch.Tensor,
    wheel_radius: float,
    body_position: torch.Tensor,
    beam_end_x: torch.Tensor,
    ground_z: torch.Tensor,
    margin: float,
    ground_tolerance: float,
) -> torch.Tensor:
    wheels_beyond = (wheel_position[:, :, 0] - wheel_radius > beam_end_x[:, None] + margin).all(-1)
    body_beyond = (body_position[:, :, 0] > beam_end_x[:, None] + margin).all(-1)
    on_ground = (wheel_position[:, :, 2] - wheel_radius - ground_z[:, None]).abs().amax(-1) < ground_tolerance
    return wheels_beyond & body_beyond & on_ground
