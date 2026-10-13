# Study 使用指南

怎么用**现在的代码**开一轮可复现实验。调度以这份 `src/rpipe/` 为准（`src/rpipe/ORIGIN`，RPipe `main` v0.3.0）。RPipe 原文在上游 `studies/README.md`。这里只写 SpecMTP 多出来的部分。入口是 `python -m spec_mtp`。

## 1. 三个词

| **比较项** | **Study** | **Experiment** | **Run** |
| --- | --- | --- | --- |
| 是什么 | 这一轮研究的壳 + 磁盘根 | 研究因素的一个取值点 | 该点 × 一个 seed 的一次实测 |
| 含 seed？ | 声明 `seeds` | **不含** | **至少**一个 |
| 磁盘 | `studies/<name>/` | **无文件夹** | `runs/<id>/` |

`axes` → Experiment；每个 × `seeds` → Run。表里的数是接受的 draft 数。`exact_match_rate` 必须是 1。速度和 `tau` 不决定结论。不把 γ 叫成 slope。

## 2. 你要准备的文件

从 [`_template/`](_template/) 复制。`docs/plan.md` 开跑前写；`docs/study_report.md` 跑完后写。

SpecMTP 固定写法：

- `recipe: recipe.py`，import 时 `register_sources()`
- `flow.study_phases: true`，`prepare_shared: false`（RPipe 的 make 下载只认 MNIST/CIFAR；SpecMTP 的 Data/权重在 **Run prepare** 写入 `shared/`）
- SpecBench → `shared/data/specbench/`，ModelScope / HF 权重 → `shared/model/`（同一 Study 只下一遍）
- **不要写 `origin: foreign`**，见 [layout.md](../docs/layout.md)
- `flow/collect`：从 raw 计算 CSV/Tracker；`flow/summarize`：成功门；`flow/write`：证据/来源复验；`flow/process`：当前 index 的 Study 终验
- 新实测写 algorithm.config.version，源码/输入改变后先改 version 再 make/remake。普通 run/launch 不刷新已有来源锁，不签收旧产物
- SpecBench 源文件在 `datasets/spec_bench/`，不要把 jsonl 塞进 Study 目录当私货

## 3. 高效率排班

对照上游 `studies/README.md` §3。写进 `docs/plan.md`。GPU 先 --round 1 串行校准权重/KV/树/mask/进程峰值，再用 system.config.vram_bytes 记录预算，小步扩大独立 Run 并发。速度对照不竞争资源；0.6B 和 4B 不同 wait。seed ≠ 并发。Windows：`PYTHONUTF8=1`，ModelScope，`D:\anaconda3\python.exe`。

## 4. 一条命令

```text
set PYTHONUTF8=1
python -m spec_mtp make studies/<name> --num-gpus 1 --init-gpu 0
python -m spec_mtp launch studies/<name> --num-gpus 1 --init-gpu 0
```

## 5. 现成 Study

| **Study** | **状态** | **问题** |
| --- | --- | --- |
| [smoke](smoke/docs/plan.md) | CPU 门 | 三种 mask 是否与普通生成逐 token 一致 |
| [_template](_template/docs/plan.md) | 空模板 | 复制后再写 |

已记下的接受数在 [history-extrapolation.md](../docs/history-extrapolation.md)，不是一个可再跑的 Study。
