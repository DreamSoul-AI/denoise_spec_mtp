# First-round experiment log (2026-10-06)

Branch `feature/research-ema-history-audit` (from local `dev` = `main` =
`b636f90`), uncommitted. All result files live under
`results/cursor_20261006_history_audit/` (gitignored, local only) or
`.test-results/<run_id>/` (CI runner output, gitignored).

## Environment

`results/cursor_20261006_history_audit/environment.json`: Windows 11, Python
3.13.9, torch 2.11.0+cu130, transformers 5.12.1, RTX 5090 D v2 present.
**All runs below used CPU.**

No LLaMA/Qwen weights in the Hugging Face cache and no
`data/spec_bench/question.jsonl`. Per the research kickoff, no weights were
downloaded this round, so there are **no real-model numbers**.

## 1. Correctness (passed)

Command: `python scripts/run_ci_checks.py` → run `20261006T211312+0800_df90c7`,
plan `cpu_pr_checks`, status passed.

| **Check** | **Result** |
| --- | --- |
| `tests/check_correctness.py` | 196/196 (README says 172) |
| `tests/check_ema_history.py` (new) | 23/23 |
| smoke `esp_static`, `esp_dynamic`, `ema_velocity` | exit 0, `exact_match_rate=1.0000` |

Metric invariants hold in every smoke row: `committed = accepted + decode_calls`
and `new_tokens = committed + 1`.

The runner's blocking behaviour was checked with controlled failures: a
non-zero check makes the run `failed` with exit code 1, and later checks are
still recorded. Missing `summary.csv` and `exact_match_rate=0.75` both produce
a failed verdict.

## 2. CPU tiny-model ablation (mechanism control only)

Model: random tiny LLaMA (vocab 256, d=64, 2 layers, seed 123), 16 synthetic
prompts of length 32, 64 new tokens, greedy, k=2, static tree `[7,2]`
(BC=30), pruning on, efficient impl. ESP and EMA share every setting except
`spec.method`. Output dir: `results/cursor_20261006_history_audit/cpu_tiny_ablation/`.

```text
out=results/cursor_20261006_history_audit/cpu_tiny_ablation
common="--save_dir $out --set data.num_prompts=16 --set eval.num_eval_prompts=16 --set eval.max_new_tokens=64"
python src/main.py --cfg_file configs/smoke/tiny_llama/run_0/esp_static.yaml   --save_name esp            $common
python src/main.py --cfg_file configs/smoke/tiny_llama/run_0/esp_static.yaml   --save_name esp_update_off $common --set spec.mask.update=false
python src/main.py --cfg_file configs/smoke/tiny_llama/run_0/ema_velocity.yaml --save_name ema            $common
python src/main.py --cfg_file configs/smoke/tiny_llama/run_0/ema_velocity.yaml --save_name ema_update_off $common --set spec.ema.update=false
python src/main.py --cfg_file configs/smoke/tiny_llama/run_0/ema_velocity.yaml --save_name ema_normalize  $common --set spec.ema.normalize=true
python src/main.py --cfg_file configs/smoke/tiny_llama/run_0/ema_velocity.yaml --save_name ema_scale0.5   $common --set spec.ema.step_scale=0.5
python src/main.py --cfg_file configs/smoke/tiny_llama/run_0/ema_velocity.yaml --save_name ema_zero_step  $common --set spec.ema.step_scale=0.0
```

Pooled over 16 prompts (`tau = Σcommitted / Σdecode_calls`):

| **Run** | **Mask** | **tau** | **accepted / calls** | **exact match** |
| --- | --- | ---: | ---: | ---: |
| `esp` | prompt mean, λ=0.1 update | 1.2956 | 236 / 778 | 1.0 |
| `esp_update_off` | prompt mean, frozen | 1.1915 | 164 / 846 | 1.0 |
| `ema_zero_step` | last token embedding, no extrapolation | 1.0792 | 75 / 934 | 1.0 |
| `ema_update_off` | last token + frozen prefill `vhat` | 1.0804 | 76 / 933 | 1.0 |
| `ema_scale0.5` | last token + 0.5·i·`vhat` | 1.0746 | 71 / 938 | 1.0 |
| `ema` | last token + i·`vhat` (repo default) | 1.0611 | 58 / 950 | 1.0 |
| `ema_normalize` | last token + i·r·unit(`vhat`) | 1.0223 | 22 / 986 | 1.0 |

The CPU wall-clock speedup vs AR is 0.60–0.80 for every run. That is expected
for a 64-dim model where block overhead dominates; it says nothing about GPU.

**What this shows.** Only the pipeline behaviour under a model with no
language signal:

- Each EMA arm's tau is about the same as the zero-step control or lower,
  and longer or normalized steps are lower still. On this model, the
  history direction adds nothing beyond "mask = last token".
- The ESP–EMA gap is mostly the anchor change (prompt mean vs last token),
  not the direction. That confirms the confound noted in the audit.

**What it does not show.** Anything about real LMs. Random embeddings have no
semantic geometry, so "difference = velocity" cannot hold here by
construction. These numbers must not be quoted as evidence for or against
EMA-Velocity.

## 3. Qwen3-8B dev slice (real model, not the paper eval)

Weights: `D:\models\Qwen3-8B`, bf16, downloaded with ModelScope because the
Hugging Face download failed on SSL. SpecBench: `data/spec_bench/question.jsonl`
(480 lines). Dev slice: first 2 questions of each of the 13 categories, category
name order, file order within a category. Written by `scripts/make_dev_slice.py`
to `results/cursor_20261006_history_audit/qwen3_8b_dev/dev_questions.jsonl`.
The other 454 prompts were not run.

Shared settings, taken from `configs/hf/qwen3_8b/run_0/esp_bc30.yaml` and
`ema_bc30.yaml`: greedy, `max_new_tokens=100`, `stop_on_eos=true`,
`enable_thinking=false`, static tree `[14]`, BC=30, eager attention, seed 123.
AR is the paired baseline inside each run. GPU time for the five arms was
145–157 s each, about 13 minutes total, inside the 30-minute budget. Card:
RTX 5090 D v2, 24455 MiB.

| **Run** | **Pooled tau** | **Depth-1 accept** | **Speedup vs AR** | **exact_match** |
| --- | ---: | ---: | ---: | ---: |
| ESP, λ=0.1 update | 1.5469 | 0.5540 | 1.28 | 0.6538 |
| ESP, mask frozen | 1.5599 | 0.5671 | 1.29 | 0.5000 |
| EMA, step_scale=0 | 1.4301 | 0.4334 | 1.19 | 0.6154 |
| EMA, default γ=1 | 1.4289 | 0.4334 | 1.19 | 0.5385 |
| EMA, normalize | 1.4368 | 0.4421 | 1.19 | 0.5769 |

k=1, so depths 2 and 3 have no attempts. Output length is not 100 on every
prompt (EOS); pooled new tokens per prompt are 84.5–84.8, so the arms are
comparable. Per category there are only 2 prompts. EMA tau is below ESP in 11
categories and tied in 2 (extraction, qa). That sign is consistent on this
slice and is not a 480-prompt result.

Reading, limited to this slice:

- The history direction does nothing measurable. Default EMA and `step_scale=0`
  (mask = last committed embedding, no extrapolation) differ by 0.001 in pooled
  tau. Normalization does not recover the gap to ESP.
- The ESP–EMA gap is the anchor: prompt-mean mask versus last-token embedding.
- Freezing the ESP mask does not hurt on this slice (1.560 vs 1.547). With 26
  prompts that is not evidence that the update is useless in general.
- Both ESP and EMA are faster than AR here (about 40 and 35 tokens/s). That
  speedup is not lossless. See below.

### bf16 greedy is not lossless on this GPU

`exact_match` is 0.50–0.65, not 1. A separate pass over the ESP arm
(`_mismatch_index.py` in the result directory) found 9 mismatches. Every one
has a full-prefix top-2 logit gap of at most 0.25, which is one bf16 unit in
the last place around logit 30. The earliest mismatch is new-token index 9.
On 5 of the 9, a fresh full-prefix forward disagrees with the AR cache path
too, so this is not specific to the tree. Tiny-LLaMA fp32 checks still match
exactly. Do not treat these GPU runs as a losslessness failure of the tree or
the EMA update.

## 4. Code changes required to run this

- `src/data/{specbench,dolly,local_prompts}.py`: transformers 5
  `apply_chat_template(..., return_tensors='pt')` returns a `BatchEncoding`,
  not a Tensor. The Qwen run crashed until this was unwrapped.
- `src/spec/decoding.py` and `src/algorithms/esp_mtp.py`: per-depth attempt and
  accept counts. Depth 1 on this tree is the only depth that has drafts.

## 5. Qwen3-4B, same slice, float32

Weights: `D:\models\Qwen3-4B`, loaded as float32 (about 16 GB). Same 26-prompt
dev file, same BC=30 `[14]` tree, greedy, 100-token cap, seed 123. Five arms,
126–138 s each. Results: `results/cursor_20261006_history_audit/qwen3_4b_dev/`.

Every arm has `exact_match_rate=1.0000`. Every arm commits the same 2165
tokens, so tau differs only because the number of decode calls differs.

| **Run** | **Committed / calls** | **Pooled tau** | **Depth-1 accept** | **Speedup vs AR** |
| --- | ---: | ---: | ---: | ---: |
| ESP, λ=0.1 update | 2165 / 1468 | 1.4748 | 0.4796 | 1.19 |
| ESP, mask frozen | 2165 / 1495 | 1.4482 | 0.4548 | 1.19 |
| EMA, step_scale=0 | 2165 / 1563 | 1.3852 | 0.3896 | 1.13 |
| EMA, default γ=1 | 2165 / 1563 | 1.3852 | 0.3896 | 1.12 |
| EMA, normalize | 2165 / 1572 | 1.3772 | 0.3817 | 1.13 |

Default EMA and `step_scale=0` have the same pooled counts. Per prompt they
are not the same run: 6 of 26 prompts differ by one or two accepted drafts,
and those differences cancel. The history direction moves a few accepts and
does not raise the total. Normalization accepts 9 fewer drafts than the
zero-step control.

ESP stays ahead of every EMA arm. EMA's category tau is below ESP in 11
categories, tied on qa, and higher only on math_reasoning (2 prompts).
Freezing the ESP update costs 24 accepted drafts (704 → 680). On the 8B bf16
slice that comparison went the other way by a similar amount and was not
lossless, so the 4B float32 number is the one to keep.

Float32 exact match on this model also explains the 8B result: those
mismatches were bf16 top-2 ties, not a tree bug. Both models, on this same
slice, say the embedding-difference direction does not beat "mask = last
token".

## 6. Still not run

- The paper's 480-prompt, 256-token setting.
- A second tree (k>1) or any model other than Qwen3-8B and Qwen3-4B.
- Momentum Guidance reproduction. The confirmation set did not separate
  "follow vhat" from step 0, so that cell stays out. See section 7.

## 7. Qwen3-4B confirmation set, float32

Prescribed by `study_plan.md` section 5.6. Same model, tree `[14]`, BC=30,
greedy, 100-token cap, seed 123, float32. The slice is the next 4 questions
of each category after the 26-prompt exploration slice (`scripts/make_dev_slice.py
--skip 2 --take 4`): 52 prompts, 13 categories, question ids disjoint from
the exploration file. Output:
`results/cursor_20261006_history_audit/qwen3_4b_confirm/`.

Every arm has `exact_match_rate=1`. Every arm commits the same 4628 tokens
(4680 new tokens, one prefill token per prompt), so tau differs only by the
number of decode calls.

| **Run** | **Committed / calls** | **Pooled tau** | **Accepted** | **Depth-1 accept** | **Speedup vs AR** |
| --- | ---: | ---: | ---: | ---: | ---: |
| ESP, mask frozen | 4628 / 3183 | 1.4540 | 1462 | 0.4593 | 1.20 |
| EMA, step_scale=0 | 4628 / 3322 | 1.3931 | 1323 | 0.3983 | 1.13 |
| ESP, λ=0.1 update | 4628 / 3161 | 1.4641 | 1479 | 0.4679 | 1.20 |
| EMA, γ=1, β=0.9 | 4628 / 3326 | 1.3915 | 1319 | 0.3966 | 1.13 |
| EMA, normalize, γ=1 | 4628 / 3337 | 1.3869 | 1310 | 0.3926 | 1.12 |

Single-factor contrasts, exploration then confirmation:

| **Contrast** | **Exploration accepts** | **Confirmation accepts** | **Call** |
| --- | ---: | ---: | --- |
| Frozen prompt mean minus last token | +71 (680−609) | +139 (1462−1323) | Separated. Same sign, and the gap grew with the set. |
| ESP update minus frozen mean | +24 (704−680) | +17 (1479−1462) | Pooled sign repeats. Net is smaller than the category swings that cancel it (qa +26, coding +23, writing −22, roleplay −20). Not a stable factor. |
| Along vhat minus step 0 | 0 (609−609) | −4 (1319−1323) | Not separated. 9 of 52 prompts differ, seven of them by −1. |
| Normalize minus along vhat | −9 (600−609) | −9 (1310−1319) | Same sign, same small net, while 26 prompts move both ways. Not a stable factor. |

The anchor result is pooled, not uniform across categories. On the
confirmation set the frozen prompt mean accepts fewer drafts than the last
token on coding (−24) and qa (−11), and more on summarization (+41),
roleplay (+35), extraction (+22), and stem (+21).

Momentum Guidance's opposite-sign mask stays unimplemented.

## 8. Both orders, memory-length sweep (2026-10-06)

`study_plan.md` section 9. Mask is the updating prompt-mean plus the slope:

`m_i = m0 + i * vhat`, with `level=order0`, `step_scale=1`, no `1-β^s` debias.
Qwen3-4B float32, tree `[14]`, greedy, 100 tokens, seed 123. Every cell below
has `exact_match=1` and the same committed-token count as its order-0 control,
so tau moves only with the call count.

Stage A, 26-prompt exploration slice, λ=0.1. Control is ESP λ=0.1: 2165/1468,
tau 1.4748, 704 accepts. Output:
`results/cursor_20261006_history_audit/qwen3_4b_explore_order/`.

| **β** | **Half-life** | **Calls** | **Tau** | **Accepts** | **Versus order 0** |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0.5 | ~1 token | 1552 | 1.395 | 620 | −84 |
| 0.9 | ~7 | 1491 | 1.452 | 680 | −24 |
| 0.99 | ~70 | 1440 | 1.503 | 732 | +28 |
| 0.999 | ~700 | 1401 | 1.545 | 770 | +66 |
| 0.9999 | ~7000 | 1395 | 1.552 | 777 | +73 |

The short memories lose drafts. The long memories gain them, and the gain
grows with β. β=0.999 and β=0.9999 differ by 7 accepts.

Stage B, same 26 prompts, only at the two β values that disagreed most
(0.5 and 0.9999). λ=0.1 is the stage A row.

| **β** | **λ** | **Tau** | **Accepts** | **Versus order 0** |
| ---: | ---: | ---: | ---: | ---: |
| 0.5 | 0.5 | 1.386 | 610 | −94 |
| 0.5 | 0.1 | 1.395 | 620 | −84 |
| 0.5 | 0.01 | 1.402 | 629 | −75 |
| 0.5 | 0.001 | 1.397 | 622 | −82 |
| 0.5 | 0.0001 | 1.396 | 621 | −83 |
| 0.9999 | 0.5 | 1.519 | 750 | +46 |
| 0.9999 | 0.1 | 1.552 | 777 | +73 |
| 0.9999 | 0.01 | 1.548 | 776 | +72 |
| 0.9999 | 0.001 | 1.550 | 777 | +73 |
| 0.9999 | 0.0001 | 1.550 | 777 | +73 |

λ does not rescue β=0.5. At β=0.9999, λ=0.5 gives back part of the gain, and
λ from 0.1 down to 0.0001 is the same 72–73 drafts. The pair taken to the
holdout is β=0.9999, λ=0.1.

Stage C, holdout `--skip 6 --take 4`, 52 prompts, question ids disjoint from
both earlier slices. Output:
`results/cursor_20261006_history_audit/qwen3_4b_holdout/`.

| **Run** | **Committed / calls** | **Tau** | **Accepts** |
| --- | ---: | ---: | ---: |
| Order 0 only, λ=0.1 | 4600 / 3085 | 1.4911 | 1525 |
| Both orders, β=0.9999, λ=0.1 | 4600 / 2894 | 1.5895 | 1723 |

The slope adds 198 accepted drafts. 46 of 52 prompts move, and the positive
counts dominate. Same sign as the exploration slice (+73 there).
