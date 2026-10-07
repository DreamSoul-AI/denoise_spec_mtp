# CI setup

Status: **configured.** The local run and the blocking behaviour were verified
on 2026-10-06. The workflow file is on `origin`. A green GitHub run is a
separate fact from this page, and the required check is not yet set in
branch protection.

## Branch flow

`feature/*` / `fix/*` → PR → `dev` → release PR → `main`. Do not push directly
to `dev` or `main`. `dev` exists locally only until a maintainer creates it on
`origin`.

## Workflow

| **Item** | **Value** |
| --- | --- |
| File | `.github/workflows/cpu-checks.yml` |
| Required check name | `cpu-checks / cpu-checks` |
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
