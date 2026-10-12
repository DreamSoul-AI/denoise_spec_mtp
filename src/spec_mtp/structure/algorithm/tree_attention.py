"""Tree attention masks and position indices (ESP Fig. 3/7, Appendix E).

Block layout (Fig. 3: "all tokens are flattened and mask tokens are placed at
the end with appropriate position indices"):

    [ root | node_1 .. node_N | masks(root) | masks(node_1) | .. | masks(node_N) ]

with nodes in BFS (depth, then rank) order and k masks per owner. Attention:

  - every block row attends to the whole KV cache (the committed prefix);
  - the root attends to itself;
  - node n attends to root + its tree ancestors + itself;
  - mask j of owner b attends to b's attend-set + masks 1..j-1 of b + itself
    (the pair-conditioning of Appendix D: p(m2 | m1, x, ...)).

Position IDs: root at its natural next position p0; a node at depth d gets
p0 + d; mask j of owner b gets pid(b) + j (the mask occupies the slot of the
j-th future token after b).

Two implementations, matching the paper's naive/efficient ablation (Table 4):

  - `build_block_attention` (naive): re-derives mask + PIDs from the tree
    structure every step by iterating over nodes.
  - `TreeAttentionCache` (efficient): computes the block-local structure once
    (static trees only), then per step only prepends zero (attend) columns
    for the grown cache and shifts PIDs by the number of accepted tokens —
    exactly the Appendix E update rule.
"""

from typing import Any
import torch


def block_layout(tree, num_masks):
    """Returns (attend_sets, rel_positions, owner_of_mask, block_size).

    attend_sets[i] is the set of *block-local* indices row i attends to.
    rel_positions[i] is the position offset from the root position p0."""
    num_nodes = tree.num_nodes
    block = 1 + num_nodes
    # Attend sets and relative positions for root + nodes.
    attend: list[set[int]] = [set() for _ in range(block)]
    rel = [0] * block
    attend[0] = {0}
    for j in range(num_nodes):
        idx = 1 + j
        parent = tree.parents[j]
        attend[idx] = set(attend[parent]) | {idx}
        rel[idx] = tree.depths[j]

    # Masks, grouped by owner (root first, then nodes in block order).
    owner_of_mask: list[int] = []
    for owner in range(block):
        base = block + len(owner_of_mask)
        for j in range(num_masks):
            mask_idx = base + j
            attend.append(set(attend[owner]) | set(range(base, mask_idx + 1)))
            rel.append(rel[owner] + j + 1)
            owner_of_mask.append(owner)
    return attend, rel, owner_of_mask, len(attend)


def mask_indices_of(tree, num_masks, owner_block_idx):
    """Block indices of the k masks owned by `owner_block_idx`."""
    block = 1 + tree.num_nodes
    base = block + owner_block_idx * num_masks
    return list(range(base, base + num_masks))


def build_block_attention(tree, num_masks, cache_len, root_position, dtype, device,
                          min_value):
    """Naive path: full 4D additive mask + PIDs from the tree structure."""
    attend, rel, _, size = block_layout(tree, num_masks)
    mask = torch.full((1, 1, size, cache_len + size), min_value, dtype=dtype, device=device)
    mask[..., :cache_len] = 0.0
    for i, cols in enumerate(attend):
        for j in cols:
            mask[0, 0, i, cache_len + j] = 0.0
    position_ids = torch.tensor(
        [[root_position + r for r in rel]], dtype=torch.long, device=device)
    return mask, position_ids


class TreeAttentionCache:
    """Efficient path (Appendix E): cache the block-local structure once;
    per step prepend attend-columns for the new cache length and shift PIDs.

    Valid only while the tree structure is unchanged, i.e. static branch
    configurations. Callers must re-`prepare` if the structure changes
    (e.g. the truncated final step)."""

    def __init__(self):
        self._structure: Any = None   # [1, 1, B, B] additive block-local mask
        self._rel: Any = None         # [1, B] relative PIDs
        self._signature = None

    def _tree_signature(self, tree, num_masks):
        return (tuple(tree.depths), tuple(tree.parents), num_masks)

    def prepare(self, tree, num_masks, dtype, device, min_value):
        attend, rel, _, size = block_layout(tree, num_masks)
        structure = torch.full((1, 1, size, size), min_value, dtype=dtype, device=device)
        for i, cols in enumerate(attend):
            for j in cols:
                structure[0, 0, i, j] = 0.0
        self._structure = structure
        self._rel = torch.tensor([rel], dtype=torch.long, device=device)
        self._signature = self._tree_signature(tree, num_masks)

    def get(self, tree, num_masks, cache_len, root_position, dtype, device, min_value):
        if self._signature != self._tree_signature(tree, num_masks):
            # First step, or the structure changed: (re)build once.
            self.prepare(tree, num_masks, dtype, device, min_value)
        size = self._structure.size(-1)
        mask = torch.empty((1, 1, size, cache_len + size), dtype=dtype, device=device)
        mask[..., :cache_len] = 0.0                      # prepended attend columns
        mask[..., cache_len:] = self._structure          # unchanged block structure
        position_ids = self._rel + root_position         # uniform PID shift
        return mask, position_ids


class DynamicTreeAttentionCache:
    """Dynamic trees (``impl: naive``, ``tree.mode: dynamic``): same mask and PIDs as
    `build_block_attention`, built faster.

    Dynamic trees change shape between steps but repeat a small set of shapes,
    so the block-local structure is memoised per tree signature (LRU) and
    filled with one indexed write instead of one Python write per entry. Per
    step only the attend columns for the current cache are prepended and the
    PIDs shifted, as in `TreeAttentionCache`. The result is bit-identical to
    the naive builder (same dtype, same 0 / ``min_value`` entries, same PIDs);
    ``tests/.../test_tree_attention_cache.py`` checks it on random trees.

    Static trees with ``impl: naive`` keep `build_block_attention`, so the
    paper's naive vs efficient ablation (Table 4) still times the naive path.
    """

    def __init__(self, max_entries=256):
        self.max_entries = int(max_entries)
        self._entries = {}       # signature -> (structure [1,1,B,B], rel [1,B]); dict order = LRU
        self.hits = 0
        self.misses = 0

    def _structure(self, tree, num_masks, dtype, device, min_value):
        key = (tuple(tree.depths), tuple(tree.parents), num_masks, dtype, str(device), float(min_value))
        entry = self._entries.pop(key, None)
        if entry is None:
            self.misses += 1
            attend, rel, _, size = block_layout(tree, num_masks)
            rows = [i for i, cols in enumerate(attend) for _ in cols]
            cols = [j for cols_i in attend for j in cols_i]
            structure = torch.full((1, 1, size, size), min_value, dtype=dtype, device=device)
            structure[0, 0, torch.tensor(rows, dtype=torch.long, device=device),
                      torch.tensor(cols, dtype=torch.long, device=device)] = 0.0
            entry = (structure, torch.tensor([rel], dtype=torch.long, device=device))
            if len(self._entries) >= self.max_entries:
                self._entries.pop(next(iter(self._entries)))
        else:
            self.hits += 1
        self._entries[key] = entry
        return entry

    def get(self, tree, num_masks, cache_len, root_position, dtype, device, min_value):
        structure, rel = self._structure(tree, num_masks, dtype, device, min_value)
        size = structure.size(-1)
        mask = torch.empty((1, 1, size, cache_len + size), dtype=dtype, device=device)
        mask[..., :cache_len] = 0.0
        mask[..., cache_len:] = structure
        return mask, rel + root_position
