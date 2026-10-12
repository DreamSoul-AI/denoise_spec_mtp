# TESTING

Tests live under `tests/spec_mtp/` and follow `src/spec_mtp/`. They cover the SpecMTP modules and the contract with the installed RPipe (recipe registration, Flow hooks, provenance, entry points). RPipe's own behaviour is tested in the RPipe repo, not here.

## CPU gate (CI and local)

```text
set PYTHONUTF8=1
pip install -e ".[dev]"
ruff check src tests studies tools
mypy
python -m pytest tests/spec_mtp
```

`python tools/ci_local.py` replays `.github/workflows/cpu-checks.yml` in a fresh worktree and venv (see [CI.md](CI.md)).

Temporary files and the pytest cache go to `.tmp/`. End-to-end tests copy the smoke Study into a pytest temp dir; only `test_smoke_study_matches_plain_generation` runs the repository Study in place (its `runs/` is gitignored).

| **tests** | **what they cover** |
| --- | --- |
| `structure/algorithm/` | masks, trees, tree attention, KV cache, lossless decode and sampling RNG order, EMA history, named mask settings |
| `structure/algorithm/test_smoke_study.py` | smoke Study through `spec_mtp` and `rpipe` entries, make + launch scripts path, exact_match failure → failed Run, bad config fails before construction, freeze on SpecMTP and on Study sources |
| `structure/data/` | category windows and synthetic prompts |
| `structure/model/` | tiny LLaMA embed and forward |
| `structure/system/`, `control/`, `artifact/` | device / dtype, NamedDict, CSV rows |
| `flow/test_checks.py` | Run gate and Study-scope gate (missing, subset, failed, mixed source digest, seeds, empty index, explicit expected factors); per-task asset rules (ar_baseline summary, alignment_probe CSV), empty rate, duplicate overall rows |
| `test_recipe.py` | no registration on import, idempotent registration on RPipe registries, config boundary checks, source lock / freeze, repository Studies expand and validate |
| `test_paper_hf.py` | `studies/paper_hf/` generated files current; 59 legacy `configs/hf` cells = 59 expanded Runs (data / model / task / eval / effective spec / seed); recipe checks. No weights, no GPU |
| `test_paper_hf_dryrun.py` | `tools/paper_hf_dryrun.py` swaps only model / data / budget / device; one tiny Run per task (esp_mtp temp 0 and 1, ar_baseline, alignment_probe) through recipe, gates and Study process |
| `test_properties.py` | hypothesis properties: source digest order-free and change-sensitive, `changed_files` symmetric, `declared_factors` = full product, gate passes iff rate is 1, variant presets idempotent / case-insensitive / unknown rejected, Windows switch parsing, cli command and Study argument parsing, cli forwards to RPipe |
| `test_profile_tool.py` | `tools/profile_cpu.py` component buckets; a tiny profiled run keeps exact match (report: [PROFILE.md](PROFILE.md)) |
| `test_win_import.py` | `SPEC_MTP_WIN_IMPORT_ORDER` logic (real DLL order needs Windows: `tools/windows_selfcheck.py`) |
| `test_package.py` | RPipe pinned and not vendored, console scripts do not override `rpipe`, source manifest coverage, cli lock rules |

## Refactor regression (manual)

`studies/smoke_tiny_llama/regression/` captures every decoder and AR token sequence plus per-prompt and summary metrics for the smoke Study and four extra tiny Studies (temperature 0 / 0.8, context limit, EOS, `ar_baseline` / `alignment_probe`, six named masks), on the old code (`b1f6191`) and the new code, and compares them. The committed result is `REFACTOR_REGRESSION.json`. It is a migration check, not a research result. After the context-limit fix (option A), `ctx_check.py` checks the old capture against the merged code: context-limit cells reach `exact_match_rate = 1` and every other cell stays identical (`CONTEXT_LIMIT_OPTION_A.json`, [CONTEXT_LIMIT.md](CONTEXT_LIMIT.md)). `test_context_limit.py` and `test_context_limit_run_passes_on_reached_budget` cover it in CI.
