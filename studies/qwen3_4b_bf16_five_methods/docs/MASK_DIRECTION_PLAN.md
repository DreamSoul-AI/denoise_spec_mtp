# 固定数据下的模板方向对照

2026-10-15，按Enmao明确指定的四类对照执行。不提出新主方法，不改原五方法定义、数据、prompt、chat模板或任何input token。五方法BC30/60各480条加一次AR的11/11完整验收已在原Study完成，本协议仅是局部分析对照。

## 一、固定上下文与八格

仍使用已冻结的输出零阶轨迹q121/R1、q401/R0、q241/R1、q161/R2，四处真实prefix/cache/tree/位置和注意力固定，下一验证块沿原输出零阶规则。8格/窗口共32格，总forward上限96，不扩CPU筛选、不生成完整新矩阵。

| 格 | 当前块输入mask的速度 |
| --- | --- |
| zero | 原输出零阶控制，不是输入零偏置 |
| input_first | 原输入一阶同历史控制 |
| input_template | 原v=e2−e1，固定于原prompt最前两token的embedding差分 |
| input_random_0/1/2 | 3个固定随机种子0/1/2，各用同一个随机方向服务全部4个prompt；范数匹配原e2−e1，固定偏置、不随内容更新 |
| input_mean | 零速度，保留原updating mean；即输入零阶，不是frozen mean |
| input_content | 仅把速度初始化移到原用户正文最前两个token，从该处起按原β处理prompt后缀，再正常更新已提交token；mean仍由完整prompt初始化并以原λ更新 |

随机方向用独立CPU Generator的标准正态向量归一化到原差分范数，再转实际BF16；记录实际范数比/与原方向余弦，范数比误差必须<1%。该CPU采样不是FP32模型前向，不搜索种子。正文位置通过原SpecBench第一turn和原tokenizer offset定位，重新渲染仅用于核对与冻结input_ids逐token完全一致；实际模型输入始终取原manifest。四处正文起始均为index3，若数据/渲染/位置不符则停止，不改prompt修正结果。

内容初始化保留自己的原生幅度，未额外归一化到模板范数，不能把其方向与幅度效应分开。它也不是只读出时换一个固定内容方向，而是从内容差分开始重新执行原生速度EMA，mean完全不变。其余β=.9999/λ=.1/γ=1、BC30/双mask/动态树剪枝不变。

## 二、判定与证据

报告每格第一/第二目标排名、树宽及实际下一块接受数，并分别相对零偏置、原模板偏置和原生输入速度统计赢平输。3个随机种子分开列，不选最优种子。目标是检验本批提升是否仅限e2−e1方向；若随机/内容也提升则否定该局部“只有原方向”版本，不能直接外推全480。

当前owner argmax/接受路径不变；输出零阶控制续接旧Run；全部局部提交选择等于对应验证前向argmax。模板/native/零偏置的已测控制逐项对照前批，不重签旧Run。独立AR仍只报告，不新增AR前向。原数据SHA、manifest SHA、内容起始、随机种子、实际速度范数/余弦与工具/协议/model/source/private logits SHA均保留。

## 三、串行资源与范围

单次命令`--template-control --early-template --direction-controls`，只用实际nvidia-smi GPU驻留Python与显存准入，初始free≥14GiB；CPU进程不查询、不读源码登记SHA。未知GPU作业/容量不足保留deferred，不抢占，不杀外部进程，不起等待或重叠队列。

仅ModelScope缓存Qwen3-4B BF16/T0/eager/default，不跑8B或测速，不进入算子机理。控制/数学/来源/有限值/OOM/预算失败保留停止，不自动重跑或换精度。源码默认配方与原成功Run不改，权重/cache/完整token/logits留本机；正式标量及报告按主题commit/push/PR合dev。
