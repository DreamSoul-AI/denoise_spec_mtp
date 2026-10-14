本Study禁用解码计时。TokensPerS/Speedup等0值是兼容占位，不能解读为性能测量；调用数见STUDY_REPORT。Run wall/estimated为流程调度记录，不比较速度。

# Numbers: output_space_4b_input_control

Generated from `process.json`. The conclusion stays in `STUDY_REPORT.md`.

## Experiments

| factors | metric | mean | std | min | max | n |
|---|---|---:|---:|---:|---:|---:|
| data.config={'path': 'datasets/spec_bench/question.jsonl', 'skip_per_category': 0, 'take_per_category': 2, 'apply_chat_template': True, 'chat_template_kwargs': {'enable_thinking': False}, 'max_prompt_len': 2048} | test_accepted | 240.0000 | 0.0000 | 240.0000 | 240.0000 | 1 |
| data.config={'path': 'datasets/spec_bench/question.jsonl', 'skip_per_category': 0, 'take_per_category': 2, 'apply_chat_template': True, 'chat_template_kwargs': {'enable_thinking': False}, 'max_prompt_len': 2048} | test_committed | 2165.0000 | 0.0000 | 2165.0000 | 2165.0000 | 1 |
| data.config={'path': 'datasets/spec_bench/question.jsonl', 'skip_per_category': 0, 'take_per_category': 2, 'apply_chat_template': True, 'chat_template_kwargs': {'enable_thinking': False}, 'max_prompt_len': 2048} | test_decodecalls | 1926.0000 | 0.0000 | 1926.0000 | 1926.0000 | 1 |
| data.config={'path': 'datasets/spec_bench/question.jsonl', 'skip_per_category': 0, 'take_per_category': 2, 'apply_chat_template': True, 'chat_template_kwargs': {'enable_thinking': False}, 'max_prompt_len': 2048} | test_exactmatchrate | 1.0000 | 0.0000 | 1.0000 | 1.0000 | 1 |
| data.config={'path': 'datasets/spec_bench/question.jsonl', 'skip_per_category': 0, 'take_per_category': 2, 'apply_chat_template': True, 'chat_template_kwargs': {'enable_thinking': False}, 'max_prompt_len': 2048} | test_tau | 1.1241 | 0.0000 | 1.1241 | 1.1241 | 1 |
| data.config={'path': 'datasets/spec_bench/question.jsonl', 'skip_per_category': 2, 'take_per_category': 2, 'apply_chat_template': True, 'chat_template_kwargs': {'enable_thinking': False}, 'max_prompt_len': 2048, 'categories': ['summarization', 'translation']} | test_accepted | 39.0000 | 0.0000 | 39.0000 | 39.0000 | 1 |
| data.config={'path': 'datasets/spec_bench/question.jsonl', 'skip_per_category': 2, 'take_per_category': 2, 'apply_chat_template': True, 'chat_template_kwargs': {'enable_thinking': False}, 'max_prompt_len': 2048, 'categories': ['summarization', 'translation']} | test_committed | 236.0000 | 0.0000 | 236.0000 | 236.0000 | 1 |
| data.config={'path': 'datasets/spec_bench/question.jsonl', 'skip_per_category': 2, 'take_per_category': 2, 'apply_chat_template': True, 'chat_template_kwargs': {'enable_thinking': False}, 'max_prompt_len': 2048, 'categories': ['summarization', 'translation']} | test_decodecalls | 198.0000 | 0.0000 | 198.0000 | 198.0000 | 1 |
| data.config={'path': 'datasets/spec_bench/question.jsonl', 'skip_per_category': 2, 'take_per_category': 2, 'apply_chat_template': True, 'chat_template_kwargs': {'enable_thinking': False}, 'max_prompt_len': 2048, 'categories': ['summarization', 'translation']} | test_exactmatchrate | 1.0000 | 0.0000 | 1.0000 | 1.0000 | 1 |
| data.config={'path': 'datasets/spec_bench/question.jsonl', 'skip_per_category': 2, 'take_per_category': 2, 'apply_chat_template': True, 'chat_template_kwargs': {'enable_thinking': False}, 'max_prompt_len': 2048, 'categories': ['summarization', 'translation']} | test_tau | 1.1919 | 0.0000 | 1.1919 | 1.1919 | 1 |

## Runs

| factors | seed | id | metrics | log |
|---|---:|---|---|---|
| data.config={'path': 'datasets/spec_bench/question.jsonl', 'skip_per_category': 0, 'take_per_category': 2, 'apply_chat_template': True, 'chat_template_kwargs': {'enable_thinking': False}, 'max_prompt_len': 2048} | 123 | `f87c6a0443b7502f` | test_accepted=240.0000, test_committed=2165.0000, test_decodecalls=1926.0000, test_exactmatchrate=1.0000, test_tau=1.1241 | run.log (machine-local: `runs/f87c6a0443b7502f/assets/logs/run.log`; excluded from clone) |
| data.config={'path': 'datasets/spec_bench/question.jsonl', 'skip_per_category': 2, 'take_per_category': 2, 'apply_chat_template': True, 'chat_template_kwargs': {'enable_thinking': False}, 'max_prompt_len': 2048, 'categories': ['summarization', 'translation']} | 123 | `b3cd39a46d8a82a6` | test_accepted=39.0000, test_committed=236.0000, test_decodecalls=198.0000, test_exactmatchrate=1.0000, test_tau=1.1919 | run.log (machine-local: `runs/b3cd39a46d8a82a6/assets/logs/run.log`; excluded from clone) |
