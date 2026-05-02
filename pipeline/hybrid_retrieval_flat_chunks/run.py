#!/usr/bin/env python3
"""Hybrid Retrieval (Flat Chunks) runner.

Runs the Hybrid Retrieval (Flat Chunks) pipeline: parse -> chunk -> index -> hybrid retrieve
on flat chunks -> schema-targeted extraction with forced citations.
"""
import argparse
import time
from pathlib import Path
import sys

PIPELINE_DIR = Path(__file__).resolve().parents[1]
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PIPELINE_DIR))

import config
from util import ensure_dirs, read_json, write_json
from parse import parse_pdf
from chunk import build_chunks
from index import build as build_index
from hybrid_retrieval_flat_chunks.extract import answer_question
import eval as eval_module


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
    return p if p.is_absolute() else base / p


def apply_runtime(config_path=None, run_name=None):
    cfg = parse_simple_yaml(resolve_path(config_path)) if config_path else {}
    config.PDF_PATH = resolve_path(cfg.get('pdf_path', str(config.PDF_PATH)))
    config.EVAL_PATH = resolve_path(cfg.get('eval_path', str(config.EVAL_PATH)))
    config.OUTPUT_DIR = resolve_path(cfg.get('output_dir', 'output'))
    config.DATA_DIR = PIPELINE_DIR / 'data_hybrid_flat_chunks'
    config.RUN_NAME = run_name or cfg.get('run_name') or 'hybrid_retrieval_flat_chunks'
    if cfg.get('openai_model'):
        config.OPENAI_MODEL = cfg['openai_model']


def run_eval():
    gts = read_json(config.EVAL_PATH)
    results = []
    for gt in gts:
        pred = answer_question(gt['question'])
        sc = eval_module.score_one(gt, pred)
        results.append({
            'id': gt['id'],
            'question': gt['question'],
            'prediction': pred,
            'score': sc,
            'expected_answer': gt.get('expected_answer'),
            'expected_page': gt.get('expected_page'),
        })
        print(gt['id'], sc)
    summary = {
        'run_name': config.RUN_NAME,
        'method': 'hybrid_retrieval_flat_chunks',
        'ts': time.time(),
        'n': len(results),
        'avg_score': round(sum(r['score']['score'] for r in results) / max(1, len(results)), 3),
        'results': results,
    }
    out = config.OUTPUT_DIR / f"results_{config.RUN_NAME}.json"
    write_json(out, summary)
    print('wrote', out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config')
    ap.add_argument('--run-name', required=True)
    args = ap.parse_args()
    apply_runtime(args.config, args.run_name)
    ensure_dirs()
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    manifest, pages = parse_pdf(Path(config.PDF_PATH))
    write_json(config.DATA_DIR / 'manifest.json', manifest)
    write_json(config.DATA_DIR / 'parsed_pages.json', pages)
    chunks = build_chunks(pages)
    write_json(config.DATA_DIR / 'chunks.json', chunks)
    n, backend = build_index()
    print(f"hybrid flat chunks parsed {manifest['pages']} pages; chunks {len(chunks)}; indexed {n} {backend}")
    run_eval()


if __name__ == '__main__':
    main()
