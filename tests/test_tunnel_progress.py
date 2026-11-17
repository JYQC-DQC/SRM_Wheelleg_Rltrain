import torch

from wheelleg.jump import TunnelTraversal


def test_progress_cannot_be_farmed_by_reversing_or_resetting_other_envs():
    path = TunnelTraversal(2, "cpu")
    enabled = torch.tensor([True, False])
    limit = torch.tensor([2.0, 2.0])
    total = torch.zeros(2)
    for x in [1.0, 0.5, 1.0, 1.5, 3.0, 0.0, 3.0]:
        total += path.progress(torch.tensor([x, x]), limit, enabled)
    torch.testing.assert_close(total, torch.tensor([2.0, 0.0]))
    path.reset(torch.tensor([1]))
    torch.testing.assert_close(path.progress(torch.ones(2), limit, enabled), torch.zeros(2))
    path.reset(torch.tensor([0]))
    torch.testing.assert_close(path.progress(torch.ones(2), limit, enabled), torch.tensor([1.0, 0.0]))
