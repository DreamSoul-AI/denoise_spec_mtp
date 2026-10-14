# ESP Table 1 reproduction — Qwen3-8B / BF16

状态：2026-10-15 计划已立项，未声称复现成功。优先于所有其他研究。此前 4B 证据全部 FP32，已按工具/测试与证据两个主题提交，并推送工作分支；PR #7 的 Branch flow/cpu-checks 已通过并合 dev（8677376e1ac878a159a3095711eac43420d97bde），不合 main。0.6B 罕见事件/局部机理和 4B FP32 扩展暂停。

## 1. 来源、目标与未公开细节

主来源：[ESP arXiv v2](https://arxiv.org/html/2603.17942v2)，§3.1/3.4/3.5、§4、Table 1、Appendix D。已读正文及本地 PDF 第 7 页表格。模型为 [Qwen/Qwen3-8B](https://modelscope.cn/models/Qwen/Qwen3-8B)，权重优先 ModelScope；仅用于本 ESP 复现，禁止拿 8B 做其他研究。

Table 1 Qwen3-8B 的 ESP τ 目标：BC30=1.63，BC60=1.74。BC10 是额外协议核验，Table 1 没有其目标。本文表注为 256-token 输出/H100，§4 正文为 100-token/A100；本次遵循 Table 1 的 256 上限，EOS 则提前停止，逐条记录实际输出长度。不得把原仓库 100-token 静态配置冒充本复现。

论文未明确公开 precision、模型 immutable revision、Qwen thinking 开关、prompt 截断策略与 τ 跨任务聚合权重。BF16 是当前用户明确要求。采用非 thinking chat template、首轮原始 prompt、不截断且纳入全部 480 条；输出单列这些实现选择，不称其为已获作者确认的配置。RTX 5090D v2 24GB 与 H100 不同，torch/transformers 版本差异也记录。用户不要求测速，因此不测 S/R。

官方 SpecBench：[hemingkx/Spec-Bench](https://github.com/hemingkx/Spec-Bench)，固定提交 fd2c1cd7d2201ef71db4c5f4e455008f017967bf，data/spec_bench/question.jsonl。本地 480 条 JSON 对象及顺序与官方完全一致；远端 SHA256=4b6d33e79484f9841c487ee87d1cf6aa8c6066f61d5d482ff09e5a007fafdf04，本地 SHA256=7dd26882f31ada100c2aa7447019b5349bddc55697021acbc5643fdc8740aa21。只存在字节排版差异。保存原文件并绑定两哈希；不得为了对齐目标筛掉难样本。

## 2. 冻结协议

| 项目 | 本次值 |
| --- | --- |
| dtype / temperature | BF16 / T0，绝不新增 FP32 模型实验 |
| mean mask | prompt embedding mean 初始化；每个已生成 token 按 m←m+0.1(e−m) 更新 |
| BC / mask count | 10/1、30/1、60/2 |
| tree | dynamic，Top-1 扩展，累计路径概率排序；父子同 token 替换为下一候选；pruning=true |
| implementation | native naive 动态树 attention/cache，保留原始模型与验证语义 |
| seed / outputs | seed123，max_new_tokens256，EOS 提前停止，warmup=false |
| input set | 全部 480 首轮，chat template enable_thinking=false；max_prompt_len40960，实际预检不丢任何条目 |
| audits | 每个 ESP 输出与该 BF16 模型独立 AR 逐 token 核验；报告所有不一致 |
| clocks | Study 局部禁用 decoding clock；零 timing 是原生字段占位，不是测量 |

BC=(k+1)(1+draft_nodes)，本次实际 draft budget=4/14/19；检查每步真实 BC 不超过预算并记录树宽。论文 Algorithm 1 的 B 与正文 Eq7 表述存在歧义；遵循 Eq7 与当前 Top-1 实现并报告映射，不暗改预算来追目标。

主指标同时报告 pooled τ=sum(committed)/sum(decode_calls)、逐 prompt τ 的均值、逐 category pooled τ 后等权均值。committed 包含 bonus，不含 prefill；另列含 prefill 的实际 model calls、新 token 数与 accepted draft 数。尾部 EOS/长度裁剪口径明确，不混淆 accepted 与 τ。目标的近似程度报告原值/差值/按两位小数是否一致；不得预先把某个聚合方式定为作者确切口径。

## 3. 执行与停止规则

1. 复用 native RPipe Study prepare→execute→collect→summarize→write→process；新 Study/version/Run，原失败和成功 Run 不重签。权重逐文件哈希、官方 ModelScope 文件名/尺寸与实际 BF16参数核验；离线缓存 immutable revision 未确认则明确记录。
2. 先新建小样本协议检查 Study（每类首条，BC10/30/60）。检查 BF16装载、动态树、256上限、精度及原生门；这只是预检，不能代替 480 条 Table 1。
3. 若全部 token exact，另建全 480 三格 Study 串行执行。若发现 mismatch，保留原始 token 与首分叉，先做同精度最小复现；不得改为 FP32、以 teacher 强制纠正、丢反例或放宽原生 exact_match_rate=1 门。
4. OOM/其他任务占显存时保留失败、等资源或用新 Run 可逆验证，不停其他任务。单卡只启动一条实验调度链，不并发加载模型。
5. 全量完成后报告配置覆盖、精度、每任务/每 prompt计数、三种 τ聚合、对目标差值与失败边界。数值不符也输出可复核负结果，再按首个可证伪差异推进，不宣称强行成功。

四任务共用 24GB GPU。记录启动前空闲显存及运行容量采样（含其他进程，非精确 allocator peak）；不使用受干扰的墙钟或 timing 占位做性能比较。预检约 13×3×2×256=19968 生成 token 上界；全量三格含独立 AR 审计约 480×3×2×256=737280 上界。串行，没有额外 teacher/warmup。容量不足先暂停该 GPU 启动，继续证据/实现核对。

## 4. 后续 4B BF16 配对（ESP 复现之后）

同批 prompt、同树/预算/长度/随机种子，比较 ESP frozen mean、输入零阶 updating mean λ=0.1、输入一阶 mean+gamma、输出零阶 final-normalized hidden 范数映射、输出一阶 final hidden+EMA velocity，另跑独立 AR。逐 prompt 列 accepted/model calls、每个对照的赢平输及 token exact。不得用此前 FP32 数字代替。

这里的 ESP frozen mean 是用户指定的后续基线，区别于 Table 1 updating mean。tied 权重直接用输出 hidden 的尺度映射，不做逆映射。当前 output provider 只支持 unpruned static chain；后续若统一采用 dynamic/pruned，必须先最小扩展并验证 owner/proxy 对齐，不能让方法使用不同树再配对。4B 子实验开始前单独冻结 PLAN、beta/gamma、精度内部计算与实际 tied-storage 检查。本阶段仅排队，不先跑 4B。

## 5. 实际进度（2026-10-15，进行中）

FP32收尾：PR #7 已经CI通过并合dev，merge8677376，main未操作。BF16预检已串行执行BC10与BC30，各13条，仅6条与独立AR完全一致，原生summarize门均失败；BC60仍在执行。不得把失败格子的τ称为可用复现结论，也不进入4B五方法。首个writing/q81在生成第10个token分叉（零基index9），是后续最小控制入口。

已冻结新Study esp_table1_bf16_numerics v2：q81、BC10、32-token上限，2×2 BF16归约/确定性设置，保持ESP树与mask公式。8项后台设置成功/异常恢复测试通过，待当前launch退出后执行。v1仅make未执行GPU，CPU测试暴露属性mock恢复问题，v2用显式try/finally恢复、新version/Run；旧目录保留。


03:36 后续：三预算原设置均失配（6/13、6/13、5/13）。q81四格token exact为no/yes/no/yes；仅reduction=False、deterministic=False原生全链通过，deterministic=True组合格因阶段恢复引起runtime终验失败，未冒称成功。已启动新Study esp_table1_bf16_reduction_check 原13条/三BC/256上限扩大验证，仍不启动4B。


03:47 扩大验证完成：reduction=False的BC10/30/60 exact为4/13、3/13、5/13，三格全失败；部分AR自身也随归约模式变化，局部q81前32token修复不能推广。已串行启动esp_table1_bf16_shape_check，q81/96token仅控制线性投影单行几何，BF16/ESP其他设置不变。16项控制/形状回归通过；仍不跑4B或全480，不把失配τ认作Table1成功。


03:50 线性形状对照两格均失败，native q81首分叉index74，253个linear单行对照index9；权重digest相同/BF16不变。只固定linear行数不是充分修复。下一项协议：每query仅按attention mask保留有效KV，再比较compact attention单独、compact+单行linear、compact+单行linear+单行RMSNorm（三格q81/96token，BF16、同ESP）；所有数学/权重与接受语义保持，明确这是数值约定控制不是作者已公开实现。先验证可见KV集合/因果位置/patch恢复，再串行执行；若仍失配，按首分叉同prefix逐层BF16算子追踪，禁止切FP32/放宽exact门。目标仍进行中，不将当前负结果标记Table1复现完成。
