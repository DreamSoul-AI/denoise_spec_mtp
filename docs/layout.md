# layout

`src/rpipe/` 是上游 RPipe `main` 的文件拷贝，提交 `804b3823ab6d2af46cbda1a65688ca8b76c60b22`（`src/rpipe/ORIGIN`，v0.3.0）。`src/spec_mtp/` 只放 SpecMTP，经 Study recipe 注册。不要把 SpecMTP 写进 `rpipe` 的默认 source。

```text
src/
  rpipe/                   vendored RPipe；Windows 上 __init__.py 先 import torch
  spec_mtp/
    recipe.py              register_sources + register(ctx)
    cli.py                 薄入口：make 写源码锁，其余转给 rpipe
    flow/checks.py         summarize/write 证据门、Study scope 门
    structure/artifact/evidence.py   实际权重/输入/runtime 证据
    structure/             algorithm / data / model / system / control / artifact
datasets/spec_bench/       SpecBench 源文件；Run prepare 拷进 shared/data
studies/                   见 studies/readme.md
configs/hf/                论文格子的旧 YAML；不是入口
tools/                     ci_local.py, windows_selfcheck.py, profile_cpu.py,
                           decode_fingerprint.py
tests/spec_mtp/            跟着 src/spec_mtp
docs/                      architecture, layout, testing, windows, brainstorm,
                           history-extrapolation；research/；papers/
```

产物：`studies/<name>/runs/<id>/`。`runs/`、`shared/`、`scripts/`、`index.json`、`process.json`、`provenance.json`、`spec_mtp_sources.json` 不进 git。

## shared/

RPipe 的 make 共享下载只认识 torchvision 数据集。SpecMTP Study 写 `flow.prepare_shared: false`，但 **Run prepare 仍然把东西写进 `shared/`**：

- SpecBench jsonl → `studies/<name>/shared/data/specbench/`
- ModelScope / HF 权重 → `studies/<name>/shared/model/`

同一 Study 里不要让每个 Run 再下一遍。源文件在 `datasets/spec_bench/`。

Study `recipe.py` 在 import 时调用 `register_sources()`。

## 不要写 `origin: foreign`

这是本仓库相对 RPipe 的规则。缺省就是 foreign，并且不改环境变量。一旦写出 `origin`，prepare 会设置 `HF_ENDPOINT`。权重走 `model.config.hub: modelscope`。只有需要 RPipe 去改 HF 镜像时才写 `origin: domestic`。
