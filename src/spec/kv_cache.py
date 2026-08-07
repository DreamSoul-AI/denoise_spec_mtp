"""KV-cache surgery for tree decoding.

A block forward appends KV entries for every block position (root, all draft
nodes, all mask tokens). After verification only the root and the accepted
path may remain: mask tokens and rejected branches must be evicted so the
cache again holds exactly the committed prefix.

Handles both transformers >= 5 (DynamicCache.layers[i].keys/.values) and
4.x (DynamicCache.key_cache/value_cache lists).
"""

import torch
from transformers.cache_utils import DynamicCache


def new_cache():
    return DynamicCache()


def _layer_tensors(cache):
    """Yields (get_k, get_v, set_k, set_v) accessors per layer."""
    if hasattr(cache, 'layers'):          # transformers >= 5
        for layer in cache.layers:
            yield layer, 'keys', 'values'
    elif hasattr(cache, 'key_cache'):     # transformers 4.x
        class _Shim:
            def __init__(self, cache, idx):
                self._c, self._i = cache, idx

            @property
            def keys(self):
                return self._c.key_cache[self._i]

            @keys.setter
            def keys(self, t):
                self._c.key_cache[self._i] = t

            @property
            def values(self):
                return self._c.value_cache[self._i]

            @values.setter
            def values(self, t):
                self._c.value_cache[self._i] = t

        for idx in range(len(cache.key_cache)):
            yield _Shim(cache, idx), 'keys', 'values'
    else:
        raise TypeError(f'Unsupported cache type: {type(cache)}')


def cache_len(cache):
    return cache.get_seq_length()


def crop(cache, keep_len):
    """Drop all cache entries from position keep_len onward."""
    if hasattr(cache, 'crop'):
        cache.crop(keep_len)
        return
    for layer, kname, vname in _layer_tensors(cache):
        setattr(layer, kname, getattr(layer, kname)[:, :, :keep_len])
        setattr(layer, vname, getattr(layer, vname)[:, :, :keep_len])


def keep_block_positions(cache, prefix_len, block_keep_indices):
    """Rewrite cache to prefix + the block entries at `block_keep_indices`
    (block-relative, in commit order). Everything else is evicted."""
    if len(block_keep_indices) == 0:
        crop(cache, prefix_len)
        return
    device_index = None
    for layer, kname, vname in _layer_tensors(cache):
        keys = getattr(layer, kname)
        values = getattr(layer, vname)
        if device_index is None or device_index.device != keys.device:
            device_index = torch.tensor(
                block_keep_indices, dtype=torch.long, device=keys.device) + prefix_len
        setattr(layer, kname, torch.cat(
            [keys[:, :, :prefix_len], keys[:, :, device_index]], dim=2))
        setattr(layer, vname, torch.cat(
            [values[:, :, :prefix_len], values[:, :, device_index]], dim=2))
