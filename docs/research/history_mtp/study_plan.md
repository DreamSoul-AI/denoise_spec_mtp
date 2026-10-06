# 历史外推 mask 的研究计划与实验规范

日期：2026年10月6日。适用代码：`feature/research-ema-history-audit`。已有数字见 `experiment_log_20261006.md`。本文件规定记号、可分离的因子、对照和判定规则。在本文件修订之前，不再增加新的模型、树或参数扫描。

# 一、已经能说的话

在 Qwen3-4B、float32、同一 26 条 SpecBench 开发提示、同一棵 `[14]` 树、贪心解码上，默认 EMA 的合并 tau 是 1.385，步长为 0 的 EMA 也是 1.385，ESP 是 1.475。五个设置的输出都和普通逐 token 生成逐 token 一致，提交的 token 数都是 2165。EMA 更慢，是因为它用了更多次模型调用（1563 对 1468），不是因为它生成了另一段文本。

这只说明：在这条切片上，**沿历史差分往前走**没有比「mask 直接等于上一个 token 的 embedding」接受更多草稿。它还没有说明 Momentum Guidance 的那种外推差，也没有说明 ESP 的优势来自「更新」本身。ESP 和 EMA 同时换了锚点和历史对象，见第四节。

这 26 条已经看过结果，之后只作为探索集。确认集必须换还没用过的提示。

# 二、统一记号

$x_t$ 是已提交 token。$e_t = E[x_t]$ 是输入 embedding，维度 $d$。$t$ 是当前已提交序列的最后一个位置。mask 槽 $i = 1,\ldots,k$ 放在位置 $t+i$，它的 logits 预测 $x_{t+i+1}$。

差分只在输入 embedding 上定义：

$$d_j = e_{j+1} - e_j.$$

历史 EMA 用同一个衰减 $\beta \in [0,1)$。$\beta$ 越大，记忆越长。初值用第一项，没有 $1-\beta^s$ 校正：

$$\hat v_1 = d_1, \qquad \hat v_j = \beta \hat v_{j-1} + (1-\beta) d_j.$$

当前一步的差分记为 $d_{\mathrm{last}} = e_{\mathrm{new}} - e_{\mathrm{prev}}$。它是 $\hat v$ 的最新观测，本身不是 EMA。

树、剪枝、block complexity、验证器、精度、提示、种子在比较时保持不变。改变 mask 只改变草稿提议。验证仍然只接受和模型自己下一步抽样相同的 token，所以 float32 贪心下输出应与普通生成一致。`exact_match` 不是效果指标，它是这轮比较是否有效的门槛。

# 三、三套公式

## （一）ESP：对 embedding 做 EMA，没有速度

论文 Eq (4)(5)。所有槽共用同一个向量：

$$m_i(0) = \frac{1}{t}\sum_{j=1}^{t} e_j, \qquad m_i(s+1) = (1-\lambda) m_i(s) + \lambda\, e_{t+s}.$$

$\lambda = 0.1$ 时等价于 $m \leftarrow m + \lambda(e-m)$。被平均的是 token embedding，不是差分。槽编号 $i$ 只改位置 id，不改 mask 向量。`update=false` 时 $m$ 停在提示均值，不再移动。

## （二）EMA-Velocity：沿历史平均差分往前走

仓库实现。锚点是上一个已提交 token，步长沿 $\hat v$：

$$m_i = e_{\mathrm{last}} + \gamma\, i\, \hat v.$$

$\gamma = 0$ 时 $m_i = e_{\mathrm{last}}$，锚点仍随每个已提交 token 更新，所以它不是冻结的提示均值。`normalize=true` 时改成

$$m_i = e_{\mathrm{last}} + \gamma\, i\, r\, \frac{\hat v}{\|\hat v\|},$$

$r$ 是 $\|d_j\|$ 的 EMA。这一步丢掉 $\hat v$ 的长度，只留方向，再用典型步长缩放。

每次提交 token 后 $\hat v \leftarrow \beta\hat v + (1-\beta)d_{\mathrm{last}}$。被拒绝的草稿不进入 $\hat v$。这条已经在 CPU 上核对过。

## （三）Momentum Guidance：离开历史平均，而不是沿着它走

论文 Eq (11)(12)。状态是 ODE 上的 $Z$，速度是网络输出 $v_i = v_\theta(Z_i, t_i)$，不是 embedding 差分：

$$m_{i+1} = (1-\beta) v_i + \beta m_i, \qquad Z_{i+1} = Z_i + \Delta t\big[v_i + \alpha(v_i - m_i)\big].$$

展开后的步方向是 $(1+\alpha)v_i - \alpha m_i$。$m$ 是过去速度的参考。外推项 $\alpha(v_i-m_i)$ 放大的是**当前速度相对历史的偏离**。

若把同一形式套到 embedding 差分上，对应的 mask 应是

$$m_i = e_{\mathrm{last}} + \gamma\, i\, \big(d_{\mathrm{last}} + \alpha(d_{\mathrm{last}} - \hat v)\big).$$

$\alpha = 0$ 时沿当前差分走。$\alpha > 0$ 时离开 $\hat v$。仓库里的 EMA-Velocity 是沿 $\hat v$ 走，对应的是把上式里的方向换成 $\hat v$，符号和角色都不同。轨迹是直线时 $d_{\mathrm{last}} = \hat v$，两者重合。轨迹转弯时两者可以反向。这套 MG 式 mask **还没有实现，也没有测量**。

MG 原式作用在连续生成 ODE 上，改变的是采样轨迹，没有 token 验证。不能把它的 FID 结果挪来解释接受长度。

# 四、因子

下面每个因子一次只动一个。已经和别的因子绑在一起的对比，不单独解释。

| **因子** | **水平** | **代码里有没有** | **4B float32 这 26 条上测过吗** |
| --- | --- | --- | --- |
| 锚点 | 提示均值，且冻结 | ESP `update=false` | 测过，tau 1.448 |
| 锚点 | 上一个 token，步长 0 | EMA `step_scale=0` | 测过，tau 1.385 |
| 历史对象 | embedding 的 EMA（ESP 更新） | ESP $\lambda=0.1$ | 测过，tau 1.475 |
| 历史对象 | 差分的 EMA，并沿它走 | EMA $\gamma=1$ | 测过，与步长 0 的合并计数相同 |
| 尺度 | $\gamma \in \{0, 0.5, 1\}$，归一化开或关 | 有 | 只测了 $0$、$1$ 和归一化。$0.5$ 只在随机小模型上跑过 |
| 记忆 | $\beta$ | 有，默认 0.9 | 这 26 条上没扫 |
| 外推符号 | 沿 $\hat v$，或沿 $d_{\mathrm{last}}-\hat v$ | 只有沿 $\hat v$ | MG 式没做 |
| 槽间日程 | 各槽同一 $\hat v$，或槽内再滚一次 EMA | `extrapolate_ema` | 这轮 $k=1$，滚不滚一样 |
| 表示 | 输入 embedding，或中间层 | 只有输入 embedding | 没做 |
| 精度 | float32，或 bf16 | 两种都跑过 | float32 上 `exact_match=1`。bf16 的 8B 运行有 top-2 差距不超过一个最小单位的分歧 |

ESP 对 EMA 的现成对比同时换了锚点和历史对象。能单独解释的对比只有：

1. 锚点。冻结的提示均值（tau 1.448）对上一个 token（tau 1.385）。提示均值在这 26 条上更好。
2. ESP 的 embedding 更新。冻结均值 1.448，更新后 1.475，多接受 24 个草稿。
3. 差分方向。步长 0 和 $\gamma=1$ 的合并 tau 都是 1.385。6 条提示上有一两个草稿的出入，总和抵消。

# 五、实验规范

## （一）问题

在树、模型、精度、提示和验证器固定时，mask 的哪一个因子改变合并接受长度。顺序是：先锚点，再「沿历史差分」相对「步长 0」，再「离开历史」相对「沿历史」。后一个问题要等前一个的确认集结果出来再改代码。

## （二）固定项

- 模型：Qwen3-4B，float32。8B bf16 只保留为精度诊断，不参加效果比较。
- 树：`[14]`，一个 mask，BC=30，静态，剪枝开，efficient。$k>1$ 属于以后的槽间日程实验。
- 解码：贪心，温度 0，`max_new_tokens=100`，遇到 EOS 停止，Qwen3 `enable_thinking=false`，种子 123。
- 历史更新只吃已提交 token。这条由 `tests/check_ema_history.py` 守住，改 mask 公式时要继续通过。

## （三）结局

主结局是合并 tau，即全部提示的已提交 token 数除以解码调用次数。不使用每条提示 tau 的平均。

同时记录：

- 深度 1 的条件接受率，分子分母都按调用加总
- `exact_match`。float32 贪心下必须是 1，否则这轮 tau 不作效果结论
- 墙钟速度。只在 `exact_match=1` 时解释为无损加速
- 每个因子相对其对照多接受或少接受的草稿数

## （四）集合

探索集是已经用过的每类前 2 条，共 26 条。确认集是每个类别接下来的 4 条，共 52 条，本文件写定之前没有跑过。最终的 480 条评估留到确认集上符号稳定之后。参数不在确认集上选。

## （五）判定

一个因子算有方向，需要同时满足：

1. 对照和它只差这一个因子
2. float32 上 `exact_match=1`
3. 探索集和确认集的合并 tau 符号相同
4. 接受草稿数的差不是个位数上的互相抵消。26 条上 24 个草稿这种量级，要在确认集上再看到同方向才算

不满足就写成「这批提示上没有分开」。随机小模型和 bf16 上对不齐的运行不参加判定。

## （六）下一轮只做这一张表

确认集，Qwen3-4B float32，上面的固定项。不再下载模型，不扫 $\beta$。

| **单元格** | **实现** | **单独回答** |
| --- | --- | --- |
| 冻结提示均值 | ESP，`update=false` | 锚点对照 |
| 上一个 token | EMA，`step_scale=0` | 锚点对照 |
| ESP 更新 | ESP，$\lambda=0.1$ | embedding EMA 相对冻结均值 |
| 沿 $\hat v$ | EMA，$\gamma=1$，$\beta=0.9$ | 差分方向相对步长 0 |
| 归一化方向 | EMA，`normalize=true`，$\gamma=1$ | 长度信号相对沿 $\hat v$ |

MG 式 $d_{\mathrm{last}} + \alpha(d_{\mathrm{last}}-\hat v)$ 不在这张表里。只有「沿 $\hat v$」在确认集上稳定地好于或差于步长 0，才值得加这个符号相反的单元格。现在探索集上两者的合并计数相同，先确认这件事是否还在。

# 六、确认集结果（2026-10-06）

第五节的表已经跑完。Qwen3-4B float32，52 条确认提示，树 `[14]`。五个单元格的 `exact_match` 都是 1，提交的 token 数都是 4628。数字和逐条对照在 `experiment_log_20261006.md` 第七节。

按第五节的判定：

1. 锚点分开了。冻结提示均值相对「上一个 token」：探索集多 71 个草稿，确认集多 139 个。合并 tau 从 1.393 到 1.454。这是两个集合上同号、而且差没有缩成互相抵消的个位数。类别并不整齐：确认集上 coding、qa 是上一个 token 更好，summarization、roleplay、extraction、stem 是提示均值更好。
2. ESP 的 embedding 更新没有写成稳定因子。合并符号和探索集相同，确认集净多 17 个草稿（tau 1.464 对 1.454）。49 条提示有出入，类别之间有加有减，净差小于这些摆动。
3. 在 $\beta=0.9$、锚点是上一个 token 时，沿 $\hat v$ 和步长 0 没有分开。确认集少 4 个草稿。这还不说明一阶没用。一阶还要在零阶均值上面加，并且 $\beta$ 要看到 0.9 和 0.9999 这两个相反的记忆长度。Momentum Guidance 仍然等这两格出来再决定。
4. 归一化相对沿 $\hat v$ 在两个集合上都少 9 个草稿。确认集上 26 条有出入，正负都有。长度信号不记成稳定因子。

本文件第一节到第五节的判定不变。模型、树、$\gamma$ 的扫描不加。$\beta$ 和 $\lambda$ 的取值只按第九节走。480 条评估留到有一个通过上述判定、并且需要更大集合的因子之后。锚点已经通过判定，但是它回答的是「提示均值对上一个 token」，不是论文的 480 条速度。

# 七、不在本轮声称的事

- EMA 普遍差于 ESP。现有差距混有锚点。
- 沿历史差分的数学已经被否定。被测量的是 $\gamma=1$、$\beta=0.9$、输入 embedding、一个 mask 槽。第九节专门补记忆长度。
- Momentum Guidance 的外推在 token 上有效或无效。对应 mask 还没写。
- 论文 Table 1 的速度。这里不是 480 条，也不是论文里的模型和输出长度。

# 八、零阶和一阶

The mask is a short extrapolation of the embedding trajectory. Two states, both kept.

Order 0 is the level. It is an EMA of embeddings. Its initial value is the mean of the prompt embeddings, then it updates on every committed token:

$$m^{(0)}_0 = \frac{1}{t}\sum_{j=1}^{t} e_j, \qquad m^{(0)} \leftarrow (1-\lambda)m^{(0)} + \lambda\, e_{\mathrm{new}}.$$

$\lambda = 0.1$. Every slot uses this same vector. This is ESP. `update=false` freezes it at the initial mean.

Order 1 is the slope. It is an EMA of successive differences. This is the proposal:

$$\hat v \leftarrow \beta\hat v + (1-\beta)(e_{\mathrm{new}} - e_{\mathrm{prev}}), \qquad \beta = 0.9.$$

The mask that keeps both terms is

$$m_i = m^{(0)} + \gamma\, i\, \hat v.$$

`level=last`, the previous default, replaces that level with the last token:

$$m_i = e_{\mathrm{last}} + \gamma\, i\, \hat v.$$

$e_{\mathrm{last}}$ is one embedding, not the order-0 EMA, and it is not initialized at the prompt mean. $\gamma = 0$ in that formula is the last-token row in the table above. It is not order 0.

| **Term** | **Formula in use** | **Measured** |
| --- | --- | --- |
| Order 0, frozen at the initial mean | ESP, `update=false` | Yes. Confirm tau 1.454 |
| Order 0, kept up to date | ESP, $\lambda=0.1$ | Yes. Confirm tau 1.464 |
| Order 1 added to the last token, $\beta=0.9$ | EMA, $\gamma=1$, anchor $e_{\mathrm{last}}$ | Yes. Same accepts as $\gamma=0$. This does not close order 1. |
| Order 0 plus order 1 | $m_i = m^{(0)} + \gamma\, i\, \hat v$ | Swept. See [report.md](report.md) sections 2–4. |

$\beta=0.9$ is one memory length. It does not close order 1. Section 9 is the sweep.

# 九、记忆长度的遍历计划

Order 1 stays open. One $\beta$ on the last-token anchor is not a sweep. This section is the only parameter list that gets run.

## Question

With both terms on,

$$m_i = m^{(0)} + \gamma\, i\, \hat v,$$

does the slope change the pooled accept count, and does that change depend on how fast each EMA forgets?

## Fixed

Qwen3-4B, float32, tree `[14]`, greedy, 100 tokens, seed 123, one mask slot, $\gamma=1$. `exact_match` must be 1, or that cell is invalid. No debiasing term $1-\beta^s$. No Momentum Guidance, no second model, no second tree, no normalization, no $\gamma$ grid.

## Values

Opposing memory lengths, one per decade of tokens. Not a dense grid.

Order 1, $\beta$. Half-life is $\ln 2 / (1-\beta)$ tokens. Large $\beta$ forgets slowly. At $0.9999$, with no debiasing, $\hat v$ stays near the first difference in the prompt.

| **$\beta$** | **Half-life** |
| ---: | ---: |
| 0.5 | about 1 token |
| 0.9 | about 7 tokens |
| 0.99 | about 70 tokens |
| 0.999 | about 700 tokens |
| 0.9999 | about 7000 tokens |

Order 0, $\lambda$. The level keeps a fraction $(1-\lambda)$ of itself each committed token. Large $\lambda$ forgets fast. The five values match the same half-lives: $0.5$, $0.1$, $0.01$, $0.001$, $0.0001$. The current runs use $\lambda=0.1$.

## Where

Stages A and B use the 26-prompt exploration slice. $\beta$ and $\lambda$ are chosen there.

The 52-prompt confirmation slice is not used to pick them. One unplanned cell already finished on it (both orders, $\beta=0.9$, $\lambda=0.1$) and is excluded from selection. The $\beta=0.9999$ run on that slice was stopped unfinished.

The holdout is untouched until stage C: the next 4 questions of each category after the confirmation window (`--skip 6 --take 4`).

## Stages

**A.** Both orders. $\lambda=0.1$ fixed. $\beta$ takes the five values. Five runs. The control is order 0 alone (ESP, $\lambda=0.1$) on the same 26 prompts.

**B.** Runs only if stage A separates. Separates means some $\beta$ beats the order-0 control, or two $\beta$ values disagree with each other, by more than a cancelling handful of drafts. The rule is the same as section 5. Then $\lambda$ takes its five values at the two $\beta$ values that disagreed most. $\lambda=0.1$ is already in stage A, so this is at most 8 new runs. If stage A does not separate, $\lambda$ is not swept.

**C.** At most two cells on the holdout: order 0 alone, and the one $(\beta, \lambda)$ pair that stage A or B marked as the extreme. If nothing separated, stage C does not run.

A null at $\beta=0.9$ does not mean order 1 is useless. A win at one $\beta$ on 26 prompts is not a result until stage C repeats the sign.

## Result (2026-10-06)

Stages A, B, and C have been run. Numbers are in `experiment_log_20261006.md` section 8. Every cell matched ordinary generation token for token.

On the 26-prompt slice, with λ=0.1, the slope's effect versus order 0 alone goes from −84 accepts at β=0.5 to +73 at β=0.9999. Short memory hurts. Long memory helps. Changing λ at those two β values does not reverse that. The holdout, 52 new prompts, repeats the long-memory sign: β=0.9999, λ=0.1 accepts 198 more drafts than order 0 alone (tau 1.589 versus 1.491).

This is one model, one tree, γ=1, and no debiasing. It does not say the last-token anchor was a good level, and it does not say Momentum Guidance.
