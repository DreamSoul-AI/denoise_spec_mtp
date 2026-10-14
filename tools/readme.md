# tools

Local utilities. Model-window diagnostics use explicitly prepared local weights; no automatic downloads.

| **script** | **purpose** |
| --- | --- |
| `diagnose_q178_operators.py` | Fixed post-entry provider slot precision and norm backend controls with canonical states; CUDA profiler names are localization evidence, full AR/path gates remain required. |
| `ci_local.py` | Replay `.github/workflows/cpu-checks.yml` in a fresh worktree and Python 3.12 venv. |
| `decode_fingerprint.py` | Capture tokens and decode stats for every shipped preset; `--compare` proves a change is output-identical. |
| `profile_cpu.py` | cProfile of `esp_mtp.evaluate` on a tiny model. tau / speed are not paper numbers. |
| `diagnose_output_windows.py` | Read-only q173 matched-window replay around the unchanged decoder; requires identical tokens/traces, records previous seed masks/logits and exact hidden consistency. |
| `diagnose_q178_numerics.py` | Process-only strict FP32 repeats and AR-prefix canonical committed-state controls, with actual KV-root checks and two self-value controls. |
| `diagnose_study_windows.py` | Manifest-bound four-prompt runner reusing frozen window/observer/transfer/slot helpers; intended for the q179–q182 follow-up. |
| `diagnose_extension.py` | Fixed q175–q178 selection and transfer replications; reuse unchanged observer/transfer/compare helpers, allow measured path/state differences and preserve planned fallback controls. |
| `diagnose_cross_prompt.py` | Fixed q171/q172/q174 replication: reuse unchanged observer/transfer helpers, both directions and original-value placebo; retain nulls, full traces and matched committed-state differences. |
| `diagnose_proxy_transfer.py` | Three fixed q173 single-slot transfers around the unchanged decoder, with original-value placebo, actual post-intervention owner selection and lossless-output gates. |
| `diagnose_mask_scale.py` | Four fixed root83 prefix forwards cross two actual seed-mask directions with two observed norms; no generated tokens or tuned default. |
| `package_selfcheck.py` | Build wheel/sdist, install into separate targets, validate both module/console entries and native + SpecMTP CLI chains; no dependency replacement. |
| `windows_selfcheck.py` | Windows native import order (`python -m rpipe` vs `python -m spec_mtp`). |

```text
python tools/<name>.py --help
```

Package check: `python tools/package_selfcheck.py --workspace .tmp/package-<new-id>`. The directory must be new. It reuses installed scientific dependencies, so it checks distribution isolation rather than a fresh dependency environment. Windows check: `python tools/windows_selfcheck.py --smoke --out .tmp/<new-id>/windows.json`; each smoke uses a fresh version and preserves its raw logs.

`diagnose_q178_norm_kernel.py --out .tmp/<new-id>`：固定q178 CUDA norm图对照，保存实际kernel关联、entry/post和numerical-effect flags。
`diagnose_q178_qproj.py --out .tmp/<new-id>`：固定85块layer0 row4 packing／FP64对照，4克隆cache块精确重放。

`diagnose_q178_phi_rms.py --out .tmp/<new-id>`：固定entry Phi和post-attention RMSNorm精度对照，区分有效／bit等价。
`diagnose_q241_canonical.py --out .tmp/<new-id>`：首个跨任务阳性的独立canonical合同，保留自值变化及等计数不同路径。
