import torch


class LandingGuidance:
    """Event-local geometry guidance; no actor inputs or acceptance rules change."""

    def __init__(self, cfg: dict, count: int, device: str):
        self.cfg = cfg
        self.flat = torch.zeros((count, 2), device=device)
        self.touch_length = torch.zeros_like(self.flat)
        self.contact_seen = torch.zeros_like(self.flat, dtype=torch.bool)
        self.touched = torch.zeros(count, dtype=torch.bool, device=device)
        self.stopped = torch.zeros_like(self.touched)
        self.u0 = torch.zeros(count, device=device)
        self.stop_error = torch.zeros_like(self.u0)
        self.path_cost = torch.zeros_like(self.u0)
        self.retained = torch.zeros_like(self.u0)
        self.window = torch.zeros((count, cfg["retention_frames"]), device=device)
        self.stop_quality = torch.zeros_like(self.u0)

    def reset(self, ids: torch.Tensor) -> None:
        for value in (
            self.flat,
            self.touch_length,
            self.contact_seen,
            self.touched,
            self.stopped,
            self.u0,
            self.stop_error,
            self.path_cost,
            self.retained,
            self.window,
            self.stop_quality,
        ):
            value[ids] = 0

    def begin(self, ids: torch.Tensor, length: torch.Tensor) -> None:
        self.reset(ids)
        # Frozen Landing's actual stance under the current height request, not body height.
        self.flat[ids] = length[ids]

    def update(self, dt, active, took_off, preparing, contact, length, vz, last_air_vz):
        cfg = self.cfg
        self.path_cost.zero_()
        air = active & took_off & ~self.touched & ~contact.any(-1)
        quality = (
            ((length - cfg["tuck_length_m"]) / (cfg["prepare_length_m"] - cfg["tuck_length_m"])).clamp(0, 1).amin(-1)
        )
        sample = air & preparing
        self.window[sample] = torch.cat((self.window[sample, 1:], quality[sample, None]), dim=-1)
        touch = active & took_off & ~self.touched & contact.any(-1)
        self.u0[touch] = (-last_air_vz[touch]).clamp_min(0)
        self.retained[touch] = self.window[touch].amin(-1)
        self.touched |= touch
        first = active[:, None] & self.touched[:, None] & contact & ~self.contact_seen
        self.touch_length[first] = length[first]
        self.contact_seen |= first
        usable = self.contact_seen & (self.touch_length > self.flat)
        falling = active & self.touched & ~self.stopped & (self.u0 >= cfg["min_touch_speed_m_s"])
        ratio = ((-vz).clamp_min(0) / self.u0.clamp_min(cfg["min_touch_speed_m_s"])).clamp(0, 1)
        reference = self.flat + (self.touch_length - self.flat).clamp_min(0) * ratio[:, None].square()
        error = (length - reference).abs() / cfg["length_sigma_m"]
        huber = torch.where(error <= 1, 0.5 * error.square(), error - 0.5)
        self.path_cost.copy_((huber * usable * contact).mean(-1) * falling * dt)
        stop = falling & (vz >= -cfg["stop_speed_m_s"])
        self.stop_error[stop] = (length[stop] - self.flat[stop]).abs().amax(-1)
        # All feet must support the first arrest; a bounce through zero cannot earn this bonus later.
        valid = stop & contact.all(-1) & usable.all(-1)
        self.stop_quality[valid] = torch.exp(-0.5 * (self.stop_error[valid] / cfg["length_sigma_m"]).square())
        self.stopped |= stop
