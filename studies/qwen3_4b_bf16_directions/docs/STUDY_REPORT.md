# BC30固定480方向对照阶段报告

当前步骤：五个新格已由原生单队列启动，首格template运行中；当前快照56/480，后续以Run进度文件为准。
实测自检：首格前56条共10,895个提交token检查通过、7,129次模型调用；不作为完整τ或总体方向结论。
出处：本机`runs/1aa045b502c798f1/assets/direction_progress.json`和逐条私有`direction_partial_private.jsonl`，完整Run不入Git。
下一步：队列继续template→random0→random1→random2→content，零偏置复用旧完整480；完成格再原生终验和配对读出。
阻塞：暂无GPU/数学门阻塞；BC60尚未声明，本轮完成后按forward/token工作量决定，不测速。

2026-10-16新指令已冻结[PLAN](PLAN.md)。四窗口不能回答总体唯一方向问题，本轮不以其结果代替全量。CPU控制/读出七项及文档四项通过；`tools/analyze_4b_full_directions.py`复用原五方法native读出，pending只记进度，不补零或平局。原生5格全部成功、Study process通过才发布正式JSON；方向与旧五方法的关系按PLAN单列。

主实验五方法加AR11/11和HF第三方失败预检均已通过PR20/21交付；PR21已合dev，相关远程分支已删。当前目标继续扩大到方向全480，目标模式仍active。本报告只填实际结果，不为pending格补τ或胜平负。

CPU集成记录：PR22首轮远端CI为497 passed/3 failed（run 38768912287），失败来自CPU工具通用模块名`analyze_results`污染旧测试，以及新工具docstring缺少使用命令。读出改用唯一模块名加载，保留原生测量代码不变；新增无污染断言后，方向/旧配对/文档13项针对回归通过。修订提交继续跑远端CI，不把旧失败记为通过，不中断GPU队列。
