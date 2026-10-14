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
