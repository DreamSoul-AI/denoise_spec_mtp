"""Tied final-hidden depth predictions for order0/order1 output masks."""

from typing import Any
import torch


class OutputHiddenMaskProvider:
    def __init__(self, num_masks, embedding_table, order=1, beta=.9, beta_prime=.99):
        self.num_masks = int(num_masks)
        self.order = int(order)
        self.beta, self.beta_prime = float(beta), float(beta_prime)
        if self.order not in (0, 1) or not 0 <= self.beta <= self.beta_prime <= 1:
            raise ValueError('output masks require order0/1 and 0 <= beta <= beta_prime <= 1')
        self.scale = embedding_table.detach().float().norm(dim=-1).mean()
        self.anchor: Any = None
        self.velocity: Any = None

    def init_from_prompt(self, prompt_embeds):
        self.prefill_masks = prompt_embeds.mean(dim=0).expand(self.num_masks, -1).clone()

    def masks(self):
        return self.prefill_masks

    def observe_committed(self, hidden):
        y = hidden.detach().float()
        if not torch.isfinite(y).all():
            raise ValueError('nonfinite output hidden observation')
        if self.anchor is None:
            self.velocity = torch.zeros_like(y)
        elif self.order:
            self.velocity = self.beta * self.velocity + (1 - self.beta) * (y - self.anchor)
        self.anchor = y.clone()

    def init_hidden(self, prompt_hidden):
        for y in prompt_hidden:
            self.observe_committed(y)

    def masks_per_owner(self, proxy_hiddens):
        """Predict depths 0..k; the decoder shares each depth across tree siblings."""
        # Proxies are at root..penultimate draft positions. The last owner
        # has no observation; simulate only, without mutating committed state.
        if proxy_hiddens.shape != (self.num_masks, self.anchor.numel()):
            raise ValueError('output proxy shape mismatch')
        anchor, velocity = self.anchor.clone(), self.velocity.clone()
        owners = []
        for owner in range(self.num_masks + 1):
            if owner < self.num_masks:
                y = proxy_hiddens[owner].detach().float()
                if self.order:
                    velocity = self.beta_prime * velocity + (1 - self.beta_prime) * (y - anchor)
                anchor = y
            else:
                anchor = anchor + velocity
            slots = torch.stack([anchor + slot * velocity for slot in range(self.num_masks)])
            norms = slots.norm(dim=-1, keepdim=True)
            if not torch.isfinite(slots).all() or not torch.isfinite(self.scale) or self.scale <= 0 or (norms <= 0).any():
                raise ValueError('output mask mapping requires finite nonzero norms')
            owners.append(self.scale * slots / norms)
        return torch.stack(owners)
