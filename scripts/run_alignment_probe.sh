#!/usr/bin/env bash
# Figure 2: mask/true-token hidden-state cosine similarity across layers on
# Dolly creative-writing (needs `datasets`; see download_data.sh --dolly).
set -euo pipefail
cd "$(dirname "$0")/.."

python src/main.py --cfg_file configs/hf/llama3_2_3b/run_0/alignment_probe.yaml
