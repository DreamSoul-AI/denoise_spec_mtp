"""Write a fixed SpecBench slice: a contiguous window of each category.

Category order is sorted by name. Within a category, questions keep file
order, which is question_id order in the upstream file. The default window
is the first 2 questions (exploration slice). The confirmation window is
the next 4, via --skip 2 --take 4. This is not the paper's 480-prompt
evaluation.
"""

import argparse
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC = os.path.join(ROOT, 'data', 'spec_bench', 'question.jsonl')
DEFAULT_DST = os.path.join(
    ROOT, 'results', 'cursor_20261006_history_audit', 'qwen3_8b_dev',
    'dev_questions.jsonl')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--skip', type=int, default=0)
    parser.add_argument('--take', type=int, default=2)
    parser.add_argument('--dst', default=DEFAULT_DST)
    args = parser.parse_args()
    by_category = {}
    with open(SRC, encoding='utf-8') as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            item = json.loads(line)
            by_category.setdefault(item['category'], []).append(item)
    picked = []
    for category in sorted(by_category):
        window = by_category[category][args.skip:args.skip + args.take]
        if len(window) < args.take:
            raise SystemExit(
                f'{category} has {len(by_category[category])} questions, '
                f'need {args.skip + args.take}')
        picked.extend(window)
    os.makedirs(os.path.dirname(args.dst), exist_ok=True)
    with open(args.dst, 'w', encoding='utf-8') as handle:
        for item in picked:
            handle.write(json.dumps(item, ensure_ascii=False) + '\n')
    print(f'wrote {len(picked)} prompts to {args.dst}')


if __name__ == '__main__':
    main()
