
import json, re, hashlib, subprocess, sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent

def ensure_dirs():
    for p in [ROOT/'data', ROOT/'output']:
        p.mkdir(parents=True, exist_ok=True)

def read_json(path: Path):
    with open(path, 'r', encoding='utf-8') as f: return json.load(f)

def write_json(path: Path, obj: Any):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f: json.dump(obj, f, ensure_ascii=False, indent=2)

def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()

def norm(s: str) -> str:
    return re.sub(r'\s+', ' ', (s or '').replace('\u00a0',' ')).strip()

def tokens(s: str):
    return re.findall(r"[A-Za-z0-9]+", (s or '').lower())

def install_hint(pkg):
    raise SystemExit(f"Missing dependency {pkg}. Run: python3 -m pip install -r requirements.txt")
