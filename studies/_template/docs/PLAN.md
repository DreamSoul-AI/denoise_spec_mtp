# Study Plan: my_study

复制后填写本轮事实，先确认计划再运行。遵循 [Study 指南](../../README.md)，结果填 [STUDY_REPORT](STUDY_REPORT.md)。本模板没有实验数字或执行授权。

## 1. 研究问题与对照

写清要回答的问题、现有结论、主指标与对照。AR 对照、ESP、EMA 或 alignment 只在本轮问题需要时选择；未实现的外部 baseline 不写成已支持。保留论文解释差异的链接，不自动宣称完整复现。

## 2. Study / Experiment / Run

- Study：填写新目录与名称。
- Experiment：填写 axes；没有 axes 时说明单组合。
- Run：每组合 × seeds；列出总数和新的 version。
- 声明：记录基底 → fixed → 轴/seed 的覆盖关系，make 后核对实际 config/index。

## 3. 变量轴

| **因素** | **字段** | **取值** | **比较目的** |
| --- | --- | --- | --- |
| 待填写 | 待填写 | 待填写 | 待填写 |

seeds 单独写，不能用并发数代替。列出已有正式接受数的格子，默认不重跑。

## 4. 固定条件与来源

| **项** | **必须记录的内容** |
| --- | --- |
| 源码 | 本仓库提交、RPipe ORIGIN、recipe、专项锁、额外参考输入 |
| 模型/tokenizer | 名称、Hub/实际 revision、权重来源和 digest；training-free 权重语义 |
| 数据/prompt | 文件与来源、切片、聊天模板、tokenization、输入 digest |
| 解码 | BC、mask 数/初始化、树模式/pruner、β/λ/γ、接受/回退和 KV/cache 合同 |
| 预算/停止 | temperature、seed、max_new_tokens、EOS、context-limit、prompt 数 |
| 精度与环境 | 实际 dtype、TF32/混合精度、attention backend、依赖、设备、随机性开关 |
| 判定 | exact_match_rate 必须为 1；主指标及各深度诊断、τ 与速度的独立口径 |

按目标原配方填写，不以示例 YAML 的 float32/T=0 替代研究条件。不为提速换成不能接收 4D 树 mask 的 backend。来源/配方变化先换 version，再显式 make/remake，不能重新签收旧成功产物。

## 5. 高效率排班与失败处理

先以 `make --round 1` 串行测量权重、KV、树、mask 和进程开销；记录实际容量后才用 `system.config.vram_bytes` 小步扩大独立 Run 并发，不套用视觉训练估计。每个 Run 独占状态/产物/logger，wait 组末等所有进程退出，不重复启动 launch。

速度对照使用同任务量并串行进行，记录预热、同步、backend、实际生成长度与整体墙钟。失败/OOM 保留 ID、退出码和日志；后续独立重算换 version。解码 checkpoint/resume 未验收，不能把 `resume: latest` 当作已支持的 KV/mask/RNG 恢复。

```powershell
$env:PYTHONUTF8 = '1'
python -m spec_mtp make studies/<name> --num-gpus 1 --init-gpu 0 --round 1
python -m spec_mtp launch studies/<name> --num-gpus 1 --init-gpu 0
```

### 5.1 时长预估

make 后、launch 前填 est；同一 wait 的预估取最慢一条，整轮求和。报告填实际值，缺失明确标记，不能拿估计冒充实测。

| **wait** | **factors** | **mode** | **seed** | **Run ID** | **est (s)** |
| --- | --- | --- | --- | --- | --- |
| 待填写 | 待填写 | eval | 待填写 | make 后填写 | 待测 |

## 6. 阶段与成功标准

默认 prepare/execute 经 recipe 和专项 Algorithm 负责构造/原始观测；collect 计算指标，summarize 在成功前检查 exact-match/证据，write 核对来源后由库定稿。Study process 只终验当前 index，不扫描旧 Run。

- 计划因素 × seed 全部存在、Run succeeded，原始 token 与 AR 按原合同一致，exact_match_rate == 1。
- 来源、配置、输入、权重/runtime 与接受/cache 证据完整；子集或混合来源不能通过完整终验。
- 同设备旧/新数值前置门通过，保留所有失败反例；不挑选通过重复或放宽阈值。
- 人写报告按 Experiment 给 mean/std/min/max/n、单位、条件和结论，附真实解码结果图；NUMBERS 不是结论。

## 7. 执行范围与验证边界

填写允许的模型/设备/格子/预算和停止条件，分别列出静态、CPU tiny、真实 GPU、安装、恢复及并行验证。短探针不替代完整矩阵；未执行项和本机原始日志不随 clone 提供的边界必须保留。
