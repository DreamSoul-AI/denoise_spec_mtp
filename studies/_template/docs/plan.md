# Study Plan: my_study

> 对照 [studies/readme.md](../../readme.md) §3。跑完后写同目录 `study_report.md`。不要跑 `_template` 本身。不要写 `origin: foreign`（[layout.md](../../../docs/layout.md)）。

## 1. 研究问题

（这一轮要比什么？成功长什么样？）

## 2. Study / Experiment / Run

- Study 名：`my_study`
- Experiment：由 `axes` 展开（不含 seed）
- Run：每个 Experiment × `seeds`

## 3. 变量轴

| **轴** | **字段** | **取值** |
| --- | --- | --- |
| （因素） | | |

## 4. 固定条件

| **项** | **取值** |
| --- | --- |
| `seeds` | `123` |
| `system.device` | `cuda` |
| `eval.temperature` | `0` |
| `exact_match_rate` | 必须是 1，否则该格作废 |

## 5. 高效率排班（§3）

- GPU 先以 --round 1 串行测量实际权重、KV cache、树展开、mask 计算和进程峰值；没有实测预算时不使用视觉训练的显存估计扩大并发。
- 校准后可用 system.config.vram_bytes 记录保守的实际预算，再小步增加独立 Run 的并发。每个 Run 独占解码状态与产物；不重叠启动多个 launch。
- 同任务量的速度比较串行进行，记录预热、同步、backend、实际生成长度和整体墙钟；不按不同负载的单 Run 时间排名。
- wait 组末等进程退出与显存释放，保留 OOM/失败；后续重算使用新 version/Run ID，不把已有成功产物当新验收。
- seed 不表示并发；不在预注册结论的那组调 β/λ/γ，已有数字格子不重跑。

```text
set PYTHONUTF8=1
python -m spec_mtp make studies/<name> --num-gpus 1 --init-gpu 0 --round 1
python -m spec_mtp launch studies/<name> --num-gpus 1 --init-gpu 0
```

`python -m spec_mtp make` = `python -m rpipe make` 加 SpecMTP 源码清单。不要从 `src/main.py` 进。

### 5.1 时长预估

`make` 之后、`launch` 之前填。同一 `wait` 的墙钟取该组最慢的一条。不含显存。

| **wait** | **factors** | **mode** | **seed** | **id** | **est** |
| ---: | --- | --- | ---: | --- | ---: |
|  |  | eval |  |  |  |
|  | 整轮 | | | |  |

## 6. 成功标准

- 计划的 Run 均 `status: succeeded`
- 每个 overall 行 `exact_match_rate == 1`；summarize/write 完成原始 token、接受/cache、输入与来源核验
- 主指标是接受的 draft 数；速度不参与判定
- `study_report.md` 按 Experiment 写结论

## 7. 执行范围与刻意不做

填写本轮允许执行的规模。列出不重跑的已有格子。
