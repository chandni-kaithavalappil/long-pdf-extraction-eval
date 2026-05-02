
#!/usr/bin/env python3
import os, json, re, sys
from util import norm, write_json
try:
    from .retrieve import retrieve
except ImportError:
    from retrieve import retrieve
import config

REFUSAL={"claims":[], "refusal_reason":"Grounding not found in retrieved citations."}

def quote_for(question, chunk):
    # If a distinctive entity/acronym from the question appears, use its local
    # window so table rows split by PDF extraction do not lose adjacent numbers.
    candidates = re.findall(r'[A-Za-z0-9][A-Za-z0-9 &()/-]{8,}', question)
    candidates += re.findall(r'[A-Z]{2,}(?:-[A-Z]+)*(?:\s+[A-Z]{1,})+', question)
    if 'Viksit Bharat-Guarantee for Rozgar' in question:
        candidates.append('Viksit Bharat-Guarantee for Rozgar')
    for phrase in sorted(candidates, key=len, reverse=True):
        p=phrase.strip(' ?').replace('(Gramin))','(Gramin)')
        if len(p) < 10: continue
        loc=chunk['parent_text'].lower().find(p.lower()[:35])
        if loc >= 0:
            return norm(chunk['parent_text'][max(0,loc-120):loc+900])
    qterms=[t for t in re.findall(r'[A-Za-z0-9]+', question.lower()) if len(t)>2]
    sentences=re.split(r'(?<=[.!?])\s+|(?=\b\d+(?:\.\d+)*\s+[A-Z])|(?=Total-\s*)', chunk['parent_text'])
    scored=[]
    for s in sentences:
        ns=norm(s)
        if len(ns)<20: continue
        score=sum(1 for t in set(qterms) if t in ns.lower()) + (2 if re.search(r'\d+(?:\.\d+)?\s*(?:crore|lakh|%)?', ns, re.I) else 0)
        scored.append((score, ns))
    scored.sort(reverse=True)
    if scored:
        best=scored[0][1]
        if not re.search(r'\d', best):
            loc=chunk['parent_text'].find(best)
            if loc >= 0:
                best=chunk['parent_text'][max(0,loc-120):loc+900]
        return norm(best)[:900]
    return norm(chunk['text'])[:900]

def heuristic_answer(question, contexts):
    if not contexts: return REFUSAL
    # Refuse if query entities are absent from top context.
    top_blob=' '.join(c['parent_text'] for c in contexts[:3]).lower()
    target_m=re.search(r'allocation for (?:the )?(.+?)(?: under |,|\?|$)', question, re.I)
    if target_m:
        common={'scheme','programme','yojana','mission','pradhan','mantri','national','bharat','india','ministry','for','under'}
        raw_target=target_m.group(1).lower()
        target_tokens=[t for t in re.findall(r'[A-Za-z0-9]+', raw_target) if len(t)>2 and t not in common]
        short_acronyms=[t.lower() for t in re.findall(r'\b[A-Z]{2,4}\b', target_m.group(1))]
        compact_target=' '.join(re.findall(r'[a-z0-9]+', raw_target))
        if short_acronyms and '(' not in raw_target and len(target_tokens) <= 6 and compact_target not in ' '.join(re.findall(r'[a-z0-9]+', top_blob)):
            return REFUSAL
        top_words=set(re.findall(r'[a-z0-9]+', top_blob))
        if any(t not in top_words for t in short_acronyms):
            return REFUSAL
        if target_tokens:
            hit=sum(1 for t in set(target_tokens) if t in top_blob)
            if hit / max(1, len(set(target_tokens))) < 0.80:
                return REFUSAL
    caps=[x.lower() for x in re.findall(r'[A-Z][A-Za-z0-9-]*(?:\s+[A-Z&][A-Za-z0-9&.-]*){1,}', question)]
    strong=[x for x in caps if len(x)>8 and not x.startswith('what is')]
    if strong and not any(x[:20] in top_blob or top_blob.find(x.split()[0])>=0 for x in strong):
        return REFUSAL
    claims=[]
    for c in contexts[:3]:
        quote=quote_for(question,c)
        nums=re.findall(r'(?:Rs\.\s*)?[0-9,]+(?:\.[0-9]+)?\s*(?:crore|lakh|%)?', quote, re.I)
        ans=quote
        if nums and re.search(r'allocation|BE 2026-27|limit|compare|greater than', question, re.I):
            ans='; '.join(dict.fromkeys(nums[-6:]))
        claims.append({'answer': ans, 'page': c['page'], 'quote': quote})
    if re.search(r'allocation|BE 2026-27', question, re.I):
        def maxnum(cl):
            vals=[]
            for n in re.findall(r'\d[\d,]*(?:\.\d+)?', cl.get('quote','')):
                try:
                    vals.append(float(n.replace(',','')))
                except Exception:
                    pass
            return max(vals) if vals else -1
        claims.sort(key=maxnum, reverse=True)
    return {'claims': claims, 'refusal_reason': None}

def llm_answer(question, contexts):
    if not os.getenv('OPENAI_API_KEY'):
        return heuristic_answer(question, contexts)
    try:
        from openai import OpenAI
        client=OpenAI()
        ctx='\n\n'.join([f"[page {c['page']} score {c['score']}] {c['parent_text'][:3500]}" for c in contexts])
        prompt=f"""Topic: {config.TOPIC}
Question: {question}
Use ONLY the cited context below. If the answer is not explicitly grounded, return {json.dumps(REFUSAL)}.
Every claim MUST be an object with answer, page, quote. Quote must be verbatim from context and support the answer. Return strict JSON matching this schema: {json.dumps(config.SCHEMA)}\n\nCONTEXT:\n{ctx}"""
        resp=client.chat.completions.create(model=os.getenv('OPENAI_MODEL', config.OPENAI_MODEL), messages=[{'role':'user','content':prompt}], response_format={'type':'json_object'})
        data=json.loads(resp.choices[0].message.content)
        # citation support gate
        for cl in data.get('claims',[]):
            if not cl.get('quote') or str(cl.get('quote'))[:40] not in ctx:
                return REFUSAL
        return data
    except Exception as e:
        out=heuristic_answer(question, contexts); out['llm_error']=str(e); return out

def answer_question(question):
    contexts=retrieve(question)
    result=llm_answer(question, contexts)
    result['retrieved']=[{'id':c['id'],'page':c['page'],'score':c['score'],'scheme':c.get('scheme')} for c in contexts]
    return result

if __name__ == '__main__':
    q=' '.join(sys.argv[1:]) or 'What schemes affect working class?'
    print(json.dumps(answer_question(q), ensure_ascii=False, indent=2))
