#!/usr/bin/env python3
"""Full-Context Dump: dump all PDF text and ask the model directly.

Run from repo root:
  python3 pipeline/full_context_dump/run.py --config configs/budget_2026_27.yaml --run-name full_context_dump_2026
"""
import os, json, re, argparse
from pathlib import Path
import sys
PIPELINE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PIPELINE_DIR))
from util import norm, write_json, read_json, install_hint
import config

try:
    from pypdf import PdfReader
except Exception:
    install_hint('pypdf')

ROOT = Path(__file__).resolve().parents[2]

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

def load_runtime():
    ap = argparse.ArgumentParser()
    ap.add_argument('--config', help='YAML config with pdf_path/eval_path/output_dir')
    ap.add_argument('--run-name', help='Output run name, e.g. full_context_dump_2026')
    args = ap.parse_args()
    cfg = parse_simple_yaml(resolve_path(args.config)) if args.config else {}

    pdf_path = resolve_path(cfg.get('pdf_path', str(config.PDF_PATH)))
    eval_path = resolve_path(cfg.get('eval_path', str(config.EVAL_PATH)))
    output_dir = resolve_path(cfg.get('output_dir', str(config.OUTPUT_DIR)))
    run_name = args.run_name or cfg.get('run_name') or ('full_context_dump_' + config.RUN_NAME)
    model = cfg.get('openai_model', getattr(config, 'OPENAI_MODEL', 'gpt-5.5'))
    return pdf_path, eval_path, output_dir, run_name, model

def dump_text(pdf_path):
    reader = PdfReader(str(pdf_path))
    parts = []
    for i, p in enumerate(reader.pages, 1):
        parts.append(f"\n[page {i}]\n" + (p.extract_text() or ''))
    return norm('\n'.join(parts))

def answer(question, full_text, model):
    if os.getenv('OPENAI_API_KEY'):
        from openai import OpenAI
        client = OpenAI()
        prompt = (
            "Answer from this PDF text only. For every claim output JSON claim "
            "objects with answer,page,quote. Refuse if not found. "
            f"Question: {question}\nPDF:\n{full_text}"
        )
        r = client.chat.completions.create(
            model=os.getenv('OPENAI_MODEL', model),
            messages=[{'role': 'user', 'content': prompt}],
            response_format={'type': 'json_object'},
        )
        return json.loads(r.choices[0].message.content)

    # fallback: crude full-text scan, not citation-safe
    terms = [t for t in re.findall(r'[A-Za-z0-9]+', question.lower()) if len(t) > 3]
    best = ''; bests = -1; page = None
    for m in re.finditer(r'\[page (\d+)\](.*?)(?=\[page \d+\]|$)', full_text, re.S):
        txt = m.group(2)
        s = sum(1 for t in set(terms) if t in txt.lower())
        if s > bests:
            bests = s; best = txt[:1200]; page = int(m.group(1))
    if bests < 2:
        return {'claims': [], 'refusal_reason': 'not found'}
    return {'claims': [{'answer': best[:500], 'page': page, 'quote': best[:900]}], 'refusal_reason': None}

def score_one(gt, pred):
    claims = pred.get('claims') or []
    if gt.get('is_negative'):
        return {'score': 1.0 if not claims else 0.0}
    blob = norm(json.dumps(claims)).lower()
    nums = re.findall(r'\d[\d,]*(?:\.\d+)?', (gt.get('expected_answer') or '').lower())
    nums_ok = sum(1 for n in nums if n.replace(',', '') in blob.replace(',', '')) / max(1, len(nums))
    page_ok = any(c.get('page') == gt.get('expected_page') for c in claims)
    return {'score': round(0.7 * nums_ok + 0.3 * (1 if page_ok else 0), 3)}

def main():
    pdf_path, eval_path, output_dir, run_name, model = load_runtime()
    output_dir.mkdir(parents=True, exist_ok=True)
    text = dump_text(pdf_path)
    gts = read_json(eval_path)
    results = []
    for gt in gts:
        pred = answer(gt['question'], text, model)
        results.append({'id': gt['id'], 'question': gt['question'], 'prediction': pred, 'score': score_one(gt, pred)})
    out = output_dir / f"results_{run_name}.json"
    write_json(out, {'run_name': run_name, 'pdf_path': str(pdf_path), 'results': results})
    print('wrote', out)

if __name__ == '__main__':
    main()
