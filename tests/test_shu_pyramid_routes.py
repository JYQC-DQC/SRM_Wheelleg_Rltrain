from types import SimpleNamespace

import pytest
import torch
from test_shu_mixed_variants import settings

from wheelleg.shu_terrain import MixedTerrainRuntime, mixed_columns


def setup_routes(count, *, reverse=0.1):
    cfg = settings()
    cfg["tile_size_m"] = (12.0, 8.0)  # intentionally non-square
    cfg["route"]["reverse_descent_share_of_stairs"] = reverse
    mix = MixedTerrainRuntime(cfg, count, "cpu")
    columns = mixed_columns(cfg)
    origins = torch.zeros(3, len(columns), 3)
    origins[..., 0] = torch.arange(3)[:, None] * 12.0
    origins[..., 1] = torch.arange(len(columns)) * 8.0
    t = SimpleNamespace(
        terrain_origins=origins,
        terrain_levels=torch.zeros(count, dtype=torch.long),
        terrain_types=torch.zeros(count, dtype=torch.long),
        env_origins=torch.zeros(count, 3),
    )
    return mix, t, columns


def test_route_shares_are_of_all_stairs_and_reverse_starts_on_raised_deck():
    torch.manual_seed(19)
    n = 30000
    mix, t, columns = setup_routes(n)
    ids = torch.arange(n)
    no = ids < 0
    mix.reset(t, ids, no, no, evaluation=False)
    stair = mix.traverse
    raised, pyramid, lip = (
        torch.tensor(mask)[t.terrain_types]
        for mask in (
            [name.endswith("_up") for name, _, _ in columns],
            [p for _, _, p in columns],
            [lip for _, lip, _ in columns],
        )
    )
    reverse = mix.reverse_descent
    assert reverse.shape == (n,) and reverse.dtype == torch.bool
    assert torch.equal(stair, pyramid)
    assert not (reverse & (~stair | ~raised)).any()
    assert stair.float().mean().item() == pytest.approx(0.4, abs=0.015)
    for mode, share in [
        (~raised & pyramid, 0.45),
        (raised & pyramid & ~reverse, 0.45),
        (reverse, 0.1),
    ]:
        assert mode[stair].float().mean().item() == pytest.approx(share, abs=0.015)
        assert lip[mode].float().mean().item() == pytest.approx(0.5, abs=0.05)

    mix.stair_rows.levels[ids[n // 2 :]] = mix.stair_rows.rows - 1
    mix.reset(t, ids, no, no, evaluation=False)
    for cohort in (ids[: n // 2], ids[n // 2 :]):
        assert set(t.terrain_types[cohort][mix.traverse[cohort]].tolist()) == {4, 5, 6, 7}
    assert set(t.terrain_types[mix.reverse_descent].tolist()) == {
        i for i, (name, _, p) in enumerate(columns) if p and name == "pyramid_up"
    }


@pytest.mark.parametrize("name,reverse", [("pyramid_down", False), ("pyramid_up", False), ("pyramid_up", True)])
@pytest.mark.parametrize("lip", [False, True])
@pytest.mark.parametrize("exit_face", ["forward", "far_slant", "side", "corner", "back"])
def test_center_to_outside_requires_safe_floor_landing_on_any_face(name, reverse, lip, exit_face):
    mix, t, columns = setup_routes(1)
    t.terrain_types[:] = columns.index((name, lip, True))
    t.env_origins[:] = t.terrain_origins[1, t.terrain_types]
    mix.traverse[:] = True
    mix.reverse_descent[:] = reverse
    previous = t.env_origins.clone()

    def visit(x, y, *, grounded=True, vx=1.0, failed=False):
        nonlocal previous
        pos = t.env_origins + torch.tensor([x, y, 0.0])
        mix.step(t, previous, pos, torch.tensor([vx]), torch.tensor([failed]), torch.tensor([[grounded, False]]))
        previous = pos

    visit(0, 0)
    assert mix.reward_active.item() and mix.route_open.item()
    assert not (mix.crossed | mix.reverse_completed).any()
    outer = 2.4 if lip else 2.6
    visit(outer + 0.19, 0)  # above the apron, but not yet clear of the obstruction
    assert not (mix.crossed | mix.reverse_completed).any()

    # The far slant has no narrow Y cap; the corner clears by its geometric
    # distance to the square, even though neither axis alone clears by 0.20 m.
    x, y = {
        "forward": (outer + 0.21, 0.0),
        "far_slant": (4.0, 3.5),
        "side": (1.0, -outer - 0.21),
        "corner": (outer + 0.15, outer + 0.15),
        "back": (-outer - 0.21, 1.0),
    }[exit_face]
    visit(x, y, grounded=False)
    assert mix.reward_active.item() and mix.route_open.item()
    assert not (mix.crossed | mix.reverse_completed).any()
    visit(x, y)  # landing; no second line crossing needed
    assert mix.crossed.item() == (not reverse)
    assert mix.reverse_completed.item() == reverse
    assert mix.route_open.item() == (not reverse)
    assert not mix.reward_active.any()
    visit(0, 0)  # both outcomes latch and never resume scoring within this episode
    assert mix.crossed.item() == (not reverse)
    assert mix.reverse_completed.item() == reverse
    assert not mix.reward_active.any()


def test_apron_rejects_stationary_birth_neighbor_reentry_and_failure():
    mix, t, columns = setup_routes(1)
    t.terrain_types[:] = columns.index(("pyramid_up", True, True))
    t.env_origins[:] = t.terrain_origins[1, t.terrain_types]
    mix.traverse[:] = True
    apron = t.env_origins + torch.tensor([3.0, 0.0, 0.0])
    near_riser = t.env_origins + torch.tensor([2.59, 0.0, 0.0])
    near_border = t.env_origins + torch.tensor([3.0, 3.9, 0.0])
    neighbor = t.env_origins + torch.tensor([3.0, 4.1, 0.0])
    center = t.env_origins.clone()
    speed, no = torch.ones(1), torch.zeros(1, dtype=torch.bool)
    wheels = torch.ones(1, 2, dtype=torch.bool)
    with pytest.raises(ValueError, match="wheel_contact"):
        mix.step(t, center, apron, speed, no)
    for prev, pos, failed in (
        (apron, apron, no),  # no outward entry
        (center, near_border, no),  # too close to neighboring tile
        (near_border, neighbor, no),
        (neighbor, apron, no),  # re-entry is not an outward transition
        (apron, near_riser, no),
        (near_riser, apron, no),  # an apron-only loop after re-entry is not a traversal
        (center, apron, ~no),  # support on a terminating step cannot certify completion
    ):
        mix.step(t, prev, pos, speed, failed, wheels)
        assert not mix.crossed.any() and mix.route_open.item()
    # On this same route valid geometry still counts, independently of command projection.
    mix.step(t, center, apron, -speed, no, wheels)
    assert mix.crossed.item() and mix.route_open.item() and not mix.reward_active.any()


def test_only_landed_reverse_promotes_short_of_fudan_displacement():
    mix, t, columns = setup_routes(6)
    ids = torch.arange(6)
    no = ids < 0
    mix.reset(t, ids, no, no, evaluation=True)
    t.terrain_types[:] = columns.index(("pyramid_up", True, True))
    t.terrain_levels[:] = mix.stair_rows.levels[:] = 1
    t.env_origins[:] = t.terrain_origins[1, t.terrain_types]
    mix.traverse[:] = True
    mix.reverse_descent[:] = ids >= 3
    start = t.env_origins.clone()
    apron = start + torch.tensor([3.0, 0.0, 0.0])
    apron[-1] = start[-1]  # never left the center
    speed = torch.ones(6)
    wheels = torch.ones(6, 2, dtype=torch.bool)
    mix.step(t, start, apron, speed, no, wheels)
    assert mix.crossed.tolist() == [True, True, True, False, False, False]
    assert mix.reverse_completed.tolist() == [False, False, False, True, True, False]
    assert mix.route_open.tolist() == [True, True, True, False, False, True]
    assert mix.reward_active.tolist() == [False, False, False, False, False, True]

    final = apron.clone()
    final[1, :2] = start[1, :2] + torch.tensor([6.0, 0.0])  # strict >6 m, not >=
    final[2, :2] = start[2, :2] + torch.tensor([5.1, 3.3])  # continued forward drive, in-tile slant >6 m
    mix.step(t, apron, final, speed, no, wheels)
    assert mix.route_open[:3].all() and not mix.reward_active[:3].any()
    failed = no.clone()
    failed[4] = True  # a later failure forfeits the reverse extra promotion
    mix.reset(t, ids, ~no, failed, evaluation=False, final_xy=final[:, :2], tracking_fraction=torch.full((6,), 0.5))
    assert not (mix.crossed | mix.reverse_completed | mix.reward_active).any()
    assert mix.stair_rows.levels.tolist() == [1, 1, 2, 2, 1, 1]
