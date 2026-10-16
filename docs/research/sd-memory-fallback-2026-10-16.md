# SD RAM准入与4B空档执行

> 首格template/0.5×全480完成；入口导出故障已通过原生collector与既有工具恢复，未重跑execute、未改原始SHA。
> pooled τ=1.471389646；prompt平均1.517576442；类别平均1.479149404；argmax80,940/80,940，AR177/480仅诊断。
> 来源：`.tmp/norm-collect-recovery-20261016/readout/norm_pending.json` 与 `recovery_evidence.json`，Run6ee3f749ee20c450。
> BC60 worker66500自然通过原RAM门并运行；剩余七格独立版本续跑，保留原v2冻结入口与失败历史。
> 显示进程分类已接入待运行Study，四phase导出与配置等82项定向CPU检查通过；不打断BC60。

2026-10-16 19:15 Enmao追加授权：核验8B实测峰值加2GB门，安全回收本会话等待进程工作集；仍不足则在GPU空闲单队列执行原4B范数八格。不改prompt、BF16 only、不测速，不终止任何活实验或其他会话进程。

8B门17305047040+2147483648=19452530688 bytes，计算正确；本轮采样峰值16503287808 bytes较旧峰值低，但仍不能消除目前主机缺口。保留原BC60进程/源码/门。19:17按官方EmptyWorkingSet API只处理已核验父子链的66500/50576/50640；三个调用成功，系统available从16487923712变为16640319488 bytes（观测差152395776，含同期系统波动）。未确认可终止的残留python，未杀进程，未处理其他会话、用户应用、文件或数据。脚本及逐PID结果原件在主仓.tmp/sd-memory-20261016/reclaim.py、reclaim_result.json。

参考：[Microsoft EmptyWorkingSet](https://learn.microsoft.com/en-us/windows/win32/api/psapi/nf-psapi-emptyworkingset)。它是工作集回收，不能据此宣称释放了等量私有提交内存或解决RAM缺口。

## 登记后续容量标定和互斥协议

4B此前借用了8B预算，不是4B实测；先对已有ModelScope4B做一次独立容量标定，再以实测进程树峰值加2GiB准入正式八格。权重14文件SHA已匹配旧snapshot；固定480中最长输入q295、1500 token用于容量上界，保持原token IDs。只做4B BF16/eager、原BC30双mask/nine drafts、template2倍；容量探针关闭EOS早停到256上界，不输出方法τ，不作为正式矩阵或新科学结果。源解码计时置零，保存数学门与容量，不测速度。首次容量探针启动预算是已有权重文件总量8060927256 bytes加当前进程RSS与2GiB，并明确不是既有峰值；测量后才冻结正式4B资源门。若该探针本身不能安全放行则保留未启动。

GPU前后均检查nvidia-smi无其他实验Python；若有dayan/量化活任务，等待自然完成。为消除BC60与4B争抢空卡，严格核验BC60仍在RAM-wait后仅对本会话66500做可逆suspend；不终止，不改其源码。容量标定/单个完整4B格结束或异常时finally恢复BC60，保留创建时间/恢复记录。八格由单一父队列逐格执行，格间若BC60已具备原RAM准入，先恢复并让BC60完成再接剩余4B；不重跑成功格、不并行队列。当前8B执行树不改、不移动，范数在主仓独立冻结make，最新明确授权替代此前“等8B自然退出才准make”的排班限制；不是绕过原未授权拒绝。

上述为登记时状态：容量与八格当时均未启动；后续实际状态以下节为准。正常本地主题commit，完整里程碑再PR。

## 实际容量结果与正式准备

量化pid76080在先占卡，第一次探针在载模前安全拒绝，未暂停BC60；唯一等待器76316随后在量化自然退出后启动容量子进程66036。固定q295/1500输入、强制256容量token的BF16数学门256/256通过；采样进程树峰值8808693760 bytes，最低available8399450112 bytes，CUDA peak reserved10076815360 bytes。探针退出码0，finally已恢复66500。正式4B初始RAM门为10956177408 bytes（实测峰值+2GiB），free VRAM门为10634 MiB（peak reserved+1024MiB）。见[容量证据](../../studies/qwen3_4b_bf16_bias_norm_scan/docs/capacity_calibration_v1.json)；它不是新正式τ结果，也不保证全部480路径的峰值不增长。每prompt保留2GiB available门，逐格继续采样。

新增独立norm_admission.py只服务4B，8B文件/门原样保留。导入测试发现新增同目录模块路径缺失，已修复；33项相关回归及Ruff通过。正式版本改为v2-capacity，原0/1倍端点与全部科学参数/固定480未变。当前准备原生make和逐格run-one，先等待实际空卡；8B一旦具备原准入，在完整格间优先让回。量化新pid63996已先上卡，不抢占。

## 八格原生队列已登记

本地提交cbcd1e4后，v2-capacity原生make成功，生成8个新Run。唯一范数父队列79868已启动，首格template0.5×的Run为6ee3f749ee20c450；当前native execute尚未开始，等待量化已在运行的GPU进程55108自然结束，不抢占。后续依次template2×、random0/1/2各0.5×/2×，逐格run-one原生全阶段，完成格后finally恢复BC60；无失败自动重试。状态与各格资源在主仓.tmp/sd-memory-20261016/norm_queue.latest.json及<run_id>.capacity.json；启动器为run_norm_queue.py，标准输出/错误分文件保留。8B原队列50576/BC60 66500保留；它的RAM条件若在格间满足，范数等待8B先上卡。

## 首格已执行与读出合同修复

量化自然释放后，19:33父队列79868接首格6ee3f749ee20c450（template0.5×），worker73008实际载模执行；同一时刻nvidia-smi只有该Python计算进程。BC60在此完整格期间仅可逆暂停，格后finally恢复。一次只读进度快照为28/480、5245 token检查数与生成数一致；这不是全量验收或τ。

CPU核对真实make索引时发现读出合同误把完整factors与局部axis直接相等比较，合法索引会被误拒绝。现使用RPipe已有deep_merge合并公共experiment_config与轴配置后严格比较，保留eval/version/spec全字段和八格次序约束；新增wrong_eval与partial_factor拒绝回归。未make测试改为隔离临时Study，避免依赖本机是否已make。35项相关回归、真实make索引预检与Ruff通过。修改仅在未被活动Run引用的分析脚本和测试，不改冻结科学/资源执行源，不重签或重跑首格。先前完整测试进程在修复前已收集旧用例，故保留7项失败记录；稳定源码的完整套件重新运行中，不记作已通过。

## 稳定源码最终CPU验收

修复后稳定源码重新完整执行`python -m pytest tests/spec_mtp -q`，553项全部通过；`ruff check src tests studies tools`通过，`mypy`56个源文件无问题。仅保留第三方原字节代码已知SyntaxWarning。此前7项旧收集用例失败不算通过，以上是独立重跑结果；35项定向检查和真实原生make索引检查也均通过。当前源分支analysis/sd-pending-results保持本地合批，不为本轮文档/准备另开PR。

## 20:13 首格恢复与原生入口修复

唯一范数父队列79868在首格execute完成后因collect包缺少run导出退出；它的finally已恢复BC60。BC60随后自然通过原19,452,530,688 bytes门开始运行，不再是RAM等待。CPU旧入账watcher因原生失败退出，未误记成功。恢复使用原有collector和tools/revalidate_run.py，保留失败result（SHA9b822e70ccbbb9b546ebe83a7630a755559bacec59483584bb5e2587b65b6d0f）及原始六文件SHA；80,940 math tokens全通过，AR exact177/480不阻塞。首格accepted25,882、committed80,460、decode_calls54,683；Σcommitted/Σdecode_calls=1.4713896457765667。读出已通过原生来源、输入与raw门，六个有效端点不等于八新格完成。

新continuation只接原axes[1:]七格、新version，原NormEval科学实现不动，修正四个phase包入口并接19:53显示进程分类；原v2入口/未运行七Run保留，不重签。新配对Study同步补四入口。82项定向回归通过，完整套件另行执行后才报告。原失败watcher输出保留；续跑入账使用新目录和逐来源映射。未启动第二GPU任务，不放松RAM门，不测速度。

续跑make七Run成功，新首格d288934359a7ede1；唯一等待队列60480，CPU只读入账器78720，旧79868/75696已退出。队列不含suspend/terminate/kill，仅等待原BC60身份自然退出、实际CUDA空闲、VRAM10634MiB与实测峰值+2GiB。每格监测进程树RSS并向上更新下一格RAM门，不下调既有峰值。首格入账已单独严格复验，原失败watcher文件保留。

完整618用例套件中仅两项工具文档检查失败（缺layout索引/用法docstring）；补齐后包含三项文档门、四阶段入口、来源映射、显示分类和原norm/paired门的89项定向检查全部通过。未声称重新全跑完整套件。工具仅docstring字节变化，因此旧新Study的七个未执行Run及冻结元数据保留备份，continuation version更新v4-documented，重新make新七ID；只替换本会话等待中的CPU队列60480/入账器78720，不触及BC60或其他GPU/显示进程。

V4 operational update: documentation-only helper SHA change; superseded unexecuted seven IDs retained with metadata backup. Current first Run `6719b3ae2c089133`, serial waiting queue `64880`, read-only ledger `50944`. Earlier60480/78720 CPU processes exited before replacement; BC60 was never interrupted. Native make/source bindings renewed only for the new version, not old completed evidence.
