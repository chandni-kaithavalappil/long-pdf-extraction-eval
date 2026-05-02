#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m pip install -q -r pipeline/requirements.txt
python3 pipeline/hybrid_retrieval_flat_chunks/run.py \
  --config configs/budget_2026_27.yaml \
  --run-name hybrid_retrieval_flat_chunks_2026
