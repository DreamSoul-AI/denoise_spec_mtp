# PR说明草稿

状态：仅本地草稿，未新建PR、未推送；基线依赖与文件范围见[publication-plan.md](<../研究计划 Denoising Speculative Decoding.md#legacy-docs-research-publication-plan>)。

标题：feat: add tied output-hidden order0/order1 masks for static chains

正文：

为实际共享input embedding与LM head权重的模型增加output_hidden mask配方，支持零阶／一阶、两槽静态未剪枝链。精确提交token更新anchor/velocity，各owner使用真实proxy hidden模拟候选；沿用原生验证、KV位置和EOS／预算语义。非tied模型及不支持的树配置显式拒绝，final hidden捕获hook在正常和失败路径均清理。

Qwen3-0.6B固定q171前置四格全部输出与独立AR相同；输入均值链接受17个draft，输出零阶／一阶均10个，因此本PR不宣称接受或速度收益，也不改变现有默认配方。ModelScope实际本地文件哈希绑定模型；默认master来源未验证为远端不可变revision。

验证依据为候选提交437f201所附记录：270项测试、Ruff/mypy、36格既有tiny轨迹兼容检查，以及wheel/sdist入口验收。实际推送后的cpu-checks和Branch flow须以该PR新HEAD为准，本轮没有执行远端CI。PR以dev为目标，并依赖先前RPipe／Study重构；仅包含清单中的实现、拒绝边界测试、Study合同和必要验收证据。权重、缓存与完整Run不在范围内。
