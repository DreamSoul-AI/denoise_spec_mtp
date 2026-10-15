# BC30固定480方向对照阶段报告

当前步骤：template全480及原生Run终验成功，单队列已自动进入random0；其余新格继续排队。
实测自检：template的80,932个提交token全过，pooled τ=1.507777653；完整矩阵仍未完成。
出处：[首格有效结果快照](direction_partial_v1.json)，完整token/trace及Run均留本机；零偏置单列旧结果复用来源。
下一步：队列继续random0→random1→random2→content；完整后再判方向总体差异，不因首格结果改对照。
阻塞：暂无GPU/数学门阻塞；BC60尚未声明，本轮完成后按forward/token工作量决定，不测速。

2026-10-16新指令已冻结[PLAN](PLAN.md)。四窗口不能回答总体唯一方向问题，本轮不以其结果代替全量。CPU控制/读出七项及文档四项通过；`tools/analyze_4b_full_directions.py`复用原五方法native读出，pending只记进度，不补零或平局。原生5格全部成功、Study process通过才发布正式JSON；方向与旧五方法的关系按PLAN单列。

主实验五方法加AR11/11和HF第三方失败预检均已通过PR20/21交付；PR21已合dev，相关远程分支已删。当前目标继续扩大到方向全480，目标模式仍active。本报告只填实际结果，不为pending格补τ或胜平负。

CPU集成记录：PR22首轮远端CI为497 passed/3 failed（run 38768912287），失败来自CPU工具通用模块名`analyze_results`污染旧测试，以及新工具docstring缺少使用命令。读出改用唯一模块名加载，保留原生测量代码不变；新增无污染断言后，方向/旧配对/文档13项针对回归通过。修订提交继续跑远端CI，不把旧失败记为通过，不中断GPU队列。

修复后远端验证：`c87382f`两项CPU CI及Branch flow全部通过，PR侧[run 38769926465](https://github.com/DreamSoul-AI/denoising-speculative-decoding/actions/runs/38769926465)完整测试500 passed、1个上游原码SyntaxWarning。仅CPU集成通过，不能替代尚未完成的GPU全480结果。

## 首格完整结果（其余方向待完成）

来源：[direction_partial_v1.json](direction_partial_v1.json)的`cells.template`、`cells.zero`及`vs_existing_five`。文件`complete=false`，不代表整个Study通过。新template Run为`1aa045b502c798f1`；zero复用旧`30/input_zero`，没有重跑。

| 组 | pooled τ | prompt mean τ | category pooled等权mean τ | accepted | 主calls | 新输出/argmax全过token | AR exact |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 固定e2−e1 | 1.507777653 | 1.541530751 | 1.513855801 | 27,227 | 53,838 | 80,932 | 179/480 |
| 零偏置/旧输入零阶 | 1.422420206 | 1.479837486 | 1.430896407 | 23,926 | 56,938 | 80,787 | 168/480 |

原生输入一阶仍是旧方法结果，含β0.9999的真实EMA更新：pooled τ=1.511957584（旧正式证据），不能称为严格固定方向。新固定e2−e1相对原生输入一阶的accepted胜/平/负为104/236/140，calls为110/234/136，逐prompt τ为105/229/146；总accepted少144、主calls多170、输出多34。由完整480数据确认二者接近但不等价，不回写主方法排名。AR一致率只诊断，输出长度不同，不把调用数差当等输出测速。

剩余三个随机种子及内容初始化尚无完整结果，不能据此判断收益是否只来自原方向。category聚合按原数据实际category等权，非已确认论文任务权重；τ不含prefill首token，主calls含prefill，accepted为裁剪前计数，沿用原报告口径。
