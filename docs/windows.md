# windows

验证输出指定 --out .tmp/<new-id>/windows_selfcheck.json。现有 CUDA torch 环境不执行 CPU wheel 覆盖安装。

本机约定：`PYTHONUTF8=1`，`D:\anaconda3\python.exe`，不另建 venv。权重用 ModelScope。CI 不跑 Windows。

这台机器上 vendored `src/rpipe/__init__.py` 在 win32 上先 import torch（上游是 numpy-first）。不要加 `sitecustomize.py`。

```text
set PYTHONUTF8=1
python tools\windows_selfcheck.py
python tools\windows_selfcheck.py --smoke
```
