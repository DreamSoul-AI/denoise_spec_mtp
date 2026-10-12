# tools/

Local utilities. No Docker, no weights, no network (except what an installed package already cached).

| **script** | **purpose** |
| --- | --- |
| `ci_local.py` | Replay `.github/workflows/cpu-checks.yml` in a fresh worktree and Python 3.12 venv (install, ruff, mypy, pin check, pytest). Each run gets its own `.tmp/ci_local/<id>/`; an advisory lock serialises worktree add/remove. A local pass is not a GitHub Actions pass. |
| `paper_hf_dryrun.py` | Swap every `studies/paper_hf` Study onto a random tiny LLaMA and run the full chain; proves presets expand, decode, and pass gates. |
| `decode_fingerprint.py` | Capture tokens and decode stats for every shipped preset; `--compare` proves a change is output-identical. |
| `profile_cpu.py` | cProfile + optional unprofiled timing of `esp_mtp.evaluate` on a tiny model; see [PROFILE.md](../docs/PROFILE.md). |
| `windows_selfcheck.py` | Windows-only native import order probe (`SPEC_MTP_WIN_IMPORT_ORDER`); on Linux the switch is a no-op. |

```text
python tools/<name>.py --help
```

`studies/paper_hf/migrate_configs.py` lives next to the generated Studies (regenerate / `--check`), not here.
