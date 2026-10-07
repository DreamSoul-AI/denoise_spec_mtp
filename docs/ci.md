# CI setup

Status: **running on GitHub.** Local blocking behaviour was verified on
2026-10-06. The check context is `cpu-checks`. The Actions page shows it as
`cpu-checks / cpu-checks`.

## Branch flow

`feature/*` / `fix/*` → PR → `dev` → release PR → `main`. Do not push directly
to `dev` or `main`.

| **Branch** | **Role** |
| --- | --- |
| `main` | Release line. Stays at `b636f90` (`fix gitignore`), the reproduction baseline. The history audit is not on `main`. |
| `dev` | Integration line. The history audit and the doc consolidation, ahead of `main`. |
| `feature/rpipe-refactor` | Cut from `dev` for the RPipe refactor. No refactor commits yet. |

`feature/research-ema-history-audit` is retired. Its commits are on `dev`.

The two commits `dev` adds over `main` already passed this check:

- [Add order-0 gamma masks and the history audit](https://github.com/DreamSoul-AI/denoise_spec_mtp/actions/runs/37499541219)
- [Consolidate the docs and record the RPipe refactor](https://github.com/DreamSoul-AI/denoise_spec_mtp/actions/runs/37670855461)

## Workflow

| **Item** | **Value** |
| --- | --- |
| File | `.github/workflows/cpu-checks.yml` |
| Required check context | `cpu-checks` |
| Triggers | push to `feature/**`, `fix/**`; PR into `dev`, `main`; manual |
| Runner | `ubuntu-24.04`, Python 3.12, CPU torch wheel, 30 min timeout |
| Permissions | `contents: read` only, no secrets |
| Artifacts | `.test-results/` uploaded on success and failure, kept 30 days |
| Maintainer | to be assigned by the repo owner |

## Entry point and plans

Local and CI both run:

```bash
python scripts/run_ci_checks.py --plan cpu_pr_checks
```

| **plan_id** | **Checks** |
| --- | --- |
| `cpu_pr_checks` | `tests/check_correctness.py`, `tests/check_ema_history.py`, three tiny-LLaMA smoke configs |
| `cpu_smoke_only` | the three smoke configs |

A smoke check passes only if the process exits 0 and the `overall` row has
`exact_match_rate == 1.0`. Any failed, missing or incomplete check makes the
run fail with exit code 1.

## Result protocol

Each run writes `.test-results/<run_id>/`:

- `manifest.json`: `run_id`, `plan_id`, commit, branch, dirty flag, environment, selected checks and commands, final status
- `results.jsonl`: one line per check, appended as each finishes
- `<check>.log`: raw output
- `smoke/<name>/`: smoke CSVs, isolated from `results/`
- `report.md`: generated even after a failure

## Out of scope

GPU model runs (`scripts/run_main_results.sh`, ablations) need weights and a
GPU. They are not in CI and must not be reported as CI-verified.
