# plan — smoke

CPU tiny LLaMA，四种合成 prompt，三种 mask variant。`exact_match_rate` 必须是 1。权重不下载；Data / 随机模型仍走 Study `shared/`。

## 高效率排班

CPU 串行一组即可。

```text
set PYTHONUTF8=1
python -m spec_mtp make studies/smoke
python -m spec_mtp launch studies/smoke
```

CI：`python -m spec_mtp run studies/smoke`。
