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

- **同类一组：** 同一模型、相近树宽的 Run 一起并行；不要把 0.6B 和 4B 塞进同一 `wait`。
- **`wait` 闸门：** 组末必须等本组进程退出、显存释放完，才开下一组。
- **吃满 GPU：** `python -m spec_mtp make studies/<name> --num-gpus 1` 默认 `--round auto`；看 **make** 打印的 `pack N waits`。
- **eval 格子：** SpecMTP 默认没有 train 波。仍按显存装箱，不要全局一个 `--round` 把轻重砍齐。
- **error：** 单条失败记 `run_id`；本波结束后对未 succeeded 的再跑。
- **seed ≠ 并发。** 不在检验预注册结论的那一组上再调 β、λ、γ。已记下的格子不重跑。

```text
set PYTHONUTF8=1
python -m spec_mtp make studies/<name> --num-gpus 1 --init-gpu 0
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
- 每个 overall 行 `exact_match_rate == 1`
- 主指标是接受的 draft 数；速度不参与判定
- `study_report.md` 按 Experiment 写结论

## 7. 执行范围与刻意不做

填写本轮允许执行的规模。列出不重跑的已有格子。
