# 输入速度模板差分最小对照

2026-10-15，接续已合dev的PR #18。138个保存输入速度与模板初始差分最大相对误差约0.095%，但代数接近不证明候选或接受相同。本次直接检验这个替代解释，不改变默认配方、科学src、旧Run或原PLAN。

## 一、冻结问题与四格

沿用相同输出零阶真实前缀/cache/当前树和BC30双mask、9节点、Qwen3-4B BF16/T0/eager/default。每格的mean都先用原生输入一阶provider按完整prompt及同一真实已提交前缀更新，λ=.1不变，只在读出mask时替换速度：

| 名称 | 局部mask |
| --- | --- |
| zero | 原输出零阶，复核旧Run续接 |
| input_first | 原输入一阶同历史，β=.9999、γ=1 |
| input_template | 相同已更新mean，速度直接设为prompt前两token的embedding差分，不含后续内容 |
| input_mean | 相同已更新mean，速度置零；不冻结mean，不冒充ESP frozen mean |

这是一次局部速度替换，不把修改后的状态写回原生生成历史；下一验证块仍使用原输出零阶mask控制规则。沿用原工具和树读出，无新框架。模型/forward/mask为BF16，原生输出内部EMA沿用既有实现，不做换精度或舍入机理实验。

## 二、窗口、指标与证伪

1. 无条件4窗口固定q121/q401/q241/q161，仍取原输出零阶第一个root_index≥8，实际R9/8/8/8。四格共16对照，总forward上限96。
2. 条件2窗口另表q121/q401，原控制第一次下一块仅accepted_nodes=[1]的前驱，实际R3/19。四格共8对照，总forward上限48；不能与无条件样本合算总体胜率。
3. 每格重新读同一当前块的mask logits，再原生建树并验证一个块；报告首/次目标排名、d1/d2宽度、真实下一块接受数、与input_first的完整两行seed logits是否相同。保存完整logits于本机，公开只保留标量和SHA。
4. 若template改变任一窗口接受数，则否定“该窗口冻结模板可替代原生输入速度”的强版本；排名或logits变化但接受相同，仍须保留差异。所有窗口相同也只能支持有限窗口，不能外推全480。
5. input_template相对input_mean的接受差异用于检验固定偏置是否在该窗口有效；不预设固定偏置一定有效，不据此宣称内容速度无价值。控制input_first与前批同位置结果逐项比对，差异即报告并停止追加，不追算子。

## 三、准入和停止

使用原工具`--template-control`，条件批另加`--active-depth`，分开新输出目录。先提交协议/工具/测试，再非抢占检查；共享GPU忙则保留deferred，绝不杀进程或抢占。权重继续复用ModelScope缓存，绑定source/model/tool/plan/raw SHA。

新出现的RPipe `watch-version-final.py`已读源码核验，仅调用已检查的CPU远端CI查询脚本；准入按脚本SHA `f33abb9086f09bbf917118b20a5fc10cd3c13cca8ec0690b6d0178ef4a399763`识别及其子进程。未知进程仍拒绝。排队最多20次、每次间隔30秒，只重试0-forward的deferred，任何执行失败不自动重跑。

零forward资源停止记录保留后补充核验`watch-version-dev.py`，同样只读远端CI，SHA `b69fd1fe0c67a405afee52be9599cd79cb06459b5abc23b17860ea9014d2ce92`。新版本额外记录未知PID，控制公式、窗口和预算不变；人工确认0-forward后可新目录重新准入，不重用失败目录或自动重试执行失败。

再次延期所见PID 53808/64588对应`watch-publication.py`，已读源码核验仅查询远端PR/CI，SHA `4f9b8c486aff8b93cc18116100e9013290e469fe8ed362639b4ebf790bf2dece`。停止本任务无模型子进程的等待队列后才修订识别并提交，再用未用过的目录续接；不操作外部查询或实验进程。

实际队列停止检查首次因子进程仍在而拒绝，后续新旧队列短暂重叠，目录存在门阻止重复尝试；已取消重复队列，原队列因目录保护退出，全部0-forward，记录不删除。后续只单次串行准入。第16次的PID 34924/63696是量化CPU校准数据准备：已读两个脚本，只有tokenizer/datasets采样及CPU tensor保存，没有模型/CUDA前向；`watch_calibration.py` SHA `dc3f6db96ca5698f19feba0a7e6a23c2f5bd7602bbf29b38cb78c03c8b29e845`，`prepare_official_calibration.py` SHA `669a03a0e26231c9e7fbb0bd1d261c892dbe2f57da1164abd06123f94c324baf`。仅识别已核验CPU作业，不操作该作业。

全部提交token必须等于对应验证前向argmax，当前owner argmax不变，输出零阶控制续接旧Run。独立AR仅旧诊断，不新增AR前向。任一数学门、来源、有限值、预算或控制失败即保存停止；不跑8B、不测速、不删数据、不改默认配方、不钻算子机理。按长期授权正常提交/推工作分支/PR合dev，保留分支，不合main。
