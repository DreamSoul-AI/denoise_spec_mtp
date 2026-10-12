# Context limit and the exact_match audit

## Root cause (measured 2026-10-12, tiny LLaMA, `max_position_embeddings=56`, prompt 32, 32 new tokens)

`SpecDecoder.generate` stops before a pass whose block would exceed the position table:
`root_position + 1 + max(tree depth) + k > max_positions` (decoding.py). The block holds the
root, the tree nodes and `k` mask slots per node, so it needs `depth + k` positions past the
root. `ar_generate` only needs one position per step and stops at `pos + 1 > max_positions`,
so its output is `max_positions + 1` tokens long (57 here) while the speculative output is
2–4 tokens shorter (53–55). In all 60 measured pairs (3 variants × temperature 0 / 0.8 ×
4 prompts, plus warm-ups) the speculative output is an exact prefix of the AR output. The
decoding is lossless; `exact_match = torch.equal(spec, ar)` fails only on length.

Before this change the old pipeline wrote such Runs as `succeeded` with
`exact_match_rate = 0`; the refactor's write gate writes them `failed`.

## Effect on paper metrics and recorded results

- `accepted`, `committed`, `decode_calls`, `tau`, `call_reduction`, `accept_d*` and the
  speculative token sequence do not change; only the audit (`exact_match`) and AR fields do.
- Cells that never reach the limit are unchanged (regression: 20 of 26 cells and all their
  token streams identical; only the 6 context-limit cells differ, in `ar_calls` / `exact_match`
  or the new column).
- history_extrapolation: Qwen3 `max_position_embeddings` 40960, prompts ≤ 2048, 100 new
  tokens; no recorded cell can reach the limit, and every recorded float32 cell already has
  `exact_match_rate = 1`. Nothing there changes and nothing is rerun.
- Paper (ESP, Table 1 / Appendix G): 256 or 100 new tokens on SpecBench / Dolly with 128K /
  32K–40K context models; the limit is not reached in the paper settings.

## Adopted (2026-10-12): option A — AR stops at the budget the speculative pass reached

`esp_mtp.evaluate`: when a prompt has `hit_context_limit = 1`, the AR reference runs with
`max_new_tokens = new_tokens` of the speculative pass (same seed and generator, so the
RNG stream is the same prefix). `exact_match` keeps its meaning “identical token sequence
under the same budget”. `hit_context_limit` stays in the row.

- Pros: one column, gate unchanged, the audit still compares full sequences.
- Cons: for those prompts `ar_time` / `ar_calls` cover fewer tokens, so `speedup` is
  measured on the shorter budget; AR's own last 2–4 tokens before the limit are not audited.
- Not adopted: option B (common-prefix audit plus `context_limit_prompts` / `ar_extra_tokens`
  columns), kept locally on branch `fix/ctx-limit-prefix-audit`.

## Regression of the adopted fix

`studies/smoke_tiny_llama/regression/ctx_check.py` compares the old code (`b1f6191`) with
the merged branch over the same 26 cells (`CONTEXT_LIMIT_OPTION_A.json`):

- 20 cells without a context-limit prompt: rows, summary, metrics and status identical.
- 6 context-limit cells (`max_position_embeddings=56`, temperature 0 / 0.8, three variants):
  `exact_match_rate` 0 → 1; only `ar_calls`, `exact_match`, AR timing and `speedup` differ.
- All speculative token sequences identical; the 24 changed AR sequences are prefixes of the
  old AR sequences.

`REFACTOR_REGRESSION.json` stays as the record of the pure migration (old = new before this fix).
