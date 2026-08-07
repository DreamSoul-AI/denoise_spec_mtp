#!/usr/bin/env bash
# Prepare all evaluation data. Run once on the GPU server (needs network).
#
#   bash scripts/download_data.sh            # SpecBench questions only
#   bash scripts/download_data.sh --models   # + pre-download model weights
#   bash scripts/download_data.sh --dolly    # + Dolly (Fig. 2 alignment probe)
set -euo pipefail
cd "$(dirname "$0")/.."

# --- SpecBench (Xia et al., 2024): 480 prompts across writing, roleplay,
# reasoning, math, coding, extraction, stem, humanities, translation,
# summarization, qa, math_reasoning (GSM8K) and rag. -----------------------
mkdir -p data/spec_bench
if [ ! -f data/spec_bench/question.jsonl ]; then
  curl -fL --retry 3 -o data/spec_bench/question.jsonl \
    https://raw.githubusercontent.com/hemingkx/Spec-Bench/main/data/spec_bench/question.jsonl
  echo "SpecBench: $(wc -l < data/spec_bench/question.jsonl) questions"
else
  echo "SpecBench already present."
fi

for arg in "$@"; do
  case "$arg" in
    --models)
      # Paper models (Section 4). LLaMA weights need HF access approval +
      # `hf auth login` (or `huggingface-cli login` on older hub versions).
      for m in meta-llama/Llama-3.2-3B-Instruct \
               meta-llama/Llama-3.1-8B-Instruct \
               Qwen/Qwen3-8B \
               Qwen/Qwen3-32B; do
        hf download "$m" || huggingface-cli download "$m"
      done
      ;;
    --dolly)
      # Dolly creative-writing samples for the Figure 2 alignment probe.
      python -c "from datasets import load_dataset; \
                 load_dataset('databricks/databricks-dolly-15k', split='train')"
      ;;
    *)
      echo "Unknown flag: $arg" >&2; exit 1 ;;
  esac
done
echo "Data ready."
