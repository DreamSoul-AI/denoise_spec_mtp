---
title: "denoising speculative decoding: Training-Free Kalman-Filtered Output-Space Masks for Parallel Drafting"
subtitle: "denoising speculative decoding 研究计划（论文版 v6，草案）"
date: "2026-10-13"
---

> 历史探索稿（2026-10-13）。含未验证理论、当时待测设想和异条件历史结果，不代表当前执行或已证实贡献。当前计划已按新版模板重写为[中文](../research-plan.md) / [English](../research-plan.en.md)；本稿原文保留，Kalman/高阶等不因保留而恢复研究。

# denoising speculative decoding: Training-Free Kalman-Filtered Output-Space Masks for Parallel Drafting

> **项目正式名称**：**denoising speculative decoding**（全小写）。代码仓库目录仍为 `denoise_spec_mtp`，仅作路径引用。
>
> **文档性质**：研究计划（论文体例），不是论文。
>
> **标注约定**：
> - 【实测】：仅限附录 C 的输入空间、树形实验；
> - 【待测】：本版主方法与卡尔曼变体，**均无实测**；
> - 【猜想】：未证明的陈述；
> - 【待作者确认】：需要作者拍板的事项。
>
> **相对 v5 的改动**：
> 1. 统一名称，并解释 denoising 的含义（§1.5）；
> 2. 新增卡尔曼自适应变体（§5.9）：状态空间模型、维度分解、预测-校正、离散代数 Riccati 稳态增益、基于新息的 Q/R 在线估计、代理观测 $R'>R$、槽位不确定性；
> 3. 新增 Algorithm 3、复杂度与数值稳定性分析；
> 4. 新增 AR / 差分 / 卡尔曼层级关系（§5.10）；
> 5. 新增命题 8–10、假设 H12–H13、实验 E16–E18、文献 [55]–[60]。

---

## Abstract

投机解码的起草器大多需要训练，因此受训练分布约束，已有工作报告 EAGLE-3 在训练域外的接受长度显著下降 [44][45]。ESP [12] 不需要训练：同一次前向既验证上一轮草稿，又在 mask 位置起草，但它的 mask 是输入 embedding 的均值，不带预测信息。

我们提出 **denoising speculative decoding**。核心想法是把相邻位置的末层 hidden 看作“对下一 token 的预测”的**含噪轨迹**，用滤波估计其 $n$ 阶状态 $(h,\nabla h,\dots,\nabla^nh)$，再外推出未来位置的 mask。方法分三层：

- **固定增益版**：逐阶 EMA，即 α-β-γ 滤波；
- **主自适应变体**：卡尔曼滤波。用状态空间模型 $s_{t+1}=Fs_t+w$、$y_t=Hs_t+v$ 描述轨迹，增益由协方差递推给出；噪声协方差 $Q$、$R$ 按新息逐序列在线估计 [56][57][58][59]，全程不训练；
- **代理观测处理**：草稿前缀上的代理 hidden 赋更大的观测噪声 $R'>R$。

状态沿每个节点的前缀累积，块内只预测，所有节点的 mask 在一次前向中并行处理。tied 模型直接用 hidden 并做范数缩放，非 tied 模型经 LatentMAS 岭回归对齐 [34]。

理论结果：

- 任意 soft mask 下保持无损；
- v4 的固定 EMA 恰是“局部线性趋势、无观测噪声”模型的稳态卡尔曼滤波，且 $\beta$ 有闭式（命题 8）；
- 稳态增益在常增益滤波中均方最优，因此最优 $\beta$ 存在（命题 9）；
- 预测协方差给出各槽位的不确定性（命题 10）。

全部实验待测，包括与网格搜索固定 $\beta$ 的对照、跨数据集无需重调，以及跨域与训练式基线对比。

---

## 1. Introduction

### 1.1 背景
投机解码 [1][2] 用便宜的草稿加一次并行验证来减少目标模型的前向次数，同时保持输出分布不变。按起草器来源，现有方法分三类：

- **训练式**：Medusa [3]、Hydra [7]、EAGLE-1/2/3 [4][5][6]、MTP [9][10]，以及学习 mask/前瞻 token 的方法 [18][27][39][40][41]；
- **免训练（检索、n-gram、迭代）**：[8][17][19][20][21][29]；
- **免训练（embedding 探测）**：ESP [12]。

### 1.2 定位：免训练意味着没有过拟合与迁移问题
训练式起草器是在某个数据分布上拟合目标模型行为的参数化模型。部署分布一旦偏离训练分布（领域、长度、模板），接受率就会下降。已有工作在跨域 [44]、长上下文 [45]、长推理链 [46] 等设置下报告了 EAGLE-3 的退化，并为此提出在线适配 [47] 或多起草器选择 [48]。

本法**不引入任何可训练参数**。起草完全由冻结的目标模型在 mask 位置完成，所用的全部量（hidden、$W_{\text{in}}$、$W_{\text{out}}$）都来自目标模型自身。因此：

- 不存在起草器对训练集的过拟合；
- 不存在训练集与部署集之间的迁移问题；
- 换模型无需重训，只需（非 tied 时）一次闭式预计算。

这一定位并不声称本法的绝对接受率高于域内的训练式方法。我们关心的是**跨域稳定性**，以及与免训练基线的比较（H1、H8）。

### 1.3 问题
ESP 的 mask 是 prompt embedding 的均值。它是上下文的词袋统计，**不包含对下一 token 的预测**。所有槽位、所有节点共用同一个向量，模型只能靠注意力从前缀中自行推断 mask 位置该填什么。

### 1.4 贡献

1. **前缀条件的高阶输出空间 mask**：用 $n$ 阶状态跟踪 hidden 轨迹，沿每个节点的草稿前缀做预测-校正，块内外推，一次前向并行处理。
2. **卡尔曼自适应变体（主自适应版本）**：在维度分解的状态空间模型上做卡尔曼滤波，用新息在线估计 $Q$、$R$，代理观测使用 $R'>R$，并由预测协方差 $P$ 给出槽位不确定性。完全免训练，逐序列自适应。
3. **统一层级**：在线 AR（线性预测）⊃ 固定系数 AR（牛顿差分）；常增益滤波（逐阶 EMA / α-β-γ）⊂ 稳态卡尔曼 ⊂ 自适应卡尔曼（§5.10）。
4. **映射**：tied 模型直接用 hidden 并做范数缩放；非 tied 模型加 LatentMAS 适配 [34]。
5. **理论**：
   - 无损性（命题 1）与加速比上界（命题 2）；
   - 统一性（命题 5）与偏差-方差权衡（命题 6、7）；
   - 固定 EMA 与稳态卡尔曼的对应及 $\beta^\star$ 闭式（命题 8）；
   - 稳态增益最优性（命题 9）；
   - 槽位不确定性（命题 10）。
6. **实验计划**（H1–H13），全部待测。

### 1.5 名称：denoising 的含义
本文把末层 hidden 序列建模为
$$y_t=Hs_t+v_t,$$
即“可预测的平滑趋势 $Hs_t$”加上“与具体 token 相关的、近似不可预测的成分 $v_t$”。

估计 $s_t$ 就是从含噪轨迹中**去噪**：

- EMA 是固定增益的去噪器；
- 卡尔曼滤波是在给定 $Q$、$R$ 下的最优线性去噪器（命题 9）；
- 零阶增益 $\kappa_0<1$ 时，连锚点 hidden 本身也被平滑（v4 中 $\kappa_0=1$，不对锚点去噪）。

因此 “denoising” 指**对输出 hidden 轨迹做状态估计（滤波）去噪**，与扩散模型的 denoising 无关。

仓库目录名 `denoise_spec_mtp` 中 “denoise” 的原始含义是否就是这一点，【待作者确认】。

## 2. Motivation

**(1) 输出端 hidden 带预测性，输入均值不带。** 末层 hidden $h_i$ 经 LM head 直接给出 $p_\theta(\cdot\mid x_{\le i})$，它在定义上就是**对下一 token 的预测**，同时编码了全部前缀。ESP 的均值 mask $\bar e=\frac1t\sum e(x_i)$ 只是输入 token 的平均，与“下一个是什么”无关。可解释性研究也表明，单个 hidden 可以解码出其后多个 token [36]。

因此，把“已经预测了下一 token”的表示放到 mask 位置，比放一个无预测性的均值更有理由帮助模型填出后续 token。这是动机，不是证据【待测】。

**(2) 一阶速度提供方向。** 零阶锚点只对应紧接着的一个 token。mask $j\ge2$ 需要更远的位置，一阶速度 $v$（hidden 差分的 EMA）给出 hidden 轨迹的局部方向，可以外推到更远的槽位。作者认为这一项有意义，所以作为主方法的一部分；它是否真能提高远槽位的接受率，由消融 E4 检验。

**(3) 前缀条件。** 链上节点 $i$ 的 mask 预测的是 $\tilde x_{1:i}$ 之后的 token。如果所有节点共用同一组 mask（仓库现状，见 §5.11），深节点的 mask 携带的就是“根之后”的信息，与其实际前缀错位。前缀条件让每个节点的 mask 与自己的前缀对齐。

**(4) 可得性。** 所需 hidden 都在上一轮块前向中已经算出，不增加前向次数。

**待测风险：soft 输入的分布偏移。** 末层 hidden 与输入 embedding 的统计分布不同，作为输入可能引起分布外激活。LatentMAS [34] 报告对齐能缓解这一问题（在推理任务上）。在本场景中这只是风险，由 E3 检验，不作为动机。

---


**(5) 高阶信息。** 单个 hidden 只给出“下一个 token”的预测。相邻位置 hidden 的一阶、二阶、三阶差分，刻画的是预测本身随位置的变化趋势：一阶对应方向，二阶对应趋势的转弯。如果这种变化在短窗口内足够平滑，高阶项可以改善远槽位 $j\ge2$ 的外推。

反过来，hidden 轨迹逐 token 跳变，带有大量与具体 token 相关、近似不可预测的成分。差分会放大这部分“噪声”（命题 6）。因此最优阶数是一个经验问题（H10），我们预期不会很高【猜想】。

## 3. Related Work

文献编号 [1]–[43] 沿用 v3，[44]–[48] 为本版新增（标题已核对）。

- **投机解码与 ESP**：基础与综述 [1][2][14]；训练式 [3]–[7][9][10][16]；免训练 [8][17]–[23][29][30]；树验证 [11][15]；扩散起草 [24]–[26]；ESP 为主基线 [12]。
- **特征层与 hidden 起草（训练式）**：EAGLE [4]–[6] 用训练过的小网络在目标特征上自回归起草；Medusa/Hydra [3][7] 在 hidden 上接训练过的头；Hidden Transfer [35] 训练中间层到未来位置的变换。
  - 本法区别：同样利用目标 hidden，但不训练任何模块，起草仍由目标模型在 mask 位置完成。
- **mask/前瞻 token（训练式）**：PaSS [18]、BiTA [39]、ParallelSpec [40]、Samragh 等 [27]、SPACE [41]。这些方法学习 mask embedding；本法在推理时解析构造 mask。
- **起草器的分布偏移**：
  - Osprey [44] 报告在数学上训练的 EAGLE-3 起草器（Qwen3-8B），域内平均接受长度 5.06，在代码上只有 1.86。
  - OWL [45] 报告 EAGLE-3 在长上下文基准 LongSpecBench 上接受长度约 1.28，低于 PLD 等免训练方法，速度降至 0.81×。
  - P-EAGLE [46] 报告在短序列上训练的起草器在长推理轨迹上接受率最多下降 25%。
  - Online Speculative Decoding [47] 以查询分布偏移为动机，在线更新起草器。
  - HedgeSpec [48] 在多个领域专家起草器之间在线选择，以应对分布外查询。
  - 以上数字均为原文报告值，不是本仓库实测。它们支撑“训练式起草器存在迁移问题”这一定位；本法在同等设置下是否更稳，记为 H8【待测】。
- **连续/soft 输入**：Coconut [31]（训练）、Soft Thinking [32]、Mixture of Inputs [33]、LatentMAS [34]（免训练）、CoCoMix [42]、Prompt tuning [38]。它们用 soft 输入改变生成内容；本法只在不提交的 mask 位置使用 soft 输入，输出逐 token 不变。
- **hidden 解码与外推**：Future Lens [36]、Tuned Lens [37]、LCM [43]、FlowCast [13]。
- **新颖性**：尚未找到“前缀条件的输出空间外推 mask + ESP 式同前向验证”的工作，有待系统检索确认。

---

- **经典外推与滤波**：
  - 卡尔曼滤波 [49] 与常增益 α-β / α-β-γ 跟踪器 [50]（含 tracking index 的稳态增益分析）；
  - 指数平滑及其趋势扩展，即 Holt 线性趋势 [52]、Gardner 综述 [53]、指数平滑的状态空间框架 [54]；
  - 线性预测 [51]。
  
  牛顿前向/后向差分插值与外推是数值分析教材内容，本文只用其标准恒等式，不另引用（教材出处待补）。本法把这些经典工具用在 LLM 末层 hidden 的位置序列上，用于构造投机解码的 mask；目前未见这样的用法（待系统检索）。

- **卡尔曼滤波及其自适应**：
  - 稳态卡尔曼增益由离散代数 Riccati 方程决定 [49]；
  - α-β / α-β-γ 跟踪器的最优增益可由 Kalata 跟踪指数给出闭式 [50]，α-β-γ 情形的解析式见 Gray & Murray [55]；
  - 噪声协方差未知时的自适应估计包括：Mehra 的基于新息的方差辨识 [56][57]、Sage–Husa 的序贯先验统计估计 [58]、Mohamed–Schwarz 的新息协方差匹配 [59]。

  本法把这些方法用在 LLM hidden 轨迹上，构造投机解码的 mask，不训练任何参数。

## 4. Problem Formulation

### 4.1 记号

| 记号 | 含义 |
|---|---|
| $W_{\text{in}}=E,\ W_{\text{out}}=W\in\mathbb R^{V\times d}$ | 输入 embedding / LM head；tied 指 $W=E$ |
| $f_\theta$ | 冻结模型，输出逐位置末层 hidden $h$（经最终归一化）与 logits $Wh$ |
| $g(\cdot)$ | 贪心预测 $\arg\max p_\theta$ |
| $k$ | 链长 = 每个节点的 mask 数 |
| $r$ | 根，即已提交的最后一个 token，位置 $p$ |
| $\tilde x_{1:k}$ | 本轮链式草稿 |
| $\Phi$ | 输出到输入的映射 |
| $\bar\nu=\frac1V\sum_w\lVert E_w\rVert$ | 输入 embedding 平均行范数 |

### 4.2 块、注意力掩码与位置编码（并行）

**块序列**（$N_B=(k+1)(k+1)$ 个位置）：
$$B=\big[\underbrace{n_0,n_1,\dots,n_k}_{\text{节点}}\ \big|\ \underbrace{M^{(0)}_{1..k}}_{\text{节点 0 的 mask}},\dots,\underbrace{M^{(k)}_{1..k}}_{\text{节点 }k\text{ 的 mask}}\big],\qquad n_0=e(r),\ n_i=e(\tilde x_i).$$

**索引**：节点 $n_i$ 在块内的索引为 $i$；$M^{(i)}_j$ 的索引为 $\iota(i,j)=(k+1)+ik+(j-1)$。

**注意力掩码** $\mathcal A\in\{0,-\infty\}^{N_B\times(p+N_B)}$：前缀 KV 共 $p$ 列，全部允许；块内规则为
$$\mathcal A[n_i,n_{i'}]=0\iff i'\le i;$$
$$\mathcal A[M^{(i)}_j,n_{i'}]=0\iff i'\le i;$$
$$\mathcal A[M^{(i)}_j,M^{(i')}_{j'}]=0\iff i'=i\wedge j'\le j;$$
$$\mathcal A[n_i,M^{(\cdot)}_{\cdot}]=-\infty\ \text{（节点不看任何 mask）}.$$

**位置编码**：
$$\mathrm{pos}(n_i)=p+i,\qquad \mathrm{pos}(M^{(i)}_j)=p+i+j.$$
$M^{(i)}_j$ 占据“前缀 $\tilde x_{1:i}$ 之后第 $j$ 个 token”的位置，与 ESP 的约定一致。不同节点的 mask 可以共享同一个 position id（例如 $M^{(0)}_2$ 与 $M^{(1)}_1$），但它们互不注意，各自的前缀不同，所以不冲突。

**并行性**：所有 $M^{(i)}$ 的**内容**都只依赖本轮前向之前已知的量（§5.1），因此 $N_B$ 个位置可在一次前向中并行处理。若下一轮接受了 $A$ 个草稿，就取 $M^{(A)}$ 位置的输出作为下一轮的草稿和状态。

**KV**：只保留前缀、$n_0$ 和 $n_{1..A}$。mask 与被拒节点的 KV 全部丢弃。

### 4.3 接受长度与目标
贪心接受长度为
$$A=\max\{a\le k:\tilde x_i=g(\text{前缀},r,\tilde x_{<i})\ \forall i\le a\},\qquad\tau=A+1.$$
目标是 $\max\mathbb E[\tau]$，约束为输出与自回归一致。

---

## 5. Method

### 5.1 上一轮留下的量与代理观测
设上一轮接受到节点 $A'$。那一轮中节点 $A'$ 的第 $\ell$ 个 mask $M^{(A')}_\ell$ 有两个输出：本轮草稿 $\tilde x_\ell$，以及末层 hidden $\tilde h_\ell$（$\ell=1..k$）。

由于 $M^{(A')}_\ell$ 的位置就是本轮节点 $n_{\ell-1}$ 的位置，$\tilde h_\ell$ 可以作为“节点 $n_{\ell-1}$ 处 hidden”的**代理观测**，它预测的正是 $\tilde x_\ell$。

已提交位置的 hidden 是**精确观测**：它们在被接受节点上已经计算过，见 Alg.2 第 10 行。

### 5.2 $n$ 阶状态与转移矩阵
**状态。** 状态为 $s=(s^{[0]},\dots,s^{[n]})\in\mathbb R^{(n+1)\times d}$，其中 $s^{[r]}$ 估计当前位置处轨迹的 $r$ 阶**前向**差分 $\Delta^r h$。

**转移。** 预测一步时，各阶前向差分满足 $\Delta^r h_{t+1}=\Delta^r h_t+\Delta^{r+1}h_t$，最高阶 $\Delta^n$ 视为常数（常 $n$ 阶差分模型，对应常加速度等模型）。因此
$$s_{j}=F\,s_{j-1},\qquad F=\begin{pmatrix}1&\gamma_1&&\\&\rho_1&\gamma_2&\\&&\ddots&\ddots\\&&&\rho_n\end{pmatrix}\otimes I_d.$$

- 标准情形 $\gamma_r=\rho_r=1$，即 $F=I+N$，$N$ 为上移位矩阵；
- $\gamma_r$ 为步长；$\rho_r\le1$ 为阻尼，类比阻尼趋势指数平滑 [53]。

**命题（牛顿外推，见命题 5(a)）。** 当 $\gamma=\rho=1$ 时，由二项式定理（$N^{n+1}=0$）得
$$F^j=\sum_{r=0}^n\binom{j}{r}N^r,\qquad \hat h_{t+j}=[F^js]^{[0]}=\sum_{r=0}^n\binom jr\,\Delta^rh_t.$$
这就是牛顿前向差分外推。

**用后向差分表示。** 若用历史观测的后向差分 $\nabla^r h_t$ 表示（$\nabla h_t=h_t-h_{t-1}$），则对 $n$ 次多项式轨迹有
$$\hat h_{t+j}=\sum_{r=0}^n\binom{j+r-1}{r}\nabla^r h_t,$$
即牛顿-格雷戈里后向公式。两种坐标的换算为 $\Delta^r=\sum_{m=0}^{n-r}\binom{r+m-1}{m}\nabla^{r+m}$（截断到 $n$ 阶），由 $\Delta=\nabla(1-\nabla)^{-1}$ 得到。

### 5.3 观测校正：各阶 EMA（α-β-γ 推广）
**预测-校正。** 收到观测 $y$ 时（精确或代理），先预测再校正：
$$s^-=Fs,\qquad s\leftarrow s^-+K\otimes(y-s^{-[0]}),\qquad K=(\kappa_0,\kappa_1,\dots,\kappa_n)^\top.$$

- $n=1$ 时为 α-β 滤波，$n=2$ 时为 α-β-γ 滤波 [50]；
- 固定 $K$ 相当于稳态（常增益）卡尔曼滤波 [49]；
- $K$ 的每个分量都是作用于全部 $d$ 维的标量，不需要学习。

**各阶独立 β 的写法（等价参数化，主实现）。** 令 $\kappa_0=1$，即零阶直接取观测值（与 v4 锚点一致）。对 $r\ge1$ 逐阶做 EMA：
$$s^{[r]}\leftarrow\beta_r\,s^{-[r]}+(1-\beta_r)\big(s^{[r-1]}_{\text{new}}-s^{[r-1]}_{\text{old}}\big).$$
这里 $s^{[r-1]}_{\text{new}}-s^{[r-1]}_{\text{old}}$ 是低一阶状态在本步的实际变化，所以“各阶差分各自 EMA”。这一写法与 $K$ 形式的对应关系为：

- $n=1$ 时 $\kappa_1=1-\beta_1$，严格成立（命题 5(b)）；
- $n\ge2$ 时两者都是常增益线性滤波器，但具体增益对应关系复杂，只作参数化选择【实现取逐阶 EMA，与 $K$ 形式的数值差异作消融 E15】。

**两类观测分开设增益。**

- 已提交位置是精确观测，用增益 $K$（或 $\beta_r$）；
- 草稿前缀上的代理观测 $\tilde h$ 噪声更大，可以用更保守的增益 $K'$（或 $\beta'_r\ge\beta_r$）。

### 5.4 沿前缀累积与块内外推
**沿前缀累积。** 设已提交状态为 $s^c$，它的最后一次校正用的是 $h_{\text{last}}=H[n_{A'}]$。节点状态为：
$$s^{(0)}=\mathrm{Corr}_{K'}\big(Fs^c,\ \tilde h_1\big),\qquad s^{(i)}=\mathrm{Corr}_{K'}\big(Fs^{(i-1)},\ \tilde h_{i+1}\big)\ (1\le i\le k-1),\qquad s^{(k)}=Fs^{(k-1)}.$$
链末节点 $k$ 没有代理观测，只做预测。

**块内外推。** 对节点 $i$：
$$M^{(i)}_j=\Phi\big([F_{\text{blk}}^{\,j-1}s^{(i)}]^{[0]}\big),\qquad j=1..k.$$
其中 $F_{\text{blk}}$ 可以与 $F$ 不同（例如另设阻尼 $\rho$），用来消融“块内是否递推、是否阻尼”。块内没有新观测，所以“逐步更新状态”就是 $s_j=F_{\text{blk}}s_{j-1}$。

**特例（命题 5）。**

- $n=0$：零阶-only，$M^{(i)}_j=\Phi(\tilde h_{i+1})$；
- $n=1$，$K=(1,1-\beta)$，$F_{\text{blk}}=\left(\begin{smallmatrix}1&\gamma\\0&\rho\end{smallmatrix}\right)$：即 v4 的一阶递推（$\rho=\beta'+(1-\beta')\gamma$）；
- $\rho=1$：冻结速度。

### 5.5 一般线性预测器（对照形式）
**形式。**
$$\hat h_{t+1}=\sum_{l=0}^{L}a_l\,h_{t-l},\qquad a\in\mathbb R^{L+1},\ \text{各维共享标量系数}.$$
多步预测时把预测值迭代代入，等价于伴随矩阵 $C(a)$ 的幂。

**(i) 固定系数（由阶数决定）。** 取 $L=n$，令 $\nabla^{n+1}\hat h_{t+1}=0$，得
$$a_l=(-1)^l\binom{n+1}{l+1},\qquad l=0..n.$$
例如 $n=1$ 时为 $2h_t-h_{t-1}$，$n=2$ 时为 $3h_t-3h_{t-1}+h_{t-2}$。系数满足 $\sum_la_l=1$（仿射，保持常数轨迹）。这与 §5.2 的无平滑差分外推完全等价（命题 5(c)）。

**(ii) 在线最小二乘（免训练，逐序列测试时拟合）。** 在最近 $W$ 个已提交位置上拟合：
$$a^\star=\arg\min_a\sum_{\tau=t-W+1}^{t}\omega^{t-\tau}\Big\lVert h_\tau-\sum_l a_lh_{\tau-1-l}\Big\rVert^2+\mu\lVert a-a^{\text{Newton}}\rVert^2.$$

- 闭式解：解一个 $(L+1)\times(L+1)$ 的正规方程，可选约束 $\sum a_l=1$；
- 每步成本 $O(WL^2d)$，或递推最小二乘 $O(L^2d)$；
- 这是 Makhoul 意义下的线性预测 [51]：系数随序列在线估计，不使用任何训练数据。

**与差分形式的关系。** 两者都是线性时不变（或慢变）预测器：

- 固定系数预测器的伴随矩阵 $C(a^{\text{Newton}})$ 与 $F=I+N$ 相似，状态一个是延迟坐标、一个是差分坐标；
- 带 EMA 校正的差分滤波，在稳态下等价于某个无穷阶（指数衰减）的线性预测器。Holt 线性趋势与某类 ARIMA 等价是经典结论，具体出处待核对。

### 5.6 映射 $\Phi$
与 v4 相同：

- tied 模型：$\Phi(h)=\bar\nu\,h/\lVert h\rVert$；
- 非 tied 模型：$\Phi(h)=\bar\nu\,hW_a/\lVert hW_a\rVert$，其中 $W_a=(W_{\text{out}}^\top W_{\text{out}}+\lambda I)^{-1}W_{\text{out}}^\top W_{\text{in}}$ [34]。

由于外推是线性的，非 tied 时可以先对状态各分量乘 $W_a$ 再外推，每轮只需 $(k+1)(n+1)$ 次 $d\times d$ 乘法。

### 5.7 开销

| 项目 | 存储 | 每轮计算 |
|---|---|---|
| 已提交状态 $s^c$ | $(n+1)d$ | 每提交一个 token 做一次校正，$O(n d)$ |
| 节点状态 $s^{(0..k)}$ | $(k+1)(n+1)d$ | $O(k\,n\,d)$ |
| 块内外推 | — | $(k+1)k$ 个 mask，每个 $O(nd)$，合计 $O(k^2nd)$ |
| 非 tied 映射 | $d^2$（$W_a$） | $O((k+1)(n+1)d^2)$ |
| 线性预测 LS（可选） | $Wd$（最近 $W$ 个 hidden） | $O(WL^2d)$ |
| 块前向（参照） | — | 约 $2N(k+1)^2$ |

例：$k=4$，$n=3$，$d=4096$，非 tied 映射约 $20\cdot2d^2\approx6.7\times10^8$ FLOPs，块前向（8B）约 $2\cdot8\times10^9\cdot25=4\times10^{11}$，比值约 0.2%（估算，非实测）。

只需额外缓存“最近 $n+1$ 个已提交 hidden”或等价的状态，以及上一轮 $M^{(A')}$ 的 $k$ 个 hidden。

### 5.8 算法
**Algorithm 1：$n$ 阶前缀条件 mask 构造**
```text
Input : committed state s^c ∈ ℝ^{(n+1)×d}; proxies h̃_1..h̃_k; F, F_blk; gains K′ (or β′_1..β′_n); Φ
Output: M⁽⁰⁾..M⁽ᵏ⁾ ∈ ℝ^{k×d}  (fixed before the forward)
 1  s ← s^c
 2  for i ← 0 to k do                                  ▷ prefix accumulation along the draft
 3      s⁻ ← F·s
 4      if i < k then s ← Corr(s⁻, h̃_{i+1}; K′)         ▷ s⁻ + K′⊗(h̃_{i+1} − s⁻[0]) or per-order EMA
 5      else s ← s⁻                                    ▷ chain end: predict only
 6      s⁽ⁱ⁾ ← s
 7  for i ← 0 to k do                                  ▷ independent → parallel
 8      u ← s⁽ⁱ⁾
 9      for j ← 1 to k do
10          M⁽ⁱ⁾_j ← Φ(u[0]);  u ← F_blk·u                ▷ s_j = F s_{j−1}
11  return M⁽⁰⁾..M⁽ᵏ⁾
```

**Algorithm 2：链式解码（贪心）**
```text
Input : prompt x_{1:t}; frozen f_θ; k; n; Φ; N_max
Output: Y (identical to greedy AR, Prop. 1)
 1  if untied: W_a ← solve(WᵀW + λI, WᵀE) in fp32
 2  (H, L) ← f_θ([e(x_{1:t}) | ē×k])                     ▷ prefill
 3  s^c ← init from H[t−n..t−1] (backward differences → Δ via §5.2)
 4  r ← argmax L[t−1]; x̃ ← argmax L[masks]; h̃_{1..k} ← H[masks]; Y ← [r]
 5  while |Y| < N_max and r ≠ EOS do
 6      M ← Alg1(s^c, h̃, F, F_blk, K′, Φ)
 7      (H, L) ← f_θ([e(r), e(x̃_{1..k}) | M⁽⁰⁾..M⁽ᵏ⁾]; 𝒜, pos as §4.2)
 8      A ← max{a : argmax L[n_{i−1}] = x̃_i ∀ i ≤ a}
 9      C ← [x̃_{1..A}, argmax L[n_A]]; truncate; Y ← Y ∥ C
10      for i ← 0 to A: s^c ← Corr(F·s^c, H[n_i]; K)      ▷ exact observations
11      h̃_{1..k} ← H[M⁽ᴬ⁾]; x̃ ← argmax L[M⁽ᴬ⁾]; r ← last(C)
12      keep KV of prefix + n_0..n_A
13  return Y
```
第 10 行：已提交状态在每个被接受节点处用精确 hidden 校正一次。bonus token 的 hidden 要等下一轮根节点才算出，因此有一步延迟。

### 5.9 卡尔曼自适应变体（主自适应版本）
**状态空间模型**：
$$s_{t+1}=F s_t+w_t,\quad w_t\sim\mathcal N(0,\mathbf Q);\qquad y_t=Hs_t+v_t,\quad v_t\sim\mathcal N(0,\mathbf R);\qquad H=[1,0,\dots,0].$$
其中 $s_t\in\mathbb R^{(n+1)\times d}$，$y_t$ 为观测到的末层 hidden。

**维度分解假设**：取 $\mathbf Q=Q\otimes I_d$，$\mathbf R=R\,I_d$，其中 $Q\in\mathbb R^{(n+1)\times(n+1)}$，$R>0$ 为标量。这样完整协方差为 $P\otimes I_d$，$P\in\mathbb R^{(n+1)\times(n+1)}$，滤波沿 $d$ 维解耦为 $d$ 个同参数的 $(n+1)$ 维滤波器，并共享同一个 $P$ 和 $K$。

- **合理性**：
  - 计算上，$P$ 只有 $(n+1)^2$ 个元素，增益是标量向量，与 v5 的“各维共享标量增益”一致；
  - 统计上，跨维度相关被忽略，各维噪声尺度被假设相同。
- **已知不成立之处**：
  - 末层 hidden 经 RMSNorm 后乘以逐维可学习权重，各维尺度不同，且常有少数大幅值维度；
  - hidden 具有各向异性。
- **可选扩展**（均仍可解耦）：
  - 逐维：$\mathbf R=\mathrm{diag}(R_1..R_d)$，$\mathbf Q=\mathrm{blockdiag}(Q_m)$，得到 $d$ 个独立小滤波器，成本 $O(dn^2)$；
  - 分组：$G$ 组共享参数；
  - 预白化：先除以 RMSNorm 权重，再用同参数滤波。
- 三种取法的比较见 E17。

**预测-校正**（每维相同，写成 $(n+1)$ 维形式）：
$$\text{预测：}\ s^-=Fs,\qquad P^-=FPF^\top+Q;$$
$$\text{校正：}\ e=y-Hs^-,\quad S=HP^-H^\top+R,\quad K=P^-H^\top S^{-1},\quad s=s^-+K\otimes e,\quad P=(I-KH)P^-(I-KH)^\top+KRK^\top.$$
$P$ 的更新采用 Joseph 形式，以保持对称正定。

**稳态增益**：若 $(F,H)$ 可观测、$(F,Q^{1/2})$ 可稳，则 $P^-$ 收敛到离散代数 Riccati 方程的解
$$P^-_\infty=FP^-_\infty F^\top-FP^-_\infty H^\top(HP^-_\infty H^\top+R)^{-1}HP^-_\infty F^\top+Q,\qquad K^\star=P^-_\infty H^\top(HP^-_\infty H^\top+R)^{-1}.$$
$F=I+N$、$H=[1,0..]$ 构成可观测对，这是标准结论；具体收敛条件以教材为准，教材出处待补。

**与 α-β 的对应（Kalata）**：对“离散白噪声加速度”模型（$n=1$，$Q=\sigma_w^2GG^\top$，$G=(T^2/2,T)^\top$，$R=\sigma_v^2$），稳态增益 $K^\star=(\alpha,\beta/T)$ 由跟踪指数 $\lambda=\sigma_wT^2/\sigma_v$ 决定。常见引述形式为：
$$r=\frac{4+\lambda-\sqrt{8\lambda+\lambda^2}}{4},\qquad\alpha=1-r^2,\qquad\beta=2(2-\alpha)-4\sqrt{1-\alpha}.$$
α-β-γ 情形另有 $\gamma=\beta^2/(2\alpha)$ 等关系 [55]。

**核对说明**：上式经二手来源（Wikipedia “Alpha beta filter” 条目与 ControlSystems.jl 文档，均注明出自 Kalata 1984 [50] 与 Gray & Murray 1993 [55]）核对，**未读到原文，记为待核对**。另外，增益约定存在因子 2 的差异（$\gamma$ 与 $2\gamma$），以原文为准。

**新息自适应的 $Q$、$R$ 在线估计**（免训练、逐序列；下列公式为常见引述形式，具体细节以原文为准，待核对）：

- **新息协方差匹配**（Mohamed–Schwarz [59]）：在窗口 $W$ 内计算标量化的新息二阶矩
  $$\hat C_t=\frac1{Wd}\sum_{\tau=t-W+1}^t\lVert e_\tau\rVert^2.$$
  由此估计
  $$\hat R=\max\big(\hat C_t-HP^-H^\top,\ r_{\min}\big),\qquad \hat Q=K\hat C_tK^\top\ (+\epsilon I).$$
- **Sage–Husa 型递推**（[58]，带遗忘因子 $b\in(0,1)$，$\delta_t=(1-b)/(1-b^{t+1})$）：
  $$\hat R_t=(1-\delta_t)\hat R_{t-1}+\delta_t\big(\tfrac1d\lVert e_t\rVert^2-HP^-H^\top\big),$$
  $$\hat Q_t=(1-\delta_t)\hat Q_{t-1}+\delta_t\big(K\tfrac1d\lVert e_t\rVert^2K^\top+P-FP_{t-1}F^\top\big).$$
  每步投影回正定锥（特征值截断），并设下界。
- **Mehra 型**（[56][57]）：用新息序列的自相关检验和辨识 $Q$、$R$。新息白则模型一致，可作为诊断指标，也用于 E17。
- **初始化**：用 prompt 段的已提交 hidden 预热（只做校正、不起草）。也可由 prompt 段的 $\lVert\nabla^rh\rVert$ 给出 $Q$、$R$ 的矩估计，此时可借助命题 6：在独立噪声模型下，$\mathbb E\lVert\nabla^{n+1}y\rVert^2=\lVert\nabla^{n+1}p\rVert^2+\binom{2n+2}{n+1}\sigma^2d$。

**两类观测**：

- 已提交位置：精确 hidden，观测噪声 $R$；
- 草稿代理 $\tilde h$：观测噪声 $R'=R+R_\delta$，$R_\delta\ge0$，相当于 $R'>R$。

$R_\delta$ 可以免训练地在线估计。一个节点被接受后，它的精确 hidden $H[n_i]$ 就可以与上一轮的代理 $\tilde h_{i+1}$ 比较，因为两者对应同一位置：
$$\hat R_\delta\leftarrow\text{EMA}\Big(\tfrac1d\lVert H[n_i]-\tilde h_{i+1}\rVert^2\Big).$$
沿节点前缀累积时用 $R'$ 校正（§5.4），块内只预测。

**槽位不确定性（扩展）**：节点 $i$ 在块内第 $j$ 步的预测协方差为
$$P^{(i)}_j=F^{\,j-1}P^{(i)}F^{(j-1)\top}+\sum_{m<j-1}F^mQF^{m\top},\qquad \sigma^{2}_{i,j}=HP^{(i)}_jH^\top$$
（每维）。可能的用法：

- (a) 自适应草稿长度：取 $k_{\text{eff}}=\max\{j:\sigma^2_{0,j}\le\theta\}$，需配合注意力块的变长或截断；
- (b) 自适应 mask 温度：在 M2 期望 embedding 映射中令 $T_j\propto\sigma_{i,j}$；
- (c) 作为接受概率的特征。

以上均为**扩展**【待测】，不进入主结果。$\sigma^2$ 与真实接受率的关系是猜想 C13。

**Algorithm 3：卡尔曼 mask provider**
```text
State : s^c ∈ ℝ^{(n+1)×d}, P^c ∈ ℝ^{(n+1)×(n+1)}, Q, R, R_δ, innovation window 𝓦
Init(prompt hiddens y_1..y_t):
 1  s^c ← backward-difference init from y_{t−n..t}; P^c ← p_0·I; Q,R ← moment init (Prop. 6) or defaults
 2  for τ in warm-up positions: (s^c, P^c, e) ← KF(s^c, P^c, y_τ, R); push e to 𝓦
ObserveCommitted(y):                                   ▷ exact hidden of an accepted node
 3  (s^c, P^c, e) ← KF(s^c, P^c, y, R); push e to 𝓦
 4  (Q, R) ← AdaptQR(𝓦, P^c, K)                         ▷ covariance matching / Sage–Husa; clamp to PSD, R ≥ r_min
ObserveProxyError(y_exact, h̃_proxy):
 5  R_δ ← EMA(‖y_exact − h̃_proxy‖²/d)
Masks(proxies h̃_1..h̃_k):                              ▷ called before the block forward
 6  s ← s^c; P ← P^c
 7  for i ← 0 to k do
 8      s ← F·s; P ← F P Fᵀ + Q
 9      if i < k then (s, P, _) ← KF_update(s, P, h̃_{i+1}, R + R_δ)
10      (s⁽ⁱ⁾, P⁽ⁱ⁾) ← (s, P)
11  for i ← 0 to k do                                  ▷ parallel over nodes
12      u ← s⁽ⁱ⁾; Σ ← P⁽ⁱ⁾
13      for j ← 1 to k do
14          M⁽ⁱ⁾_j ← Φ(u[0]); σ²_{i,j} ← Σ[0,0]              ▷ σ² optional (extensions)
15          u ← F_blk·u; Σ ← F_blk Σ F_blkᵀ + Q
16  return M, σ²
KF_update(s, P, y, R):  e ← y − s[0]; S ← P[0,0] + R; K ← P[:,0]/S
                        s ← s + K⊗e; P ← (I−K hᵀ)P(I−K hᵀ)ᵀ + K R Kᵀ  (h = e_0, Joseph); return (s, P, e)
```
（KF = 预测 + KF\_update。）

**复杂度**：

- 协方差递推与 $d$ 无关，每步 $O(n^3)$；$n\le3$ 时可以忽略。
- 状态更新每步 $O(nd)$。
- 每轮：
  - 前缀累积 $O(k(nd+n^3))$；
  - 块内外推 $O(k^2(nd+n^3))$；
  - 自适应估计 $O(d+n^3)$。
- 逐维扩展把协方差部分乘以 $d$，变为 $O(dn^3)$。
- 与 v5 的固定增益版相比，额外开销只有 $n$ 维小矩阵运算。

**数值稳定性**：

- 状态与协方差用 fp32；
- $P$ 用 Joseph 形式更新，每步对称化 $P\leftarrow(P+P^\top)/2$；
- $R$、$Q$ 设下界并投影回正定锥；
- 高阶（$n\ge2$）下 $F$ 的幂会放大，块内可用阻尼 $\rho<1$；
- $S=P_{00}+R$ 为标量，不需要矩阵求逆。

### 5.10 三种预测器的层级关系

| 层级 | 形式 | 系数 / 增益来源 | 假设 | 免训练 |
|---|---|---|---|---|
| 在线线性预测（小 AR） | $\hat h_{t+1}=\sum_{l\le L}a_lh_{t-l}$，$a$ 由逐序列在线（加权）最小二乘拟合 | 推理时逐序列拟合 | 局部平稳的线性动态 | 是 |
| 牛顿差分（固定 AR） | $a_l=(-1)^l\binom{n+1}{l+1}$；等价于 $F=I+N$、不平滑 | 由阶数 $n$ 唯一决定 | 局部 $n$ 次多项式、无噪声 | 是 |
| 常增益滤波（逐阶 EMA / α-β-γ） | $s\leftarrow Fs+K\otimes(y-[Fs]_0)$，$K$ 固定 | 手设或网格搜索 $\beta$ | 多项式趋势 + 噪声，增益固定 | 是（但需选参） |
| 稳态卡尔曼 | 同上，$K=K^\star(Q,R)$ 解自 DARE | 由 $(Q,R)$ 决定 | 线性高斯状态空间模型，$Q$、$R$ 已知 | 是 |
| 自适应卡尔曼 | 时变 $K_t$，$Q$、$R$ 由新息在线估计 | 逐序列在线估计 | $Q$、$R$ 未知、慢变 | 是 |

```text
 online AR (fit a_l per sequence) ──special case: fixed a_l = Newton──▶ Newton difference (fixed AR, no smoothing)
          ▲ steady-state Kalman ≡ infinite-order AR with geometrically decaying a_l (classical equivalence, ref. TBD)
 constant-gain filter (EMA / α-β-γ) ──K chosen optimally for (Q,R)──▶ steady-state Kalman ──Q,R estimated online──▶ adaptive Kalman
 Newton difference = difference-state filter without smoothing (β_r = 0, Prop. 5c); fixed EMA (n=1) = steady-state Kalman of local-linear-trend, R→0 (Prop. 8)
```

一句话概括三者：

- 线性预测器是推理时逐序列在线拟合的小 AR；
- 差分是局部多项式假设下系数固定的 AR；
- 卡尔曼是带最优（且可在线自适应）增益的状态空间版本，固定 EMA 是它的稳态特例（命题 8）。

### 5.11 实现说明（仓库只读核查，2026-10-13）
**现状**：

1. **每个节点已有自己的 $k$ 个 mask 槽位，结构上已按前缀并行。**
   - `tree_attention.block_layout` 的块布局为 `[root | node_1..node_N | masks(root) | masks(node_1) | … ]`，每个 owner 有 $k$ 个 mask；
   - mask $j$ 注意 owner 的注意集（前缀 + 祖先 + owner 自身）、同 owner 的 mask $1..j-1$ 和自身；
   - 位置为 `rel[owner] + j + 1`；
   - 节点不注意 mask。
   
   这与 §4.2 的 $\mathcal A$ 和 pos 一致（链式即 `branches: [1]*k`）。下一轮种子取最深接受节点的 mask（`mask_indices_of(tree, k, n_star)`）。

2. **但 mask 的内容在所有 owner 之间完全相同。**
   - `decoding.py` 中 `masks = provider.masks()` 返回 $[k,d]$，随后执行 `masks.unsqueeze(0).expand(1 + num_nodes, k, -1)`，把同一组向量复制给每个 owner；
   - provider 状态只通过 `on_token_committed(new_embed, prev_embed)` 用**已提交** token 的**输入** embedding 更新，不看草稿前缀，也不接收 hidden。

3. **hidden**：`HFCausalLM.forward` 有 `output_hidden_states` 参数，但 `SpecDecoder` 不请求 hidden。末项是否经过最终归一化尚待核对。

**要改什么**（仅列清单，未改代码）：

| 改动 | 位置 | 说明 |
|---|---|---|
| provider 接口返回 $[1+N,k,d]$，输入为草稿前缀与代理 hidden | `mask_providers.py` | 新增 `masks_per_owner(draft_tokens, draft_hiddens, ...)`；保留旧接口供 ESP 使用 |
| 用逐 owner 张量替换 `expand` | `decoding.py`（块 embedding 拼接处） | 按 `block_layout` 的 owner 顺序 reshape |
| 前向请求末层 hidden，保存 $H[n_A]$ 与 $H[M^{(A)}]$ | `decoding.py`、`hf_causal.py` | 只取末层，避免保留全部层 |
| 状态更新改用 hidden（已提交节点的精确 hidden） | `decoding.py` 提交循环 | 替代 `on_token_committed(embed)` 或与之并存 |
| 非 tied 时预计算 $W_a$ 与 $\bar\nu$ | 新模块 | fp32，一次 |
| 注意力掩码与位置编码 | `tree_attention.py` | **无需改动**：结构只依赖树形状，efficient 缓存路径仍然适用 |

树形扩展时，节点前缀为其祖先路径，按祖先链折叠状态即可。

**对此前说法的纠正**：v3 §11 写的“所有 owner 共用同一组 mask”，就 mask 向量的**数值**而言准确；但没有说明注意力和位置**已经**按 owner（前缀）独立、天然并行。因此，实现前缀条件 mask 只需改 mask 的内容（provider 与拼接），不需要改注意力或位置编码。

---


**高阶实现补充（v5，未改代码）**：

- **缓存**：provider 维护已提交状态 $s^c\in\mathbb R^{(n+1)\times d}$（或最近 $n+1$ 个已提交 hidden 的环形缓冲），并保留上一轮 $H[M^{(A)}]$ 的 $k$ 个 hidden。
- **接口**：新增 `observe_committed(hidden)` 与 `masks_per_owner(proxy_hiddens) -> [1+N,k,d]`。
- **配置**：`order n`、`F/F_blk`（$\gamma_r,\rho_r$）、`K` 与 `K′`（或 $\beta_r,\beta'_r$）、`predictor ∈ {difference, linear_fixed, linear_ls}`。
- **需要改的文件**：`mask_providers.py`、`decoding.py`、`hf_causal.py`（只请求末层 hidden）；`tree_attention.py` 不变。
- **数值**：建议用 fp32 保存状态。高阶差分在 bf16 下抵消误差大，需在 E12 检查。

## 6. Theoretical Analysis

### 命题 1（soft mask 下的无损性）
**条件**：节点输入为离散 token embedding；注意力满足 $\mathcal A$（节点不看 mask）；$\mathrm{pos}(n_i)=p+i$；算术精确。

**结论**：对任意 mask 内容（包括逐节点不同的 soft 向量），

- (a) 贪心输出与自回归逐 token 一致；
- (b) 以 mask 分布 $q$ 作草稿分布、按 $\min(1,p/q)$ 接受并在拒绝时从残差分布重采样 [1][2]，输出与自回归采样同分布。

**证明**：节点 logits 与 mask 无关，等于自回归在前缀 $(\cdot,\tilde x_{1:i})$ 上的条件分布。草稿分布 $q$ 在本轮之前已经确定，所以标准投机采样引理逐位置适用。KV 只保留离散输入的节点。$\square$

浮点下以 exact\_match 检验。仓库现有的 $T>0$ 路径不是残差采样，(b) 需要新实现。

### 命题 2（链式加速比上界）
$$S\le\frac{\mathbb E[\tau]\,c_1}{c_B+c_\Phi}\le\mathbb E[\tau]\le k+1.$$
其中 $c_1$ 为单 token 前向开销，$c_B$ 为块前向开销，$c_\Phi$ 为映射开销。

### 命题 3（hidden 与 logit 外推等价）
外推是线性组合，而 $W$ 是线性映射，因此 $W\hat a_j$ 等于在 logits 上做同样外推的结果。在分布空间外推不等价。$\square$

### 命题 4（tied 下岭回归对齐近似恒等）
若 $W_{\text{out}}=W_{\text{in}}=E$，则 $W_a=(E^\top E+\lambda I)^{-1}E^\top E$，且
$$\lVert W_a-I\rVert_2=\frac{\lambda}{\sigma_{\min}^2(E)+\lambda}.$$
当 $\lambda\ll\sigma_{\min}^2$ 时 $W_a\approx I$。所以在 tied 模型上岭回归映射几乎不起作用，直接用 hidden 加范数缩放即可。$\sigma_{\min}$ 的实际数值待测（E8 可顺带计算）。


### 命题 5（统一：零阶、一阶、线性预测都是特例）
(a) **牛顿外推。** 当 $\gamma_r=\rho_r=1$ 时，$[F^js]^{[0]}=\sum_{r\le n}\binom jr s^{[r]}$。

*证明*：$F=I+N$，$N$ 幂零（$N^{n+1}=0$），且 $N$ 与 $I$ 可交换，由二项式展开即得。$\square$

(b) **v4 是 $n=1$ 的特例。** 取 $n=1$，$\kappa_0=1$，$\kappa_1=1-\beta$，$F=\left(\begin{smallmatrix}1&1\\0&1\end{smallmatrix}\right)$。则校正后零阶等于观测值，一阶为 $v\leftarrow\beta v+(1-\beta)(y-y_{\text{prev}})$，正是 v4 的速度 EMA。块内用 $F_{\text{blk}}=\left(\begin{smallmatrix}1&\gamma\\0&\rho\end{smallmatrix}\right)$，得到 v4 的 $\hat a_j=a+\gamma c_j(\rho)v$。$n=0$ 时为零阶-only。

*证明*：

- 预测：$s^{-[0]}=y_{\text{prev}}+v$，$s^{-[1]}=v$；
- 零阶校正：$s^{[0]}=s^{-[0]}+1\cdot(y-s^{-[0]})=y$；
- 一阶校正：$s^{[1]}=v+(1-\beta)(y-y_{\text{prev}}-v)=\beta v+(1-\beta)(y-y_{\text{prev}})$；
- 块内：$F_{\text{blk}}^{\,j}$ 的 $(0,1)$ 元为 $\gamma\sum_{s<j}\rho^s$。$\square$

(c) **固定系数线性预测器等价于无平滑差分外推。** 若各阶状态直接取历史观测的后向差分（无 EMA，$\beta_r=0$），则一步外推 $\hat h_{t+1}$ 等于 $a_l=(-1)^l\binom{n+1}{l+1}$ 的线性预测器。

*证明*：由 $\nabla^{n+1}\hat h_{t+1}=\sum_{m=0}^{n+1}(-1)^m\binom{n+1}m h_{t+1-m}=0$ 解出 $\hat h_{t+1}$。$\square$

### 命题 6（一步外推的偏差-噪声放大分解）
**设定**：观测 $h_\tau=p_\tau+\varepsilon_\tau$。其中 $p$ 为确定性轨迹；$\varepsilon_\tau$ 独立、零均值、协方差 $\sigma^2I_d$。考虑无平滑 $n$ 阶外推（命题 5(c)）$\hat h_{t+1}=\sum_{l=0}^n a_lh_{t-l}$。

**结论**：
$$\mathbb E\lVert\hat h_{t+1}-p_{t+1}\rVert^2=\underbrace{\lVert\nabla^{n+1}p_{t+1}\rVert^2}_{\text{偏差}^2}+\underbrace{\sigma^2d\Big[\tbinom{2n+2}{n+1}-1\Big]}_{\text{噪声放大}}.$$

*证明*：

1. 由命题 5(c)，$p_{t+1}-\sum_la_lp_{t-l}=\nabla^{n+1}p_{t+1}$。
2. 因此 $\hat h_{t+1}-p_{t+1}=-\nabla^{n+1}p_{t+1}+\sum_la_l\varepsilon_{t-l}$。
3. 交叉项期望为 0；噪声项方差为 $\sigma^2d\sum_la_l^2$。
4. $\sum_{l=0}^n\binom{n+1}{l+1}^2=\sum_{m=1}^{n+1}\binom{n+1}m^2=\binom{2n+2}{n+1}-1$（范德蒙德恒等式）。$\square$

**数值**：噪声放大因子 $\binom{2n+2}{n+1}-1$ 在 $n=0,1,2,3$ 时分别为 $1,5,19,69$，按约 $4^{n+1}$ 增长。

**推论（最优阶数条件）**：阶数从 $n$ 增加到 $n+1$ 能降低一步 MSE，当且仅当
$$\lVert\nabla^{n+1}p\rVert^2-\lVert\nabla^{n+2}p\rVert^2>\sigma^2d\Big[\tbinom{2n+4}{n+2}-\tbinom{2n+2}{n+1}\Big].$$
所以只有当轨迹的高阶差分随阶数快速衰减、且噪声较小时，高阶才有益。

### 命题 7（多步外推的方差增长）
同样设定下，$j$ 步无平滑外推可写为 $\hat h_{t+j}=\sum_{l=0}^n\ell_l(j)\,h_{t-l}$。其中 $\ell_l$ 是以节点 $\{0,-1,\dots,-n\}$ 为插值点的拉格朗日基函数在 $j$ 处的值。噪声方差为 $\sigma^2d\sum_l\ell_l(j)^2$。

由于每个 $\ell_l$ 是 $n$ 次多项式，方差随 $j$ 以 $O(j^{2n})$ 增长。

*证明*：$n$ 次多项式外推是拉格朗日插值在 $j$ 处取值，其余同命题 6。$\square$

**含义**：远槽位的高阶外推方差增长更快，这为块内阻尼 $\rho<1$ 或低阶块内外推提供了理由。

### 猜想 C11（平滑的作用）
EMA 校正（$\beta_r>0$）降低噪声放大，代价是滞后偏差。存在使 $\mathbb E[A]$ 最大的 $(n,\beta_{1..n})$ 组合，且最优 $n$ 较小（$\le2$）。命题 6、7 只覆盖无平滑情形，带平滑的稳态误差分析（参照 [50] 的 tracking index）未完成。

### 猜想 C12（hidden 噪声模型）
末层 hidden 的逐 token 变化中，“可预测趋势”占比有限，独立噪声假设只是近似。可以在 E13 中用已提交 hidden 的 $\lVert\nabla^r h\rVert$ 随 $r$ 的变化，经验估计命题 6 中偏差项与噪声项的相对大小。若 $\lVert\nabla^rh\rVert$ 随 $r$ 按 $\approx\sqrt{\binom{2r}{r}}$ 增长，说明以噪声为主。


### 命题 8（固定 EMA 是稳态卡尔曼的特例；$\beta^\star$ 闭式）
**设定**：$n=1$，$F=\left(\begin{smallmatrix}1&1\\0&1\end{smallmatrix}\right)$，$H=[1,0]$。取“局部线性趋势”模型 $Q=\mathrm{diag}(q_0,q_1)$，其中 $q_0>0$ 为水平噪声、$q_1>0$ 为斜率噪声，并令 $R\to0$（观测无噪声）。

**结论**：稳态卡尔曼增益为 $K^\star=(1,\ \kappa_1^\star)$，其中
$$\kappa_1^\star=\frac{\pi}{1+\pi},\qquad \pi=\frac{\phi+\sqrt{\phi^2+4\phi}}{2},\qquad\phi=\frac{q_1}{q_0}.$$
因此 v4 的固定 EMA（$\kappa_0=1$，$\kappa_1=1-\beta$）恰是该模型的稳态卡尔曼，且
$$\beta^\star=1-\kappa_1^\star=\frac1{1+\pi(\phi)}.$$
$\beta^\star$ 随信噪比 $\phi$ 单调递减：$\phi\to0$（斜率几乎不变）时 $\beta^\star\to1$，即长记忆；$\phi\to\infty$ 时 $\beta^\star\to0$。

**证明**：

1. $R=0$ 时，校正后位置方差为 0，所以稳态 $P=\mathrm{diag}(0,p)$。
2. 预测协方差 $P^-=FPF^\top+Q=\left(\begin{smallmatrix}p+q_0&p\\p&p+q_1\end{smallmatrix}\right)$。
3. 增益 $K=P^-H^\top/P^-_{00}=(1,\,p/(p+q_0))$。
4. 校正后斜率方差为 $p+q_1-p^2/(p+q_0)$；稳态要求它等于 $p$，得 $p^2-q_1p-q_1q_0=0$，正根 $p=q_0\pi$。
5. 代入得 $\kappa_1^\star=\pi/(1+\pi)$。
6. 校正后 $s^{[0]}=y$，$s^{[1]}=v+\kappa_1(y-y_{\text{prev}}-v)=(1-\kappa_1)v+\kappa_1\nabla y$，即 EMA，其中 $\beta=1-\kappa_1$。$\square$

**含义**：

- 网格搜索 $\beta$，等价于在“无观测噪声的局部线性趋势模型”族中搜索信噪比 $\phi$；
- $R>0$ 时最优 $\kappa_0<1$，即锚点本身也被去噪。这一自由度超出了 v4/v5 的固定 EMA 族，是卡尔曼版本可能带来增益的理论来源（H12）；
- $n\ge2$ 的逐阶 EMA 是否都能作为某个对角 $Q$ 的稳态卡尔曼，未证明，记为猜想 C14。

**与 Kalata 的关系**：Kalata [50] 的离散白噪声加速度模型（$Q$ 秩 1）在 $R>0$ 时给出 $\alpha<1$ 的闭式（§5.9，待核对）。本命题用的是另一种 $Q$ 结构（对角、$R\to0$），两者都是 α-β 族的稳态卡尔曼特例。

### 命题 9（稳态增益的均方最优性，最优 β 存在）
在线性高斯模型下，给定 $(Q,R)$：

- 卡尔曼滤波在所有线性（实际上是所有可测）估计器中使预测均方误差最小 [49]；
- 在所有使误差动态稳定的常增益滤波 $K$ 中，$K^\star$（DARE 解）使稳态预测误差协方差最小（标准结论，教材出处待补）。

**推论**：对命题 8 的模型族，最优 $\beta^\star(\phi)$ 存在且唯一。若真实 hidden 轨迹近似符合某个 $(Q,R)$，则网格搜索得到的最优 $\beta$ 应接近 $\beta^\star(\hat\phi)$，可在 E16 中检验。

**意义**：最优 $\beta$ 由数据的噪声结构决定，不是超参数。自适应卡尔曼逐序列估计 $(Q,R)$，等价于逐序列选取 $\beta$，因此有望跨数据集免调参（H12）。

### 命题 10（槽位预测方差的递推）
块内预测满足 $P^{(i)}_{j+1}=F_{\text{blk}}P^{(i)}_jF_{\text{blk}}^\top+Q$，因此
$$\sigma^2_{i,j+1}=[F_{\text{blk}}P^{(i)}_jF_{\text{blk}}^\top]_{00}+Q_{00}.$$
当 $F_{\text{blk}}=I+N$、$n\ge1$ 时，$[FPF^\top]_{00}=P_{00}+2P_{01}+P_{11}$。若 $P_{01}\ge-P_{11}/2$（例如 $P$ 由 Riccati 递推得到且位置与斜率误差非负相关），则 $\sigma^2_{i,j}$ 关于 $j$ 严格递增（$Q_{00}>0$ 时）。

**证明**：$F=I+N$ 的第 0 行为 $(1,1,0,\dots)$，代入二次型即得。$\square$

一般条件下的单调性未证明，记为猜想 C15。

### 猜想（卡尔曼）

- **C13**：$\sigma^2_{i,j}$ 与逐槽接受率负相关，可用于自适应 $k$ 或温度。
- **C14**：$n\ge2$ 的逐阶 EMA 可以表示为某对角 $Q$、$R\to0$ 模型的稳态卡尔曼。
- **C15**：不加协方差符号条件时，命题 10 的单调性是否仍然成立。
- **C16**：由数据估计的 $(\hat Q,\hat R)$ 可预测最优阶数。具体做法是按命题 6 的推论，用 $\hat Q$ 的高阶分量与 $\hat R$ 之比判定增阶是否有益。

### 猜想

- **C6（预测性）**：$\mathbb E[A]$ 满足 输出空间零阶 > ESP 均值。
- **C9（一阶）**：一阶外推在远槽位（$j\ge2$）上提高逐槽接受率。
- **C10（前缀条件）**：前缀条件优于共享状态，且增益随节点深度 $i$ 增大。
- **C7（分布偏移风险）**：soft 输入可能引起分布外激活；范数缩放能否缓解，待测。

---

## 7. Hypotheses
记 $\Delta_x(\pi,\pi')$ 为逐 prompt 接受数之差。检验采用确认集上的配对 bootstrap 95% CI + Wilcoxon，对多个假设做 Holm 校正。

- **H1（主效应）**：$\Delta(\text{Ours},\text{ESP})>0$，在至少 2 个规模、至少 2 个数据切片上成立。
- **H2（零阶预测性）**：$\Delta(\text{零阶-only},\text{ESP})>0$。
- **H3（一阶）**：$\Delta(\text{零阶+一阶},\text{零阶-only})>0$，且增益集中在 $j\ge2$。
- **H4（前缀条件）**：$\Delta(\text{前缀条件},\text{共享状态})>0$，且逐节点深度的增益单调非减（描述性）。
- **H5（块内递推）**：在 $\rho\ne1$ 时，递推优于冻结。负对照为 $\gamma=1$ 或 $k=1$。
- **H6（映射）**：
  - tied：hidden + 范数缩放 ≥ 原始 hidden；
  - 非 tied：$W_a$ 映射 ≥ 直接 hidden；
  - 负对照：tied 上 $W_a$ 映射与恒等无差异。
- **H7（偏移判别）**：相对固定偏移基线 $\pi_{\text{off}}$ 有显著增益。
- **H8（跨域稳定性）**：定义域外保留率 $\mathrm{R}=\mathbb E[\tau]_{\text{OOD}}/\mathbb E[\tau]_{\text{ID}}$，其中 ID/OOD 以训练式基线的训练分布划分。假设 $\mathrm R_{\text{Ours}}>\mathrm R_{\text{EAGLE-3}}$，且 OOD 上 $\mathbb E[\tau]_{\text{Ours}}$ 与 EAGLE-3 的差距小于 ID 上的差距。由于本法免训练，其 $\mathrm R$ 只反映任务本身难度的差异。

- **H9（高阶增益）**：存在 $n\ge2$，使 $\Delta(n,\,n{=}1)>0$，且增益集中在 $j\ge2$ 的槽位。
- **H10（最优阶数）**：$\mathbb E[A]$ 关于 $n\in\{0,1,2,3\}$ 呈单峰；最优阶数 $n^\star$ 与命题 6 推论用经验 $\lVert\nabla^r h\rVert$ 估计出的阶数一致（描述性检验）。
- **H11（预测器形式）**：带 EMA 的差分滤波优于同阶无平滑外推（固定系数线性预测）；在线最小二乘线性预测与差分滤波的差异作双侧检验。
- **H12（自适应 ≥ 最优固定）**：在每个确认集上，自适应卡尔曼的 $\mathbb E[A]$ 不低于在**该数据集上**网格搜索得到的最优固定 $\beta$（非劣效界 $-\delta$，$\delta$ 待作者确认）；且在**另一数据集上调出的** $\beta$ 迁移过来时，自适应卡尔曼显著更优（跨数据集无需重调）。
- **H13（估计的 Q/R 预测最优阶数）**：由 $(\hat Q,\hat R)$ 和命题 6 推论预测的阶数 $\hat n$，与 E13 经验最优的 $n^\star$ 一致（逐数据集比较，描述性检验，配合 Spearman 相关）。

---

## 8. Experimental Plan

### 8.1 数据

- **主数据**：Spec-Bench [14] 480 条，切片为 first 26（选参）/ next 52 / last 52 / 全量（确认）。
- **跨域（H8）**：对每个训练式基线，按其训练数据定义 ID/OOD：
  - EAGLE 系列以 ShareGPT 类对话为训练分布（以所用权重的说明为准【待核对】），ID 取对话类子集；
  - OOD 取 Spec-Bench 中的数学、代码、检索增强、摘要等子类，以及长上下文集（如 LongSpecBench [45]，可得性待核对）；
  - 可选：自训一个只用数学数据的 EAGLE-3 起草器，复刻 [44] 的设置【需算力，待作者确认】。
- **模板**：聊天模板开/关作为一个因素。

### 8.2 模型

| 模型 | tied | $d$ | 映射 |
|---|---|---:|---|
| Qwen3-0.6B | 是 | 1024 | hidden + 缩放 |
| Qwen3-1.7B | 是 | 2048 | hidden + 缩放 |
| Qwen3-4B | 是 | 2560 | hidden + 缩放 |
| Qwen3-8B | 否 | 4096 | $W_a$ 适配 |
| Qwen3-14B | 否 | 5120 | $W_a$ 适配 |

tied 与 $d$ 来自 HF config。EAGLE-3 的公开起草器是否覆盖这些目标模型尚【待核对】，H8 的模型选择以此为准。

### 8.3 基线

- 自回归；
- ESP 均值；
- 输入空间外推（附录 B）；
- 固定偏移 $\pi_{\text{off}}$；
- 免训练：PLD、Lookahead [8]、STAND [21]；
- 训练式：EAGLE-3 [6]（公开权重），以及可选的 Medusa [3]/Hydra [7]。训练式基线只用于 H8 和参照。

### 8.4 指标

- 主指标：$\sum A$ 与 $\mathbb E[\tau]$；
- 逐槽、逐节点深度的接受率；
- 跨域保留率 $\mathrm R$；
- 墙钟 $S$ 与 $c_\Phi/c_B$；
- exact\_match = 1 作为门槛；
- 机制指标：mask 输入的范数与激活统计（C7）。

### 8.5 实验矩阵（$k\in\{1,\dots,4\}$，全部待测）

| 编号 | 类型 | 设置 | 假设 |
|---|---|---|---|
| E1 | 基线复现 | ESP 原设置（树形，附录） | — |
| E2 | 主对照 | Ours vs ESP vs 输入空间外推 | H1 |
| E3 | 映射 | 缩放开/关、原始 hidden、期望 embedding、$W_a$（$\lambda$ 扫描） | H6、C7 |
| E4 | 阶数 | ESP → 零阶-only → +一阶冻结 → +一阶递推，按槽 $j$ 分解 | H2、H3、H5 |
| E5 | 前缀条件 | 前缀条件 vs 共享 $(a^{(0)},v^{(0)})$，按节点深度 $i$ 分解 | H4 |
| E6 | 空间 | hidden vs logit（应相同）vs 分布 | 命题 3 |
| E7 | 偏移判别 | vs $\pi_{\text{off}}$ | H7 |
| E8 | 规模/tied | 0.6B–14B；tied 上 $W_a$ vs 恒等 | H6、命题 4 |
| E9 | 采样 | 残差投机采样，$T\in\{0.7,1\}$ | 命题 1b |
| E10 | 墙钟 | $S$、$c_\Phi/c_B$ | 命题 2 |
| E11 | 跨域 | ID/OOD × {Ours, ESP, PLD, EAGLE-3}，报告 $\mathbb E[\tau]$、$\mathrm R$、$S$ | H8 |
| E12 | 失败分析 | 冷启动、长上下文、OOD 激活、bf16 | 边界 |

**跨域表模板（E11）**

| 方法 | 训练 | ID $\mathbb E[\tau]$ | OOD $\mathbb E[\tau]$ | $\mathrm R$ | OOD $S$ |
|---|---|---:|---:|---:|---:|
| EAGLE-3 | 是 | 待测 | 待测 | 待测 | 待测 |
| PLD | 否 | 待测 | 待测 | 待测 | 待测 |
| ESP | 否 | 待测 | 待测 | 待测 | 待测 |
| Ours | 否 | 待测 | 待测 | 待测 | 待测 |


**高阶消融（全部待测）**

| 编号 | 类型 | 设置 | 假设 |
|---|---|---|---|
| E13 | 阶数 | $n\in\{0,1,2,3\}$，各阶 $\beta_r\in\{0,0.5,0.9,0.99\}$，在选参集上做网格或逐阶搜索；按槽位 $j$ 分解；同时记录经验 $\lVert\nabla^r h\rVert$ | H9、H10、命题 6、C12 |
| E14 | 预测器 | 差分滤波 vs 固定系数线性预测（$L=n$）vs 在线 LS（$W\in\{16,64\}$，$L\in\{1,2,3\}$） | H11 |
| E15 | 增益与阻尼 | 逐阶 EMA vs $K$ 形式；代理增益 $K'$ vs $K$；块内 $\rho\in\{1,0.9,0.7\}$ | C11、命题 7 |

**卡尔曼与自适应实验（全部待测）**

| 编号 | 类型 | 设置 | 假设 |
|---|---|---|---|
| E16 | 自适应 vs 固定 | 固定 $\beta$ 网格（各数据集各自最优 / 跨数据集迁移）vs 稳态卡尔曼（$Q$、$R$ 由 prompt 段矩估计）vs 自适应卡尔曼（协方差匹配 / Sage–Husa，$W\in\{16,64\}$，$b\in\{0.95,0.99\}$）；同时比较网格最优 $\beta$ 与 $\beta^\star(\hat\phi)$ | H12、命题 8/9 |
| E17 | 模型假设 | 维度共享 vs 逐维 vs 分组 vs 预白化；代理 $R'$ 固定倍数 vs 在线 $\hat R_\delta$；新息白度检验（Mehra 自相关） | §5.9、C12 |
| E18 | 阶数预测与不确定性 | 用 $(\hat Q,\hat R)$ 预测 $\hat n$，与 E13 对照；$\sigma^2_{i,j}$ 与逐槽接受率的相关；扩展：自适应 $k$、自适应温度 | H13、C13、C16 |

---

## 9. Preliminary Results
v4 主方法没有实测。仓库已有数字为输入空间、树形、$k=1$，见附录 C，不作为本方法的证据。

## 10. Limitations

1. 尚无实测数据。
2. 首轮 mask 只能用 ESP 均值（冷启动）。
3. $\tilde h_\ell$ 是代理 hidden：它来自上一轮另一前缀下的计算，当草稿与真实前缀不一致时会产生误差。
4. 链末节点 $k$ 没有代理，只能靠外推。
5. soft 输入的分布偏移是待测风险。
6. 本法的绝对接受率可能低于域内的训练式方法；定位依赖 H8 的结果。
7. 残差采样需要新实现。
8. 新颖性有待系统检索确认。

9. 命题 6、7 假设独立噪声且无平滑，与实际 hidden 轨迹不一定相符；带平滑的误差分析未完成。
10. 高阶差分对数值精度敏感（bf16）。
11. 卡尔曼变体依赖维度分解与线性高斯假设；自适应 $Q$、$R$ 估计在短序列上可能不稳定。

## 11. Timeline & Venue（建议）

| 阶段 | 内容 | 时长 |
|---|---|---|
| P1 | 实现 §5.11 改动清单（需授权改代码）；核对 hidden 归一化；4B first 26 检查 | 2 周 |
| P2 | E2–E7 | 4 周 |
| P3 | E8–E11（含 EAGLE-3 跨域） | 4 周 |
| P4 | E12、附录树形、写作 | 3 周 |

目标会议：ICML / NeurIPS / ICLR，或 ACL / EMNLP（建议）。

## 12. Open Questions for Author

1. 代理 hidden $\tilde h_\ell$ 的定义（位置对齐方式）是否认可？链末节点 $a^{(k)}$ 采用外推还是复用 $a^{(k-1)}$？
2. 前缀速度沿草稿折叠时，是否使用与已提交历史相同的 $\beta$？
3. H8 的 ID/OOD 划分，以及是否自训起草器以复刻 [44]？
4. 是否实现残差投机采样？
5. 模型范围、精度与预算。
6. 确认 “denoising” 的含义即“对输出 hidden 轨迹做滤波去噪”（§1.5），以及论文定位。

---

7. 高阶状态的主参数化选哪一种：逐阶独立 $\beta_r$（推荐）还是 $K$ 增益形式？代理观测是否用单独的增益 $K'$？
8. 阶数搜索预算：$n\le3$ 是否足够？在线 LS 线性预测进主文还是放附录？
9. 卡尔曼变体作为“主自适应变体”还是直接作为主方法？H12 的非劣效界 $\delta$ 取多少？
10. 维度分解采用共享、逐维还是预白化？


## References

1. Y. Leviathan, M. Kalman, Y. Matias. *Fast Inference from Transformers via Speculative Decoding.* ICML 2023. <https://arxiv.org/abs/2211.17192>
2. C. Chen et al. *Accelerating Large Language Model Decoding with Speculative Sampling.* arXiv 2023. <https://arxiv.org/abs/2302.01318>
3. T. Cai et al. *Medusa: Simple LLM Inference Acceleration Framework with Multiple Decoding Heads.* ICML 2024. <https://arxiv.org/abs/2401.10774>
4. Y. Li et al. *EAGLE: Speculative Sampling Requires Rethinking Feature Uncertainty.* ICML 2024. <https://arxiv.org/abs/2401.15077>
5. Y. Li et al. *EAGLE-2: Faster Inference of Language Models with Dynamic Draft Trees.* EMNLP 2024. <https://arxiv.org/abs/2406.16858>
6. Y. Li et al. *EAGLE-3: Scaling up Inference Acceleration of LLMs via Training-Time Test.* NeurIPS 2025. <https://arxiv.org/abs/2503.01840>
7. Z. Ankner et al. *Hydra: Sequentially-Dependent Draft Heads for Medusa Decoding.* COLM 2024. <https://arxiv.org/abs/2402.05109>
8. Y. Fu et al. *Break the Sequential Dependency of LLM Inference Using Lookahead Decoding.* ICML 2024. <https://arxiv.org/abs/2402.02057>
9. F. Gloeckle et al. *Better & Faster Large Language Models via Multi-token Prediction.* ICML 2024. <https://arxiv.org/abs/2404.19737>
10. DeepSeek-AI. *DeepSeek-V3 Technical Report.* arXiv 2024. <https://arxiv.org/abs/2412.19437>
11. X. Miao et al. *SpecInfer: Accelerating Generative LLM Serving with Tree-based Speculative Inference and Verification.* ASPLOS 2024. <https://arxiv.org/abs/2305.09781>
12. R. Goel et al. *Efficient Training-Free Multi-Token Prediction via Embedding-Space Probing.* ICML 2026. <https://arxiv.org/abs/2603.17942>
13. D. J. Bajpai et al. *FlowCast: Trajectory Forecasting for Scalable Zero-Cost Speculative Flow Matching.* ICLR 2026. <https://arxiv.org/abs/2602.01329>
14. H. Xia et al. *Unlocking Efficiency in LLM Inference: A Comprehensive Survey of Speculative Decoding.* ACL 2024 Findings. <https://arxiv.org/abs/2401.07851>
15. Z. Chen et al. *Sequoia: Scalable, Robust, and Hardware-aware Speculative Decoding.* NeurIPS 2024. <https://arxiv.org/abs/2402.12374>
16. M. Stern, N. Shazeer, J. Uszkoreit. *Blockwise Parallel Decoding for Deep Autoregressive Models.* NeurIPS 2018. <https://arxiv.org/abs/1811.03115>
17. A. Santilli et al. *Accelerating Transformer Inference for Translation via Parallel Decoding.* ACL 2023. <https://arxiv.org/abs/2305.10427>
18. G. Monea et al. *PaSS: Parallel Speculative Sampling.* ENLSP Workshop @ NeurIPS 2023. <https://arxiv.org/abs/2311.13581>
19. N. Yang et al. *Inference with Reference: Lossless Acceleration of Large Language Models.* arXiv 2023. <https://arxiv.org/abs/2304.04487>
20. Z. He et al. *REST: Retrieval-Based Speculative Decoding.* NAACL 2024. <https://arxiv.org/abs/2311.08252>
21. W. Song et al. *Accelerated Test-Time Scaling with Model-Free Speculative Sampling.* EMNLP 2025. <https://arxiv.org/abs/2506.04708>
22. J. Zhang et al. *Draft & Verify: Lossless LLM Acceleration via Self-Speculative Decoding.* ACL 2024. <https://arxiv.org/abs/2309.08168>
23. F. Liu et al. *Kangaroo: Lossless Self-Speculative Decoding via Double Early Exiting.* NeurIPS 2024. <https://arxiv.org/abs/2404.18911>
24. J. K. Christopher et al. *Speculative Diffusion Decoding: Accelerating Language Generation through Diffusion.* NAACL 2025. <https://arxiv.org/abs/2408.05636>
25. G. Li et al. *DiffuSpec: Unlocking Diffusion Language Models for Speculative Decoding.* arXiv 2025. <https://arxiv.org/abs/2510.02358>
26. S. Agrawal et al. *Structuring The Future: Diffusion LLM Speculative Decoding via Calibrated Draft Graphs.* arXiv 2025. <https://arxiv.org/abs/2509.18085>
27. M. Samragh et al. *Your LLM Knows the Future: Uncovering Its Multi-Token Prediction Potential.* arXiv 2025. <https://arxiv.org/abs/2507.11851>
28. S. Kou et al. *CLLMs: Consistency Large Language Models.* ICML 2024. <https://arxiv.org/abs/2403.00835>
29. G. Oliaro et al. *SuffixDecoding: Extreme Speculative Decoding for Emerging AI Applications.* NeurIPS 2025. <https://arxiv.org/abs/2411.04975>
30. H. Xia et al. *SWIFT: On-the-Fly Self-Speculative Decoding for LLM Inference Acceleration.* ICLR 2025. <https://arxiv.org/abs/2410.06916>
31. S. Hao et al. *Training Large Language Models to Reason in a Continuous Latent Space* (Coconut). COLM 2025. <https://arxiv.org/abs/2412.06769>
32. Z. Zhang et al. *Soft Thinking: Unlocking the Reasoning Potential of LLMs in Continuous Concept Space.* arXiv 2025. <https://arxiv.org/abs/2505.15778>
33. Y. Zhuang et al. *Text Generation Beyond Discrete Token Sampling* (Mixture of Inputs). arXiv 2025. <https://arxiv.org/abs/2505.14827>
34. J. Zou et al. *Latent Collaboration in Multi-Agent Systems* (LatentMAS). ICML 2026 Spotlight. <https://arxiv.org/abs/2511.20639>；代码 <https://github.com/Gen-Verse/LatentMAS>
35. P. Wu et al. *Parallel Decoding via Hidden Transfer for Lossless Large Language Model Acceleration.* arXiv 2024. <https://arxiv.org/abs/2404.12022>
36. K. Pal et al. *Future Lens: Anticipating Subsequent Tokens from a Single Hidden State.* CoNLL 2023. <https://arxiv.org/abs/2311.04897>
37. N. Belrose et al. *Eliciting Latent Predictions from Transformers with the Tuned Lens.* arXiv 2023. <https://arxiv.org/abs/2303.08112>
38. B. Lester, R. Al-Rfou, N. Constant. *The Power of Scale for Parameter-Efficient Prompt Tuning.* EMNLP 2021. <https://arxiv.org/abs/2104.08691>
39. F. Lin et al. *BiTA: Bi-Directional Tuning for Lossless Acceleration in Large Language Models.* arXiv 2024. <https://arxiv.org/abs/2401.12522>
40. Z. Xiao et al. *ParallelSpec: Parallel Drafter for Efficient Speculative Decoding.* arXiv 2024. <https://arxiv.org/abs/2410.05589>
41. H. Yi et al. *Generation Meets Verification: Accelerating LLM Inference with Smart Parallel Auto-Correct Decoding* (SPACE). ACL 2024 Findings. <https://arxiv.org/abs/2402.11809>
42. J. Tack et al. *LLM Pretraining with Continuous Concepts* (CoCoMix). arXiv 2025. <https://arxiv.org/abs/2502.08524>
43. LCM team. *Large Concept Models: Language Modeling in a Sentence Representation Space.* arXiv 2024. <https://arxiv.org/abs/2412.08821>
44. F. Bie et al. *Osprey: Target-agnostic Pre-training Makes Stronger Drafters in Speculative Decoding.* EMNLP 2026（arXiv 评论：Accepted at EMNLP 2026）. <https://arxiv.org/abs/2609.09338>
45. J. Lee et al. *OWL: Overcoming Window Length-Dependence in Speculative Decoding for Long-Context Inputs.* arXiv 2025. <https://arxiv.org/abs/2510.07535>
46. M. Hui et al. *P-EAGLE: Parallel-Drafting EAGLE with Scalable Training.* arXiv 2026. <https://arxiv.org/abs/2602.01469>
47. X. Liu et al. *Online Speculative Decoding.* arXiv 2023（发表渠道待核对）. <https://arxiv.org/abs/2310.07177>
48. H. Liu et al. *Not-a-Bandit: Provably No-Regret Drafter Selection in Speculative Decoding for LLMs* (HedgeSpec). ICLR 2026（arXiv 评论）. <https://arxiv.org/abs/2510.20064>

[44]–[48] 的标题与第一作者于 2026-10-13 用 arXiv API 核对。[44][45][46] 中引用的数字取自原文 HTML 正文，不是本仓库实测。


49. R. E. Kalman. *A New Approach to Linear Filtering and Prediction Problems.* Journal of Basic Engineering, 1960. <https://doi.org/10.1115/1.3662552>
50. P. R. Kalata. *The tracking index: A generalized parameter for α-β and α-β-γ target trackers.* 22nd IEEE Conference on Decision and Control, 1983. <https://doi.org/10.1109/CDC.1983.269580>
51. J. Makhoul. *Linear prediction: A tutorial review.* Proceedings of the IEEE, 1975. <https://doi.org/10.1109/PROC.1975.9792>
52. C. C. Holt. *Forecasting seasonals and trends by exponentially weighted moving averages.* International Journal of Forecasting, 2004（1957 年报告的重刊）. <https://doi.org/10.1016/j.ijforecast.2003.09.015>
53. E. S. Gardner Jr. *Exponential smoothing: The state of the art.* Journal of Forecasting, 1985. <https://doi.org/10.1002/for.3980040103>
54. R. J. Hyndman, A. B. Koehler, R. D. Snyder, S. Grose. *A state space framework for automatic forecasting using exponential smoothing methods.* International Journal of Forecasting, 2002. <https://doi.org/10.1016/S0169-2070(01)00110-8>

[49]–[54] 的标题、渠道与年份于 2026-10-13 用 Crossref API 核对。牛顿差分外推的教材出处待补。“阻尼趋势”的原始出处（通常归于 Gardner & McKenzie）未核对，正文只引用了综述 [53]。

55. J. E. Gray, W. J. Murray. *A derivation of an analytic expression for the tracking index for the alpha-beta-gamma filter.* IEEE Transactions on Aerospace and Electronic Systems, 1993. <https://doi.org/10.1109/7.220956>
56. R. K. Mehra. *On the identification of variances and adaptive Kalman filtering.* IEEE Transactions on Automatic Control, 1970. <https://doi.org/10.1109/TAC.1970.1099422>
57. R. K. Mehra. *Approaches to adaptive filtering.* IEEE Transactions on Automatic Control, 1972. <https://doi.org/10.1109/TAC.1972.1100100>
58. A. P. Sage, G. W. Husa. *Algorithms for sequential adaptive estimation of prior statistics.* 1969 IEEE Symposium on Adaptive Processes (8th) Decision and Control, 1969. <https://doi.org/10.1109/SAP.1969.269927>
59. A. H. Mohamed, K. P. Schwarz. *Adaptive Kalman Filtering for INS/GPS.* Journal of Geodesy, 1999. <https://doi.org/10.1007/s001900050236>
60. P. R. Kalata. *The Tracking Index: A Generalized Parameter for α-β and α-β-γ Target Trackers.* IEEE Transactions on Aerospace and Electronic Systems, 1984. <https://doi.org/10.1109/TAES.1984.310438>（[50] 为同名 1983 CDC 会议版；跟踪指数公式以本期刊版为准，原文待核对）

[55]–[60] 的标题、渠道与年份于 2026-10-13 用 Crossref API 核对。说明：

- §5.9 中 Kalata 的 α-β 闭式公式只经二手来源核对；
- Sage–Husa 与协方差匹配的具体更新式按常见引述形式书写，原文细节待核对；
- Joseph 形式与 DARE 收敛条件的教材出处待补。
---

## 附录 A：《研究计划规范》六方面对照

| 方面 | 位置 | 状态 |
|---|---|---|
| 文献调研 | §3、References（60 篇） | 已核对；新颖性待验证 |
| 数据 | §8.1 | 跨域划分待核对 |
| 模型 | §4.1、§8.2–8.3 | tied 已核对；全部待测 |
| 算法 | §4.2、§5.1–5.10、§6、§5.11 | 已形式化；代码未改 |
| 指标 | §4.3、§8.4、§7 | 待实施 |
| 实验设计 | §7 H1–H13、§8.5 E1–E18 | 全部待测 |

## 附录 B：输入空间外推（对照）
状态在输入 embedding 空间维护：
$$\hat v^e\leftarrow\beta\hat v^e+(1-\beta)(e_{\text{new}}-e_{\text{prev}}),\qquad m_j=\hat e+\gamma c_j(\rho)\hat v^e.$$

- 长记忆下 $\hat v^e\approx d_1$，退化为固定偏移（C1）。
- 输入空间的前缀条件版本可以**精确**计算：草稿 token 的 $e(\tilde x_i)$ 在前向前已知，所以可以沿草稿折叠 $\hat e,\hat v^e$。这可以作为“前缀条件”效应在输入空间的对照。
- 仓库中 `extrapolate_ema: true` 部分实现了递推（$\beta'=\beta$）。

**树形扩展**：节点前缀为其祖先路径，命题 1 推广为“节点只注意祖先”。

## 附录 C：仓库已有实测（输入空间，树形 $[14]$，$k=1$）
来源：`docs/history-extrapolation.md`。

条件：Qwen3，fp32，贪心，单 seed；所有格子 exact\_match = 1。**与 v3 输出空间方法无关。**

| 模型 | 切片 | 冻结均值 | 更新均值 | 输入空间一阶外推（选定） |
|---|---|---:|---:|---:|
| 0.6B | first 26 / next 52 / last 52 | 726 / 1550 / 1598 | 701 / 1473 / 1468 | 723 / 1553 / 1575 |
| 1.7B | first 26 / next 52 / last 52 | 778 / 1747 / 1723 | 757 / 1639 / 1626 | 780 / 1709 / 1719 |
| 4B | first 26 / next 52 / last 52 | 680 / 1462 / 1476 | 704 / 1479 / 1525 | 777 / 1686 / 1723 |
| 4B | 全量 480 | 12809 | — | 15009 |

$\beta$ 扫描、$\gamma$ 扫描、$[7,2]$ 树的数字见 v2 附录 C。

