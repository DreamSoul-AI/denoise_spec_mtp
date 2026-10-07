# TESTING

## CPU gate (CI and local)

```text
set PYTHONUTF8=1
pip install -e .
python scripts/run_ci_checks.py
```

Plans:

| **plan** | **checks** |
| --- | --- |
| `cpu_pr_checks` | correctness + ema_history + RPipe smoke study |
| `cpu_smoke_only` | `studies/smoke_tiny_llama` via `python -m rpipe run` |

Evidence: `.test-results/<run_id>/` (`manifest.json`, `results.jsonl`, `report.md`).

## Correctness scripts

| **script** | **role** |
| --- | --- |
| `tests/spec_mtp/spec/test_correctness.py` | masks, trees, lossless decode |
| `tests/spec_mtp/spec/test_ema_history.py` | EMA velocity state hygiene |

Legacy YAML smoke (`configs/smoke/`, `src/main.py`) remains for ad-hoc runs;
CI uses the RPipe study.

## Optional RPipe suite

```text
python tests/run.py --core
```

Requires full `tests/rpipe/` markers (see upstream TESTING.md in `.tmp/RPipe`).
