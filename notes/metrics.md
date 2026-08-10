# Metrics Reference — result CSV schemas and invariants

Every run writes into `results/<save_root>/<save_name>/`:
`spec_metrics.csv` (one row per prompt) and `summary.csv` (one row per
SpecBench category + one `overall` row). NOTE: the Logger appends across
re-runs of the same save_name — delete the old dir or slice the tail when
re-running.

## spec_metrics.csv (algorithm: esp_mtp) — per prompt

| column | meaning |
|---|---|
| `prompt` | prompt index within the run (also the per-prompt RNG seed offset: `run.seed + idx`) |
| `category` | SpecBench category; group key for summary.csv (`synthetic` in smoke runs) |
| `new_tokens` | ALL tokens generated, including the one committed by the prefill pass |
| `committed` | tokens committed by decode passes only (accepted drafts + bonus tokens; excludes the prefill token). Numerator of tau |
| `decode_calls` | number of decode block-forwards. Denominator of tau |
| `accepted` | accepted draft-tree nodes summed over passes = `committed` minus the bonus tokens |
| `tau` | `committed / decode_calls` — the paper's average acceptance length: tokens per model call, bonus included |
| `spec_time` | wall-clock seconds: prefill + all decode passes (device-synced) |
| `hit_context_limit` | 1 if generation stopped because the next block would not fit `max_position_embeddings` |
| `ar_time` * | wall time of the AR reference run, same prompt / seed / sampling |
| `ar_calls` * | AR forward passes = prefill + one per subsequent token |
| `exact_match` * | 1 iff speculative output == AR output token-for-token (losslessness audit) |

\* present only with `eval.run_ar_baseline: true`.

## summary.csv (algorithm: esp_mtp) — per category + `overall`

| column | meaning |
|---|---|
| `prompts` | prompts in the group |
| `tau` | POOLED: sum(committed) / sum(decode_calls) — call-weighted, not a mean of per-prompt taus; long generations count more, matching "average per model call" literally |
| `call_reduction` | `1 - 1/tau` — fraction of forward passes saved vs AR; reproduces Table 6 arithmetic (tau=1.56 -> 0.359) |
| `new_tokens_per_prompt` | sum(new_tokens)/prompts — sanity column; ~= `max_new_tokens` unless EOS / context-limit stops runs early |
| `tokens_per_s` | sum(new_tokens)/sum(spec_time) — absolute throughput incl. prefill |
| `speedup` * | sum(ar_time)/sum(spec_time) — the paper's S/R as a ratio of pooled wall times on identical prompts |
| `exact_match_rate` * | mean of `exact_match` — MUST be 1.0000; anything less is a decoding bug (or an astronomically rare fp tie at T>0) |

## Invariants (audit any run at a glance)

1. `committed ~= accepted + decode_calls` — each pass commits its accepted
   chain + exactly one bonus token. Allowed slack: on the final pass,
   budget/EOS truncation trims `committed` while `accepted` was counted
   pre-truncation. Large gaps = bug.
2. `new_tokens = committed + 1` (the +1 is the prefill token), same
   final-pass caveat.
3. `tau >= 1` always — even 0% acceptance commits the bonus. tau = 1.0
   means "the tree never helps", not "broken"; broken looks like
   `exact_match_rate < 1`.
4. tau is impl-invariant; speedup is not. `impl: naive` vs `efficient`
   (Table 4) must give identical tau — wall time only. tau differences
   between methods live entirely in draft quality.
5. ESP vs EMA at the same BC config: same block cost per call, so ranking
   by pooled tau IS ranking by model calls saved; `speedup` confirms it
   survives real-clock overheads (mask building, cache surgery).

## Other schemas sharing the file names

- `ar_baseline` runs: `spec_metrics.csv` has `prompt, category, ar_calls,
  ar_time, ar_new_tokens`; `summary.csv` has `prompts, tokens_per_s` only.
- `alignment_probe` runs write `alignment_metrics.csv` instead: `layer,
  cos_accepted, cos_rejected, n_accepted, n_rejected` — the Figure 2
  curves in table form.

## The comparison that matters

`esp_bc30/summary.csv` vs `ema_bc30/summary.csv`, `overall` row, `tau`
column — the meeting's success criterion ("比他们效果好一点点"), valid only
with `exact_match_rate = 1.0` on both sides.
