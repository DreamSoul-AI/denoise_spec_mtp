# TESTING

Tests live under `tests/spec_mtp/` and follow `src/spec_mtp/`. They cover the SpecMTP modules and the contract with the installed RPipe (recipe registration, Flow hooks, provenance, entry points). RPipe's own behaviour is tested in the RPipe repo, not here.

## CPU gate (CI and local)

```text
set PYTHONUTF8=1
pip install -e ".[dev]"
python -m pytest tests/spec_mtp
```

Temporary files and the pytest cache go to `.tmp/`. End-to-end tests copy the smoke Study into a pytest temp dir; only `test_smoke_study_matches_plain_generation` runs the repository Study in place (its `runs/` is gitignored).

| **tests** | **what they cover** |
| --- | --- |
| `structure/algorithm/` | masks, trees, tree attention, KV cache, lossless decode and sampling RNG order, EMA history, named mask settings |
| `structure/algorithm/test_smoke_study.py` | smoke Study through `spec_mtp` and `rpipe` entries, make + launch scripts path, exact_match failure → failed Run, bad config fails before construction, freeze on SpecMTP and on Study sources |
| `structure/data/` | category windows and synthetic prompts |
| `structure/model/` | tiny LLaMA embed and forward |
| `structure/system/`, `control/`, `artifact/` | device / dtype, NamedDict, CSV rows |
| `flow/test_checks.py` | Run gate and Study-scope gate (missing, subset, failed, mixed source digest, seeds) |
| `test_recipe.py` | no registration on import, idempotent registration on RPipe registries, config boundary checks, source lock / freeze, repository Studies expand and validate |
| `test_package.py` | RPipe pinned and not vendored, console scripts do not override `rpipe`, source manifest coverage, cli lock rules |

## Refactor regression (manual)

`studies/smoke_tiny_llama/regression/` captures every decoder and AR token sequence plus per-prompt and summary metrics for the smoke Study and four extra tiny Studies (temperature 0 / 0.8, context limit, EOS, `ar_baseline` / `alignment_probe`, six named masks), on the old code (`b1f6191`) and the new code, and compares them. The committed result is `REFACTOR_REGRESSION.json`. It is a migration check, not a research result.
