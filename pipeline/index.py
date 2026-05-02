
#!/usr/bin/env python3
import pickle, re
from util import ensure_dirs, read_json, write_json, tokens
import config
from bm25 import BM25

def build():
    chunks=read_json(config.DATA_DIR/'chunks.json')
    docs=[c['text']+' '+(c.get('scheme') or '')+' '+(c.get('ministry') or '') for c in chunks]
    bm25=BM25(docs)
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        vectorizer=TfidfVectorizer(ngram_range=(1,2), min_df=1, max_df=0.95, sublinear_tf=True)
        matrix=vectorizer.fit_transform(docs)
        dense={'backend':'tfidf', 'vectorizer':vectorizer, 'matrix':matrix}
    except Exception:
        dense={'backend':'none'}
    with open(config.DATA_DIR/'index.pkl','wb') as f: pickle.dump({'chunks':chunks,'bm25':bm25,'dense':dense}, f)
    write_json(config.DATA_DIR/'index_manifest.json', {'chunks':len(chunks),'backend':dense['backend']})
    return len(chunks), dense['backend']

if __name__ == '__main__':
    ensure_dirs(); n,b=build(); print(f'indexed {n} chunks with BM25 + {b} -> {config.DATA_DIR/"index.pkl"}')
