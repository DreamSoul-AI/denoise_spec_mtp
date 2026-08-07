"""Generic Hugging Face causal-LM adapter for ESP-style tree decoding.

ESP (Goel et al., ICML 2026) needs three things from the base model:
  1. access to the input embedding table E (for mask-token synthesis, Eq 4/5);
  2. a forward pass that accepts `inputs_embeds`, explicit `position_ids`, a
     custom 4D tree-attention mask, and a KV cache;
  3. the LM head logits at every block position (verification + probing).

Any RoPE decoder (LLaMA3, Qwen3) exposed through AutoModelForCausalLM works.
`type: tiny_llama` builds a small randomly initialized LlamaForCausalLM so the
whole pipeline can be exercised on CPU without downloading weights.

NOTE: use attn_implementation eager or sdpa. flash_attention_2 cannot consume
arbitrary 4D attention masks, which tree attention requires.
"""

import torch
import torch.nn as nn

from core.tools import get_dtype


class HFCausalLM(nn.Module):

    def __init__(self, name_or_path=None, local_files_only=False, torch_dtype='auto',
                 attn_implementation='eager', tiny_config=None):
        super().__init__()
        if tiny_config is not None:
            from transformers import LlamaConfig, LlamaForCausalLM
            config = LlamaConfig(
                vocab_size=int(tiny_config.get('vocab_size', 256)),
                hidden_size=int(tiny_config.get('hidden_size', 64)),
                intermediate_size=int(tiny_config.get('intermediate_size', 128)),
                num_hidden_layers=int(tiny_config.get('num_layers', 2)),
                num_attention_heads=int(tiny_config.get('num_heads', 4)),
                num_key_value_heads=int(tiny_config.get('num_kv_heads', 2)),
                max_position_embeddings=int(tiny_config.get('max_position_embeddings', 512)),
                attn_implementation=attn_implementation,
            )
            self.hf = LlamaForCausalLM(config)
        else:
            from transformers import AutoModelForCausalLM
            kwargs = dict(
                local_files_only=bool(local_files_only),
                attn_implementation=attn_implementation,
            )
            try:  # transformers >= 4.56 prefers `dtype`; older only knows `torch_dtype`
                self.hf = AutoModelForCausalLM.from_pretrained(
                    name_or_path, dtype=get_dtype(torch_dtype), **kwargs)
            except TypeError:
                self.hf = AutoModelForCausalLM.from_pretrained(
                    name_or_path, torch_dtype=get_dtype(torch_dtype), **kwargs)
        self.hf.eval()
        self.config = self.hf.config
        self.vocab_size = self.config.vocab_size
        self.max_positions = getattr(self.config, 'max_position_embeddings', 4096)

    @property
    def embedding_table(self):
        """Input embedding matrix E in R^{V x d} (Section 3.1)."""
        return self.hf.get_input_embeddings().weight

    @property
    def device(self):
        return self.embedding_table.device

    @property
    def dtype(self):
        return self.embedding_table.dtype

    def embed(self, input_ids):
        """Token ids -> input embeddings e_i = E[x_i]."""
        return self.hf.get_input_embeddings()(input_ids)

    @torch.no_grad()
    def forward(self, inputs_embeds, position_ids, attention_mask_4d=None,
                past_key_values=None, output_hidden_states=False):
        """One forward pass over a (tree-)block of embeddings.

        attention_mask_4d: additive float mask [1, 1, q_len, kv_len] with 0 for
        attend and dtype-min for blocked, or None for the plain causal prefill
        path. Returns the full model output (logits at every block position).
        """
        return self.hf(
            inputs_embeds=inputs_embeds,
            position_ids=position_ids,
            attention_mask=attention_mask_4d,
            past_key_values=past_key_values,
            use_cache=past_key_values is not None,
            output_hidden_states=output_hidden_states,
        )

    def min_mask_value(self):
        return torch.finfo(self.dtype).min


def build_model(cfg):
    model_cfg = cfg.model
    model_type = str(model_cfg.get('type', 'hf_causal')).lower()
    if model_type == 'tiny_llama':
        return HFCausalLM(
            attn_implementation=model_cfg.get('attn_implementation', 'eager'),
            tiny_config=model_cfg.get('tiny', {}),
        )
    if model_type == 'hf_causal':
        return HFCausalLM(
            name_or_path=model_cfg.name_or_path,
            local_files_only=model_cfg.get('local_files_only', False),
            torch_dtype=model_cfg.get('torch_dtype', 'auto'),
            attn_implementation=model_cfg.get('attn_implementation', 'eager'),
        )
    raise ValueError(f'Unsupported model.type: {model_type}')
