"""Mask-token embedding providers.

ESPMaskProvider implements Section 3.1 of the ESP paper (Goel et al., ICML
2026) including every initialization studied in its ablations:

  - mean_prompt      Eq (4), "Mean (soft init)"; the paper's default.
  - last_k           Table 5 "Last K (hard init)": embeddings of the last k
                     prompt tokens. The paper writes m_i = e_{t-k-i}, which
                     for i=1..k indexes tokens *before* the last k; we follow
                     the stated semantics ("uses the embeddings of the last k
                     prompt tokens") and use m_i = e_{t-k+i}, so m_k = e_t.
  - sample_embedding Table 5 "Sample": m_i ~ N(mu, sigma^2 I) with mu, sigma
                     the mean / standard deviation of the full embedding
                     table (computed per dimension across the V rows).
  - offset_embedding Appendix G.8 out-of-distribution stress test:
                     m_i = mu + offset_scale * sigma  (offset_scale = 5, 10).

and the generation-phase update rule Eq (5):

    m_i[s+1] = m_i[s] + lambda * (e_{t+s} - m_i[s])        for all i,

applied once per generated token (s indexes generation steps), with the
default lambda = 0.1 and the Appendix G.9 ablation values {0.01, 0.5}.
`update: false` freezes the mask at its initialization — an extra ablation
(not in the paper) probing whether the on-the-fly update matters at all.

EMAVelocityMaskProvider is our replacement for Eq (4)+(5) (see
notes/ema_velocity_method.md and lark_transcripts/summary_july31.md):
consecutive prompt-embedding differences are treated as a velocity field
(flow-matching view of AR); an EMA of those differences gives a biased but
variance-reduced gradient estimate at the sequence tail, and mask i
extrapolates i steps along it:

    v_j    = e_{j+1} - e_j
    vhat_j = beta * vhat_{j-1} + (1 - beta) * v_j          (EMA over prefill)
    m_i    = e_last + step_scale * i * vhat                (i = 1..k)

During generation each committed token folds its actual difference into the
EMA: vhat <- beta * vhat + (1 - beta) * (e_new - e_prev). Everything else
(tree, verification, block complexity) is identical to ESP — only Eq (4)/(5)
are swapped, per the July discussion ("只是换它这个 4 和 5 Equation").
"""

import torch


class ESPMaskProvider:
    """Mask tokens per ESP Section 3.1 (Eq 4 init variants + Eq 5 update)."""

    def __init__(self, num_masks, embedding_table, init='mean_prompt', lam=0.1,
                 update=True, offset_scale=5.0, generator=None):
        self.num_masks = int(num_masks)
        self.embedding_table = embedding_table
        self.init = str(init).lower()
        self.lam = float(lam)
        self.update = bool(update)
        self.offset_scale = float(offset_scale)
        self.generator = generator
        self._masks = None  # [k, d]

    def init_from_prompt(self, prompt_embeds):
        """prompt_embeds: [t, d] input embeddings of the full prompt."""
        k, d = self.num_masks, prompt_embeds.size(-1)
        if self.init == 'mean_prompt':
            # Eq (4): m_i = (1/t) sum_j e_j, identical for all i.
            mean = prompt_embeds.mean(dim=0, keepdim=True)
            self._masks = mean.expand(k, d).clone()
        elif self.init == 'last_k':
            if prompt_embeds.size(0) < k:
                raise ValueError(f'last_k init needs a prompt with >= {k} tokens')
            self._masks = prompt_embeds[-k:].clone()
        elif self.init == 'sample_embedding':
            mu = self.embedding_table.mean(dim=0)
            sigma = self.embedding_table.std(dim=0)
            noise = torch.randn(
                (k, d), generator=self.generator,
                device=mu.device, dtype=torch.float32,
            ).to(mu.dtype)
            self._masks = mu.unsqueeze(0) + noise * sigma.unsqueeze(0)
        elif self.init == 'offset_embedding':
            # G.8: mu + c * sigma pushes the mask outside the table distribution.
            mu = self.embedding_table.mean(dim=0)
            sigma = self.embedding_table.std(dim=0)
            mask = mu + self.offset_scale * sigma
            self._masks = mask.unsqueeze(0).expand(k, d).clone()
        else:
            raise ValueError(f'Unsupported mask.init: {self.init}')

    def masks(self):
        """Current mask embeddings [k, d]; shared across all tree positions."""
        return self._masks

    def on_token_committed(self, new_embed, prev_embed):
        """Eq (5) with e_{t+s} = the newly generated token's embedding."""
        if not self.update:
            return
        self._masks = self._masks + self.lam * (new_embed.unsqueeze(0) - self._masks)


class EMAVelocityMaskProvider:
    """Ours: EMA-of-differences velocity extrapolation replacing Eq (4)/(5)."""

    def __init__(self, num_masks, embedding_table, beta=0.9, step_scale=1.0,
                 update=True, generator=None):
        self.num_masks = int(num_masks)
        self.embedding_table = embedding_table  # unused; kept for a uniform ctor
        self.beta = float(beta)
        self.step_scale = float(step_scale)
        self.update = bool(update)
        self.generator = generator
        self._velocity = None  # vhat, [d]
        self._anchor = None    # e of the last committed token, [d]

    def init_from_prompt(self, prompt_embeds):
        if prompt_embeds.size(0) < 2:
            raise ValueError('EMA velocity needs a prompt with >= 2 tokens')
        diffs = prompt_embeds[1:] - prompt_embeds[:-1]  # v_j = e_{j+1} - e_j
        vhat = diffs[0].clone()
        for j in range(1, diffs.size(0)):
            vhat = self.beta * vhat + (1.0 - self.beta) * diffs[j]
        self._velocity = vhat
        self._anchor = prompt_embeds[-1].clone()

    def masks(self):
        # m_i = e_last + step_scale * i * vhat. Extrapolating i steps along a
        # constant velocity: folding the extrapolated difference back into the
        # EMA is a fixed point (beta*v + (1-beta)*v = v), so the linear form
        # is exact for the within-block masks.
        steps = torch.arange(
            1, self.num_masks + 1,
            device=self._anchor.device, dtype=self._anchor.dtype,
        ).unsqueeze(1)
        return self._anchor.unsqueeze(0) + self.step_scale * steps * self._velocity.unsqueeze(0)

    def on_token_committed(self, new_embed, prev_embed):
        if self.update:
            diff = new_embed - prev_embed
            self._velocity = self.beta * self._velocity + (1.0 - self.beta) * diff
        # The anchor always tracks the last committed token, even when the
        # velocity EMA is frozen (update: false ablation).
        self._anchor = new_embed.clone()


def build_mask_provider(spec_cfg, embedding_table, generator=None):
    method = str(spec_cfg.get('method', 'esp')).lower()
    num_masks = int(spec_cfg.get('num_masks', 1))
    if method == 'esp':
        mask_cfg = spec_cfg.get('mask', {})
        return ESPMaskProvider(
            num_masks=num_masks,
            embedding_table=embedding_table,
            init=mask_cfg.get('init', 'mean_prompt'),
            lam=mask_cfg.get('lam', 0.1),
            update=mask_cfg.get('update', True),
            offset_scale=mask_cfg.get('offset_scale', 5.0),
            generator=generator,
        )
    if method == 'ema_velocity':
        ema_cfg = spec_cfg.get('ema', {})
        return EMAVelocityMaskProvider(
            num_masks=num_masks,
            embedding_table=embedding_table,
            beta=ema_cfg.get('beta', 0.9),
            step_scale=ema_cfg.get('step_scale', 1.0),
            update=ema_cfg.get('update', True),
            generator=generator,
        )
    raise ValueError(f'Unsupported spec.method: {method}')
