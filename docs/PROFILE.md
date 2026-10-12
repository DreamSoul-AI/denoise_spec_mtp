# CPU profile

Tool: `python tools/profile_cpu.py` (CPU, random tiny LLaMA, no weights). It wraps `esp_mtp.evaluate`, the unchanged decode loop the Algorithm runs, in cProfile, and reports speed, `tau`, `exact_match_rate` and self time by component. Reproduce the two runs below with the commands shown; raw JSON / Markdown land in `.tmp/profile*/` (not tracked).

**Not a paper number.** Random weights accept few drafts (tau 1.1–1.8), so speculative decoding is slower than AR here. What the profile does answer: how much CPU time is SpecMTP's own code (tree, tree mask, KV cache bookkeeping, mask providers, decoder loop) versus the model forward.

## Small (`--hidden 128 --layers 4 --vocab 512 --threads 1`, 2026-10-12)

```text
python tools/profile_cpu.py --variant esp_static --variant esp_dynamic --variant ema_velocity \
  --variant llama3/esp_bc60 --variant qwen3/esp_bc60 --variant llama3/impl_naive_bc30
```

Machine: x86_64 (8 CPUs), Linux; torch 2.14.1+cpu, threads 1. Tiny LLaMA hidden 128, 4 layers, vocab 512, 4 prompts x 32 tokens, 64 new tokens, temperature 0. Random weights: tau and speedup are not paper numbers; cProfile overhead inflates Python-heavy parts.

| **variant** | **exact_match** | **tau** | **decode calls** | **spec tok/s** | **AR tok/s** |
| --- | --- | --- | --- | --- | --- |
| `esp_static` | 1.0 | 1.726 | 146 | 593.8 | 557.9 |
| `esp_dynamic` | 1.0 | 1.5849 | 159 | 504.4 | 589.1 |
| `ema_velocity` | 1.0 | 1.575 | 160 | 550.1 | 579.8 |
| `llama3/esp_bc60` | 1.0 | 1.7872 | 141 | 528.7 | 582.4 |
| `qwen3/esp_bc60` | 1.0 | 1.5849 | 159 | 457.9 | 581.9 |
| `llama3/impl_naive_bc30` | 1.0 | 1.5849 | 159 | 512.6 | 581.3 |

Self-time share by component (profiled run, spec + AR + warm-up):

| **component** | **esp_static** | **esp_dynamic** | **ema_velocity** | **llama3/esp_bc60** | **qwen3/esp_bc60** | **llama3/impl_naive_bc30** |
| --- | --- | --- | --- | --- | --- | --- |
| torch kernels (C calls) | 43.5% | 40.7% | 43.0% | 45.6% | 46.2% | 41.3% |
| model forward (torch nn / transformers) | 46.1% | 43.1% | 45.3% | 44.4% | 43.6% | 43.8% |
| tree attention | 0.4% | 5.7% | 0.4% | 0.4% | 0.4% | 5.0% |
| other builtins | 3.0% | 3.2% | 3.0% | 2.9% | 3.0% | 3.1% |
| decoder loop | 1.7% | 1.6% | 1.7% | 1.5% | 1.5% | 1.6% |
| other torch | 1.3% | 1.3% | 1.6% | 1.3% | 1.2% | 1.3% |
| other Python | 1.6% | 1.6% | 1.6% | 1.5% | 1.5% | 1.6% |
| kv cache | 1.2% | 1.2% | 1.3% | 1.1% | 1.2% | 1.3% |
| tree build / prune | 0.8% | 1.2% | 0.8% | 1.0% | 1.1% | 0.8% |
| mask providers | 0.3% | 0.3% | 1.1% | 0.3% | 0.3% | 0.3% |

## Larger (`--hidden 512 --layers 8 --vocab 4096 --threads 4`, 2026-10-12)

```text
python tools/profile_cpu.py --hidden 512 --layers 8 --vocab 4096 --threads 4 --variant esp_static \
  --variant esp_dynamic --variant ema_velocity --variant llama3/esp_bc60 --variant qwen3/esp_bc60 --out .tmp/profile_large
```

Machine: x86_64 (8 CPUs), Linux; torch 2.14.1+cpu, threads 4. Tiny LLaMA hidden 512, 8 layers, vocab 4096, 4 prompts x 32 tokens, 64 new tokens, temperature 0. Random weights: tau and speedup are not paper numbers; cProfile overhead inflates Python-heavy parts.

| **variant** | **exact_match** | **tau** | **decode calls** | **spec tok/s** | **AR tok/s** |
| --- | --- | --- | --- | --- | --- |
| `esp_static` | 1.0 | 1.12 | 225 | 102.9 | 218.4 |
| `esp_dynamic` | 1.0 | 1.1053 | 228 | 97.4 | 224.1 |
| `ema_velocity` | 1.0 | 1.125 | 224 | 102.1 | 226.2 |
| `llama3/esp_bc60` | 1.0 | 1.125 | 224 | 75.4 | 210.7 |
| `qwen3/esp_bc60` | 1.0 | 1.1053 | 228 | 78.1 | 230.6 |

Self-time share by component (profiled run, spec + AR + warm-up):

| **component** | **esp_static** | **esp_dynamic** | **ema_velocity** | **llama3/esp_bc60** | **qwen3/esp_bc60** |
| --- | --- | --- | --- | --- | --- |
| torch kernels (C calls) | 64.9% | 63.7% | 64.6% | 68.3% | 67.1% |
| model forward (torch nn / transformers) | 30.6% | 29.6% | 30.5% | 27.8% | 28.8% |
| tree attention | 0.2% | 2.1% | 0.2% | 0.2% | 0.2% |
| other builtins | 1.2% | 1.4% | 1.3% | 1.1% | 1.2% |
| kv cache | 0.9% | 0.8% | 0.9% | 0.7% | 0.8% |
| decoder loop | 0.7% | 0.7% | 0.7% | 0.6% | 0.6% |
| other torch | 0.5% | 0.5% | 0.6% | 0.4% | 0.4% |
| other Python | 0.5% | 0.5% | 0.5% | 0.4% | 0.4% |
| tree build / prune | 0.3% | 0.5% | 0.3% | 0.4% | 0.4% |
| mask providers | 0.1% | 0.1% | 0.4% | 0.1% | 0.1% |

## Reading

- Every variant keeps `exact_match_rate = 1` under profiling.
- SpecMTP-owned code (tree attention + tree build + KV cache + mask providers + decoder loop) is about 4–10% of self time on the small model and about 2–4% on the larger one; the rest is the model forward (Python dispatch in torch / transformers plus C kernels). The C-kernel share grows with model size, so on real models the decoder overhead shrinks further.
- The 4D tree-attention mask is the only SpecMTP part that stands out: 5–6% with dynamic trees / `impl: naive` (mask rebuilt per call) against 0.2–0.4% with static trees / `impl: efficient` (cached). Addressed by the dynamic-tree mask cache below.
- The BC=60 paper presets cost the most per decode call (bigger tree block): in the larger run 75–78 spec tok/s against about 100 for the smoke variants at similar tau.
- cProfile overhead inflates Python-heavy parts; absolute tok/s without the profiler are higher. Compare variants inside one run only.
- GPU behaviour (kernel launch, memory bandwidth, bf16) is not covered.

## Dynamic-tree mask cache (2026-10-12, branch `perf/dynamic-tree-mask`)

`DynamicTreeAttentionCache` (`tree_attention.py`) replaces the per-entry Python fill of `build_block_attention` for `tree.mode: dynamic`: the block-local structure is memoised per tree signature (LRU, 256 entries) and filled with one indexed write; per step only the cache columns are prepended and the PIDs shifted. Static trees with `impl: naive` keep the literal builder so the Table 4 naive-vs-efficient ablation still times the naive path; `impl: efficient` is unchanged.

Output identity (all must match before / after):

- `tools/decode_fingerprint.py`: 555 cells (every smoke variant and paper preset × T 0 / 0.7 / 1 × 3 prompts, plus a 64-position context-limited model): tokens, `new_tokens`, `accepted`, `committed`, `decode_calls`, `tau`, depth attempts / accepts, `hit_context_limit` identical (fingerprint sha256 `150154ecea4dfc76…` both).
- `tools/paper_hf_dryrun.py --keep`: all 59 Runs' `spec_metrics.csv` / `summary.csv` / `alignment_metrics.csv` identical except timing columns.
- Smoke regression capture (5 Studies, 26 cells, every spec and AR token sequence): identical to the pre-change capture; `ctx_check.py` against `b1f6191` still ok.
- `test_tree_attention_cache.py`: bit-identical mask and PIDs to the naive builder on random dynamic trees (fp32 / bf16, cache hits and eviction).

Speed (`tools/profile_cpu.py --timing-repeats 3`, best unprofiled spec tok/s; same machine, same run order; ±4% is noise, see the unchanged static rows):

| **model** | **variant** | **tau before / after** | **decode calls** | **spec tok/s** | **tree-attention self time** |
| --- | --- | --- | --- | --- | --- |
| hidden 128, 4 layers, 1 thread | `esp_dynamic` | 1.5849 / 1.5849 | 159 / 159 | 617.4 → 741.5 (+20%) | 5.7% → 0.5% |
| hidden 128, 4 layers, 1 thread | `ema_velocity` | 1.575 / 1.575 | 160 / 160 | 686.8 → 726.4 (+6%) | 0.4% → 0.4% |
| hidden 128, 4 layers, 1 thread | `llama3/esp_bc60_dynamic` | 1.5849 / 1.5849 | 159 / 159 | 443.6 → 567.3 (+28%) | 9.6% → 0.5% |
| hidden 128, 4 layers, 1 thread | `qwen3/esp_bc60_dynamic` | 1.5849 / 1.5849 | 159 / 159 | 463.4 → 565.5 (+22%) | 9.5% → 0.4% |
| hidden 128, 4 layers, 1 thread | `llama3/impl_naive_bc30` | 1.5849 / 1.5849 | 159 / 159 | 639.5 → 658.8 (+3%) | 4.9% → 4.9% |
| hidden 128, 4 layers, 1 thread | `esp_static` | 1.726 / 1.726 | 146 / 146 | 770.5 → 795.5 (+3%) | 0.4% → 0.4% |
| hidden 512, 8 layers, 4 threads | `esp_dynamic` | 1.1053 / 1.1053 | 228 / 228 | 109.9 → 111.3 (+1%) | 2.2% → 0.2% |
| hidden 512, 8 layers, 4 threads | `llama3/esp_bc60_dynamic` | 1.1053 / 1.1053 | 228 / 228 | 77.9 → 87.1 (+12%) | 3.5% → 0.2% |
| hidden 512, 8 layers, 4 threads | `qwen3/esp_bc60_dynamic` | 1.1053 / 1.1053 | 228 / 228 | 82.5 → 91.0 (+10%) | 3.4% → 0.2% |
| hidden 512, 8 layers, 4 threads | `esp_static` | 1.12 / 1.12 | 225 / 225 | 124.6 → 119.8 (-4%) | 0.2% → 0.2% |

Dynamic presets gain about 20–28% on the small model and 10–12% for BC=60 on the larger one; the tree-attention share drops from 6–10% to under 0.5%. Unchanged paths (static efficient, static naive, EMA static) move within noise.
