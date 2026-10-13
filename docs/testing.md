# testing

`tests/spec_mtp/` 测 SpecMTP 以及它和这份 `src/rpipe/` 的合同。RPipe 自己的行为在上游测。

```text
set PYTHONUTF8=1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -e ".[dev]" --no-deps
ruff check src tests studies tools
mypy
python -m pytest tests/spec_mtp
```

工作流：`.github/workflows/cpu-checks.yml`。重放：`python tools/ci_local.py`。GPU Study 和真实权重不在 CI。冒烟必须 `exact_match_rate == 1`。

现有 GPU 环境不执行上面的 CPU torch 安装。测试使用独立 --basetemp=.tmp/<new-id>。Ruff 的 vendored facade 例外见 [兼容记录](bugs.md)。tiny 接受数是回归基线；完整链还检查原始 token、来源漂移、证据缺失和 Study 完整性。

CPU 剖析：`python tools/profile_cpu.py`。输出身份：`python tools/decode_fingerprint.py`。Windows：`python tools/windows_selfcheck.py`。
