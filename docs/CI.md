# CI setup

Status: **success runs exist; merge blocking is not verified yet.** Local
blocking behaviour was verified on 2026-10-06. The check context is
`cpu-checks`. The Actions page shows it as `cpu-checks / cpu-checks`.

This workflow is the CI check only. It does not build a release artifact and
it does not publish anything. A green run is not a release.

## Branch flow

`feature/*` / `fix/*` / `refactor/*` → PR → `dev` → release PR → `main`.
Do not push directly to `dev` or `main`. Work branches are deleted after they
merge. Naming follows `feature/<scope>-<name>`, `fix/<scope>-<name>`, and
`refactor/<scope>-<name>`.

| **Branch** | **Role** |
| --- | --- |
| `main` | Release line. Stays at `b636f90` (`fix gitignore`), the reproduction baseline. The history audit is not on `main`. |
| `dev` | Integration line. Daily PRs land here. It is ahead of `main` by the history audit and the doc consolidation. |
| `refactor/spec-rpipe` | RPipe refactor branch (vendor `src/rpipe`, `studies/smoke_tiny_llama`). |

`feature/research-ema-history-audit` is retired. Its commits are on `dev`.

The commits that moved the history audit onto the integration line already passed this check:

- [Add order-0 gamma masks and the history audit](https://github.com/DreamSoul-AI/denoise_spec_mtp/actions/runs/37499541219)
- [Consolidate the docs and record the RPipe refactor](https://github.com/DreamSoul-AI/denoise_spec_mtp/actions/runs/37670855461)

## Workflow

| **Item** | **Value** |
| --- | --- |
| File | `.github/workflows/cpu-checks.yml` |
| Required check context | `cpu-checks` |
| Triggers | push to `feature/**`, `fix/**`, `refactor/**`, and `dev`; PR into `dev` or `main`; manual |
| Runner | `ubuntu-24.04`, Python 3.12, CPU torch wheel, 30 min timeout |
| Permissions | `contents: read` only, no secrets |
| Artifacts | `.test-results/` uploaded on success and failure, kept 30 days |
| Maintainer | to be assigned by the repo owner |

## Entry point and plans

Local and CI both run:

```bash
pip install -e .
python scripts/run_ci_checks.py --plan cpu_pr_checks
```

| **plan_id** | **Checks** |
| --- | --- |
| `cpu_pr_checks` | `tests/spec_mtp/spec/test_correctness.py`, `test_ema_history.py`, RPipe `studies/smoke_tiny_llama` |
| `cpu_smoke_only` | RPipe smoke study only |

A smoke check passes only if the process exits 0 and the `overall` row has
`exact_match_rate == 1.0`. Any failed, missing or incomplete check makes the
run fail with exit code 1.

## Result protocol

Each run writes `.test-results/<run_id>/`:

- `manifest.json`: `run_id`, `plan_id`, commit, branch, dirty flag, environment, selected checks and commands, final status
- `results.jsonl`: one line per check, appended as each finishes
- `<check>.log`: raw output
- Smoke CSVs live under `studies/smoke_tiny_llama/runs/*/assets/` (gitignored), not `results/`
- `report.md`: generated even after a failure

## Out of scope

GPU model runs (`scripts/run_main_results.sh`, ablations) need weights and a
GPU. They are not in CI and must not be reported as CI-verified.
