"""Named mask settings for history-extrapolation Studies.

A Study axis sets ``algorithm.config.mask``. Optional ``beta``, ``lam``, and
``gamma`` override the defaults. The tree is the history protocol: one mask
slot, static ``[14]``, block complexity 30.
"""

from spec_mtp.structure.control.spec_mtp.named import _convert

_TREE = {
    'num_masks': 1,
    'impl': 'efficient',
    'tree': {'mode': 'static', 'branches': [14], 'pruning': True},
}


def spec_for(name, beta=None, lam=None, gamma=None, branches=None, num_masks=None):
    key = str(name or '').lower()
    if key == 'frozen_mean':
        body = {
            **_TREE,
            'method': 'esp',
            'mask': {'init': 'mean_prompt', 'lam': 0, 'update': False},
        }
    elif key == 'last_token':
        body = _ema(level='last', step_scale=0, beta=0.9, lam=0.1)
    elif key == 'updating_mean':
        body = _ema(level='order0', step_scale=0, beta=0.9, lam=0.1 if lam is None else lam)
    elif key == 'gamma_last':
        body = _ema(
            level='last',
            step_scale=1.0 if gamma is None else gamma,
            beta=0.9 if beta is None else beta,
            lam=0.1,
            normalize=False,
        )
    elif key == 'gamma_last_unit':
        body = _ema(
            level='last',
            step_scale=1.0 if gamma is None else gamma,
            beta=0.9 if beta is None else beta,
            lam=0.1,
            normalize=True,
        )
    elif key == 'mean_plus_gamma':
        body = _ema(
            level='order0',
            step_scale=1.0 if gamma is None else gamma,
            beta=0.9999 if beta is None else beta,
            lam=0.1 if lam is None else lam,
            normalize=False,
        )
    else:
        raise ValueError(f'unknown mask setting: {name!r}')
    if branches is not None:
        body['tree']['branches'] = [int(x) for x in branches]
    if num_masks is not None:
        body['num_masks'] = int(num_masks)
    return _convert(body)


def _ema(level, step_scale, beta, lam, normalize=False):
    return {
        **_TREE,
        'method': 'ema_velocity',
        'ema': {
            'beta': float(beta),
            'step_scale': float(step_scale),
            'normalize': bool(normalize),
            'extrapolate_ema': False,
            'update': True,
            'level': level,
            'lam': float(lam),
        },
    }
