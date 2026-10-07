#!/usr/bin/env bash
# CPU smoke: RPipe study smoke_tiny_llama (exact_match_rate must be 1.0).
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONUTF8=1
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)/src"
export MPLBACKEND=Agg
python -m rpipe run studies/smoke_tiny_llama
