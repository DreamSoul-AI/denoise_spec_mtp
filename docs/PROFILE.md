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
- The 4D tree-attention mask is the only SpecMTP part that stands out: 5–6% with dynamic trees / `impl: naive` (mask rebuilt per call) against 0.2–0.4% with static trees / `impl: efficient` (cached). A cache for dynamic masks would be the first optimisation to try; it is not done here (no algorithm change in this round).
- The BC=60 paper presets cost the most per decode call (bigger tree block): in the larger run 75–78 spec tok/s against about 100 for the smoke variants at similar tau.
- cProfile overhead inflates Python-heavy parts; absolute tok/s without the profiler are higher. Compare variants inside one run only.
- GPU behaviour (kernel launch, memory bandwidth, bf16) is not covered.
