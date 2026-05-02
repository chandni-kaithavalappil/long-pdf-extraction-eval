#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m pip install -q -r requirements.txt
python3 parse.py
python3 chunk.py
python3 index.py
python3 eval.py
