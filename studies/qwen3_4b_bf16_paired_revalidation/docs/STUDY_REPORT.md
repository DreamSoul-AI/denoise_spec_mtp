# 4B BF16五方法加AR独立复验：CPU准备状态

> **20:55终止后续执行：仅原BC60继续，本Study待执行格暂停，保留全部已有来源/结果；旧排班仅为历史。**
>  原E2已11/11完成；本次独立复验已原生make 11格，尚无execute或新τ，不重签旧证据。
> 原480输入/token IDs、ModelScope快照、五方法、BC30/60双mask/BF16/T0与独立AR配置逐字段核对。
> 完整618项CPU回归全过；另增十个原配置的显式BF16/tied CPU微型模型数学门检查全部通过，Ruff/mypy通过。
> 首格入账与七格/11格共18个待执行Run绑定均核验；GPU仍仅BC60与随后七格，未开配对GPU队列。

唯一[中文计划](<../../../docs/研究计划 Denoising Speculative Decoding.md#paired-followup-20261016>) / [English](<../../../docs/Research Plan Denoising Speculative Decoding.md#paired-followup-20261016>)，不可变commit与来源在[source_refs.json](source_refs.json)。模型和输入合同复用原Study原文件，不重复保存prompt或权重。

正确性门复用原native verifier：全部Spec提交token等于各自验证forward logits argmax，包括prefill首token、owner/哈希/提交覆盖；独立AR差异只诊断，AR不冒充Spec审计。输出长度不同，accepted/calls/tau按不同实际路径配对，不能解释为等长测速或因果空间差异。

代码入口：../recipe.py、paired_repeat.py、paired_admission.py、analyze_results.py。后者复用原load_cell/compare/三聚合/图工具，全部11格与native Study process通过后才写正式JSON/图。当前没有本次新τ或赢平输结论，旧数据仅作为以后独立复验对照。

19:53显示分类只接入本次尚未运行的Study；实际XML探针把10个显示上下文归为不阻塞，当前正在跑的python73008纯C上下文为已知CUDA阻塞。WDDM逐进程显存N/A如实保留，不当0或伪造CUDA分量；未知进程仅有正CUDA显存证据才阻塞。依据[NVIDIA文档](https://docs.nvidia.com/deploy/nvidia-smi/index.html)。原8B/范数冻结资源源文件未改，不终止或挂起显示进程。

## 20:50 CPU队列复验

原生make已生成AR一次加BC30/60各五方法的11个独立Run，shared/model仅建立到既有已核验ModelScope缓存的junction，不复制权重、不下载。全部Run config.yaml与对应完整factor/原配置逐字段匹配，seed123、原数据和模型合同不变；原生来源和计划冻结检查通过。七格续跑另核验七个新Run，首格result SHA与数学总计和入账器一致；这18个新Run均没有result/raw，未假填旧结果。见[cpu_readiness_v1.json](cpu_readiness_v1.json)，含索引/配置SHA与本机测试XML哈希。

完整回归XML为`.tmp/cpu-revalidation-20261016/full.xml`：618项、0失败、0错误。测试收集后新增的`test_prepared_methods_argmax.py`另跑10项全过，XML为`prepared-methods-fixed.xml`；没有将两次说成一次628项全跑。新检查使用实际cast到BF16并核对真实weight tying的CPU tiny模型，每个Spec配置6个提交token均被原生argmax审计覆盖，AR故意不一致不阻塞，末token篡改被拒绝。最初测试夹具默认untied被output_hidden前置条件正确拒绝，改为与4B实际tied合同一致后通过；不是放宽产品门。它不替代真实4B全480或GPU数值/性能证据。

GPU排班不变：BC60 worker66500继续，七格队列64880等其自然退出，入账器50944只读；新配对11格不启动GPU队列。`git fetch --prune`后无可新增清理的已合topic，唯一已合活动分支仍载BC60，待自然退出并核验数据后清理；当前工作分支未合，保留。不为本轮CPU准备单独开PR。
