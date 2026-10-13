# tools

Local utilities. No Docker, no weights, no network (except what an installed package already cached).

| **script** | **purpose** |
| --- | --- |
| `ci_local.py` | Replay `.github/workflows/cpu-checks.yml` in a fresh worktree and Python 3.12 venv. |
| `decode_fingerprint.py` | Capture tokens and decode stats for every shipped preset; `--compare` proves a change is output-identical. |
| `profile_cpu.py` | cProfile of `esp_mtp.evaluate` on a tiny model. tau / speed are not paper numbers. |
| `package_selfcheck.py` | Build wheel/sdist, install into separate targets, validate both module/console entries and native + SpecMTP CLI chains; no dependency replacement. |
| `windows_selfcheck.py` | Windows native import order (`python -m rpipe` vs `python -m spec_mtp`). |

```text
python tools/<name>.py --help
```

Package check: `python tools/package_selfcheck.py --workspace .tmp/package-<new-id>`. The directory must be new. It reuses installed scientific dependencies, so it checks distribution isolation rather than a fresh dependency environment. Windows check: `python tools/windows_selfcheck.py --smoke --out .tmp/<new-id>/windows.json`; each smoke uses a fresh version and preserves its raw logs.
