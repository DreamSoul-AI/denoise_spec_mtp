# 非官方第三方ESP原字节验收

2026-10-15，按Enmao授权尝试HF dataset `Harshvardhan-Mestha/esp-reproduction-artifacts`，commit `ad76f8da29f3bfc7faa20488193c6aa83a9f708c`。它不是作者官方代码，不能替代此前作者来源核查结论。全部4个code/入口文件原字节放src，另保留README及原结果JSON，ORIGIN逐文件SHA及省略的非执行海报/logbook列清单。完整Git clone留本机，不改入口或修正算法。

## 一、兼容边界

原run.sh会安装依赖；原runner硬编码FP16、10个示例prompt、BC60/2及测速。本任务不执行这些动作。外部验收工具仅调用原`ESPDecoder.generate_esp`，加载已有ModelScope Qwen3-8B BF16/eager权重，采用原Table1 SpecBench480冻结manifest和数据，T0贪心、max256、BC10/30/60均单mask、seed123。实际输入token必须与原manifest逐token一致，不改prompt或模板。

原类仍保留其原始flat候选、draft softmax temperature=1、无KV复用等算法；未改成论文动态树剪枝。它是第三方原算法在共同外部设定下的兼容性/正确性验收，不冒称完全同协议Table1复现。计时仅在第三方模块作用域替换为常量，不测AR/TPS、不改全局时钟；原source字节不变。权重/model snapshot、数据、prompt和source/工具/协议全部绑定SHA。

## 二、数学门与停止

先只对固定第一条q121，在三个BC串行验收，原max256不变，每格最多24次模型前向。通过前置数学门才能讨论完整480；如原算法失败，不重写或换候选/数据修结果。

验收只读同一次verification forward的logits，核对原算法即将追加的真实前缀：第一个token对应prompt末行，后续token对应其前一已追加draft的位置。不能把draft自身行或包含未提交候选的末mask行当作正确前缀的预测。每个计划提交token必须等于对应前缀父行argmax，出现第一个不等即拒绝并在实际追加前停止，保留位置、margin、前向计数和私有token证据。独立AR不新增或作门，永不追BF16算子机理。

原算法按最后self-match索引追加之前全部draft，因此会检查真实计划追加的prefix，不只检查其报告n_acc个位置。source报告的model calls可能不含proposal forward，另外逐前向计数；失败格valid_tau为空，不能用上游declared_tau冒充tokens/实际调用，也不能给出论文差值。

如果发生兼容错误或预算不足，同样保留失败，不自动重跑或改源码。其余预算仍可在同一模型上独立做相同固定q121前置验收，最多72次前向。完整480未执行就明确标注，第三方仓库既有结果单列为外部结果，不作为本机测量。

## 三、资源与交付

8B只用于此Table1尝试。单进程顺序跑三个预算，加载前实际nvidia-smi无其他GPU驻留Python且free≥20GiB，各预算再核对GPU驻留作业；CPU进程不查、不登记SHA，不起背景等待或重叠队列，不抢占/杀外部作业。权重优先复用ModelScope缓存，不改CUDA torch或另建venv。

报告含基线/论文差距与不可比设置，全部数字给来源路径，明确非官方、未跑480或失败边界。源代码原样保留，标量结果/报告按主题commit/push/PR合dev，合后删除相应远程工作分支。本地分支、cache、权重、完整token和失败证据不删，不合main、不强推、不花钱、不弹窗。
