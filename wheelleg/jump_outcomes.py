"""One final verdict per jump request, with nonexclusive failure reasons."""

import torch


class JumpOutcomeTracker:
    fields = (
        "events",
        "successes",
        "event_failures",
        "height_failures",
        "speed_failures",
        "heading_failures",
        "handoff_failures",
    )

    def __init__(self, count: int, device: str):
        self.recorded = torch.zeros(count, dtype=torch.bool, device=device)
        self.counts = torch.zeros((2, len(self.fields)), dtype=torch.long, device=device)

    def record(self, ids, moving, checks, event_failed, handoff_failed):
        fresh = ~self.recorded[ids]
        ids, moving, checks = ids[fresh], moving[fresh], checks[fresh]
        event_failed, handoff_failed = event_failed[fresh], handoff_failed[fresh]
        success = checks.all(-1) & ~event_failed & ~handoff_failed
        # A pre-landing failure has no completed height/speed/heading acceptance or handoff observation.
        assessed = ~event_failed
        values = torch.stack(
            (
                torch.ones_like(success),
                success,
                event_failed,
                assessed & ~checks[:, 0],
                assessed & ~checks[:, 1],
                assessed & ~checks[:, 2],
                assessed & handoff_failed,
            ),
            dim=-1,
        )
        self.counts.index_add_(0, moving.long(), values.long())
        self.recorded[ids] = True
        return ids, success

    def reset(self, ids):
        self.recorded[ids] = False
