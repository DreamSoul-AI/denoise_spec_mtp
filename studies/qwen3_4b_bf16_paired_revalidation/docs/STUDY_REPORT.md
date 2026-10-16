# 4B BF16五方法加AR独立复验：CPU准备状态

> 原E2已11/11完成；本次新版本准备不代表原结果有缺格，不重签旧证据。
> 原480输入/token IDs、ModelScope快照、五方法、BC30/60双mask/BF16/T0与独立AR配置逐字段核对。
> 73项联合CPU回归及Ruff通过；实际未make预检0/11有效，只写pending，未新增模型forward。
> 新Study仅CPU准备，GPU须等范数八格完成且入账；BC60原队列有准入时优先。

唯一[中文计划](<../../../docs/研究计划 Denoising Speculative Decoding.md#paired-followup-20261016>) / [English](<../../../docs/Research Plan Denoising Speculative Decoding.md#paired-followup-20261016>)，不可变commit与来源在[source_refs.json](source_refs.json)。模型和输入合同复用原Study原文件，不重复保存prompt或权重。

正确性门复用原native verifier：全部Spec提交token等于各自验证forward logits argmax，包括prefill首token、owner/哈希/提交覆盖；独立AR差异只诊断，AR不冒充Spec审计。输出长度不同，accepted/calls/tau按不同实际路径配对，不能解释为等长测速或因果空间差异。

代码入口：../recipe.py、paired_repeat.py、paired_admission.py、analyze_results.py。后者复用原load_cell/compare/三聚合/图工具，全部11格与native Study process通过后才写正式JSON/图。当前没有本次新τ或赢平输结论，旧数据仅作为以后独立复验对照。

19:53显示分类只接入本次尚未运行的Study；实际XML探针把10个显示上下文归为不阻塞，当前正在跑的python73008纯C上下文为已知CUDA阻塞。WDDM逐进程显存N/A如实保留，不当0或伪造CUDA分量；未知进程仅有正CUDA显存证据才阻塞。依据[NVIDIA文档](https://docs.nvidia.com/deploy/nvidia-smi/index.html)。原8B/范数冻结资源源文件未改，不终止或挂起显示进程。
