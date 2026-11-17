import pytest

torch = pytest.importorskip("torch")

from wheelleg.history import HISTORY_FRAMES, HistoryBuffer  # noqa: E402


def test_history_buffer_shift_refresh_and_partial_reset():
    history = HistoryBuffer(2, "cpu")

    def frames(a, b):
        return torch.tensor([[a], [b]], dtype=torch.float32).expand(-1, 35)

    def check(first, second):
        flat = history.flat()
        assert flat.shape == (2, 175)
        expected = torch.tensor([first, second], dtype=flat.dtype)
        torch.testing.assert_close(flat.view(2, HISTORY_FRAMES, 35), expected[:, :, None].expand(-1, -1, 35))

    history.update(frames(1, 10), new_step=False)
    check([1] * 5, [10] * 5)
    history.update(frames(1.5, 15), new_step=False)
    check([1.5] * 5, [15] * 5)
    with torch.inference_mode():
        history.update(frames(2, 20), new_step=True)
        history.update(frames(2.5, 25), new_step=False)
    check([1.5] * 4 + [2.5], [15] * 4 + [25])
    history.reset(torch.tensor([1]))
    history.update(frames(3, 30), new_step=True)
    check([1.5] * 3 + [2.5, 3], [30] * 5)
    history.update(frames(4, 40), new_step=True)
    check([1.5, 1.5, 2.5, 3, 4], [30] * 4 + [40])
