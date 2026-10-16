# 固定480的4B五方法加AR独立复验准备

> 20:55 Enmao最终范围：复现收尾，仅既有8B BC60继续。本文准备的待执行格暂停，不启动；数据/结果与冻结来源保留，旧排班说明不再执行。


原Study已11/11验收；本Study按19:46新指示准备独立复验，当前已make 11格、尚未execute，不修补或重签旧结果。唯一计划：[中文](<../../docs/研究计划 Denoising Speculative Decoding.md#paired-followup-20261016>) / [English](<../../docs/Research Plan Denoising Speculative Decoding.md#paired-followup-20261016>)；不可变计划commit与原始来源SHA在docs/source_refs.json。

配置逐字段复用原Study（仅experiment/version身份变化）：AR一次，BC30/60各ESP frozen mean、输入零阶、输入一阶、输出零阶、输出一阶，共11格。双mask、动态树剪枝、BF16/eager/T0/256/EOS、同480 token IDs和seed不变；无新方法，不改prompt，不测速。原方法β/范数/EMA定义完整沿用，不把空间比较误称同一EMA配方。

recipe只复用原PairedUntimedEval/build_cuda，添加只读来源检查和实际GPU/实测4B host峰值+2GiB门；每prompt保留2GiB。初始容量取已测BC30最大输入，尚不保证BC60峰值；逐Run采样，不降低门或抢占。Spec native逐提交token verifier argmax门必须全过；独立AR不提供draft接受数，其一致率/首分叉仅诊断。完整native process与11格通过后才发布正式JSON/图。

排班：当前范数八格全部成功且入账后才接卡；原BC60具备原准入时优先。仅CPU准备不启动第二GPU队列、不重跑旧11格当作本次证据。原始Run/权重不进Git，CPU模拟不替代真实验收。

## CPU入口和显示分类

`python analyze_results.py --output-dir <新目录>`仅只读验收；全部11格和native process成功后才发布正式JSON/原配对图，保留accepted/calls/tau三种逐prompt胜平负、三个tau聚合、与旧E2每格的配对、AR首分叉及输出长度。未完成时只有paired_pending.json。

按19:53规则，新Study使用tools/gpu_admission.py的白名单+NVIDIA XML进程类型。G和已知Figma/浏览器/Office/RayLink/ToDesk/Sunlogin/Parsec/TeamViewer的显示混合上下文不阻塞；未知进程只有正的CUDA显存证据才阻塞。WDDM的N/A不能当0：已知python等运行时的纯C计算上下文仍等待；未知C+G的总显存不伪称CUDA分量，列为未证实并保留实际free VRAM门。依据[NVIDIA文档](https://docs.nvidia.com/deploy/nvidia-smi/index.html)。该工具无终止/挂起进程API，仅接入新Study，活动8B与范数资源文件不改。

## 已执行CPU验收

原生声明展开与源合同、缺失/重复/乱序/λ/eval篡改拒绝、资源门先于载模与两个解码入口、未make只生成pending，以及tiny BF16真实逐token数学门检查均通过。联合显示分类、范数入账与原范数合同回归共73项通过，Ruff通过；完整CPU套件另行记录，不将局部通过冒充全量。

当前CPU只读预检输出在主仓.tmp/paired-followup-20261016/preflight/paired_pending.json：complete=false、valid_cells=0，未使用旧11格填本次新格。原基线逐格对照会写入versus_original；只有新的共同AR与全部新Spec原生成功后才签收本次配对。

20:50更新：618项完整CPU回归全过，另10项五方法/双预算的显式BF16/tied微型模型argmax正负检查通过；实际18个待执行Run及恢复首格绑定见[CPU证据](docs/cpu_readiness_v1.json)。make仅准备，不启动第二GPU队列。
