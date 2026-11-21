from math import pi
from types import SimpleNamespace

import pytest
import torch
from test_shu_commands import settings as command_settings
from test_shu_mixed_variants import settings as pyramid_settings
from test_shu_pyramid_routes import setup_routes

from wheelleg.jump import JumpEvent, collision_bounds_w, tunnel_geometry
from wheelleg.shu_commands import ShuCommands
from wheelleg.shu_terrain import (
    LEGACY_PROFILES,
    LEGACY_STAIR_PROFILES,
    MixedTerrainRuntime,
    mixed_columns,
    route_active,
    route_progress_and_stuck,
)


def mixed_settings():
    return dict(
        rows=3,
        route=dict(vx_range_m_s=(0.5, 1.0), clearance_m=0.2),
        tile_size_m=(8.0, 8.0),
        groups=dict(rough=0.1, grid=0.1, slope=0.1, stairs=0.4),
        stair_lip=dict(height_m=0.05, width_m=0.1),
        stair_weights=dict.fromkeys(LEGACY_STAIR_PROFILES, 1.0),
        profiles={
            name: dict(
                row_range=[0, 2],
                command_mode="free" if i < 4 else "traverse",
                exit_distance_m=2.0,
                geometry={"spawn_x_m": 1.0, "first_edge_x_m": 1.5, "step_width_m": 0.5},
            )
            for i, name in enumerate(LEGACY_PROFILES)
        },
    )


def test_pyramid_runtime_progresses_rows_and_restores_state():
    torch.manual_seed(1)
    count = 2000
    cfg = pyramid_settings()
    mix = MixedTerrainRuntime(cfg, count, "cpu")
    columns = torch.arange(len(mixed_columns(cfg)))
    origins = torch.zeros(3, len(columns), 3)
    origins[..., 0] = torch.arange(3).unsqueeze(-1) * 12
    origins[..., 1] = columns * 12
    terrain = SimpleNamespace(
        terrain_origins=origins,
        terrain_levels=torch.zeros(count, dtype=torch.long),
        terrain_types=torch.zeros(count, dtype=torch.long),
        env_origins=torch.zeros(count, 3),
    )
    ids = torch.arange(count)
    no = torch.zeros(count, dtype=torch.bool)
    mix.reset(terrain, ids, no, no, evaluation=False)
    assert set(terrain.terrain_types[mix.traverse].unique().tolist()) == {4, 5, 6, 7}
    assert (terrain.terrain_types == 0).float().mean().item() == pytest.approx(0.30, abs=0.04)
    mix.stair_rows.levels[:5] = torch.tensor([0, 1, 2, 2, 1])
    mix.traverse[:5] = torch.tensor([True, True, True, False, True])
    ran = ~no.clone()
    ran[4] = False
    final = terrain.env_origins[:, :2].clone()
    final[[0, 2, 3], 0] += 7
    mix.reset(terrain, ids[:5], ran, no, evaluation=False, final_xy=final, tracking_fraction=torch.zeros(count))
    assert mix.stair_rows.levels[[0, 1, 3, 4]].tolist() == [1, 0, 2, 1]
    restored = MixedTerrainRuntime(cfg, count, "cpu")
    restored.load_state_dict(mix.state_dict())
    torch.testing.assert_close(restored.stair_rows.levels, mix.stair_rows.levels)
    restored.reset(terrain, ids, no, no, evaluation=False)
    assert torch.equal(terrain.env_origins, origins[terrain.terrain_levels, terrain.terrain_types])
    assert torch.equal(restored.traverse, restored.route_columns[restored.column_profiles[terrain.terrain_types]])
    assert route_active(torch.tensor([False, True, True]), torch.tensor([1.0, 0.0, 1.0])).tolist() == [
        False,
        False,
        True,
    ]


def test_legacy_straight_route_can_return_from_side_excursion_but_not_finish_on_another_tile():
    count = 7
    mix = MixedTerrainRuntime(mixed_settings(), count, "cpu")
    terrain = SimpleNamespace(
        terrain_types=torch.full((count,), 4, dtype=torch.long), env_origins=torch.zeros(count, 3)
    )
    mix.traverse[:6] = True
    start = torch.zeros(count, 3)
    halfway = start + torch.tensor([1.0, 0.0, 0.0])
    halfway[1, 1] = 5.0  # beyond this tile: not a route stop or a latched failure
    no = torch.zeros(count, dtype=torch.bool)
    forward = torch.ones(count)
    mix.step(terrain, start, halfway, forward, no)
    assert torch.equal(mix.route_open, mix.traverse)
    final = start + torch.tensor([2.1, 0.0, 0.0])
    final[4, 1] = 5.0
    forward[2] = 0.0
    forward[5] = -1.0
    failed_at_exit = no.clone()
    failed_at_exit[3] = True
    mix.step(terrain, halfway, final, forward, failed_at_exit)
    assert mix.crossed.tolist() == [True, True, False, False, False, False, False]
    assert mix.reward_active.tolist() == [True, True, False, False, True, False, False]
    assert not mix.reverse_completed.any()
    # Only these legacy fixtures still stop driving when their forward crossing latches.
    mix.step(terrain, final, start, torch.zeros(count), no)
    assert mix.crossed[0] and not mix.route_open[0] and not mix.reward_active.any()


def test_pyramid_forward_and_reverse_keep_signed_drive_after_completion():
    mix, terrain, columns = setup_routes(3)
    ids = torch.arange(3)
    no = ids < 0
    mix.traverse.fill_(True)
    mix.reverse_descent[2] = True
    terrain.terrain_types[:] = torch.tensor(
        [columns.index((name, False, True)) for name in ("pyramid_down", "pyramid_up", "pyramid_up")]
    )
    cmd = ShuCommands.for_mixed(command_settings(), len(ids), "cpu", route=dict(vx_range_m_s=(1.0, 1.0)))
    cmd.reset(ids, route=mix.traverse, reverse_descent=mix.reverse_descent)
    yaw = torch.tensor([0.0, 0.2, pi - 0.2])
    cmd.prepare(yaw, ~no, no, no, ids * 0, route_open=mix.route_open)
    assert cmd.value[:, 0].sign().tolist() == [1, 1, -1]

    center = terrain.env_origins.clone()
    apron = center + torch.tensor([3.0, 0.4, 0.0])
    wheels = torch.ones(3, 2, dtype=torch.bool)
    mix.step(terrain, center, apron, cmd.value[:, 0] * yaw.cos(), no, ~wheels)
    assert mix.route_open.all() and mix.reward_active.all()
    mix.step(terrain, apron, apron, cmd.value[:, 0] * yaw.cos(), no, wheels)
    cmd.prepare(yaw, ~no, no, no, ids * 0 + 1, route_open=mix.route_open)
    assert cmd.value[:, 0].sign().tolist() == [1, 1, -1]
    assert cmd.vx_active.all()
    assert mix.crossed.tolist() == [True, True, False]
    assert mix.reverse_completed.tolist() == [False, False, True]
    assert not mix.reward_active.any()


@pytest.mark.parametrize("exit_distance", [1.2, 6.8])
def test_route_exit_must_be_past_last_riser_and_before_end_of_tile(exit_distance):
    s = mixed_settings()
    s["profiles"]["double_up"]["exit_distance_m"] = exit_distance
    with pytest.raises(ValueError, match="double_up.*route spawn and exit"):
        MixedTerrainRuntime(s, 1, "cpu")


def test_route_progress_and_stuck_are_axial_and_reset_when_inactive():
    x = torch.tensor([1.0, 0.4, 0.0, -0.1])
    prev = torch.zeros_like(x)
    active = torch.tensor([False, True, True, True])
    a = route_progress_and_stuck(
        active,
        x,
        prev,
        prev,
        torch.full_like(x, 0.5),
        torch.ones_like(active),
        dt=0.5,
        window_s=1.0,
        distance_m=0.3,
    )
    progress, start, elapsed, stuck = a
    torch.testing.assert_close(progress, torch.tensor([0.0, 0.4, 0.0, -0.1]))
    torch.testing.assert_close(start, x)
    assert not elapsed.any()
    assert stuck.tolist() == [False, False, True, True]
    b = route_progress_and_stuck(
        torch.zeros_like(active),
        x,
        x,
        start,
        elapsed,
        stuck,
        dt=0.5,
        window_s=1.0,
        distance_m=0.3,
    )
    assert not b[0].any() and not b[2].any() and not b[3].any()


def test_tunnel_rejects_early_first_touch_or_underpass_even_after_rolling_beyond():
    settings = dict(height_range_m=(0.2, 0.2), event_duration_s=1.0, landing_stable_s=0.2)
    event = JumpEvent(settings, 3, "cpu")
    yes, no = torch.ones(3, dtype=torch.bool), torch.zeros(3, dtype=torch.bool)
    z = torch.full((3,), 0.3)
    air = torch.zeros(3, 2, dtype=torch.bool)
    event.request(yes)
    event.trigger(z, before_beam=yes)

    def tick(contact, *, over=no, blocked=no, valid=yes):
        airborne = ~contact.any(-1)
        event.update(
            0.1,
            z,
            airborne.float(),
            contact,
            yes,
            valid,
            no,
            wheel_clearance=airborne.float() * 0.2,
            takeoff_clearance_m=0.02,
            above_beam=over,
            blocked_at_beam=blocked,
        )

    tick(~air)
    tick(air, over=torch.tensor([True, True, False]), blocked=torch.tensor([False, False, True]))
    tick(torch.tensor([[True, False], [True, False], [True, True]]), valid=torch.tensor([True, False, True]))
    tick(~air)
    tick(~air)
    assert event.landing_pulse.tolist() == [True, False, False]
    assert event.invalid.tolist() == [False, True, True]


def test_link_local_collision_offset_rotates_with_the_body():
    q = torch.tensor([[[2**-0.5, 0.0, 0.0, 2**-0.5]]])
    bounds = torch.tensor([[[0.0, -0.1, 0.0], [0.2, 0.1, 0.4]]])
    lo, hi = collision_bounds_w(torch.tensor([[[1.34, 0.0, 0.0]]]), q, bounds)
    torch.testing.assert_close(lo, torch.tensor([[[1.24, 0.0, 0.0]]]), atol=1e-6, rtol=0)
    torch.testing.assert_close(hi, torch.tensor([[[1.44, 0.2, 0.4]]]), atol=1e-6, rtol=0)
    settings = dict(beam_length_m=0.35, lane_width_m=0.8, clearance_margin_m=0.03, landing_margin_m=0.05)
    before, over, blocked, past = tunnel_geometry(
        (lo, hi), torch.tensor([[1.0, 0.0, 0.0]]), torch.tensor([0.27]), settings
    )
    assert not before.item() and not over.item() and blocked.item() and not past.item()
