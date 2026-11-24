import numpy as np
import pytest

from tools.play_jump import replay_tunnel_check
from wheelleg.jump import TunnelTraversal

SITE = dict(start_x_m=0.0, end_x_m=0.35, center_y_m=0.0, width_m=0.8, height_m=0.2)


def check(tracker, low, high, flight=True, contact=False, wheel_rear_x=(0.5, 0.5), wheel_clearance=(0.0, 0.0)):
    valid, invalid, _ = replay_tunnel_check(
        tracker,
        np.array(low),
        np.array(high),
        SITE,
        flight,
        np.array([contact, contact]),
        np.array(wheel_clearance),
        np.array(wheel_rear_x),
        0.02,
        0.01,
    )
    return valid, invalid


@pytest.mark.parametrize("height", [0.10, 0.15, 0.20, 0.25, 0.30])
def test_far_ground_first_touch_can_precede_tail_clearance(height):
    site = dict(SITE, height_m=height)
    t = TunnelTraversal(1, "cpu")

    def sample(low, high, flight, contact, wheel_x):
        return replay_tunnel_check(
            t,
            np.array(low),
            np.array(high),
            site,
            flight,
            np.array(contact),
            np.zeros(2),
            np.array(wheel_x),
            0.02,
            0.01,
        )

    sample([[-0.8, -0.1, 0.0]], [[-0.3, 0.1, 0.4]], False, [True, True], [-0.5, -0.5])
    sample([[0.0, -0.1, height + 0.05]], [[0.2, 0.1, height + 0.2]], True, [False, False], [0.1, 0.1])
    # Supporting wheel is on rear ground. The elevated tail still overlaps the roof.
    valid, invalid, _ = sample(
        [[0.25, -0.1, height + 0.05], [0.45, -0.1, 0.0]],
        [[0.40, 0.1, height + 0.2], [0.60, 0.1, 0.3]],
        False,
        [True, False],
        [0.45, 0.3],
    )
    assert valid.item() and not invalid.item() and not t.cleared.item()
    valid, invalid, _ = sample([[0.40, -0.1, 0.0]], [[0.8, 0.1, 0.4]], False, [True, True], [0.5, 0.5])
    assert valid.item() and not invalid.item() and t.cleared.item()


def test_near_ground_contact_and_roof_contact_still_invalidate_first_landing():
    for wheel_x, wheel_z in [((0.1, 0.1), (0.0, 0.0)), ((0.5, 0.5), (0.2, 0.2))]:
        t = TunnelTraversal(1, "cpu")
        check(t, [[-0.8, -0.1, 0.0]], [[-0.3, 0.1, 0.4]], flight=False)
        valid, invalid = check(
            t,
            [[0.1, -0.1, 0.25]],
            [[0.3, 0.1, 0.4]],
            flight=False,
            contact=True,
            wheel_rear_x=wheel_x,
            wheel_clearance=wheel_z,
        )
        assert invalid.item() and not valid.item()
        valid, invalid = check(t, [[0.5, -0.1, 0.0]], [[0.9, 0.1, 0.4]], flight=False, contact=True)
        assert invalid.item() and not valid.item()  # Driving off the roof cannot repair that attempt.


def test_collision_parts_behind_roof_need_not_be_above_roof():
    t = TunnelTraversal(1, "cpu")
    check(t, [[-0.8, -0.1, 0.0]], [[-0.3, 0.1, 0.4]], flight=False)
    # Front body clears the roof; rear part is low but has not reached the obstacle.
    _, invalid = check(t, [[0.0, -0.1, 0.25], [-0.4, -0.1, 0.05]], [[0.2, 0.1, 0.4], [-0.1, 0.1, 0.3]])
    assert not invalid.item()
    valid, invalid = check(t, [[0.5, -0.1, 0.0]], [[1.0, 0.1, 0.4]], flight=False, contact=True)
    assert valid.item() and not invalid.item()


@pytest.mark.parametrize("bottom,flight", [(0.19, True), (0.0, False), (0.0, True)])
def test_roof_landing_ground_driving_and_underpass_are_not_success(bottom, flight):
    t = TunnelTraversal(1, "cpu")
    check(t, [[-0.8, -0.1, 0.0]], [[-0.3, 0.1, 0.4]], flight=False)
    valid, invalid = check(t, [[0.0, -0.1, bottom]], [[0.2, 0.1, bottom + 0.1]], flight=flight)
    assert invalid.item() and not valid.item()


def test_bypassing_tunnel_side_is_not_success():
    t = TunnelTraversal(1, "cpu")
    valid, invalid = check(t, [[-0.8, 0.5, 0.3]], [[-0.3, 0.7, 0.4]])
    assert invalid.item() and not valid.item()
