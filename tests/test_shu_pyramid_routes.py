from types import SimpleNamespace

import pytest
import torch
from test_shu_mixed_variants import settings

from wheelleg.shu_terrain import MIXED_PROFILES, MixedTerrainRuntime, mixed_columns


def setup_routes(count, *, share=1.0, reverse=0.1):
    cfg = settings()
    cfg["tile_size_m"] = (12.0, 8.0)  # intentionally non-square
    cfg["pyramid"] = {"share_of_stairs": share}
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


@pytest.mark.parametrize("pyramid_share", [0.5, 1.0])
def test_route_shares_are_of_all_stairs_not_just_inverted_towers(pyramid_share):
    torch.manual_seed(19)
    n = 30000
    mix, t, columns = setup_routes(n, share=pyramid_share)
    ids = torch.arange(n)
    no = ids < 0
    mix.reset(t, ids, no, no, evaluation=False)
    stair = mix.traverse
    up, pyramid, lip = (
        torch.tensor(mask)[t.terrain_types]
        for mask in (
            [name.endswith("_up") for name, _, _ in columns],
            [p for _, _, p in columns],
            [lip for _, lip, _ in columns],
        )
    )
    reverse = mix.reverse_descent
    assert reverse.shape == (n,) and reverse.dtype == torch.bool
    assert not (reverse & (~stair | up | ~pyramid)).any()
    assert stair.float().mean().item() == pytest.approx(0.4, abs=0.015)
    for mode, share in [
        (up & pyramid, (pyramid_share - 0.1) / 2),
        (~up & pyramid & ~reverse, (pyramid_share - 0.1) / 2),
        (reverse, 0.1),
    ]:
        assert mode[stair].float().mean().item() == pytest.approx(share, abs=0.015)
        assert lip[mode].float().mean().item() == pytest.approx(0.5, abs=0.05)
        double = torch.tensor([name.startswith("double") for name, _, _ in columns])[t.terrain_types]
        assert double[mode].float().mean().item() == pytest.approx(0.7, abs=0.05)

    mix.stair_rows.top_cleared[ids[n // 2 :]] = True
    mix.reset(t, ids, no, no, evaluation=False)
    triple = mix.column_profiles[t.terrain_types] >= MIXED_PROFILES.index("triple_up")
    assert not triple[: n // 2].any() and triple[n // 2 :].any()
    assert set(t.terrain_types[mix.reverse_descent].tolist()) == {
        i for i, (name, _, p) in enumerate(columns) if p and name.endswith("_down")
    }


@pytest.mark.parametrize(
    "name,lip", [("double_up", False), ("double_up", True), ("double_down", False), ("double_down", True)]
)
def test_grounded_platforms_in_order_not_x_lines_or_side_boundaries(name, lip):
    mix, t, columns = setup_routes(1)
    t.terrain_types[:] = columns.index((name, lip, True))
    t.env_origins[:] = t.terrain_origins[1, t.terrain_types]
    mix.traverse[:] = True
    previous = t.env_origins.clone()

    def visit(x, y, *, grounded=True, vx=1.0, failed=False):
        nonlocal previous
        pos = t.env_origins + torch.tensor([x, y, 0.0])
        mix.step(t, previous, pos, torch.tensor([vx]), torch.tensor([failed]), torch.tensor([[grounded, False]]))
        previous = pos

    # Center x=5 relative to spawn. Run around the side, far beyond the old lane.
    visit(5, 5)
    visit(10, 0)
    assert mix.route_open.item() and not mix.reached_center.item()
    visit(1.45, 0)  # inside the first X edge, short of the safe central platform
    assert not mix.reached_center.item()
    visit(5, 1.55)  # inside the outer ring, but not safely inside the innermost tread
    assert not mix.reached_center.item()
    center_y = 1.40 if lip and name.endswith("_up") else 1.50
    visit(5, center_y + 0.01)
    assert not mix.reached_center.item()
    visit(5, center_y - 0.01, grounded=False)
    visit(5, center_y - 0.01, failed=True)
    assert not mix.reached_center.item()
    visit(5, center_y - 0.01, vx=-0.3)  # entry from +Y, independent of projected command
    assert mix.reached_center.item() and not mix.reward_active.item() and mix.route_open.item()

    # Left outer deck, side deck, far corner, next tile: none is the opposite face's exit.
    for x, y in [(0, 0), (6, 3), (10, 2.1), (12, 0)]:
        visit(x, y)
        assert not mix.crossed.item() and mix.route_open.item()
    far_x = 9.30 if lip and name.endswith("_down") else 9.20
    visit(far_x - 0.01, 0)
    visit(far_x + 0.01, 0, grounded=False)
    visit(far_x + 0.01, 0, failed=True)
    assert not mix.crossed.item()
    visit(far_x + 0.01, 0)  # land in the accepted area; no second line crossing needed
    assert mix.crossed.item() and not mix.route_open.item()


def test_half_route_stops_only_on_central_low_deck_never_counts_full_or_prerequisite():
    mix, t, columns = setup_routes(2)
    ids = torch.arange(2)
    no = ids < 0
    mix.reset(t, ids, no, no, evaluation=True)
    t.terrain_types[:] = columns.index(("double_down", True, True))
    t.terrain_levels[:] = 1  # actually at the prerequisite's configured row
    t.env_origins[:] = t.terrain_origins[1, t.terrain_types]
    mix.traverse[:] = True
    mix.reverse_descent[:] = torch.tensor([True, False])
    start = t.env_origins
    center = start + torch.tensor([5, 0, 0])
    end = start + torch.tensor([10, 0, 0])
    speed = torch.ones(2)
    wheels = torch.ones(2, 2, dtype=torch.bool)
    with pytest.raises(ValueError, match="wheel_contact"):
        mix.step(t, start, center, speed, no)
    mix.step(t, start, center, speed, no, ~wheels)
    assert mix.route_open.all()
    mix.step(t, center, center, speed, no, wheels)
    assert mix.route_open.tolist() == [False, True] and not mix.crossed.any()
    mix.step(t, center, end, speed, no, wheels)
    assert mix.crossed.tolist() == [False, True] and not mix.route_open.any()
    mix.stair_rows.levels[:] = 0
    mix.assigned[:] = True
    mix.reset(t, ids[:1], ~no, no, evaluation=False, final_xy=center[:, :2], tracking_fraction=torch.zeros(2))
    assert mix.reached_center.tolist() == [False, True] and mix.crossed.tolist() == [False, True]
    mix.reset(t, ids[1:], ~no, no, evaluation=False, final_xy=end[:, :2], tracking_fraction=torch.zeros(2))
    assert not mix.reached_center.any() and not mix.crossed.any()
    assert mix.stair_rows.levels.tolist() == [1, 1]
