# q241–q244真实跨任务批次与首个canonical跟进

2026-10-14。依据[原草案PLAN](PLAN.md)及[真实执行增补](EXECUTION_PLAN.md)完成四个原生Run、16输出和20次固定窗口诊断；全部独立AR一致、无context缩短，来源/输入/model/有效因素/Study门通过。原始PLAN和checker协议的“未运行”是当时状态，未修改或重签；本报告记录实际执行。source670c744e0535dcad，ModelScope11文件实际hash、Qwen3-0.6B tied/FP32/eager/T0、100新token预算、static[1,1]/k2、beta.9/beta_prime.99，原生runtime默认与原配方保持。

## 原生与固定双向结果

| qid | prompt / new tokens | 输入accepted | 零阶 | 一阶 | 固定根 | 一阶←零阶 | 零阶←一阶 | 一阶原值 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 241 | 692 / 100 | 14 | 13 | 11 | 716 | 12 | 10 | 11 |
| 242 | 647 / 100 | 21 | 15 | 14 | 658 | 18 | 14 | 14 |
| 243 | 595 / 100 | 35 | 15 | 10 | 600 | 9 | 17 | 10 |
| 244 | 901 / 90 | 15 | 15 | 10 | 905 | 9 | 10 | 10 |
| 汇总 | 390 new / cell | 85 | 58 | 45 | — | 48 | 51 | 45 |

接受数沿用原生所有深度draft验证计数、在预算/EOS最终裁剪前统计，不能把它们直接当作实际提交token数或速度。q242零阶15accepted+85calls大于99committed的末端预算现象按原始口径保留；合法depth2证据还要求对应AR第二target实际存在。部分输出达到100预算，结论只覆盖这些有限轨迹，未扩长或换prompt。

全部四条都有自然语义路径差异，八个移植方向都改变接受总数；一阶←零阶两增两减，零阶←一阶一增三减。不是一阶稳定收益：本批原一阶45低于零阶58和输入85，累计16个开发单位（12translation+4summarization）为输入145/零103/一92，仅描述性汇总，不做随机样本概率、统计显著性、单seed稳定性或任务全面泛化结论。

## 可核验证伪与状态边界

[批次hypotheses](hypotheses_v1.json)由冻结checker实际运行：H1=observed；四条全部可行，无infeasible替代null。H3=not_falsified_in_captured_native_or_transfer_windows，没有满足同位、同一正确第一AR候选、可用第二target、非first-EOS且实际depth2改变的见证；不能把第二margin、未对齐root或预算外接受当作见证，也不能确认全局first-slot-only解释。该JSON的H2=not_tested是原批次状态，后续另有独立合同与证据，原JSON保留。

[固定window选择](window_selection_v1.json)仅按原choose_window规则、在logits/hidden观察前冻结；没有增根、gain搜索、替换prompt或逼迫旧owner路径。完整[移植记录](transfer_diagnosis_v1.json)保留每个原始／新／未访问root、局部损失和收益、两槽rank合法性、真source owner和所有语义trace；[离线核验](analysis_v1.json)重新检查只换[0,1]以及状态equality字段对应真实张量。

后期同位state经常不再逐元素相同：八移植的最大anchor delta约3.81e-5至7.63e-5，一阶最大velocity delta約3.58e-6至8.11e-6；零阶velocity一直为0。它们在完整AR相同的不同块/owner计算路径下出现，不把全部效应概括为纯proxy中介，也不因幅度小就忽略。原值回填的全trace/state保持原值，错误第一槽/EOS/缺target/重复格/失败质量标志都有明确拒绝门。

## 首个阳性q241：canonical量化预测未保持

按原跟进准则选第一file-order有接受变化的可行单位q241，一阶←零阶、entry716、原11→12；另写[CANONICAL_PLAN](CANONICAL_PLAN.md)，在任何canonical计算前冻结，未把新格子附加到原生Study或重签其产物。

| 对照 | accepted | decode calls |
| --- | ---: | ---: |
| native self | 11 | 88 |
| native graft | 12 | 87 |
| canonical self | 14 | 85 |
| canonical graft | 14 | 85 |

native两格精确复现旧诊断全部captured张量与全语义路径。一次792-position teacher的所查exact-root cosine最低.999999523，满足预声明>=.99999；每个真实root>716按相同AR-prefix回填native chronological CPU-FP32 anchor/v并核对KV root，输入proxies在每次patch未改。四输出均AR一致，所有captured同位canonical state门通过；teacher和CPU重算本身是数值干预，不是精确实数基准。

[canonical分析](canonical_analysis_v1.json)给出H2局部“接受总数差保持+1”预测的反例：差由+1变0。**canonical self也从11变14，且两个canonical cell完整语义路径仍不同**，所以这不是“移植影响全消失”，更不能据此唯一归因committed微差。当前回填最大anchor约1.89e-4、velocity约1.93e-5，变动可继续影响后续mask/proxy与path；cosine接近1不保证接受轨迹不变。它明确阻止把q178的canonical8/9稳定直接外推到新prompt。[完整canonical记录](canonical_diagnosis_v1.json)保留新旧roots与回填幅度，未虚构未观察位置的hidden。

![真实接受数与q241独立跟进](figures/acceptance_v1.png)

图由[plot_results.py](../plot_results.py)读取正式native和canonical JSON产生，无新模型forward；[图源hash](figures/source_v1.json)绑定两个来源和图。左图为原生四prompt计数，右图是单独冻结的跟进，不混作原生第五cell，也不以等总数掩盖路径差异。

## 实际资源、来源与复跑

| 原生case | Run ID | make est秒 | 实际Flow秒 |
| --- | --- | ---: | ---: |
| frozen_mean_chain | 743d1f6142b3f3dd | 3 | 42.922 |
| output_order0 | 7e34df29d2881838 | 3 | 36.683 |
| output_order1 | a14c58b5f4a2d4a8 | 3 | 36.232 |
| AR | df90405ec5a03f58 | 3 | 25.882 |

首格校准wall46.159秒、RSS6031347712 bytes、GPU全局7318MiB、可用主存最低9201266688；其余3格launch wall119.064秒、RSS6705946624、GPU7336MiB、最低8286580736，round1且跳过已成功首格。原生16输出共1560newtokens，内部AR审计1170，未超固定预算；make通用视觉容量估计26.5GiB不是实测解码占用，按真实首格校准判断。

20诊断共1950newtokens/1704model forwards，wall91.553秒、RSS4882354176、GPU7272MiB。独立canonical4格400newtokens/349生成forward+1teacher，wall33.264秒、RSS4887367680、GPU6102MiB。均.5s采样，含背景、漏短峰；不当allocator峰或硬件/方法速度排名。

ModelScope缓存仅junction复用，实际11文件/模型digest/输入IDs前后门通过；provider默认master仍不能声称远端immutable revision。transfer raw1894476053 bytes、SHAa69db9e942ff58b7428100a02efeca5edf6fcd8a43b0ba8332a073c06c0bab3f；canonical raw330998213 bytes、SHA0829de37ec82cbfc19f9e7e3d82c4a697d168bccfacc058b23a1d5d4d717d2d9，仅本机.tmp。完整Run/shared/weights/cache/tensors/profiler不入Git，报告只存正式scalar和语义证据。未知的跨环境bit复现仍须新version/Run，原生已成功格不重跑。

## 后续边界

q178本轮[入口Phi与RMSNorm对照](../../output_space_extension/docs/STUDY_REPORT.md)均有有效非零高精度替换，8/9路径保持；局部稳定与本批q241自值变化共同说明不能作全算子/全prompt舍入鲁棒性主张。后续应解释q241 canonical自值变化的首个排序分叉，或在新固定单位上检验H2，先写新target／budget，不逐层搜索有利结果。现阶段保留所有正负结果，不调默认、扩长prompt或以总数相等推断路径等价。

收尾核验：30项针对性测试通过，Ruff通过，mypy检查56个源码文件无错误；5个相关Study的科学source与RPipe provenance冻结门通过，20诊断及Phi/RMS、canonical张量离线复核与旧正式结果逐项一致。新测量工具／协议保留原始字节；旧operator_analyzer快照的Git blob恢复为本机已测量的CRLF字节，仅修复存档换行，不改分析逻辑或历史测量文件。10个精确字节路径的暂存blob与本机文件一致。

未推远程、未开／合PR、未改科学src/default、未删数据。

## q241结构化归因与状态因素反例（2026-10-15）

按新冻结[STATE_FACTOR_PLAN](STATE_FACTOR_PLAN.md)，执行[选择性回填工具](../../../tools/diagnose_q241_state_factors.py)与[结构化分析](../analyze_state_factors.py)。复用q241/seed123/entry716及已有792-position teacher状态，六次生成共600新token、525forward、零teacher／warmup，全部独立AR一致。两个native审计控制重现旧完整语义路径、stats和全部captured张量；四新格在每个真实KV root>716只回填一个坐标，核对另一坐标和incoming proxies未在patch修改，后续自然变化保留。旧成功原生Run和canonical格不重跑、不重签。

| committed同步因素 | 自值accepted | 一阶←零阶accepted | 移植相对自值 |
| --- | ---: | ---: | ---: |
| native（旧格+本轮审计） | 11 | 12 | +1 |
| 仅anchor（本轮） | 13 | 13 | 0 |
| 仅velocity（本轮） | 13 | 13 | 0 |
| anchor+velocity（旧canonical格） | 14 | 14 | 0 |

[完整新生成证据](state_factor_diagnosis_v1.json)与[结构化结果](state_factor_analysis_v1.json)保存正式scalar、全部语义trace、各回填幅度和未访问根。相对native，同步anchor或velocity的自值均+2、移植均+1；双同步自值+3、移植+2。预声明H5“两个状态因素计数效应可加”在自值上被反例收紧：14-13-13+11=-1，而移植为14-13-13+12=0。这个不同交互项再次阻止把原+1消失解释成单一、线性、可按百分比分配的committed舍入贡献。两种选择性同步都使计数差不保持，是q241固定单位的额外反例验证，不是假装新的随机跨任务样本。

### canonical自值／移植为何同数不同路径

双同步两格的第一语义分叉是root720，真实source719/owner0相同。该位置captured anchor和velocity逐元素相同，proxies最大差5.195926666259766；正确第一AR候选264的margin由自值-2.7185325622558594变为移植+1.2852745056152344，命中恢复。随后共同根增益720/731/734/774与损失741/750/780/785各四个相抵；两侧各四个独有root也完整记录，不能按共同根之外假造对齐。**14／14保留了历史代理输入导致的不同候选路径；root720当前committed state差异不是该局部差异的必要条件。** 这并不排除上游历史曾受到committed数值路径影响；本轮未固定整个KV/cache或上游数值路径，不能将proxy差视作唯一中介。两个只同步一项的13／13格也从root720分叉，H6“等接受总数意味着等语义路径”在这三个配对上均有反例。

### 自值控制与committed回填的贡献边界

native自值对双同步自值的首个接受分叉发生在root756，共同根756/783/785新增三个接受，原路径的757/784/786因实际进度而消失。root756 anchor差3.4332275390625e-5、velocity差3.516674041748047e-6，但其代理已累计分化，proxies差22.688066482543945，第一AR候选margin由-.6922931671142578变为+1.2724342346191406。移植控制与双同步移植首分叉在751，第一margin+1.1363706588745117变为-1.1761016845703125：先失去一个，再在756/758/783新增三个，净+2。这里的间接代理传播与排序跨界不可被单个state微差幅度替代。

因此可量化的是这些具体同步干预的接受数效应及路径交互，不能据此认定某一原始committed微差唯一必要／充分。原+1对比消失包含自值基线的+3变化，并非移植影响消失。下一项有价值的局部实验是冻结首个分叉的上游输入，区分即时state改动与累积proxy传播；若实施须新协议，不能把本轮全程同步结果冒充该直接效应。

本轮生成wall35.397秒、.5s采样RSS5132173312 bytes、GPU全局6172MiB、最低可用主存11330322432，含背景且非allocator峰。raw485128429 bytes，SHA914b8331d633f299a089364de5e8556866dc7a5be1637af26c9ae6cc81d5b65b，本机.tmp保留；只有正式scalar/trace证据入Git。现有cross-task四prompt范围未扩大，H5/H6是对已见q241的解释性新假设，不作为独立泛化证据。科学src/default与原PLAN/helpers保持，不推送、不开PR、不删数据。

本轮收尾核验：37项针对性测试及Ruff通过，5个Study的科学source/RPipe冻结门通过，80格保存向量的标量差重新计算一致，18个精确字节路径的暂存blob与本机文件一致。完整原生矩阵、安装包、更多seed/层未重跑；科学源码/default/旧helper/成功Run无改动。

## 固定帧state／proxy分离与两prompt两seed扩展（2026-10-15）

本轮在4a02551之后另冻[LOCAL_FACTOR_PLAN](LOCAL_FACTOR_PLAN.md)与[STATE_EXTENSION_PLAN](STATE_EXTENSION_PLAN.md)，实现[固定帧工具](../../../tools/diagnose_q241_local_factors.py)和[扩展工具](../../../tools/diagnose_state_extension.py)，正式[诊断](local_factor_diagnosis_v1.json)、[扩展诊断](state_extension_diagnosis_v1.json)及[独立离线复核](local_extension_analysis_v1.json)保留所有格与质量门。旧工具／协议／成功Run未修改。

### 首次分叉的时序与真实owner链

源码实读说明：当前树先由上个块选定owner的mask logits生成，之后才调用当前provider.masks_per_owner。因而root720当前state相同这个事实，本身不能定位已经构建的root720候选来源；应检验source719的映射。下表来自两次新canonical完整重放，AR、trace、stats及所有旧captured张量精确复现。

| 实际root | seed来自root／owner | self候选 | graft候选 | self／graft接受节点 |
| --- | --- | --- | --- | --- |
| 716 | 715／0 | 323, 323 | 323, 323 | []／[] |
| 717 | 716／0 | 323, 323 | 323, 323 | [1]／[1] |
| 719 | 717／1 | 11, 11 | 323, 11 | []／[] |
| 720 | 719／0 | 13, 13 | 264, 13 | []／[1] |

717接受一阶节点后进到719；718不是访问点。候选身份在719已经不同但均未命中，首次接受语义分叉仍在720。719 owner0两mask位于720／721，第一logit预测721位置的AR token264；这是root720树的第一候选来源，不是root720当前mask的输出。

### 固定source719：代理替换足以恢复第一候选

以canonical self的完整source719输入／KV／树节点／positions／attention为固定帧。S0=canonical committed anchor/v，S1=同位native self的anchor/v；P0=canonical self incoming proxies，P1=canonical graft incoming proxies。每格只重新计算六mask embeddings，root/node三行和KV保持bit相同，用新cache重放三次。全部原值格完整logits/finalhidden复现，三次结果bit一致，所有格验证三行输出bit相同。

| source719格 | 最大mask差 | root720第一候选 | 对AR264 margin |
| --- | ---: | ---: | ---: |
| S0P0原值 | 0 | 13 | -2.7185325622558594 |
| S1P0只换state | 5.960464477539063e-8 | 13 | -2.7185325622558594 |
| S0P1只换proxy | .011132031679153442 | 264 | +1.2852745056152344 |
| S1P1同时换 | .011132031679153442 | 264 | +1.2852745056152344 |

即时state替换确有非零差：anchor3.814697265625e-5、velocity2.9802322387695312e-6，mask也改变；它不是无效数值控制，但在这组固定输入上未改变第一候选判定。P1与P0最大差1.6823768615722656。**只换代理所得两条owner0 seed logits与真实canonical graft在root720保存的seed logits全向量bit一致**，而root720原值帧的验证root预测确为264。由此在这个固定上下文中，累计到source719的代理内容足以恢复导致root720命中的候选；该对比不需要即时committed微差变化，也未借助更换cache或树节点。

这是owner0、该输入的局部充分性与时序证据，不是全解码因果百分比；没有证明全程state回填对其他位置无影响，也未拆解代理内容每个上游分量。S1是一次同位native-state交换，与上一轮每个root反复回填的总效应不同。

### 当前root720：即时映射影响后续seed，不影响已构建树

固定canonical self的root720帧再做同样四格三重复。state交换anchor2.288818359375e-5、velocity2.4139881134033203e-6，P1差5.195926666259766；state-only mask差4.470348358154297e-8，proxy-only约.037551105。所有格当前root/node验证logits与finalhidden完全相同，因此不改变固定树当前是否命中。后续第一seed对下一AR42377的margin从-1.5146942138671875变为proxy-only的-1.5333003997802734，两者top1仍13，变化保留为非命中结果。没有将24个直接块重放称为24次完整生成或新接受率矩阵。

### 非加性并不普遍，两组greedy seed仅为重放控制

按原文件顺序新增q242、q243各两个固定seed，以原entry658／600、100新token、T0同配方测试。每单位两次原生观测+七次移植，共36次生成／3600新token／3124生成forward；四次747／747／695／695-position teacher，captured exact-root cosine最低.9999997615814209，原样构造canonical状态。全输出与原独立AR一致，baseline全语义／stats相同，单坐标另一state与incoming proxies保全、真KV根、双同步和全部captured回填状态门通过。

| qid／seed | self：native／anchor／velocity／both | graft：native／anchor／velocity／both | self交互 | graft交互 |
| --- | --- | --- | ---: | ---: |
| 241／123（旧证据） | 11／13／13／14 | 12／13／13／14 | -1 | 0 |
| 242／124 | 14／15／14／15 | 18／16／15／13 | 0 | 0 |
| 242／127 | 14／15／14／15 | 18／16／15／13 | 0 | 0 |
| 243／125 | 10／12／9／17 | 9／11／11／10 | +6 | -3 |
| 243／128 | 10／12／9／17 | 9／11／11／10 | +6 | -3 |

交互仍定义为both-anchor-velocity+native，接受数沿用预算裁剪前draft验证口径。q242是“每个单位都非零交互”的反例；q243复现非加性，但符号／幅度不同。它收紧了普遍性假设，不支持稳定收益或统计泛化。q242 native graft相对self+4，双同步为-2；q243分别-1／-7，原值基线改变继续影响配对结论。

T0的select_token走argmax，output_hidden初始化／映射无随机抽样；两个seed在完整trace/stats和六固定窗口的seed logits/masks都bit一致。因此本轮增加两个prompt，不把它们描述成四个独立随机样本。每单位只capture预声明entry+前三+后两共六root（q242：658/659/661/662/744/745；q243：600/601/603/604/692/693）；完整实际trace保留，未访问与新增根明确。六窗口内未出现新的合法同第一正确候选depth2翻转，不能外推为全路径H3成立。

### 成本、证据与剩余边界

local两完整控制200new／172forward+24固定块／零teacher，wall22.613秒、.5s采样RSS4971773952 bytes、GPU全局6580MiB；raw385504563 bytes、SHA712edc1cd3403236c47782bdffb2d73b8617a7413e5bef3df4be0f450b973540。extension wall96.031秒、RSS4920774656、GPU6576MiB；raw318391853 bytes、SHAf04c2199397daf77e35538e2a202d9c79cda1e3b6c7f00e5f35e79878996df17。本机.tmp保留cache帧与张量；GPU值包含背景，采样不是allocator峰，不能用于性能排行。

新增回归覆盖单因素输入保全、固定帧因果注意力／当前验证不变／后续mask输出改变、独立cache、冻结六root规则、greedy seed解释以及716→717→719→720的真实source-owner/候选时序一致性。scope限于q241两个固定块及另两个greedy prompt；未做采样温度、多设备、长路径干预或其他owner充分性试验。科学源码/default、旧helper与原合同不变，未推送、未开PR、未删除数据。

收尾核验：42项针对性测试、Ruff与5个Study科学source/RPipe冻结门通过；新分析重跑保持原证据逐项一致，26个精确字节路径暂存blob与本机文件一致。旧helper/协议/科学src/default无改动，本轮3800生成新token、24额外固定块、4teacher均在预声明预算内。完整安装包/长矩阵/随机采样温度未重跑。

## 非T0完整路径与实际owner1对照（2026-10-15）

依据6cca8fc另冻[SAMPLING_PLAN](SAMPLING_PLAN.md)与[OWNER_PLAN](OWNER_PLAN.md)，执行[采样工具](../../../tools/diagnose_sampling_paths.py)、[owner1工具](../../../tools/diagnose_q241_owner1.py)及[复核](../analyze_sampling_owner.py)。正式[采样诊断](sampling_diagnosis_v1.json)、[owner诊断](owner1_diagnosis_v1.json)、[联合分析](sampling_owner_analysis_v1.json)保留完整路径、256条件验证draw、概率与负结果。原科学source/default/配方、旧诊断工具和合同保持。

### 原source719上下文中的随机验证

先固定上一轮root720真实验证root logits，让旧source719的四个S/P格供给首draft候选，用原生CUDA select_token的multinomial在T=.8／1、seeds200–263分别抽64次验证token。每个温度同一draw bank在所有格共享；state-only候选与原值相同，proxy-only与both候选相同。抽样确实消耗Generator状态；不是拿贪心argmax替代随机验证。这里只评首槽，第二槽的验证分布会依赖选中的第一节点，不能用第一槽结果冒充整条路径。

| 原owner0候选因素 | 候选ID | T=.8首槽命中／64 | T=1首槽命中／64 |
| --- | ---: | ---: | ---: |
| 原值／state-only | 13 | 0 | 0 |
| proxy-only／both | 264 | 64 | 63 |

同位root720验证概率的native CUDA-FP32 mass：T=.8的13／264约5.4372435e-9／.999661922454834；T=1约2.4411347e-7／.9980924725532532。因此原固定上下文中，代理恢复的候选在随机验证下也有明显不同的接受机会；即时state交换仍未改候选。每个温度64个draw是条件Monte Carlo，不是64个新prompt或完整采样轨迹；T=.8恰好全draw为264，T=1有两种token，不因前者观察全同就称其非随机。

raw中exact_candidate_probability字段是原生CUDA-FP32 softmax的数值结果，名称沿用而不宣称精确实数。复核用同后端重算bit一致，另存CPU-FP64参考；owner0候选264在T=.8的绝对差约1.8333e-7、T=1约2.7820e-9。跨后端CPU-FP32复核的失败不当作原生抽样失败，也不通过放宽抽样输出门掩盖；已保存的实际draw与命中数未修改。

### 两条新的完整采样路径

q241/T=.8/seeds123,124/max100/EOS；每单位新生成独立AR，再运行output0/output1，全部输出token精确等于对应AR。两个AR输出彼此不同，突破旧greedy前缀。entry只按原choose_window从实际语义trace选出，并在hidden/logits观测前写锁；没有逼迫访问旧719或选择收益最大的入口。每单位再观察两baseline，执行order1原值self及一阶←零阶；原值完整trace／stats复现，移植through-entry、单槽范围和全AR输出门通过。

| seed／T | 实际entry | 零阶accepted | 一阶accepted | self | graft | graft-self |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 123／.8 | 697 | 11 | 10 | 10 | 9 | -1 |
| 124／.8 | 715 | 9 | 9 | 9 | 10 | +1 |

两移植都改变完整语义路径，符号相反。本轮接受数仍沿用最终预算裁剪前draft计数。原source719条件恢复不等于新采样prefix上的稳定收益；新窗口没有canonical等state因素分解，不把全程移植效应唯一归为proxy中介。这两seed是有限新采样路径，不是统计稳定性结论。

每单位实际7次生成含独立AR，合计14次／1400new／1284forward（其中AR200token／200forward），零teacher／warmup；capture预声明六root，完整actual trace保留，未访问／新增根明确。不重签原生Study或将温度改入默认配置。

### 另一个真实owner：内容改变，但未恢复接受

选择旧真实source717／owner1，mask rows5/6位置719/720，seed下一root719。两次新的T0 canonical完整控制均精确复现旧AR／trace／stats／全部captured张量。固定self的source717 KV／树／根节点／positions／attention，四个S/P格三次fresh-cache重放；12块原值完整logits／hidden精确，重复bit一致，所有格验证三行输出保持，state/proxy/cache scope门通过。

| owner1格 | 最大mask差 | root719首候选 | 对贪心AR1008 margin |
| --- | ---: | ---: | ---: |
| S0P0原值 | 0 | 11 | -18.067363739013672 |
| S1P0只换state | 4.470348358154297e-8 | 11 | -18.067363739013672 |
| S0P1只换proxy | .0055773258209228516 | 323 | -18.32495880126953 |
| S1P1同时换 | .0055773258209228516 | 323 | -18.32495880126953 |

proxy-only两条owner1 seed logits与真实graft下一root719保存值全向量bit一致。它复现了另一个owner的代理内容对候选的影响，却没有恢复greedy接受：11、323都不是1008。固定实际root719验证logits再抽T=.8／1、seeds200–263，所有格各0/64命中。其native candidate mass分别约1.4171e-11／2.2575e-11与2.0936e-9／3.0386e-9，确实非零且不同；64次零命中没有足够信息排除这些罕见概率差，不称为绝对无效。

该owner1与原owner0不同prefix位置、不同正确token与验证概率，不把两者当“owner编号本身”的纯因果比较。结果收紧“代理内容改变就必恢复命中”的解释：内容传播在另一个真实owner存在，接受恢复依赖验证目标与分布。没有搜索其他owner来替换此负结果，也未做第二槽或全路径因果百分比分配。

### 复现成本、回归与剩余范围

sampling wall47.418秒，.5s采样RSS5500076032 bytes、GPU全局7129MiB、最低可用主存10042523648；raw62414293 bytes、SHA164c03066172732ece3eabea256871c9ea61a9f04992fbbf4831c8e57fd37d20。owner两控制200new／172forward+12直接块，wall22.812秒、RSS4972376064、GPU7114MiB；raw192179087 bytes、SHA69cb9734e2a19d5a48664d84982f2d64e6b7089bb1274629bbe46e14b8cf71a1。共1600生成新token、12额外块、256条件draw、零teacher；资源含背景、不是allocator峰。cache/weights/raw完整帧仅本机.tmp。

新增回归覆盖multinomial消耗RNG与共享draw、不同seed实际随机性、正温度draft仍top1而verifier采样、output_hidden两order两seed两温度对fresh AR的token一致，以及owner1 rows5/6与positions719/720，防止误读owner0 rows3/4。本轮证据允许：固定原上下文中的首槽恢复在非T0仍成立，另owner内容变化不必恢复接受，新的完整采样路径存在正负效应。未证明多prompt／多温度／多设备泛化，未将full-path sampled新窗口做等state causal分解，也未证明极小概率事件无效。不推送、不开PR、不合并、不删数据。

收尾核验：47项针对性测试、Ruff与5个Study科学source/RPipe冻结门通过；联合分析重跑与原formal证据一致，34个精确字节路径暂存blob与本机文件一致。1600生成new、12额外块、256条件draw在新协议预算内；旧source/default/配方/工具/Run未改。未做多prompt采样泛化、罕见事件统计检验或安装包／长矩阵重跑。

## 四prompt三seed完整采样扩展与罕见事件检测边界（2026-10-15）

按a5ede78后新冻结[SAMPLING_EXPANSION_PLAN](SAMPLING_EXPANSION_PLAN.md)与[RARE_EVENT_PLAN](RARE_EVENT_PLAN.md)，执行[多prompt工具](../../../tools/diagnose_sampling_expansion.py)、[罕见抽样工具](../../../tools/diagnose_rare_events.py)和[离线复核](../analyze_sampling_expansion.py)。旧q241 seeds123/124两行保留为development，不重跑；新加q241 seed125及q242/243/244 seeds123/124/125，共10新单位。全部T=.8、max100/EOS和原源/默认配方，独立AR、两native、两观测和两self/graft门通过，模型/输入/来源/窗口范围保持。

### 完整矩阵的正负边界

| qid | seed | 来源 | 实际entry | 零阶accepted | 一阶self | graft | graft-self |
| --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 241 | 123 | 旧development | 697 | 11 | 10 | 9 | -1 |
| 241 | 124 | 旧development | 715 | 9 | 9 | 10 | +1 |
| 241 | 125 | 本轮 | 713 | 9 | 8 | 10 | +2 |
| 242 | 123 | 本轮 | 647 | 16 | 13 | 18 | +5 |
| 242 | 124 | 本轮 | 648 | 8 | 7 | 12 | +5 |
| 242 | 125 | 本轮 | 659 | 16 | 12 | 14 | +2 |
| 243 | 123 | 本轮 | 600 | 13 | 14 | 9 | -5 |
| 243 | 124 | 本轮 | 600 | 11 | 12 | 10 | -2 |
| 243 | 125 | 本轮 | 600 | 13 | 10 | 15 | +5 |
| 244 | 123 | 本轮 | 905 | 12 | 10 | 9 | -1 |
| 244 | 124 | 本轮 | 905 | 10 | 12 | 9 | -3 |
| 244 | 125 | 本轮 | 923 | 12 | 12 | 11 | -1 |

正式[完整诊断](sampling_expansion_diagnosis_v1.json)与[分析](sampling_expansion_analysis_v1.json)覆盖全部12单位，其中6增／6减、0null、0infeasible，各prompt三个独立AR输出均不同。汇总zero140／self129／graft136只是这组固定单位的描述，不代表方法稳定优势。q242三次都正、q244三次都负，q241／q243混合；原窗口局部恢复不能预测跨prompt的一致方向。负结果在固定q244、T=.8、当前Qwen3-0.6B FP32/eager、100预算／链k2范围重复，不把3seed称为随机prompt人口统计或一般负结论。

每单位7次完整生成均含自身新AR审计。新70生成／7000new／6328forward，旧14生成／1400new保留不重签；接受计数仍在预算最终裁剪前。旧Source719没有强制访问，entry按原choose_window冻结，capture六root，后续actual owner/root与完整trace不强迫对齐。新probe只换[0,1]，原值self全部重现；全输出逐token等于该seed自己的sampled AR。没有canonical等state分解，不能把完整路径净差唯一归为proxy因素。

### 重复零命中与检测能力

在原实际owner1验证root719上，T=.8／1各用fresh seeds300–4395运行4096个native CUDA select_token单token抽样，共8192draw，零Qwen forward／teacher／生成续写；四S/P格共用各温度的一条draw bank，不当四组独立实验。候选11/323在两温度都0/4096；RNG消耗门通过，T=.8观察1种token、T=1观察2种，不用零命中代替随机性验证。[完整rare记录](rare_event_diagnosis_v1.json)保存全部draw和native CUDA-FP32及CPU-FP64质量。

| 温度／候选 | native softmax mass | 理想4096次至少一命中概率 | 理想95%至少一命中所需draw |
| --- | ---: | ---: | ---: |
| .8／11 | 1.4170972e-11 | 5.8044298e-8 | 211399213797 |
| .8／323 | 2.2575285e-11 | 9.2468365e-8 | 132699641295 |
| 1／11 | 2.0935800e-9 | 8.5752668e-6 | 1430913701 |
| 1／323 | 3.0386205e-9 | 1.2446112e-5 | 985885636 |

理想独立Bernoulli模型下，0/4096的单侧95%上界为.0007311125564754343，仍远大于所有记录质量。用-log1p/expm1稳定计算小概率，避免把1-p舍成1产生假零；95%检测量仅指至少一次命中，不等于检验两极小概率差的样本量。**零命中在本预算下重复，不是概率为零或已排除罕见影响。** 不运行10^9–10^11次暴力采样，不扩大温度或改logits制造有利事件；native有限精度sampler对极小概率的数值可达性未验证，理想Bernoulli功效也不冒充该实现的真实尾概率。

### 资源、复现与下一假设

新完整矩阵wall178.287秒、.5s采样RSS5076901888 bytes、GPU全局7661MiB、最低主存10350784512；raw312037981 bytes、SHA6db9b1e5f387657de37b8e62aa38250c6099554809f199448797091ad474ea5f。rare wall6.967秒、RSS1086337024、GPU3193MiB、8192draw；所有weights/cache/tensors保留本机.tmp，GPU含背景、采样非allocator峰，不作速度排名。零teacher/warmup、旧科学source/default/配方/helper/Run未改，不推送／PR／合并／删除。

本轮补稀有事件端点、无效输入、tiny p稳定性、零观测上界、最小95%检测数回归。完整路径方向具有prompt与seed依赖，下一项按最小成本检验“首个局部接受变化符号能预测最终净差”，将另冻协议、读取同一批完整语义trace，不增加有利窗口、不将已有总数当新独立证据。

## 报告更新后继续H7：首个局部方向不能预测净方向（2026-10-15）

完成上节矩阵／rare报告后、查看首次分叉前，另冻[FIRST_DELTA_PLAN](FIRST_DELTA_PLAN.md)，执行[完整轨迹计数工具](../analyze_first_delta.py)，结果存[结构化分析](first_delta_analysis_v1.json)。这是对已知最终数的解释性检验，不称新held-out样本；没有新模型forward、draw、prompt或窗口搜索。

H7要求：首个按时间出现的self/graft语义分叉之accepted-node数差符号，应与最终净接受差符号相同。仅比较TRACE_KEYS，排除mask norm等早期诊断元数据。每侧accepted须等于全部trace accepted_nodes计数和，首个分叉真实root必须相同；后续只按实际共有／独有root作计数，不强迫对齐或只选能解释净差的根。

| 新单位 | 第一次分叉root | 第一accepted差 | 最终差 | 共同root总差 | graft-only减self-only接受差 |
| --- | ---: | ---: | ---: | ---: | ---: |
| q242／123 | 651 | -1 | +5 | +6 | -1 |
| q242／125 | 685 | -1 | +2 | +1 | +1 |

10个新单位中两例反驳H7：第一次损失不决定完整路径损失。其余8新单位方向一致；两旧development行单列，未用它们代替新检验。上述共同／独有root和最终数严格满足计数恒等式，所有根与双方记录保存；它说明后期收益和路径访问变化能反转早期方向，不是把这些根称为彼此可替换的hidden状态，也不是各state/proxy张量的因果百分比。

q244三seed的首变和最终都是负，属于当前prompt／温度／预算下的重复负结果；q242三seed最终正，其中两seed首变负。局部即时恢复、第一次接受变化和完整路径净差是不同指标。新回归覆盖早期收益后净损失、收益抵消为零、方向保留、忽略非语义metadata、缺失count或不共享前缀拒绝。下一项仍未验证的是新sampled窗口的canonical等state因素分解与有限精度sampler的极小概率可达性；不从H7计数恒等式推断已完成它们。

收尾核验：58项针对性测试、Ruff与5个Study科学source/RPipe冻结门通过；矩阵/rare/H7分析重跑与正式证据一致，45个精确字节路径暂存blob与本机文件一致。新7000生成new、8192条件draw、H7零新forward均在新合同范围。旧science/default/helper/Run不改，未扩展多任务/多温度/硬件，也未证明native rare尾可达性。
