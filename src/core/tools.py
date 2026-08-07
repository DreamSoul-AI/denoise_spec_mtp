import os
import random

import numpy as np
import torch


def seed_everything(seed, deterministic=False):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    if deterministic:
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False


def makedir_exist_ok(path):
    is_file = os.path.splitext(path)[1] != ''
    if is_file:
        path = os.path.dirname(path)
    os.makedirs(path, exist_ok=True)


def get_device(cfg_device):
    if cfg_device == 'auto':
        return 'cuda' if torch.cuda.is_available() else 'cpu'
    return cfg_device


def get_dtype(tag):
    tag = str(tag).lower()
    if tag in ('auto', 'none'):
        return 'auto'
    mapping = {
        'float32': torch.float32, 'fp32': torch.float32,
        'float16': torch.float16, 'fp16': torch.float16,
        'bfloat16': torch.bfloat16, 'bf16': torch.bfloat16,
    }
    if tag not in mapping:
        raise ValueError(f'Unsupported torch_dtype: {tag}')
    return mapping[tag]


def sync_device(device):
    """Synchronize before wall-clock timing so speedup ratios are honest."""
    if str(device).startswith('cuda') and torch.cuda.is_available():
        torch.cuda.synchronize()
