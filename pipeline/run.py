#!/usr/bin/env python3
"""End-to-end agentic pipeline runner.

Supports:
  python pipeline/run.py --config configs/budget_2025_26.yaml --run-name agentic_2025

The YAML parser is intentionally tiny: key: value only. Paths are resolved
relative to the repository root, so the command works from repo root.
"""
import argparse
from pathlib import Path

import config
from util import ensure_dirs, write_json
from parse import parse_pdf
from chunk import build_chunks
from index import build as build_index
import eval as eval_module

ROOT = Path(__file__).resolve().parents[1]
PIPELINE_DIR = Path(__file__).resolve().parent

def parse_simple_yaml(path):
    data = {}
    for raw in Path(path).read_text(encoding='utf-8').splitlines():
        line = raw.split('#', 1)[0].strip()
        if not line or ':' not in line:
            continue
        k, v = line.split(':', 1)
        data[k.strip()] = v.strip().strip('"').strip("'")
    return data

def resolve_path(value, base=ROOT):
    p = Path(value)
    return p if p.is_absolute() else (base / p)

def apply_runtime(config_path=None, run_name=None):
    cfg = parse_simple_yaml(resolve_path(config_path)) if config_path else {}
    config.PDF_PATH = resolve_path(cfg.get('pdf_path', str(config.PDF_PATH)))
    config.EVAL_PATH = resolve_path(cfg.get('eval_path', str(config.EVAL_PATH)))
    config.OUTPUT_DIR = resolve_path(cfg.get('output_dir', str(config.OUTPUT_DIR)))
    config.DATA_DIR = PIPELINE_DIR / 'data'
    config.RUN_NAME = run_name or cfg.get('run_name') or config.RUN_NAME
    if cfg.get('openai_model'):
        config.OPENAI_MODEL = cfg['openai_model']

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', help='YAML config with pdf_path/eval_path/output_dir')
    ap.add_argument('--run-name', help='Output run name')
    args = ap.parse_args()

    apply_runtime(args.config, args.run_name)
    ensure_dirs()

    if not Path(config.PDF_PATH).exists():
        raise SystemExit(f'PDF not found: {config.PDF_PATH}')
    if not Path(config.EVAL_PATH).exists():
        raise SystemExit(f'Eval file not found: {config.EVAL_PATH}')

    manifest, pages = parse_pdf(Path(config.PDF_PATH))
    write_json(config.DATA_DIR / 'manifest.json', manifest)
    write_json(config.DATA_DIR / 'parsed_pages.json', pages)
    print(f"parsed {manifest['pages']} pages from {config.PDF_PATH} -> {config.DATA_DIR / 'parsed_pages.json'}")

    chunks = build_chunks(pages)
    write_json(config.DATA_DIR / 'chunks.json', chunks)
    print(f"built {len(chunks)} chunks -> {config.DATA_DIR / 'chunks.json'}")

    n, backend = build_index()
    print(f"indexed {n} chunks with BM25 + {backend} -> {config.DATA_DIR / 'index.pkl'}")

    eval_module.main()

if __name__ == '__main__':
    main()
