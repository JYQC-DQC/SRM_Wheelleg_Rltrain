import pytest
import torch

from shu_train.wheelleg.safety import leaky_termination, numerical_failure


@pytest.mark.parametrize("dtype", [torch.float32, torch.float64])
def test_exact_sustained_boundary_and_full_decay(dtype):
    counter = torch.zeros(3, dtype=dtype)
    risk = torch.tensor([True, False, True])
    for k in range(40):
        counter, fired = leaky_termination(counter, risk, 0.01, 0.4, 2.0)
        assert fired.tolist() == ([True, False, True] if k == 39 else [False] * 3)
    torch.testing.assert_close(counter, torch.tensor([40.0, 0.0, 40.0], dtype=dtype))

    clean = torch.zeros_like(risk)
    for k in range(200):
        counter, fired = leaky_termination(counter, clean, 0.01, 0.4, 2.0)
        assert not fired.any()
        if k == 99:
            # Repeated fractional subtraction in float32 introduces sub-microsecond error.
            torch.testing.assert_close(counter, torch.tensor([20.0, 0.0, 20.0], dtype=dtype), atol=1e-4, rtol=0)
    torch.testing.assert_close(counter, torch.zeros_like(counter), atol=1e-4, rtol=0)


def test_interruption_leaks_per_lane_and_resumes_without_reset():
    counter = torch.tensor([38.6, 38.6, 0.1, 40.0], dtype=torch.float64)
    before = counter
    saved = before.clone()
    risk = torch.tensor([True, False, False, True])
    counter, fired = leaky_termination(counter, risk, 0.01, 0.4, 2.0)
    torch.testing.assert_close(counter, torch.tensor([39.6, 38.4, 0.0, 40.0], dtype=counter.dtype))
    assert fired.tolist() == [False, False, False, True]
    counter, fired = leaky_termination(counter, torch.ones_like(risk), 0.01, 0.4, 2.0)
    torch.testing.assert_close(counter, torch.tensor([40.0, 39.4, 1.0, 40.0], dtype=counter.dtype))
    assert fired.tolist() == [True, False, False, True]
    torch.testing.assert_close(before, saved)


def test_non_integer_duration_crosses_on_next_bad_interval():
    counter = torch.tensor([2.0, 1.0])
    updated, fired = leaky_termination(counter, torch.tensor([True, True]), 0.1, 0.25, 1.0)
    torch.testing.assert_close(updated, torch.tensor([2.5, 2.0]))
    assert fired.tolist() == [True, False]


def test_immediate_fault_bypasses_sustained_counter_including_release():
    raw_velocity = torch.tensor([[float("nan"), 0, 0], [0, 0, 0], [0, 0, 0]])
    thresholds = dict(joint_velocity_abs_max=1, base_linear_velocity_abs_max=1, base_angular_velocity_abs_max=1)
    numerical = numerical_failure(torch.zeros(3, 6), raw_velocity, torch.zeros_like(raw_velocity), thresholds)
    # Immediate faults are ORed outside the helper; release suppression applies only to ordinary counting.
    release = torch.tensor([True, False, False])
    risk = torch.tensor([True, True, False])
    counter, sustained = leaky_termination(torch.zeros(3), risk & ~release & ~numerical, 0.01, 0.4, 2.0)
    assert counter.tolist() == [0.0, 1.0, 0.0]
    assert (numerical | sustained).tolist() == [True, False, False]


@pytest.mark.parametrize("times", [(0, 0.4, 2), (0.01, float("nan"), 2), (0.01, 0.4, -2)])
def test_rejects_invalid_host_timing(times):
    with pytest.raises(ValueError, match="finite and positive"):
        leaky_termination(torch.zeros(1), torch.zeros(1, dtype=torch.bool), *times)


@pytest.mark.skipif(not torch.cuda.is_available(), reason="requires CUDA")
def test_cuda_step_does_not_synchronize():
    counter = torch.tensor([39.0, 20.0], device="cuda")
    condition = torch.tensor([True, False], device="cuda")
    prior = torch.cuda.get_sync_debug_mode()
    torch.cuda.set_sync_debug_mode("error")
    try:
        counter, fired = leaky_termination(counter, condition, 0.01, 0.4, 2.0)
    finally:
        torch.cuda.set_sync_debug_mode(prior)
    torch.testing.assert_close(counter.cpu(), torch.tensor([40.0, 19.8]))
    assert fired.cpu().tolist() == [True, False]
