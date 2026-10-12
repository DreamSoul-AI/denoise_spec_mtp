# Study 使用指南

怎么用**现在的代码**开一轮可复现实验。调度以这份 `src/rpipe/` 为准（`src/rpipe/ORIGIN`，RPipe `main` v0.3.0）。RPipe 原文在上游 `studies/readme.md`。这里只写 SpecMTP 多出来的部分。入口是 `python -m spec_mtp`。

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

- `recipe: recipe.py`，import 时 `register_sources()`，这样 make 能往 `shared/data` 落 Data
- `flow.study_phases: true`。**不要写 `prepare_shared: false`**，除非真的不能提前建构 Data
- Data → `shared/data`，权重 → `shared/model`（同一 Study 只下一遍）
- **不要写 `origin: foreign`**，见 [layout.md](../docs/layout.md)
- `flow/write`：`exact_match` 门；`flow/process`：Study scope 门
- SpecBench 源文件在 `datasets/spec_bench/`，不要把 jsonl 塞进 Study 目录当私货

## 3. 高效率排班

对照上游 `studies/readme.md` §3。写进 `docs/plan.md`。同类、相近耗时一组；0.6B 和 4B 不要同一 `wait`。seed ≠ 并发。Windows：`PYTHONUTF8=1`，ModelScope，`D:\anaconda3\python.exe`。

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
