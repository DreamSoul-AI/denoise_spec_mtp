# BC30固定480方向对照阶段报告

当前步骤：BC30全部六格各480完成；补齐Study process通过，原GPU队列自然exit0。
最新发现：content τ=1.364829262低于zero1.422420206；三预定随机方向均高于zero，random2也高于template。
出处：[正式证据](direction_evidence_v1.json)及[最终报告](../../../docs/research/4b-full-direction-controls-2026-10-16.md)；485,860审计token全argmax通过。
下一步：CPU回归、PR22合dev、清理对应远程分支；本轮BC60方向不追加，理由见最终报告。
阻塞：无；以下为保留的历史阶段快照，未完成表述仅指各自快照时点，不代表当前状态。

2026-10-16新指令已冻结[PLAN](PLAN.md)。四窗口不能回答总体唯一方向问题，本轮不以其结果代替全量。`tools/analyze_4b_full_directions.py`复用原五方法native读出，pending只记进度，不补零或平局。最终取原template成功格、补齐Study四个预定成功格及旧zero；补齐Study process必须通过，原Study资源失败终验原样保留。六格均完整并通过来源与数学门核对后才发布正式JSON；方向与旧五方法的关系按PLAN单列。

新版研究计划已按模板十章重写并纳入文献表：[中文正本](https://github.com/DreamSoul-AI/denoising-speculative-decoding/blob/b00ecc0a188bb1a2845f061e958fdac37da7bcce/docs/research-plan.md)、[英文译本](https://github.com/DreamSoul-AI/denoising-speculative-decoding/blob/b00ecc0a188bb1a2845f061e958fdac37da7bcce/docs/research-plan.en.md)，由PR23经CI合dev。两个中文规范/模板逐字节沿用RPipe固定版本；英文规范/模板仅各一处导航适配，来源和SHA在其standards README。本次是对现有研究的组织补全，不是事后预注册；本Study及补齐Study的冻结PLAN/科学源码原字节保持，content原进程未被打断。计划远程分支已清理，当前方向工作分支保留，见[清理记录](../../../docs/research/remote-branch-cleanup-2026-10-15.md)。

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

首格快照时三个随机种子及内容初始化尚无完整结果；后续完整格另列如下，不回写该快照。category聚合按原数据实际category等权，非已确认论文任务权重；τ不含prefill首token，主calls含prefill，accepted为裁剪前计数，沿用原报告口径。

## 随机0完整结果（矩阵仍未完成）

补齐Run `2c3e7547a4f931a7`原生succeeded，全480经原生来源/输入/合同/argmax复核通过。来源：[direction_partial_v2.json](direction_partial_v2.json)的`cells.random0`、`vs_template`及`vs_existing_five`；`complete=false`，原资源失败与新Run替换关系均保留，未改旧首格快照。

| 组 | pooled τ | prompt mean τ | category pooled等权mean τ | accepted | 主calls | 新输出/argmax全过token | AR exact |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 同范数随机0 | 1.495188134 | 1.537621631 | 1.508771530 | 26,938 | 54,617 | 81,425 | 179/480 |

| 第二组相对第一组 | accepted胜/平/负 | calls胜/平/负 | τ胜/平/负 | Δaccepted | Δ主calls | Δ新输出 |
| --- | --- | --- | --- | --- | --- | --- |
| template → random0 | 201/53/226 | 186/51/243 | 195/46/239 | -289 | +779 | +493 |
| zero → random0 | 363/29/88 | 333/28/119 | 360/27/93 | +3,012 | -2,321 | +638 |
| 原生input_first → random0 | 191/54/235 | 184/49/247 | 183/47/250 | -433 | +949 | +527 |

该固定随机种子的范数比在480条均为0.999963522，cosine_to_template均为0.030544994，完整prompt mean全保留；这些是BF16方向初值的实际标量，不用理想范数1替代。固定模板首差分在这批输入相同，因此同一随机种子也给出同一固定偏置。随机0相对zero的总量及多数逐promptτ均改善，说明本批收益并非只在e2−e1方向出现；但template略优于该随机0，且仍有88条accepted和93条τ输给zero。两个其他随机种子与content未完整，不据单种子推断任意方向普遍有效或方向不重要。输出长度相差638，calls差不能解释为同输出加速；AR一致率仅诊断。

## 随机1完整结果（矩阵仍未完成）

Run `5fec59e54de877eb`完整480并原生succeeded，来源：[direction_partial_v3.json](direction_partial_v3.json)的`cells.random1`及两类配对。pooled τ=1.464349086、prompt mean τ=1.511211546、category pooled等权mean τ=1.478840563；accepted=25,809、主calls=55,710、decode calls=55,230、decode committed=80,876、实际新输出/argmax全过token=81,356，AR exact=175/480仅诊断。

| 第二组相对第一组 | accepted胜/平/负 | calls胜/平/负 | τ胜/平/负 | Δaccepted | Δ主calls | Δ新输出 |
| --- | --- | --- | --- | --- | --- | --- |
| template → random1 | 172/51/257 | 168/47/265 | 164/45/271 | -1,418 | +1,872 | +424 |
| zero → random1 | 308/25/147 | 292/30/158 | 306/28/146 | +1,883 | -1,228 | +569 |
| 原生input_first → random1 | 178/41/261 | 170/38/272 | 167/36/277 | -1,562 | +2,042 | +458 |

480条方向初值范数比均为1.000066400，cosine_to_template均为0.014653734，完整prompt mean全保留。两个预定随机种子相对zero均改善，但幅度不同且仍弱于template；不等于任意同范数方向都有效，也未分离方向与长期解码路径差异。random2/content仍待完整，输出长度差及全部输局保留。按用户最新排班指示，random1完整终验后才释放GPU给量化v3，未中途中止。

## 随机2完整结果（仅content待完成）

Run `95aff7e5e533a947`完整480并原生succeeded，来源：[direction_partial_v4.json](direction_partial_v4.json)的`cells.random2`、`vs_template`与`vs_existing_five`。pooled τ=1.523884714、prompt mean τ=1.581027391、category pooled等权mean τ=1.533153390；accepted=27,680、主calls=53,045、decode calls=52,565、decode committed=80,103、新输出/argmax全过token=80,583，AR exact=170/480仅诊断。

| 第二组相对第一组 | accepted胜/平/负 | calls胜/平/负 | τ胜/平/负 | Δaccepted | Δ主calls | Δ新输出 |
| --- | --- | --- | --- | --- | --- | --- |
| template → random2 | 257/48/175 | 257/53/170 | 267/47/166 | +453 | -793 | -349 |
| zero → random2 | 384/23/73 | 383/19/78 | 401/17/62 | +3,754 | -3,893 | -204 |
| 原生input_first → random2 | 257/43/180 | 257/53/170 | 263/46/171 | +309 | -623 | -315 |

480条方向初值范数比均为1.000049949，cosine_to_template均为−0.046994805，完整prompt mean全保留。三个预先指定随机种子全部高于zero，且random2同时高于template及原生input_first；不支持“这批收益只来自e2−e1方向”，固定模板方向也不是这三个随机种子中的必然最优。随机0/1弱于template、random2强于template全部保留，不挑种子回写主实验或推荐新方法。只有三个固定方向、单模型/预算/greedy路径，不能据此称任意方向有效；输出差异使calls和接受数不是等输出性能比较。content仍待完整，最终矩阵及聚合待其原生终验。

## GPU准入中断与补齐

random0原Run `be910fe1fa042b28`在北京时间00:57:07的下一prompt准入时观察到真实GPU Python PID65348，按冻结规则抛出`Foreign GPU work appeared`，原生状态failed。此前完整46条共9,028个提交token经原生`_check_argmax`对token/hash/owner链复核通过，实际5,923次模型调用。该格不是方法正确性失败或OOM，也没有有效全480τ。

证据：[resource_interruption_v1.json](resource_interruption_v1.json)，绑定原failed result、完整私有partial JSONL和progress SHA；完整失败Run保留，不把46条拼接成全量或重签成成功。外部PID随后已不在实际GPU列表，原串行队列自动进入random1；不杀外部作业，不重启当前有效进程、不另开队列。原队列结束后仅为缺失因素建立新版本完整480补齐，具体门与唯一有效格选择见[RECOVERY_PLAN](RECOVERY_PLAN.md)。原Study可能保留失败终验，最终如需跨Study组合，会逐项披露，不宣称原失败Study通过。

原队列最终自然exit1：random1完成50条、random2完成9条后分别遇GPU Python PID28472/62864；content在加载前遇PID62864未获准入。原Study终验passed=false，状态原样保留。新增三格partial逐token/hash/owner核验通过，共105次完整prompt执行、20,977个提交token、13,854次模型调用仅列资源损耗，不作为有效全量结果。全部终态与SHA见[resource_interruptions_v2.json](resource_interruptions_v2.json)。补齐版只将两个资源assert改为同进程等待5秒再查，方向control原文保持，15项方向/旧配对/文档CPU回归及Ruff通过；等待不改prompt、不作为测速。

组合读出回归：只允许替换原生failed且明确为上述GPU资源拒绝的格；成功、运行中或argmax失败格均拒绝替换。逐项核对两Study的source_refs与control原文、旧五方法spec/eval/seed/model/runtime合同，最终同时披露原失败Study和补齐Study终验。新增断言纳入方向9项测试并全过，Ruff通过；首次本机测试有2项因沙箱默认pytest临时目录不可创建而setup error，改用仓库`.tmp`内独立basetemp后9项全部通过，未修改GPU执行文件。实时读出仅确认template及zero两格完整，其余记进度，不生成正式全量JSON。
