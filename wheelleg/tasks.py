"""Task selection is usable before importing Torch or starting Isaac Sim."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Task:
    policy: str
    stage: str
    initialize_from: str | None


TASKS = {
    "p1-flat": Task("p1", "flat", None),
    "p1-landing": Task("p1", "landing", "p1-flat"),
    "p1-stairs": Task("p1", "stairs", "p1-landing"),
    "p1-recovery": Task("p1", "recovery", "p1-stairs"),
    "p2-spin": Task("p2", "spin", "p1-flat"),
    "p3-jump": Task("p3", "jump", "p1-landing"),
    "p3-tunnel": Task("p3", "tunnel", "p3-jump"),
}
