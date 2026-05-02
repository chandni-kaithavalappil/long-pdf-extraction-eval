
#!/usr/bin/env python3
"""Structure-aware parser: page text + inferred ministries/demands/sections.
Uses PyPDF as the runnable default. If you later install Docling/Unstructured,
this is the component to swap while preserving parsed_pages.json schema.
"""
import re, sys, time
from pathlib import Path
from util import ensure_dirs, write_json, sha256_file, norm, install_hint
import config

try:
    from pypdf import PdfReader
except Exception:
    install_hint('pypdf')

MINISTRY_RE = re.compile(r"Ministry of ([A-Za-z &,.'()-]+)", re.I)
DEMAND_RE = re.compile(r"Demand No\.\s*(\d+)\s*\n?\s*([A-Za-z &,.'()/-]+)?", re.I)
SECTION_RE = re.compile(r"^(Notes on Demands for Grants|No\.\s*\d+/.+|\d+\.\s+[A-Z][^\n]{5,120}|Total-\s*[^\n]{5,120})", re.M)

def parse_pdf(pdf_path: Path):
    reader = PdfReader(str(pdf_path))
    pages=[]; current_ministry=None; current_demand=None; current_section=None
    for i, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text(extraction_mode='layout') or ''
        except Exception:
            try:
                text = page.extract_text() or ''
            except Exception:
                text = ''
        text = norm(text)
        m=MINISTRY_RE.search(text)
        if m: current_ministry='Ministry of '+norm(m.group(1))[:160]
        d=DEMAND_RE.search(text)
        if d: current_demand={'number': d.group(1), 'name': norm(d.group(2) or '')[:160]}
        s=SECTION_RE.search(text)
        if s: current_section=norm(s.group(1))[:220]
        lines=[norm(x) for x in re.split(r'(?<=[.!?])\s+|\n+', text) if norm(x)]
        pages.append({
            'page': i,
            'text': text,
            'lines': lines,
            'ministry': current_ministry,
            'demand': current_demand,
            'section': current_section,
            'parser': 'pypdf-layout',
        })
    manifest={'pdf_path': str(pdf_path), 'sha256': sha256_file(pdf_path), 'pages': len(pages), 'parsed_at': time.time(), 'parser':'pypdf-layout'}
    return manifest, pages

if __name__ == '__main__':
    ensure_dirs(); pdf=Path(config.PDF_PATH)
    if not pdf.exists(): raise SystemExit(f'PDF not found: {pdf}')
    manifest,pages=parse_pdf(pdf)
    write_json(config.DATA_DIR/'manifest.json', manifest)
    write_json(config.DATA_DIR/'parsed_pages.json', pages)
    print(f"parsed {manifest['pages']} pages from {pdf} -> {config.DATA_DIR/'parsed_pages.json'}")
