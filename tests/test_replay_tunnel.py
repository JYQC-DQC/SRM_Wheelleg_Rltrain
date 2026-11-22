import numpy as np
import pytest

from tools.play_jump import replay_tunnel_check
from wheelleg.jump import TunnelTraversal

SITE = dict(start_x_m=0.0, end_x_m=0.35, center_y_m=0.0, width_m=0.8, height_m=0.2)


def check(tracker, low, high, flight=True, contact=False):
    return replay_tunnel_check(
        tracker,
        np.array(low),
        np.array(high),
        SITE,
        flight,
        np.array([contact, contact]),
        np.zeros(2),
        0.02,
        0.01,
    )


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
