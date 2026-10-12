"""Prompt text -> token ids [1, L] with the model's tokenizer."""


def render(tokenizer, text, apply_template=True, template_kwargs=None):
    if apply_template:
        encoded = tokenizer.apply_chat_template(
            [{'role': 'user', 'content': text}],
            add_generation_prompt=True, return_tensors='pt',
            **dict(template_kwargs or {}))
        # transformers 5 returns a BatchEncoding; earlier versions a Tensor.
        return encoded['input_ids'] if hasattr(encoded, 'keys') else encoded
    return tokenizer(text, return_tensors='pt').input_ids
