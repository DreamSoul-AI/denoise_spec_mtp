# SD RAM准入与4B空档执行

> 4B BF16容量探针完成，256/256数学门通过，实测峰值8,808,693,760 bytes；正式门为10,956,177,408 bytes。
> 范数v2八格已make，单一父队列79868等待实际GPU空闲；首格6ee3f749ee20c450尚未execute，不填τ。
> BC60原worker66500及RAM门保留，探针后已恢复；格间满足原8B准入时优先让回。
> 本轮33项相关回归和Ruff通过；按主题本地提交，完整里程碑再PR。

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
