
#!/usr/bin/env python3
import re, math
from util import ensure_dirs, read_json, write_json, norm
import config

SCHEME_RE = re.compile(r"(?:^|\s)(?:\d+(?:\.\d+)*\s+)?([A-Z][A-Za-z0-9 &,()/'-]{8,120}(?:Scheme|Programme|Yojana|Abhiyan|Mission|Assistance|Subvention|Awaas|Rozgar|Livelihoods)[A-Za-z0-9 &,()/'-]*)", re.I)

def infer_scheme(text):
    heading=re.search(r'(?:^|\s)\d+(?:\.\d+)*\s+([^:]{3,120}?(?:Scheme|Programme|Yojana|Abhiyan|Mission|Assistance|Subvention|Awaas|Rozgar|Livelihoods)(?:\s+[A-Za-z()&/-]+){0,6})(?=\s*(?::|\.\.\.|[0-9]))', text, re.I)
    if heading:
        return norm(heading.group(1))[:180]
    m=SCHEME_RE.search(text)
    return norm(m.group(1))[:180] if m else None

def parent_section_id(page, scheme, current_parent=None):
    """Stable-ish parent key for sibling table/prose chunks.

    It intentionally uses existing parse metadata plus the nearest scheme
    heading. This preserves the original parse/chunk behavior while adding
    enough hierarchy for Hierarchical Retrieval with Parent Expansion.
    """
    demand=page.get('demand') or {}
    ministry=page.get('ministry') or ''
    section=page.get('section') or ''
    heading=scheme or (current_parent or {}).get('scheme') or section or 'unknown'
    key='|'.join([str(demand.get('number') or ''), ministry, heading])
    key=re.sub(r'[^a-zA-Z0-9]+','-', key.lower()).strip('-')
    return key[:180] or 'unknown'

def split_page(page):
    text=page['text']
    # Prefer semantically meaningful table/prose lines; then pack into parent-aware chunks.
    units=[]
    for part in re.split(r'(?=\b\d+(?:\.\d+)*\s+[A-Z])|(?=Total-\s*)|(?=\bNet\s*)', text):
        part=norm(part)
        if len(part) > 40: units.append(part)
    if not units: units=[text]
    chunks=[]; buf=''
    target=config.CHUNK_TOKENS_APPROX*5
    for u in units:
        if len(buf)+len(u)>target and buf:
            chunks.append(buf); buf=u
        else:
            buf=(buf+' '+u).strip()
    if buf: chunks.append(buf)
    return chunks

def build_chunks(pages):
    out=[]; cid=0; current_parent={}
    for idx,p in enumerate(pages):
        prev_text=pages[idx-1]['text'][-config.CHUNK_OVERLAP_CHARS:] if idx>0 else ''
        next_text=pages[idx+1]['text'][:config.CHUNK_OVERLAP_CHARS] if idx+1<len(pages) else ''
        for j,text in enumerate(split_page(p)):
            cid+=1
            parent=norm((prev_text+' '+text+' '+next_text))
            scheme=infer_scheme(text)
            if scheme:
                current_parent={'scheme': scheme}
            parent_id=parent_section_id(p, scheme, current_parent)
            out.append({
                'id': f"p{p['page']}_c{j+1}", 'page': p['page'], 'text': text, 'parent_text': parent,
                'section': p.get('section'), 'ministry': p.get('ministry'), 'demand': p.get('demand'),
                'scheme': scheme, 'parent_section_id': parent_id, 'source': 'budget_pdf'
            })
    return out

if __name__ == '__main__':
    ensure_dirs(); pages=read_json(config.DATA_DIR/'parsed_pages.json')
    chunks=build_chunks(pages)
    write_json(config.DATA_DIR/'chunks.json', chunks)
    print(f"built {len(chunks)} chunks -> {config.DATA_DIR/'chunks.json'}")
