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

脚本在 Study 目录里，由 `make` 生成。不要从仓库根的 `src/main.py` 进。
