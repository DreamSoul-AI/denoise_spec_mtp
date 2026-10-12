# Windows

**未在 Windows 上验证。** 本轮（2026-10-12）只在 Linux 上测了开关逻辑和自检脚本本身。

## 导入顺序开关

旧包在 win32 上先 import Torch（2026-10-06 本机：先 import NumPy 会在 `blas_fpe_check` 出错）。RPipe dev 在 win32 上先 import NumPy（与 Conda NumPy 共用 libiomp5md）。两者相反，现在用环境变量切换：

| **`SPEC_MTP_WIN_IMPORT_ORDER`** | **行为** |
| --- | --- |
| 不设 / `torch` | 先 Torch（旧包行为，默认）；没装 Torch 时退回 NumPy |
| `numpy` | 先 NumPy（同 RPipe dev） |
| `off` | spec_mtp 不预导入，谁先 import 谁决定 |

只在 `sys.platform == 'win32'` 生效。`python -m spec_mtp` 走包入口的 preload。editable 安装还会加载 `src/sitecustomize.py`（site.py 在把 `src/` 加进 `sys.path` 之后 import），所以 `python -m rpipe` 和生成的 `launch.ps1` / `run-one` 也会先 Torch。取值写错会在 import 时报错。代码在 `src/spec_mtp/_win_import.py`。

## 自检

```text
set PYTHONUTF8=1
python tools\windows_selfcheck.py
python tools\windows_selfcheck.py --smoke
```

每个用例开一个新进程：三种取值加默认（spec_mtp 先导入），以及 rpipe 先导入；每个用例做 NumPy / Torch 矩阵运算和一次 tiny LLaMA 前向。`--smoke` 再对通过的取值各跑一次 `studies/smoke_tiny_llama`（CPU，副本在临时目录）。结果打印成表并写 `windows_selfcheck.json`，全部通过时退出码 0。不下载权重、不联网。

选默认值的依据：自检里哪种取值通过就用哪种。若 `torch` 和 `numpy` 都通过，可以改成 `numpy` 与 RPipe 一致；若只有 `torch` 通过，`python -m rpipe` 入口在这台机器上可能出错，应改用 `python -m spec_mtp`。
