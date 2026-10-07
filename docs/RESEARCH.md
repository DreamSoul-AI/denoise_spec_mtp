# History extrapolation

Qwen3, float32, tree `[14]`, one mask slot, block complexity 30. Greedy, temperature 0, at most 100 new tokens, seed 123, Qwen3 thinking off. Branch `feature/research-ema-history-audit`.

Every float32 cell matches ordinary generation token for token. Within one model and one prompt group, every row commits the same tokens. The number in each table is how many draft tokens were kept.

Qwen3-8B in bf16 did not match token for token, so it is not in these tables.

The formulas are in [ARCHITECTURE.md](ARCHITECTURE.md). Short form used below:

```text
m_i = m0 + γ · i · vhat
```

`m0` starts as the mean of the prompt input embeddings and then moves with `λ`. `vhat` is the EMA of input-embedding steps, decay `β`. This tree has one slot, so `i = 1`. Gamma on the last token is the other origin: `m_i = e_last + γ · i · vhat`.

`off` means that term is not in the mask. It is not the number 0. `β = 0` was not run. `γ` other than 0 and 1 was not run.

## Prompt groups

SpecBench, file order within each category. The three groups share no question. `β` and `λ` were chosen on the first 26 only.

| **Group** | **Which questions** | **Prompts** |
| --- | --- | ---: |
| First | first 2 in each category | 26 |
| Next | the next 4 | 52 |
| Last | the 4 after those | 52 |

## Qwen3-4B

Recorded 2026-10-06, except the last-52 frozen mean and last token, which were run on 2026-10-08. Those two commit the same 4600 tokens as the other last-52 rows.

### First 26 and the next 52

| **Setting** | **β** | **λ** | **γ** | **26 accepts** | **Next 52 accepts** |
| --- | ---: | ---: | ---: | ---: | ---: |
| Frozen prompt mean | off | 0 | 0 | 680 | 1462 |
| Last token | off | off | 0 | 609 | 1323 |
| Updating mean | off | 0.1 | 0 | 704 | 1479 |
| Gamma on the last token | 0.9 | off | 1 | 609 | 1319 |
| Gamma, direction only, on the last token | 0.9 | off | 1 | 600 | 1310 |

The next 52 has no long-memory gamma cell.

### First 26: gamma on the updating mean, varying β

`λ = 0.1`.

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

### First 26: gamma at β = 0.5, varying λ

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

### First 26: gamma at β = 0.9999, varying λ

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

### Last 52

| **Setting** | **β** | **λ** | **γ** | **Accepts** |
| --- | ---: | ---: | ---: | ---: |
| Frozen prompt mean | off | 0 | 0 | 1476 |
| Last token | off | off | 0 | 1358 |
| Updating mean | off | 0.1 | 0 | 1525 |
| Mean plus gamma | 0.9999 | 0.1 | 1 | 1723 |

## Qwen3-0.6B and Qwen3-1.7B

Recorded 2026-10-07. Same tree, decoding, and slices. Committed tokens: 0.6B is 1937, 4259, and 4300 on the three groups. 1.7B is 2204, 4804, and 4743.

The pair taken to the 52-prompt groups is the one with the most accepts on the 26. 0.6B uses `β = 0.9999`, `λ = 0.1`. 1.7B uses `β = 0.999`, `λ = 0.1` (780 against 775 at `β = 0.9999`).

### Qwen3-0.6B baselines

| **Setting** | **β** | **λ** | **γ** | **26 accepts** | **Next 52 accepts** | **Last 52 accepts** |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Frozen prompt mean | off | 0 | 0 | 726 | 1550 | 1598 |
| Last token | off | off | 0 | 548 | 1176 | 1165 |
| Updating mean | off | 0.1 | 0 | 701 | 1473 | 1468 |
| Gamma on the last token | 0.9 | off | 1 | 548 | 1178 | 1166 |
| Gamma, direction only, on the last token | 0.9 | off | 1 | 543 | 1160 | 1154 |
| Mean plus gamma (picked) | 0.9999 | 0.1 | 1 | 723 | 1553 | 1575 |

### Qwen3-0.6B, first 26, varying β

`λ = 0.1`. Gamma is on the updating mean.

| **Setting** | **β** | **λ** | **γ** | **Accepts** |
| --- | ---: | ---: | ---: | ---: |
| Frozen prompt mean | off | 0 | 0 | 726 |
| Last token | off | off | 0 | 548 |
| Updating mean | off | 0.1 | 0 | 701 |
| Mean plus gamma | 0.5 | 0.1 | 1 | 555 |
| Mean plus gamma | 0.9 | 0.1 | 1 | 650 |
| Mean plus gamma | 0.99 | 0.1 | 1 | 700 |
| Mean plus gamma | 0.999 | 0.1 | 1 | 718 |
| Mean plus gamma | 0.9999 | 0.1 | 1 | 723 |

### Qwen3-0.6B, first 26, varying λ

| **Setting** | **β** | **λ** | **γ** | **Accepts** |
| --- | ---: | ---: | ---: | ---: |
| Mean plus gamma | 0.5 | 0.5 | 1 | 549 |
| Mean plus gamma | 0.5 | 0.1 | 1 | 555 |
| Mean plus gamma | 0.5 | 0.01 | 1 | 560 |
| Mean plus gamma | 0.5 | 0.001 | 1 | 564 |
| Mean plus gamma | 0.5 | 0.0001 | 1 | 564 |
| Mean plus gamma | 0.9999 | 0.5 | 1 | 705 |
| Mean plus gamma | 0.9999 | 0.1 | 1 | 723 |
| Mean plus gamma | 0.9999 | 0.01 | 1 | 716 |
| Mean plus gamma | 0.9999 | 0.001 | 1 | 709 |
| Mean plus gamma | 0.9999 | 0.0001 | 1 | 708 |

### Qwen3-1.7B baselines

| **Setting** | **β** | **λ** | **γ** | **26 accepts** | **Next 52 accepts** | **Last 52 accepts** |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Frozen prompt mean | off | 0 | 0 | 778 | 1747 | 1723 |
| Last token | off | off | 0 | 573 | 1295 | 1356 |
| Updating mean | off | 0.1 | 0 | 757 | 1639 | 1626 |
| Gamma on the last token | 0.9 | off | 1 | 573 | 1290 | 1354 |
| Gamma, direction only, on the last token | 0.9 | off | 1 | 574 | 1260 | 1330 |
| Mean plus gamma (picked) | 0.999 | 0.1 | 1 | 780 | 1709 | 1719 |

### Qwen3-1.7B, first 26, varying β

`λ = 0.1`. Gamma is on the updating mean.

| **Setting** | **β** | **λ** | **γ** | **Accepts** |
| --- | ---: | ---: | ---: | ---: |
| Frozen prompt mean | off | 0 | 0 | 778 |
| Last token | off | off | 0 | 573 |
| Updating mean | off | 0.1 | 0 | 757 |
| Mean plus gamma | 0.5 | 0.1 | 1 | 585 |
| Mean plus gamma | 0.9 | 0.1 | 1 | 706 |
| Mean plus gamma | 0.99 | 0.1 | 1 | 773 |
| Mean plus gamma | 0.999 | 0.1 | 1 | 780 |
| Mean plus gamma | 0.9999 | 0.1 | 1 | 775 |

### Qwen3-1.7B, first 26, varying λ

| **Setting** | **β** | **λ** | **γ** | **Accepts** |
| --- | ---: | ---: | ---: | ---: |
| Mean plus gamma | 0.5 | 0.5 | 1 | 574 |
| Mean plus gamma | 0.5 | 0.1 | 1 | 585 |
| Mean plus gamma | 0.5 | 0.01 | 1 | 600 |
| Mean plus gamma | 0.5 | 0.001 | 1 | 600 |
| Mean plus gamma | 0.5 | 0.0001 | 1 | 598 |
| Mean plus gamma | 0.999 | 0.5 | 1 | 746 |
| Mean plus gamma | 0.999 | 0.1 | 1 | 780 |
| Mean plus gamma | 0.999 | 0.01 | 1 | 770 |
| Mean plus gamma | 0.999 | 0.001 | 1 | 770 |
| Mean plus gamma | 0.999 | 0.0001 | 1 | 770 |

## Picked pair against the frozen prompt mean

The 52-prompt columns were not used to choose `β` or `λ`.

| **Model** | **Group** | **Frozen prompt mean** | **Updating mean** | **Mean plus gamma** |
| --- | --- | ---: | ---: | ---: |
| 0.6B | First 26 | 726 | 701 | 723 |
| 0.6B | Next 52 | 1550 | 1473 | 1553 |
| 0.6B | Last 52 | 1598 | 1468 | 1575 |
| 1.7B | First 26 | 778 | 757 | 780 |
| 1.7B | Next 52 | 1747 | 1639 | 1709 |
| 1.7B | Last 52 | 1723 | 1626 | 1719 |
| 4B | First 26 | 680 | 704 | 777 |
| 4B | Last 52 | 1476 | 1525 | 1723 |

## Wrap-up

1. The frozen prompt mean accepts more drafts than the last token on every model and every group that has both rows.
2. Gamma on the last token, `β = 0.9` and `γ = 1`, stays on the last-token count. The direction-only variant does not rise above it.
3. Gamma on the updating mean depends on `β`. `β = 0.5` accepts fewer drafts than the updating mean. `β = 0.999` or `0.9999` accepts more. `λ` does not reverse that.
4. On 4B, long-memory gamma also beats the frozen mean: 777 against 680 on 26 prompts, and 1723 against 1476 on the last 52. On 0.6B and 1.7B the picked pair only returns to the frozen mean.
5. The updating mean versus the frozen mean has the opposite sign on 4B (updating is a little higher) and on the two smaller models (frozen is higher).

## Not run

The 480-prompt set, a deeper tree, a debiased `vhat`, Momentum Guidance, `β = 0`, any `γ` other than 0 and 1, any `i` other than 1, and long-memory gamma on the 4B next-52 group.

## Local files

Result directories are gitignored.

- 4B last-52 frozen mean and last token: `results/qwen3_4b_last52_20261008/`
- 0.6B and 1.7B: `results/sweep_20261007/`, plus the first four 26-prompt cells in `results/try_qwen3_0_6b_20261007/` and `results/try_qwen3_1_7b_20261007/`
- Slices: `results/slices_20261007/`, from `scripts/make_dev_slice.py` with skip/take `0/2`, `2/4`, and `6/4`

On this Windows machine a run needs `PYTHONUTF8=1` so the slice is read as UTF-8. A cell is `src/main.py` with `configs/hf/qwen3_8b/run_0/ema_bc30.yaml` or `esp_bc30.yaml`, `model.torch_dtype=float32`, and `eval.num_eval_prompts` set to the group size. Frozen mean: ESP with `spec.mask.update=false`. Last token: EMA with `spec.ema.step_scale=0`. Mean plus gamma: EMA with `spec.ema.level=order0`.
