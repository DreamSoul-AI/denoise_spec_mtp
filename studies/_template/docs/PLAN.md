# PLAN — my_study

写在开跑之前。复制本目录后再改问题和判定。

## 一、问题

## 二、判定

1. `exact_match_rate` 必须是 1，否则该格作废。
2. 主指标写在这里。速度不参与判定。

## 三、固定

## 四、刻意不做

## 五、怎么跑

```text
set PYTHONUTF8=1
python -m spec_mtp make studies/<name>
studies/<name>/scripts/launch.ps1
```

`python -m spec_mtp make` = `python -m rpipe make` 加 SpecMTP 源码清单（`spec_mtp_sources.json`）。脚本在 Study 目录里，由 `make` 生成，转调 `rpipe launch`。不要从仓库根的 `src/main.py` 进。

`recipe.py` 注册 SpecMTP source；`flow/write/run.py` 在 result 定稿前执行 `exact_match_rate` 门；`flow/process/run.py` 只在 Study scope 检查全部声明格子是否齐全且通过。没有额外职责的阶段不加 hook。
