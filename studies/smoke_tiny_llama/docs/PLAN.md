# PLAN — smoke_tiny_llama

## Goal

Verify the RPipe-wrapped speculative MTP path on CPU: random tiny LLaMA,
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

CI calls `python -m spec_mtp run studies/smoke_tiny_llama`, which is the runner that script starts.

Artifacts live under `studies/smoke_tiny_llama/runs/<id>/assets/` (`summary.csv`,
`spec_metrics.csv`, tracker). This directory is gitignored.

## Pass criteria

- Three succeeded Runs (one per variant).
- Each `assets/summary.csv` has `category=overall` and `exact_match_rate=1`.
- Pooled `accepted` counts match the legacy baseline captured before refactor
  (refactor regression only; not a new research result).
