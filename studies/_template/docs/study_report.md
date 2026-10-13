# Study Report: my_study

## 摘要

| **项目** | **内容** |
| --- | --- |
| 研究目标 | 填写本轮要回答的问题，链接 [plan.md](plan.md) |
| 记录日期与实验日期 | 分别填写 |
| 主要结果 | 按 Experiment 汇总接受的 draft 数；`exact_match_rate` 必须是 1 |
| 当前状态 | 区分执行完成、质量通过、跳过、失败和未执行 |
| 验证边界与未完成项 | 填写不可比条件、缺失证据与下一步 |

数字来源为 `summary.csv` / Study 根的 `process.json`。日志引用各 Run 的 `assets/logs/run.log`。

## 1. 怎么跑的（§3）

```text
python -m spec_mtp make studies/<name> --num-gpus 1 --init-gpu 0
python -m spec_mtp launch studies/<name> --num-gpus 1 --init-gpu 0
```

make 打印的 `pack N waits:` 。整轮预估 ___，实际 ___。error / resume：（有则记 `run_id`）。

## 2. 结果与结论

按 Experiment 聚合，不要扁平 run 列表。主指标是 `accept_d1`（深度 2 时用 `accept_d1+accept_d2`）。速度和 `tau` 不决定结论。

## 3. Run 明细

| **factors** | **seed** | **id** | **exact_match** | **accept_d1** | **est** | **actual** | **log** |
| --- | --- | --- | --- | --- | --- | --- | --- |
|  |  |  |  |  |  |  | `../runs/<id>/assets/logs/run.log` |

## 4. 复现条件

记录源码提交、`src/rpipe/ORIGIN`、环境、数据切片、seed、实际预算。独立重跑使用新 `version`，保留旧证据。
