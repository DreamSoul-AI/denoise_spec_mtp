# tools

Local utilities. No Docker, no weights, no network (except what an installed package already cached).

| **script** | **purpose** |
| --- | --- |
| `ci_local.py` | Replay `.github/workflows/cpu-checks.yml` in a fresh worktree and Python 3.12 venv. |
| `decode_fingerprint.py` | Capture tokens and decode stats for every shipped preset; `--compare` proves a change is output-identical. |
| `profile_cpu.py` | cProfile of `esp_mtp.evaluate` on a tiny model. tau / speed are not paper numbers. |
| `windows_selfcheck.py` | Windows native import order (`python -m rpipe` vs `python -m spec_mtp`). |

```text
python tools/<name>.py --help
```
