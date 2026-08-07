"""ESP-style speculative decoding engine (generation + parallel verification).

One `generate` call reproduces the ESP loop (Fig. 1):

  prefill   prompt + k mask tokens in one causal forward pass. The last
            prompt position yields the next committed token (the first tree
            root); the k mask positions yield the distributions that seed the
            first draft tree. Mask KV entries are evicted afterwards.

  decode    each pass processes one block: [root | draft tree | masks], with
            a tree attention mask and tree position IDs. The same forward
            pass (i) verifies draft tokens by exact match against the base
            model's own prediction chain (lossless, "sample matching"),
            (ii) yields the bonus/correction token, and (iii) produces the
            mask logits — at the masks of the deepest accepted node — that
            seed the next tree. Cache keeps only root + accepted path.

Verification draws one sample per committed token in chain order, so with a
shared torch.Generator the output equals plain autoregressive decoding
token-for-token (greedy at temperature 0) — the audit used by the smoke
tests. tau = committed tokens (accepted + bonus) per decode call.
"""

import time

import torch

from spec import kv_cache
from spec.mask_providers import build_mask_provider
from spec.tree import build_tree, node_budget_for
from spec.tree_attention import (TreeAttentionCache, build_block_attention,
                                 mask_indices_of)


def select_token(logits_row, temperature, generator):
    """Greedy at temperature 0, else one multinomial draw ("sample matching")."""
    if temperature <= 0.0:
        return int(logits_row.argmax(dim=-1).item())
    probs = torch.softmax(logits_row.float() / temperature, dim=-1)
    return int(torch.multinomial(probs, num_samples=1, generator=generator).item())


def tree_probs(mask_logits, temperature):
    """Candidate-ranking distribution per mask; matches the verifier at T>0."""
    if temperature <= 0.0:
        return torch.softmax(mask_logits.float(), dim=-1)
    return torch.softmax(mask_logits.float() / temperature, dim=-1)


class SpecDecoder:

    def __init__(self, model, spec_cfg, eval_cfg, eos_ids=(), generator=None):
        self.model = model
        self.spec_cfg = spec_cfg
        self.eval_cfg = eval_cfg
        self.eos_ids = set(int(e) for e in eos_ids)
        self.generator = generator
        self.temperature = float(eval_cfg.get('temperature', 0.0))
        self.max_new_tokens = int(eval_cfg.get('max_new_tokens', 100))
        self.stop_on_eos = bool(eval_cfg.get('stop_on_eos', True))
        self.num_masks = int(spec_cfg.get('num_masks', 1))

        self.impl = str(spec_cfg.get('impl', 'efficient')).lower()
        tree_mode = str(spec_cfg.get('tree', {}).get('mode', 'dynamic')).lower()
        if self.impl == 'efficient' and tree_mode != 'static':
            # Appendix E: the cached-mask fast path assumes a fixed tree
            # structure; dynamic trees change shape every step.
            raise ValueError('spec.impl=efficient requires spec.tree.mode=static; '
                             'use spec.impl=naive with dynamic trees')
        if self.impl not in ('naive', 'efficient'):
            raise ValueError(f'Unsupported spec.impl: {self.impl}')
        self._attn_cache = TreeAttentionCache() if self.impl == 'efficient' else None

        # Log the realized block complexity (Eq 7) for bookkeeping.
        if tree_mode == 'static':
            widths = [int(b) for b in spec_cfg.tree.branches]
            self.nominal_block_complexity = (self.num_masks + 1) * (1 + sum(widths))
        else:
            budget = node_budget_for(int(spec_cfg.block_complexity), self.num_masks)
            self.nominal_block_complexity = (self.num_masks + 1) * (1 + budget)

    def _is_eos(self, token):
        return self.stop_on_eos and token in self.eos_ids

    @torch.no_grad()
    def generate(self, prompt_ids):
        """prompt_ids: [1, t]. Returns (output_ids [1, t+n], stats dict)."""
        model = self.model
        device, dtype = model.device, model.dtype
        min_value = model.min_mask_value()
        prompt_ids = prompt_ids.to(device)
        t = prompt_ids.size(1)
        k = self.num_masks

        provider = build_mask_provider(self.spec_cfg, model.embedding_table,
                                       generator=self.generator)
        stats = {'prefill_calls': 1, 'decode_calls': 0, 'accepted': 0,
                 'committed': 0, 'hit_context_limit': 0}

        # ---- Prefill: [prompt | m_1..m_k], plain causal mask. -------------
        start = time.perf_counter()
        prompt_embeds = model.embed(prompt_ids)[0]                    # [t, d]
        provider.init_from_prompt(prompt_embeds)
        masks = provider.masks().to(dtype)                            # [k, d]
        prefill_embeds = torch.cat([prompt_embeds, masks], dim=0).unsqueeze(0)
        position_ids = torch.arange(t + k, device=device).unsqueeze(0)
        cache = kv_cache.new_cache()
        out = model(prefill_embeds, position_ids, attention_mask_4d=None,
                    past_key_values=cache)
        cache = out.past_key_values
        logits = out.logits[0]                                        # [t+k, V]

        root_token = select_token(logits[t - 1], self.temperature, self.generator)
        mask_logits = logits[t:t + k].clone()                         # [k, V]
        kv_cache.crop(cache, t)                                       # evict masks

        committed = [root_token]
        prev_token_embed = prompt_embeds[-1]
        root_embed = model.embed(torch.tensor([[root_token]], device=device))[0, 0]
        provider.on_token_committed(root_embed, prev_token_embed)
        prev_token_embed = root_embed
        stats['prefill_time'] = time.perf_counter() - start

        # ---- Decode: simultaneous verification + generation. --------------
        decode_start = time.perf_counter()
        while len(committed) < self.max_new_tokens and not self._is_eos(committed[-1]):
            remaining = self.max_new_tokens - len(committed)
            probs = tree_probs(mask_logits, self.temperature)
            tree = build_tree(self.spec_cfg, probs, committed[-1])
            num_nodes = tree.num_nodes
            block_size = tree.block_size(k)
            cache_len = kv_cache.cache_len(cache)
            root_position = t + len(committed) - 1
            assert cache_len == root_position, 'cache must hold exactly the prefix'
            if root_position + 1 + max(tree.depths or [0]) + k > model.max_positions:
                stats['hit_context_limit'] = 1
                break

            # Block embeddings: root, node tokens, k masks per owner.
            node_ids = torch.tensor([tree.tokens], dtype=torch.long, device=device)
            node_embeds = model.embed(node_ids)[0] if num_nodes else \
                torch.empty(0, prompt_embeds.size(-1), device=device, dtype=dtype)
            masks = provider.masks().to(dtype)
            block_embeds = torch.cat([
                prev_token_embed.unsqueeze(0),         # root = last committed token
                node_embeds,
                masks.unsqueeze(0).expand(1 + num_nodes, k, -1).reshape(-1, masks.size(-1)),
            ], dim=0).unsqueeze(0)

            if self.impl == 'efficient':
                attn, position_ids = self._attn_cache.get(
                    tree, k, cache_len, root_position, dtype, device, min_value)
            else:
                attn, position_ids = build_block_attention(
                    tree, k, cache_len, root_position, dtype, device, min_value)

            out = model(block_embeds, position_ids, attention_mask_4d=attn,
                        past_key_values=cache)
            cache = out.past_key_values
            logits = out.logits[0]                                    # [block, V]
            stats['decode_calls'] += 1

            # Verify: walk the model's own prediction chain through the tree.
            cur = 0
            accepted_nodes = []
            committed_now = []
            while True:
                y = select_token(logits[cur], self.temperature, self.generator)
                committed_now.append(y)
                match = None
                for child in tree.children_of(cur):
                    if tree.tokens[child - 1] == y:
                        match = child
                        break
                if match is None:
                    break
                accepted_nodes.append(match)
                cur = match

            stats['accepted'] += len(accepted_nodes)

            # EOS / budget truncation both end generation after this pass.
            stop = False
            for idx, token in enumerate(committed_now):
                if self._is_eos(token):
                    committed_now = committed_now[:idx + 1]
                    stop = True
                    break
            if len(committed_now) > remaining:
                committed_now = committed_now[:remaining]
                stop = True

            for token in committed_now:
                new_embed = model.embed(torch.tensor([[token]], device=device))[0, 0]
                provider.on_token_committed(new_embed, prev_token_embed)
                prev_token_embed = new_embed
            committed.extend(committed_now)
            stats['committed'] += len(committed_now)

            if stop:
                break

            # Cache keeps root + accepted path; masks/rejects are evicted.
            kv_cache.keep_block_positions(cache, cache_len, [0] + accepted_nodes)

            # Next tree seeds: masks of the deepest accepted node (or root).
            n_star = accepted_nodes[-1] if accepted_nodes else 0
            mask_rows = mask_indices_of(tree, k, n_star)
            mask_logits = logits[mask_rows].clone()

        stats['decode_time'] = time.perf_counter() - decode_start
        stats['new_tokens'] = len(committed)
        stats['block_complexity'] = self.nominal_block_complexity
        output = torch.cat([
            prompt_ids,
            torch.tensor([committed], dtype=torch.long, device=device),
        ], dim=1)
        return output, stats


@torch.no_grad()
def ar_generate(model, prompt_ids, eval_cfg, eos_ids=(), generator=None):
    """Plain KV-cached autoregressive decoding: the tau/speedup reference and
    the lossless audit target (identical sampling semantics as SpecDecoder)."""
    temperature = float(eval_cfg.get('temperature', 0.0))
    max_new_tokens = int(eval_cfg.get('max_new_tokens', 100))
    stop_on_eos = bool(eval_cfg.get('stop_on_eos', True))
    eos = set(int(e) for e in eos_ids)

    device = model.device
    prompt_ids = prompt_ids.to(device)
    t = prompt_ids.size(1)
    start = time.perf_counter()

    cache = kv_cache.new_cache()
    position_ids = torch.arange(t, device=device).unsqueeze(0)
    out = model(model.embed(prompt_ids), position_ids, attention_mask_4d=None,
                past_key_values=cache)
    cache = out.past_key_values
    committed = [select_token(out.logits[0, -1], temperature, generator)]
    calls = 1

    while len(committed) < max_new_tokens:
        if stop_on_eos and committed[-1] in eos:
            break
        pos = t + len(committed) - 1
        if pos + 1 > model.max_positions:
            break
        ids = torch.tensor([[committed[-1]]], dtype=torch.long, device=device)
        out = model(model.embed(ids),
                    torch.tensor([[pos]], dtype=torch.long, device=device),
                    attention_mask_4d=None, past_key_values=cache)
        cache = out.past_key_values
        committed.append(select_token(out.logits[0, -1], temperature, generator))
        calls += 1

    stats = {
        'ar_calls': calls,
        'ar_time': time.perf_counter() - start,
        'ar_new_tokens': len(committed),
    }
    output = torch.cat([
        prompt_ids,
        torch.tensor([committed], dtype=torch.long, device=device),
    ], dim=1)
    return output, stats
