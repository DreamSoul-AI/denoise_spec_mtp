# Architecture

Training-free multi-token prediction. One decode loop, two mask providers: ESP and EMA-velocity. The mask is a vector in input-embedding space, concatenated into `inputs_embeds`. It is not mapped back to a token id. The model emits logits; greedy or sampled argmax yields a real token; verification compares token ids.

Paper: *Efficient Training-Free Multi-Token Prediction via Embedding-Space Probing*, [arXiv:2603.17942](https://arxiv.org/abs/2603.17942). Local PDF: `docs/papers/2603.17942v2.pdf`.

调度来自 vendored RPipe（[layout.md](layout.md)）。解码是 eval Algorithm `(eval, spec_mtp)`，由 Study `recipe.register(ctx)` 注册。

## Run path and gates

`python -m spec_mtp` / `python -m rpipe` → prepare → recipe（校验、注册、来源锁）→ 建构 Data / Model / Algorithm → execute 保存 raw → Study collect 计算指标 → Study summarize 拒绝失配 → Study write 再验来源与证据 → 库定稿 result → process。AR 基线开着且 `exact_match_rate != 1`，或缺少 overall 行，该 Run 为 `failed`。Study scope 的 process 在缺 Run、失败、或集合是 index 的真子集时不通过。

RPipe 的 `provenance.json` 只哈希 `rpipe` 包和 Study 文件。SpecMTP 在 Study 外面，所以 `spec_mtp.structure.artifact.sources` 哈希 `src/spec_mtp/**/*.py`，make 时写 `spec_mtp_sources.json`。存在专项锁时源码变更在建构前失败；freeze:true 还要求锁存在。执行快照与当前来源在 summarize/write/process 再核对。

Float32 greedy、共享 seed，必须和普通生成逐 token 一致。`exact_match` 是这个审计，不是质量指标。质量指标是接受的 draft 数（[history-extrapolation.md](history-extrapolation.md)）。

专项阶段职责实现位于 `spec_mtp.flow/{collect,summarize,write,process}/run.py`；证据判断位于 `structure/artifact/validation.py`，跨层输入和 recipe 经 `structure/api/`。Study 仅导入阶段 run，prepare/execute 继续复用库默认阶段。根 cli/recipe、flow.checks 和 data.prompts 保留兼容导出；详细旧新映射见 [rpipe-migration.md](rpipe-migration.md)。

## One decode step

1. 已提交 token：`e = E[x]`。
2. mask provider 给出 `k` 个向量，接在 root 和每个 draft 节点后面。
3. 一次 forward 覆盖 `[root | tree nodes | k masks per node]`。块大小 `(k+1)(1 + sum K_i)`。
4. 沿模型自己的 next-token 链走树。token id 相同则接受；第一次失配是 bonus token。
5. 只把已提交 token 再 embed 给 provider。被拒的 draft 不进历史。
6. 丢掉被拒位置的 KV。一步之后 `cache_len == root_pos`。bonus 是下一块的 root，不是缓存位。

## ESP

`ESPMaskProvider`。默认 init 是 prompt embedding 均值，每提交一个 token：

```text
m ← (1 − λ) m + λ e_new
```

论文 `λ = 0.1`。`spec.mask.update: false` 冻结 prompt 均值。各槽共用这一向量，槽下标只改 position id。消融还有 last-k、sample_embedding、`μ + cσ`。Last-K 下标选择见 `mask_providers.py`。

`mask.init: sample_embedding` 从与 `SpecDecoder` 采样相同状态的 **fork** 里抽噪声，不消耗采样 `Generator`。temperature > 0 时才能和 `ar_generate` 逐 token 对上。论文这条消融本身是 T=0。

## EMA-velocity

`EMAVelocityMaskProvider`，`spec.method: ema_velocity`。差分只在输入 embedding：

```text
vhat ← β vhat + (1 − β) (e_new − e_prev)
```

第一个 prompt 差分播种 `vhat`。没有 `1 − β^s` 校正。`β = 0.9999` 时 `vhat` 贴近那一次差分。`β = 0` 只用最近一步。格子见 [history-extrapolation.md](history-extrapolation.md)。

```text
m_i = origin + γ · i · step(vhat)
```

`γ` 是 `spec.ema.step_scale`。单槽树用 `i = 1`。这里的 `origin` 是 **EMA 锚点**（`spec.ema.level`），不是 `study.yaml` 的数据源开关。

| **level** | **锚点** |
| --- | --- |
| `last`（代码默认） | 最近一次已提交 embedding |
| `order0` | ESP 均值（prompt 均值，再按上面的 `λ` 更新） |

`γ = 0` 去掉速度项。研究表里的 `off` 表示该项不存在，不是数字 0。`normalize: true` 把 `vhat` 收成单位方向乘差分范数的 EMA。`extrapolate_ema: true` 只在一块内部滚 EMA，不改已提交状态。两者默认 false。`update: false` 冻结 `vhat`，last-token 锚点仍会动。

## Tree and verification

静态枝是固定列表，例如 `[14]`（一块复杂度 30）。动态枝按论文 Algorithm 1、top-1 扩展。剪枝用下一个 token 替换「与父节点相同」的候选。

验证是和模型自己的链做 token id 精确匹配，不是 residual sampling。每个已提交 token 按顺序抽一次，temperature 1 时与普通生成对齐（共享 generator）。

`spec.impl: efficient` 复用 attention mask 并平移 position id，只适用于静态树。`naive` 每步重建。动态树用 `DynamicTreeAttentionCache`（与 naive builder 逐位相同；缓存键含 tree shape **以及** dtype / device / min_value）。

## Choices that differ from a literal reading of the paper

1. 一次 pass 提交多个 token 时，`λ` 按提交顺序各更新一次。
2. Last-K 用 prompt 最后 `k` 个 embedding。印刷下标 `e_{t−k−i}` 指到更前面。
3. sample-init 的标准差按维。
4. 印刷枝 `[7,5,3]` 块复杂度是 64 不是 60。代码保留印刷枝，日志记 64。
5. 配置默认 100 new tokens。Table 1 图注写 256。用 `eval.max_new_tokens` 覆盖。
6. BC=120 消融用 `[15,10,4]`。
7. 第一棵树在第一个 new token 出现之前就提出。
8. Qwen3 thinking 关闭。
9. `impl: efficient`（Appendix E）只用于静态树。动态树走缓存过的 naive mask。静态 `impl: naive` 保留逐项 builder，给 Table 4 计时。
10. BC=60 主配置是静态 + efficient。动态树是单独的 `*_bc60_dynamic.yaml`。
11. `tau` 是每次 decode call 提交的 token 数。prefill 不进分母。`call_reduction = 1 − 1/tau`。
12. PLD、STAND、LADE 不在本仓库。自回归基线在。
13. `sample_embedding` 用 fork 后的 generator（见上）；论文消融 T=0，两种实现在 T=0 无差别。

## Context limit（方案 A）

投机块需要 root + 树 + 每节点 `k` 个 mask 槽，会比逐步 AR 更早撞 `max_position_embeddings`。投机输出是 AR 的前缀，只差长度；`torch.equal(spec, ar)` 会失败。

**采用方案 A**：该 prompt 的 AR 参照用投机侧实际达到的 `max_new_tokens`。`exact_match` 仍表示「同一预算下序列相同」。`hit_context_limit` 留在行里。接受数、投机 token、`tau` 不变；这些 prompt 的 `ar_time` / `ar_calls` / `speedup` 按较短预算算。

history-extrapolation 和论文设置（长上下文、100/256 new tokens）碰不到上限。未采用方案 B（前缀审计加额外列）。

实际输入证据记录完整 prompt token、EOS、模型 state_dict SHA256、模型 commit、tokenizer vocabulary/template/special tokens、实际 dtype/backend/TF32 与本地输入文件 SHA256。模型加载后和定稿前比较权重哈希；不把依赖版本或 seed 代替实际输入。远端未下载的文件无法在 make 冻结；实际加载后的权重与 tokenizer 证据绑定到新 Run，不宣称 Hub 全生态已验收。

## Result files

写在 `studies/<name>/runs/<id>/assets/`。不要复用 Run 目录，CSV logger 会追加。新格子用 `python -m spec_mtp make` 拿到新 id。

`spec_metrics.csv` 每 prompt 一行：`prompt`、`category`、`new_tokens`、`committed`、`decode_calls`、`accepted`、`tau`、`spec_time`、`hit_context_limit`。开了 AR 基线还有 `ar_time`、`ar_calls`、`exact_match`。`hit_context_limit = 1` 时 AR 按方案 A 截断。

`accepted` 是留下的 draft。`committed = accepted + decode_calls`（预算或 EOS 截断的最后一拍除外）。`tau = committed / decode_calls`。`summary.csv` 的 `tau` 是 `sum(committed) / sum(decode_calls)`。`exact_match_rate` 必须是 1。`tau` 在 naive / efficient 之间不变，墙钟会变。

`ar_baseline` 只写 AR 列。alignment probe 写 `alignment_metrics.csv`，不写投机 CSV。

## v0.3.0 适配验收合同（2026-10-13）

- 继续使用固定提交的 vendored RPipe；唯一允许的框架例外是 Windows torch-first 导入。Factory、调度、Tracker、日志、状态、provenance 和 readout 由库承担。
- 专项 execute 保存原始 prompt/output/AR token、逐步接受与 cache 观测；collect 从原始观测计算 CSV 和 Tracker 指标；summarize 拒绝 exact-match 失败；write 再核对证据、来源、实际输入与运行环境后由库定稿。
- recipe 注册和构造检查不解码。现有 prepare_shared:false 是本项目 Data builder 与上游 torchvision-only make 的实际边界，Run prepare 继续使用 shared/data 与 shared/model，不取消共享约定。
- 专项源码锁覆盖新增、删除、修改；终验比较执行快照与当前来源、输入 token、配置、模型权重/tokenizer 文件和运行条件。普通 run/launch 保留锁，并在进入库前预检来源（拒绝时不改旧 result）；make/remake 只可为新 version 接受来源变化，已有成功 Run 不重新签收。
- Study process 重新核验当前 index 的 Run 证据，拒绝缺失、混合来源和声明子集；不扫描历史 Run。专项失败同时把通用 process envelope 标记 complete=false；report 在生成数字表前复验当前 index。
- 不改变 decoder 的采样、mask、树、cache、EOS 或预算语义。增加观测不构成新论文实现；历史接受数保留原日期和来源。

此次需触及 recipe/CLI、专项来源与证据、Algorithm 适配、Study collect/summarize/write/process、对应测试与使用文档；不恢复已删除 runner，不实现研究草案。

## v0.3.1 report 身份与质量共存（2026-10-14）

当前执行库固定 7a15c46，report 使用上游当前 index/process 的 Study、Run ID、seed、factors 身份门与原子 NUMBERS 写入。专项入口先只读校验身份，再将真实 process envelope 传入 Study gate；证据/来源/完整性失败同步 complete=false，并保留旧数字表。上游合法部分聚合可 readout，本项目研究 report 仍要求完整矩阵与专项质量通过，不放宽 exact-match。解码和全部科学配方不变；已完成的 v0.3.0 数字仍绑定原来源。
