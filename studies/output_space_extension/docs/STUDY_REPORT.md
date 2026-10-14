# Study Report: output_space_extension

2026-10-14：固定q175–q178四个新prompt的四方法原生Run与Study门全部通过，16份输出对独立AR一致；随后20次固定窗口观测/双向替换/原值回填也全部逐token一致。q175/176/177保留null，q178双向均从8变9个接受。此处复现了局部接受变化，但不是q173后期两个first-slot命中及严格同位状态不变的完整复制。默认配方、科学src与旧Run保留，未推送、合并或删数据。

## 先前分析与预声明假设

[PLAN](PLAN.md)在新输出前整理q173与q171/172/174的窗口位置、自然接受差异与margin，并提出H1排序边界、H2实际owner路径混入recipient历史、H3终止/未利用owner对照。q173 root83距输入末尾14，较q171/172/174的0/3/9晚，但其注入L2 .05366并不最大；q171更长后续路径仍null，q174到EOS即停，所以位置/幅度不能单独解释特殊性。q173后期94/97的自然两方法margin分别跨正负，而先前其他prompt受扰后没有跨越。已有q173量只覆盖原五个固定观测根，未补造全位置logits。

新输入按文件顺序translation skip14/take4，q175/176/177/178，input35/46/52/76token；[prompt清单](prompts_manifest.json)冻结文本、datasetSHA与独立渲染IDs。仍同一ModelScope Qwen3-0.6B文件快照、实际tied权重、FP32/eager/CUDA、非thinking、T0/EOS/预算100、unpruned[1,1]/k2/BC9、beta .9/beta_prime .99。源码670c744e0535dcad，生成器123/124/125/126；T0的这些seed不代表随机重复。

## 四prompt小矩阵

[原始精选](execution_v1.json)、[原生数字](NUMBERS.md)、[同位轨迹](trajectory_diagnosis.json)、[干预精选](transfer_diagnosis_v1.json)与[矩阵JSON](matrix_v1.json)均保留所有样本。

| qid/seed | new tokens | 输入accepted | 零阶 | 一阶 | 固定根 | 一阶←零阶 | 零阶←一阶 | 一阶原值 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 175/123 | 12 | 4 | 3 | 3 | 38 | 3 | 3 | 3 |
| 176/124 | 16 | 1 | 0 | 0 | 46 | 0 | 0 | 0 |
| 177/125 | 24 | 7 | 4 | 4 | 57 | 4 | 4 | 4 |
| 178/126 | 36 | 7 | 8 | 8 | 85 | 9 | 9 | 8 |

原生合计new88/committed84，输入/零/一accepted19/15/15、calls65/69/69。单Run std=0，不是四次独立seed重复。总数相同不能代替轨迹：q178原零阶depth1=8/depth2=0，一阶depth1=7/depth2=1，root86零阶接受1、一阶2，root91零阶1、一阶0；它们合计均8。其余三prompt两输出接受轨迹一致。

[窗口冻结](window_selection_v1.json)仅从原生语义轨迹按预声明规则产生，先写后测hidden。q175/177/178选择首个符合条件的共同命中前根；q176无命中，按预声明fallback选择首个继续拒绝根46，不换prompt。两baseline观测各只捕获实际访问根，transfer沿真实path选seed owner；union targets本次5/15/14/19根，未访问/新访问根全部保留。不是按margin挑最易翻转位置。

## q178：接受变化及负面变化同时保留

原零/一阶前期first seed至root86相同，所选root85第一槽也逐元素相同。第二槽donor L2 .052757025，单次[0,1]置换范围/原值回填门通过。

- 一阶←零阶：root86接受2→1（损失一个depth2），root91 0→1，root108 1→2，净accepted8→9、calls27→26；新增root88，原root92/110不再访问。
- 零阶←一阶：root86 1→2、root94 0→1、root108 1→2，但root100/106各1→0；净8→9、calls27→26。新增root101/107，原root88/95/110不再访问。新root101/107不在冻结张量targets，只保留语义轨迹，不能当成有同位hidden观测。
- 一阶原值回填完整复现原一阶8/27与验证/提交/KV轨迹；没有把两真实移植中的坏点抹去。

[事后第二槽与路径核验](slot_diagnosis_v1.json)从已保存两槽完整logits/张量复算，无辅助forward。第一槽指标预声明，第二槽scalar扩展明确标为post hoc，不冒称事先只凭first-slot假设即可解释所有深度。只有第一草稿正确且第二AR target存在时，第二槽AR路径才有效；否则即使它碰巧预测下一token，也不记深度2成功。

| q178同位根 | 原零阶正确margin | 原一阶正确margin | 一阶←零阶 | 零阶←一阶 | 层/限制 |
| --- | ---: | ---: | ---: | ---: | --- |
| 86 | -0.904274 | 0.141495 | -0.904274 | 0.141495 | 第二槽，第一草稿正确，路径有效 |
| 91 | 0.727850 | -2.011871 | 1.223572 | 2.681343 | 第一槽 |
| 94 | -0.116480 | -0.214975 | -0.087296 | 0.312654 | 第一槽，仅反向恢复 |
| 108 | -0.906744 | -1.377937 | 0.982765 | 1.964050 | 第二槽，第一草稿正确，路径有效 |

root86第一槽margin始终+.182526且seed不变，第二槽向量/词表logits复制donor时，该初次深度2消失或恢复；root85/86 committed anchor和velocity与recipient均逐元素相同。它支持早期同位seed的因果作用，位置比q173的后期first-slot传播更直接。root86后实际最深owner由1/2改变，后续路线和数值状态不能强称全部不变：一阶←零阶在16个可匹配窗口仅2个anchor/v均逐元素相同，anchor max_abs差3.05176e-5、velocity差2.38419e-6；零阶←一阶15个匹配窗口也仅2个anchor逐元素相同，anchor max_abs同上、velocity始终0。虽差异小且所有最终token相同，本轮未对它们独立介入，不能排除数值状态影响或把后期收益归因纯代理。

这里两个方向都提升1个，而不是互相变成另一原轨迹。接受排序由特定prefix与实际owner历史决定，不能说零阶或一阶在此稳定更优，也不授权以这次事后single-slot动作作为默认配方。

## null和假设边界

q175/177移植改变后续first seed（每方向3/12个匹配根），但完整接受/提交/KV不变，同位anchor/v全部逐元素相同。q176无接受，第二槽虽实际改变（L2 .103197），first seed在15个根完全不变，owner0持续拒绝，未使用owner1传播；这是H3预声明控制。原值回填四条全部复现，没有新增边界错误。

H1收紧：候选的有效排序跨越与具体深度命中变化一致，q178要求同时检查合法第二槽，first-slot margin并不足以解释全部accepted统计。q175/177再次表明非零历史扰动不自动成为收益。H2得到局部路径例证，但仍非全位置中介因果证明：q178一阶←零阶在root88/89 first seed与零阶donor基线相同，root89再次接受后root91不再相同；反向root86接受到owner2后root89已不等于一阶donor。last owner2无proxy观测会模拟anchor+velocity，其first slot与q173后期owner0的Phi(proxy0)结构不同；不能把owner0的无直接速度项结论推广到所有owner。该解释属于对保存路径的事后分析，未新增velocity对照。H3支持零命中/终止对照的有限解释，不能据此排除其他入口的效果。

累计q171–q178仍八个相邻translation开发prompt、每个一个固定入口、同模型T0，非随机抽样、显著性或跨任务泛化。新四prompt只有q178出现自然零/一阶局部深度差异，未发现另一条自然总accepted一阶胜零阶；q178证明接受变化可出现在q173之外，却不复现q173的全部具体模式和严格后期state条件。旧三prompt报告末尾附累计表，避免只展示这条正结果。

## Run、资源与复现

| case | Run ID | make est秒 | 实际Flow秒 |
| --- | --- | ---: | ---: |
| frozen_mean_chain | 93ed6f06e60979c0 | 3 | 21.726 |
| output_order0 | 1569bb4445d55cde | 3 | 21.835 |
| output_order1 | 6460d4249fd942bc | 3 | 20.740 |
| AR | 53dd1e7d13f1f4e6 | 3 | 18.839 |

native launch实际wall103.791秒，.5秒采样RSS峰6592802816 bytes、线程55、GPU全局6292MiB、可用主存最低9365364736 bytes；observer wall22.486秒，RSS4902768640 bytes、线程13、GPU全局5718MiB、最低主存12183564288 bytes。背景占用和采样遗漏均保留，不等于allocator峰/硬件速度排名。四Run包含16输出；20 diagnostic generations共440 new tokens/363 model forwards，后者等于各1+实际calls，辅助forward0，低于固定预算。

ModelScope缓存通过同目录junction复用11文件，未重新下载、改环境或权重；snapshot provider default/master仍不能声称远端immutable revision，实际hash绑定本地文件。原生make→launch→process→report及来源/输入/模型/独立AR/完整性门均通过，diagnostic前后PLAN/选择/tool/helpers/原raw/runtime/src也一致。首次独立tokenizer清单的BatchEncoding JSON失败发生在make/解码前，改为模板文本再分词并与原生IDs核验相同；未改变选择或源代码，说明保留.tmp。

正式复跑需新version和Run目录，按[PLAN](PLAN.md)执行；诊断工具[diagnose_extension.py](../../../tools/diagnose_extension.py)消费已冻结的窗口文件，out必须新目录。离线[analyze_results.py](../analyze_results.py)检查SHA并拒绝覆盖不同既存JSON。完整selected张量333134109 bytes，仅本机.tmp/extension-transfer-20261014-v1，SHA1ea61e0ae8566854a81dafc8806f82dd3144a3fc135a7e87483b7440cf97f2ef，不随Git。14项针对性/新Study展开/文档检查、Ruff及mypy56通过；完整旧科学回归不重跑冒充新批次。没有推送、合并或删数据。

## q178确定性与规范committed-state对照（2026-10-14）

按测量前 [NUMERICAL_PLAN](NUMERICAL_PLAN.md) 执行11次生成与1次112-position teacher前向。原native/default/src不改，原两个工具不改；严格FP32/eager、TF32两项关闭、matmul highest、CUBLAS_WORKSPACE_CONFIG=:4096:8、deterministic algorithms=true且warn_only=false、cudnn deterministic=true/benchmark=false只覆盖该诊断子进程。新prompt原生实验继续原deterministic=false配方。结果见[测量证据](numerical_diagnosis_v1.json)、[离线核验](numerical_analysis_v1.json)、[PLAN评审](NUMERICAL_PLAN_REVIEW.md)，原预声明文件未改或重签。

| q178固定模式 | 无移植零阶 | 无移植一阶 | 一阶←零阶 | 零阶←一阶 | decode calls（无移植/移植） |
| --- | ---: | ---: | ---: | ---: | ---: |
| 原FP32已保存 | 8 | 8 | 9 | 9 | 27 / 26 |
| 严格FP32确定性 | 8 | 8 | 9（重复两次） | 9（重复两次） | 27 / 26 |
| 规范同位anchor/v | 8 | 8 | 9 | 9 | 27 / 26 |

两方向严格重复的全部已捕获mask/logits/hidden/state逐元素相同，完整实际语义轨迹相同。严格模式两baseline复现原native trace，原值回填也复现；变路径对baseline的anchor max_abs3.05176e-5、一阶velocity2.38419e-6仍在。故开启确定性并不会让不同packing的浮点计算逐元素相同；本批差异能重复，不是同一路径的随机漂移。

首个可匹配状态差异在root89。一阶原路径root86接受[1,2]，其精确position88在该块row2被观测并成为下一anchor；一阶←零阶root86只接受[1]，再访问root88，以row0计算同一position88。后者root89 anchor与所保留root88 exact hidden逐元素相同；前者strict root89 anchor又与旧runtime原baseline相同。两anchor差max_abs1.52588e-5、velocity差1.43051e-6。位置来源由native观察规则和实际trace定位，改变的块/attention/KV布局是模型层面的来源证据；本轮未用CUDA profiler独立锁定某个GEMM/softmax kernel，也未保存所有中间验证row hidden，不能声称完整低层证明。

规范对照只做一次完整AR teacher，再用原provider.observe_committed按时间顺序重建每个prefix长度p的anchor/v（至p-1），root85不覆盖、其后每个实际root回填对应同位状态，保留输入proxies。root由真实mutable KV长度读取且在modelprehook再核对，不用旧trace强制根或owner。两无移植自值控制均8/27，两移植均9/26，且规范移植与严格移植的完整接受/提交/KV语义轨迹相同。在规范同阶控制与移植共同root>85的anchor/v已逐元素一致时，后期命中模式仍在，排除了这些committed-state微差作为本固定效果的必要条件。规范teacher和CPU EMA重算本身也可能带入不同舍入，故两自值控制不可省；并未隔离proxy hidden内部数值差。

解释因此分层：root86第二槽直接跨过候选排序边界，导致最深owner1/2改变；随后实际owner/proxy路线改变未来候选排序。排序是T0直接判定规则，owner历史是上游可能机制，不能当作二选一。没有强制固定候选或伪造owner，规范状态对照仅收紧committed微差解释，不证明所有owner中介或全局EMA收益。

11次输出均与原独立AR36token相同，396new tokens，302生成forward+1teacher=303；实际采样wall24.883秒、RSS4901736448 bytes、线程13、GPU全局5659MiB、可用主存最低13485785088 bytes。采样.5s含背景/漏短峰，不用于速度排名。teacher与观察exact hidden cosine>=.99999，source/model/snapshot/PLAN/tool/oldraw绑定前后通过。selected244790261 bytes仅本机.tmp/q178-numerical-20261014-v1，SHA2f71c78210b1609a889b0d3cfec223fd818dd74c625d6eed32540d91008d86a0。首次离线脚本导入路径失败在加载数据/模型前，改同目录import后复算通过，说明保留；测量tool/data没改。3项新针对性覆盖prefix末位、实际cache根与异常恢复，完整本轮验收另有日志，不更新旧全量计数。

新q179–q182的独立原生与双向结果见[后续报告](../../output_space_followup/docs/STUDY_REPORT.md)。完整权重/缓存/selected张量不入Git，未改默认、科学src、推送、合并或删数据。

## q178 provider算子隔离（2026-10-14）

本轮先冻结[OPERATOR_PLAN](OPERATOR_PLAN.md)，在已有规范前缀anchor/v和root85单槽移植上，分别改变**root85之后**的代理映射计算。S64把模拟EMA/slot计算放到CPU FP64，再将slot转回FP32并保留原GPU norm；N64/N32保留原GPU FP32 slot，只把norm标量分别换为CPU FP64归约后转FP32／CPU FP32归约，scale乘除仍在GPU。每次调用使用当时真实proxies，映射本身不改anchor/v/proxies；后续模型输出和proxy历史可以变化。

| 映射方式 | self accepted / calls | 一阶←零阶 accepted / calls | 相对对应native的完整语义轨迹 |
| --- | ---: | ---: | --- |
| native规范状态控制 | 8 / 27 | 9 / 26 | 原规范控制张量与轨迹精确重放 |
| S64 slot计算精度 | 8 / 27 | 9 / 26 | 相同 |
| N64 norm计算精度 | 8 / 27 | 9 / 26 | 相同 |
| N32 norm计算后端 | 8 / 27 | 9 / 26 | 相同 |

root86/89/108的六组冻结状态输入逐组重算：native生成的全部mask与旧保存值逐元素相同，三变体有效改变mask，最大max_abs5.960464477539063e-8；后续同位seed logits出现小幅数值变化，所检查窗口最大约8.36e-4，但合法双槽margin和实际接受路径保持。[离线分析](operator_analysis_v1.json)记录root86/91/108的两槽margin和第一槽路径合法性，不从无效第二槽推断接受。工具和既有规范/移植helpers的来源绑定前后相同。

CPU/CUDA profiler捕获一次规范self root86 provider mapping，共84个CUDA launch、3个aten::linalg_vector_norm调用；External id将norm关联到实际符号`_ZN2at6native13reduce_kernelILi512ELi1ENS0_8ReduceOpIfNS0_10NormTwoOpsIfffLb1EEEjfLi4ELi4EEEEEvT1_`。这定位的是provider中的norm归约。N32在相同FP32输入下替换该算子后端，N64改变归约精度，均没有改变本固定对照的完整路径。不能据此把旧pos88 transformer hidden微差归因给这个kernel，也没有隔离其内部指令／归约树。

解释范围是：root85之后这些provider运算的舍入／归约实现不是维持本次移植路径和8→9差异的必要条件。root85原donor/self向量保持native，root86初次排序因此不受本次变体直接干预；**入口向量映射的舍入、transformer生成proxy hidden的舍入、算子交互、反向零阶对照均未独立排除**。后者已写成新Study的[固定行q_proj协议草案](../../output_space_cross_task/docs/KERNEL_PLAN.md)，尚未执行。规范状态同步也不是精确实数模型。

8次完整输出均与独立AR一致，288new tokens/220 model forwards，辅助模型forward0；实际采样wall26.896秒、RSS5150023680 bytes、线程13、GPU全局6267MiB、最低可用主存11469459456 bytes。资源采样.5s含背景且可能漏短峰，不是allocator峰或速度比较。selected182573933 bytes只在本机.tmp/q178-operators-20261014-v1，SHA0a6cc44cf424e83d1ecc2d34a433e6cca8255b1c60581edf54649f2ba19c1538；Chrome trace也只在本机，其SHA与真实kernel名已保留[正式证据](operator_diagnosis_v1.json)。profiler的单cycle事件提示已保留日志，没有丢弃失败数据或安装依赖。

[PLAN结果评审](OPERATOR_PLAN_REVIEW.md)保留边界；[跨任务Study](../../output_space_cross_task/README.md)仅草案和分词预检，q241–244未make/launch。[最小提交清单与PR草稿](../../../docs/research/publication-plan.md)仅本地准备。科学src670c744e0535dcad、默认、原PLAN／旧helper／成功Run保持不变；未推送、合并或删除，完整weights/cache/raw tensors不入Git。

工具导航验收发现新CLI缺少docstring运行示例，补齐示例和layout导航；测量时原文以[源码快照](operator_tool_v1.py.txt)保留并核对旧tool SHA，执行AST除模块docstring外一致，旧报告未重签。初次分析原JSON保留，[后续离线复核](operator_analysis_v2.json)绑定当前分析器。草案description冒号未加引号被配置展开拒绝，已就地修复，失败发生在make／模型运行前并保留记录。

本轮累计26项相关测试／展开／文档检查通过，Ruff与mypy56通过；四旧Study的来源／PLAN锁及16份原始证据门复核通过。首次草案YAML与工具导航检查失败已保留，修复后仅重验受影响项。两份测量源码快照用局部.gitattributes保留原字节，暂存Git blob与旧证据SHA一致；未改旧测量JSON或重签合同。
