# 4B 早期同前缀模板对照

2026-10-15。Enmao最新要求准入只看实际GPU计算进程及可用显存，CPU Python不再检查或登记SHA。PR #19已完成晚窗口/条件窗口24格模板控制，不重跑已有格。本次沿CPU定位的早期候选前移窗口，其他科学源码、默认配方和旧证据不改。

## 一、窗口与四格

仍以原BC30输出零阶Run重建真实前缀，固定同一当前树/cache/已验证历史，四格为输出零阶、输入原生速度、输入固定模板首差分、输入零速度。三种输入控制共用同一已更新mean，β=.9999、λ=.1、γ=1；zero mean不是frozen mean。复用原工具`--template-control --early-template`。

| prompt | 当前输出零阶root | 控制下一root | 原输入两路径首接受差异root |
| --- | --- | --- | --- |
| q121 | 1 | 2 | 2 |
| q401 | 0 | 1 | 1 |
| q241 | 1 | 3 | 3 |
| q161 | 2 | 4 | 3 |

前三处选原控制中到达候选差异root的前驱；q161输出零阶轨迹跳过root3，保留固定root2→4作为反向候选的邻近对照，不声称精确复现原输入root3。候选来自已有结果的条件选择，不是随机样本，原路径与本轮控制路径不同。所有位置在开跑前固定，不按本轮结果换窗口。

每格读当前mask两行logits、原生建下一树，再验证一个块，报告目标排名、树宽、实际接受数、完整seed logits是否等于原生输入速度。当前owner argmax必须保持，输出零阶续接旧Run，所有局部提交选择均须等于验证logits的argmax。独立AR不新增前向、不作阻塞门。每格两次干预前向，加前缀重建，总forward上限64；不沿干预路径继续生成。

## 二、资源准入与执行

只查询GPU0的`nvidia-smi --query-compute-apps=pid,process_name`和`--query-gpu=memory.free,memory.used`；排除本进程PID后，如有GPU驻留Python则延期。Windows WDDM会列出桌面程序，桌面进程不当作Python实验；其显存仍计入实际free。CPU进程不查CIM、不读源码、不登记SHA。显存门为初始空闲≥14GiB（4B BF16约8GB权重加临时KV/树与余量），加载后只查有无其他GPU Python，保留查询记录。这是观测准入，不冒称全局原子排他。

只启动一个串行命令，不启动后台或重叠等待队列。GPU忙则保留0-forward的deferred；不杀其他作业。GPU空闲且容量通过立即加载已核验ModelScope缓存。单个输出目录只创建一次，失败记录不覆盖；质量、来源、控制、预算或OOM失败即保存停止，不自动重跑，不换精度、不追算子。

仅Qwen3-4B BF16/T0/eager/default，不跑8B、FP32模型或测速。来源/工具/本协议/原始观测/私有logits绑定SHA，标量结果及报告按主题commit、push、PR合dev；完整权重/cache/logits/token留本机，不删数据和分支、不强推、不合main。
