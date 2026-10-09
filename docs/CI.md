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
| `refactor/spec-rpipe` | RPipe layout: `src/spec_mtp` follows RPipe; SpecMTP code is in each layer's `spec_mtp/` submodule. |

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
| Maintainer | to be assigned by the repo owner |

## Entry point and plans

Local and CI both run:

```bash
pip install -e .
python -m pytest tests/spec_mtp
```

The suite is the SpecMTP modules under `tests/spec_mtp/`, including the smoke Study. A smoke variant passes only when its `overall` row has `exact_match_rate == 1.0`.

## Result protocol

Pytest writes its cache under `.tmp/pytest-cache/` (gitignored). Smoke CSVs live under `studies/smoke_tiny_llama/runs/*/assets/` (gitignored).

## Out of scope

GPU cells are Studies under `studies/`. They need weights and a GPU.
They are not in CI and must not be reported as CI-verified.
