"""Temporary forensic instrumentation; does not modify upstream packages or training hyperparameters."""
import json
import math
import runpy
from pathlib import Path

import torch
from rsl_rl.runners import OnPolicyRunner

out = Path('runs/ppo_forensics')
out.mkdir(exist_ok=True)
log = (out / 'trace.jsonl').open('a', buffering=1)
original_init = OnPolicyRunner.__init__
original_clip = torch.nn.utils.clip_grad_norm_
active = {}


def stats(x):
    x = x.detach()
    return {'max': float(x.abs().max()), 'mean': float(x.double().mean()),
            'finite': bool(torch.isfinite(x).all())}


def emit(event, **values):
    log.write(json.dumps({'event': event, 'iteration': active.get('iteration'), **values}) + '\n')


def snapshot(reason):
    alg = active['alg']
    s = alg.storage
    torch.save({'reason': reason, 'iteration': active.get('iteration'),
                'model': alg.policy.state_dict(), 'optimizer': alg.optimizer.state_dict(),
                'observations': {k: v.detach().cpu() for k,v in s.observations.items()},
                'rewards': s.rewards.detach().cpu(), 'returns': s.returns.detach().cpu(),
                'values': s.values.detach().cpu(), 'advantages': s.advantages.detach().cpu(),
                'actions': s.actions.detach().cpu()}, out / 'first_anomaly.pt')
    emit('ANOMALY', reason=reason)
    raise FloatingPointError(reason)


def diagnostic_clip(parameters, *args, **kwargs):
    parameters = list(parameters)
    norm = original_clip(parameters, *args, **kwargs)
    n = float(norm)
    active['grad_max'] = max(active.get('grad_max', 0), n)
    if not math.isfinite(n):
        snapshot('nonfinite gradient norm before optimizer')
    if n > 1e12:
        snapshot('gradient norm exceeds 1e12')
    return norm


def initialize(self, *args, **kwargs):
    original_init(self, *args, **kwargs)
    alg = self.alg
    active['alg'] = alg
    update = alg.update
    evaluate = alg.policy.evaluate
    step = alg.process_env_step
    def diagnostic_evaluate(obs, **kw):
        value = evaluate(obs, **kw)
        if not torch.isfinite(value).all() or value.abs().max() > 1e8:
            snapshot('critic prediction nonfinite or above 1e8')
        return value
    alg.policy.evaluate = diagnostic_evaluate
    def process(obs, rewards, dones, extras):
        active['iteration'] = self.current_learning_iteration
        for key, x in obs.items():
            m = x.detach().abs().amax(0)
            if not torch.isfinite(x).all() or m.max() > 1e6:
                emit('observation_anomaly', group=key, per_feature=m.cpu().tolist())
                snapshot('observation nonfinite or above 1e6')
        if not torch.isfinite(rewards).all():
            snapshot('nonfinite environment reward')
        return step(obs, rewards, dones, extras)
    alg.process_env_step = process
    def diagnostic_update():
        active['iteration'] = self.current_learning_iteration
        active['grad_max'] = 0
        s = alg.storage
        report = {'lr_before': alg.learning_rate,
                  'features': {k:v.detach().abs().flatten(0,1).amax(0).cpu().tolist() for k,v in s.observations.items()},
                  **{k:stats(getattr(s,k)) for k in ('rewards','returns','values','advantages','actions')}}
        emit('before_update', **report)
        if any(not report[k]['finite'] or report[k]['max'] > 1e8 for k in ('returns','values','rewards')):
            snapshot('rollout targets or values nonfinite/above1e8')
        losses = update()
        emit('after_update', losses=losses, lr_after=alg.learning_rate,
             gradient_norm_max=active['grad_max'], std=alg.policy.std.detach().cpu().tolist())
        return losses
    alg.update = diagnostic_update


OnPolicyRunner.__init__ = initialize
torch.nn.utils.clip_grad_norm_ = diagnostic_clip
runpy.run_module('isaac.scripts.train', run_name='__main__')
