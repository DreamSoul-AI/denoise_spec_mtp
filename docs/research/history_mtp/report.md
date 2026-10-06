# Experiment report

Date: 2026-10-06. Model: Qwen3-4B, float32. Tree: `[14]`, one mask slot, block complexity 30. Decoding: greedy, temperature 0, at most 100 new tokens, seed 123, Qwen3 thinking off. Branch: `feature/research-ema-history-audit`. Commands and paths: [experiment_log_20261006.md](experiment_log_20261006.md). Factor rules: [study_plan.md](study_plan.md).

Every float32 cell matches ordinary generation token for token. Within one table, every row commits the same tokens. The number is how many draft tokens were kept.

Qwen3-8B in bf16 did not match token for token, so it is not in these tables.

## Formula

Order 0 is the level. It starts as the mean of the prompt embeddings and then moves toward each committed token:

$$m^{(0)} \leftarrow (1-\lambda)\, m^{(0)} + \lambda\, e_{\mathrm{new}}.$$

Gamma is the first-order term. \(\hat v\) is an average of the steps between embeddings:

$$\hat v \leftarrow \beta\, \hat v + (1-\beta)\, (e_{\mathrm{new}} - e_{\mathrm{prev}}).$$

\(i\) is the step. Slot \(i\) is \(i\) steps ahead: slot 1 takes one step, slot 2 takes two. This tree has one slot, so every row uses \(i=1\).

$$m_i = m^{(0)} + \gamma\, i\, \hat v.$$

\(\gamma=0\) removes gamma. \(\gamma=1\) is the gamma in the tables. No other \(\gamma\) was run. With \(i=1\) and \(\gamma=1\), the mask is \(m^{(0)}+\hat v\).

The ESP formula has no gamma. Its \(i\) only picks the slot, and every slot shares one vector.

The earlier code put gamma on the last token instead of on \(m^{(0)}\):

$$m_i = e_{\mathrm{last}} + \gamma\, i\, \hat v.$$

There is no \(1-\beta^{s}\) correction. At \(\beta=0.9999\), \(\hat v\) stays near the first difference in the prompt.

`off` in a β or λ cell means that term is not in the mask. It is not the number 0. β=0 would still add gamma, using only the latest embedding step, and that setting was not run.

## Prompt groups

SpecBench, file order within each category. The three groups share no question.

| **Group** | **Which questions** | **Prompts** |
| --- | --- | ---: |
| First | first 2 in each category | 26 |
| Next | the next 4 | 52 |
| Last | the 4 after those | 52 |

Two baselines. Both have γ=0.

- **Frozen prompt mean.** λ=0. The mask is the average of the prompt embeddings and never moves.
- **Last token.** λ is off. The mask is the latest committed token.

## First 26 and the next 52

| **Setting** | **β** | **λ** | **γ** | **26 accepts** | **Next 52 accepts** |
| --- | ---: | ---: | ---: | ---: | ---: |
| Frozen prompt mean | off | 0 | 0 | 680 | 1462 |
| Last token | off | off | 0 | 609 | 1323 |
| Updating mean | off | 0.1 | 0 | 704 | 1479 |
| Gamma on the last token | 0.9 | off | 1 | 609 | 1319 |
| Gamma, direction only, on the last token | 0.9 | off | 1 | 600 | 1310 |

## First 26: gamma, varying β

λ=0.1. Gamma is added to the updating mean. The first three rows are the references, with γ=0.

| **Setting** | **β** | **λ** | **γ** | **Accepts** |
| --- | ---: | ---: | ---: | ---: |
| Frozen prompt mean | off | 0 | 0 | 680 |
| Last token | off | off | 0 | 609 |
| Updating mean | off | 0.1 | 0 | 704 |
| Mean plus gamma | 0.5 | 0.1 | 1 | 620 |
| Mean plus gamma | 0.9 | 0.1 | 1 | 680 |
| Mean plus gamma | 0.99 | 0.1 | 1 | 732 |
| Mean plus gamma | 0.999 | 0.1 | 1 | 770 |
| Mean plus gamma | 0.9999 | 0.1 | 1 | 777 |

## First 26: gamma at β=0.5, varying λ

| **Setting** | **β** | **λ** | **γ** | **Accepts** |
| --- | ---: | ---: | ---: | ---: |
| Frozen prompt mean | off | 0 | 0 | 680 |
| Last token | off | off | 0 | 609 |
| Updating mean | off | 0.1 | 0 | 704 |
| Mean plus gamma | 0.5 | 0.5 | 1 | 610 |
| Mean plus gamma | 0.5 | 0.1 | 1 | 620 |
| Mean plus gamma | 0.5 | 0.01 | 1 | 629 |
| Mean plus gamma | 0.5 | 0.001 | 1 | 622 |
| Mean plus gamma | 0.5 | 0.0001 | 1 | 621 |

## First 26: gamma at β=0.9999, varying λ

| **Setting** | **β** | **λ** | **γ** | **Accepts** |
| --- | ---: | ---: | ---: | ---: |
| Frozen prompt mean | off | 0 | 0 | 680 |
| Last token | off | off | 0 | 609 |
| Updating mean | off | 0.1 | 0 | 704 |
| Mean plus gamma | 0.9999 | 0.5 | 1 | 750 |
| Mean plus gamma | 0.9999 | 0.1 | 1 | 777 |
| Mean plus gamma | 0.9999 | 0.01 | 1 | 776 |
| Mean plus gamma | 0.9999 | 0.001 | 1 | 777 |
| Mean plus gamma | 0.9999 | 0.0001 | 1 | 777 |

## Last 52

The two baselines were not run on this group.

| **Setting** | **β** | **λ** | **γ** | **Accepts** |
| --- | ---: | ---: | ---: | ---: |
| Updating mean | off | 0.1 | 0 | 1525 |
| Mean plus gamma | 0.9999 | 0.1 | 1 | 1723 |

## Wrap-up

1. The frozen prompt mean, γ=0 and λ=0, accepts more drafts than the last token: 680 against 609 on 26 prompts, and 1462 against 1323 on the next 52.
2. Gamma on the last token, β=0.9 and γ=1, stays on the last-token count: 609, then 1319.
3. Gamma on the updating mean depends on β. At β=0.5 it is below the frozen mean (620 against 680). At β=0.9999 it is above it (777 against 680). On the last 52 prompts that pair is above the updating mean, 1723 against 1525. The frozen mean was not run on those 52.
4. At β=0.9999, λ from 0.1 to 0.0001 stays at 776–777. λ=0.5 lowers it to 750, still above the frozen mean. λ does not lift β=0.5 up to the frozen mean.

Not claimed: the 480-prompt setting, a second model, a deeper tree, a debiased \(\hat v\), or Momentum Guidance. β=0 was not run. γ other than 0 and 1 was not run. \(i\) other than 1 was not run.
