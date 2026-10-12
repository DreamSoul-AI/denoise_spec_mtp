# PLAN — smoke_tiny_llama

## Goal

Verify the speculative MTP path on CPU through the installed RPipe (recipe-registered `spec_mtp` sources): random tiny LLaMA,
four synthetic prompts, greedy decoding, AR baseline enabled. Every variant
must reach `exact_match_rate = 1` on the overall summary row.

## Variants

| **variant** | **spec** |
| --- | --- |
| `esp_static` | ESP, static tree `[7, 2]`, efficient impl |
| `esp_dynamic` | ESP, dynamic tree BC=30, naive impl |
| `ema_velocity` | EMA-velocity masks, static `[7, 2]` |

## Run

```text
set PYTHONUTF8=1
python -m spec_mtp make studies/smoke_tiny_llama
studies/smoke_tiny_llama/scripts/launch.ps1
```

CI calls `python -m spec_mtp run studies/smoke_tiny_llama`; the scripts call `rpipe launch`. Both reach the same RPipe FlowRunner.

Study files: `recipe.py` (register + checks), `flow/write/run.py` (exact_match gate before the result is written), `flow/process/run.py` (Study scope: all three variants × seed present and passed).

Artifacts live under `studies/smoke_tiny_llama/runs/<id>/assets/` (`summary.csv`,
`spec_metrics.csv`, tracker). This directory is gitignored.

## Pass criteria

- Three succeeded Runs (one per variant); a Run with `exact_match_rate != 1` is written `failed`.
- Each `assets/summary.csv` has `category=overall` and `exact_match_rate=1`.
- `spec_mtp_study_check.json` has `complete: true, passed: true` and one SpecMTP source digest.
- Pooled `accept_d1` matches the pre-refactor baseline 27 / 31 / 8
  (refactor regression only; not a new research result).

## Refactor regression (2026-10-12)

`regression/capture.py` runs the same Studies on the old code (`b1f6191`) and the new code and records every
token sequence; `regression/compare.py` writes `regression/REFACTOR_REGRESSION.json`. Pass: every cell equal
(tokens, per-prompt rows, summaries, result status) except timing fields.
