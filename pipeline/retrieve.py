
#!/usr/bin/env python3
import pickle, re, math, sys
from util import tokens, norm
import config

def load_index():
    with open(config.DATA_DIR/'index.pkl','rb') as f: return pickle.load(f)

def normalize_scores(xs):
    if not xs: return []
    lo=min(xs); hi=max(xs)
    return [(x-lo)/(hi-lo+1e-9) for x in xs]

def dense_scores(dense, query):
    if dense.get('backend')!='tfidf': return []
    qv=dense['vectorizer'].transform([query])
    return (dense['matrix'] @ qv.T).toarray().ravel().tolist()

def rerank_score(query, chunk):
    qt=set(tokens(query)); text=chunk['parent_text'].lower(); ct=set(tokens(chunk['parent_text']))
    overlap=len(qt & ct)/max(1,len(qt))
    exact=sum(1 for phrase in re.findall(r'[A-Z][A-Za-z0-9 &()/-]{4,}', query) if phrase.lower() in text)
    number_bonus=0.15 if re.search(r'\d+\.\d+|\b\d{3,}\b|crore|lakh', text) else 0
    table_bonus=min(0.35, 0.015*len(re.findall(r'\d+(?:\.\d+)?', text))) if re.search(r'allocation|BE\s*2026|budget\s*2026', query, re.I) else 0
    exact_acronym=0.25 if any(x.lower() in text for x in re.findall(r'[A-Z]{2,}(?:-[A-Z]+)*(?:\s+[A-Z]{1,})*', query)) else 0
    meta_bonus=0.1 if (chunk.get('scheme') and any(t in (chunk['scheme'] or '').lower() for t in qt)) else 0
    return overlap + 0.25*exact + exact_acronym + number_bonus + table_bonus + meta_bonus

def retrieve(query, top_k=None, rerank_k=None, filters=None):
    idx=load_index(); chunks=idx['chunks']; top_k=top_k or config.TOP_K; rerank_k=rerank_k or config.RERANK_K
    bm=normalize_scores(idx['bm25'].scores(query)); ds=normalize_scores(dense_scores(idx['dense'], query) or [0]*len(chunks))
    candidates=[]
    for i,c in enumerate(chunks):
        if filters:
            ok=True
            for k,v in filters.items():
                if v and v.lower() not in str(c.get(k,'')).lower(): ok=False
            if not ok: continue
        score=0.55*(bm[i] if i<len(bm) else 0)+0.35*(ds[i] if i<len(ds) else 0)+0.10*rerank_score(query,c)
        candidates.append((score,c))
    candidates=sorted(candidates, key=lambda x:x[0], reverse=True)[:top_k]
    reranked=sorted([(s+0.25*rerank_score(query,c),c) for s,c in candidates], key=lambda x:x[0], reverse=True)[:rerank_k]
    return [{**c, 'score': round(s,4)} for s,c in reranked]

if __name__ == '__main__':
    q=' '.join(sys.argv[1:]) or config.TOPIC
    for r in retrieve(q): print(r['score'], 'p'+str(r['page']), r.get('scheme'), norm(r['text'])[:300])
