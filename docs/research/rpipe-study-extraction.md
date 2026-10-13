# 宏观问题到最小 Study

## 一、问题、假设与当前实现

宏观方案是 [research-plan-v6.md](research-plan-v6.md)。其 §5.11 与 E1–E2 需要先有可靠输入空间基线，再检验未实现的输出空间 mask。已有结构只共享 provider 向量，owner 的位置和 attention 已独立；现有 EMA 更新来自提交 token 的输入 embedding。输出 hidden 外推、Kalman 和 PLD/STAND/LADE 等外部 baseline 未补写成支持。

提取 [input_mask_baseline](../../studies/input_mask_baseline/docs/PLAN.md)：在同一真实预训练模型、固定新 prompt 与原解码配方上，现有 frozen_mean、gamma_last 及 AR 能否留下可核验的一致输出、接受/cache 轨迹与来源？这是工程与数值前置问题；若任一 token 不一致则否决流程质量。它不检验 H1–H13，不要求 EMA 接受数优于 ESP，也不以吞吐证明机制。

“免训练”只表示本轮不更新模型权重；调 β/λ/γ 或选择数据仍可产生选择偏差，不能据此宣称没有过拟合/迁移问题。原草案中的此类解释保留为待验证主张；本轮不选参，不使用最好重复替代失败。

## 二、文献与工作指引的实际读取范围

执行库固定 804b3823，结构与流程依据该提交 README / concept / layout / code / structure / flow / Study 指南及测试规范。参考仓库现已为 DreamSoul-AI/RPipe；本地 HEAD a8b08d9 的 README/AGENTS 有其他任务修改，research.md、feedback.md 为未提交工作稿，远端 main 两文件尚不可取得（404）。工作稿只用于研究/反馈要求，不冒称发布基线，不覆盖其内容。

交接前补充（2026-10-14）：v0.3.1 已发布，实际标签提交 7a15c46b75c5eb951cccd60ed7b9fc3463db90f5；本轮又读取该提交根 README、research.md、feedback.md、flow.md 与实际 report.py。前述 404 是初读时状态。发布后的研究/反馈规范可从固定源码取得，knowledge 参考仍为上述 09078015。执行副本尚未升级，按交接任务复验；不将先前工作稿或 v0.3.0 的实验改写为 v0.3.1 成果。

knowledge 固定 09078015ad8c80971ac4abd5b5ad2e322cd0e1a1：完整读取 research-plan、literature-search、paper-analysis、pytorch-project 的 SKILL.md 和 research-plan 中文指南。research-plan 已有本地技能；其余三份只读取参考，没有安装或执行其工具。六方面规范不新增运行依赖，也不授权大矩阵。

本轮定向检索 ESP / SpecBench / Qwen，不作系统综述或新颖性证明。阅读深度：ESP v2 的 §2、§3.1–3.5、§4 与 Figure 2/方法和指标说明；SpecBench 官方 README 的协议/质量比较与许可入口；Qwen3-0.6B 官方模型卡的权重、聊天模板与许可。未独立核验宏观草案其余参考文献和卡尔曼推导，H12 的非劣效 δ 等决策仍待确认。

| **来源** | **作者材料与本课题用途** | **边界** |
| --- | --- | --- |
| [ESP v2](https://arxiv.org/html/2603.17942v2) | 冻结模型上进行 embedding mask 探测、树验证；§3.1 区分均值初始化与生成期更新。为输入空间 baseline 提供依据 | 本轮使用已有 frozen_mean / gamma_last，前者关闭更新；不称完整论文复现。正文与表注的设备/输出预算不一致，不用其速度数字作本机门 |
| [SpecBench](https://github.com/hemingkx/Spec-Bench) | 官方统一评测与相同环境比较；已有文件的 translation 第 11 条用于前置门 | 不是完整 Benchmark 或跨域确认集；代码 Apache-2.0 不自动证明全部聚合数据的单独许可，实际研究须沿数据来源协议 |
| [Qwen3-0.6B](https://huggingface.co/Qwen/Qwen3-0.6B/blob/main/README.md) | 预训练聊天模型、非 thinking 模板；模型卡 Apache-2.0 | 实际使用既有 ModelScope 缓存，权重/tokenizer 以文件 digest 锁定，未把可变 master 伪称固定远端 revision |

## 三、六方面与停止门

文献提供基线范围；数据使用本仓库固定 SpecBench 文件的 q171、translation 单 prompt，不进入原 first/next/last 的前 10 条/类，避免重复正式数字格子。模型沿用 Qwen3-0.6B float32/eager/非 thinking 配方，不更新权重。算法复用 named mask 的原 static [14]、一 mask、BC30、β/λ/γ，不实现输出空间新方法。主门为 exact-match=1 与完整证据，accepted/各深度、new_tokens/committed/τ 分开；AR 与 alignment 的指标语义单独报告。实验为四个固定 case × seed123 的串行前置门，无选参、无多重比较或总体显著性主张。

100-token/EOS/T=0 沿用既有真实模型协议。每格对应一个 Run，先核对完整 config 和来源，再运行；任一门失败保留反例并停止扩大。alignment 四个 hindsight 步只验接口和计数，不以单样本复现 ESP Figure 2。资源先串行测量，不并行性能排名；大规模矩阵和解码恢复另需计划与授权。细节与结果留在该 Study。
