
#!/usr/bin/env python3
import json, re, time
from pathlib import Path
from util import read_json, write_json, norm, ensure_dirs
from extract import answer_question
import config

def score_one(gt, pred):
    claims=pred.get('claims') or []
    if gt.get('is_negative'):
        return {'score': 1.0 if not claims else 0.0, 'reason': 'negative expects refusal'}
    blob=norm(json.dumps(claims, ensure_ascii=False)).lower()
    exp=norm(gt.get('expected_answer') or '').lower()
    page_ok=any(c.get('page')==gt.get('expected_page') for c in claims)
    key_nums=re.findall(r'\d[\d,]*(?:\.\d+)?', exp)
    nums_ok=sum(1 for n in key_nums if n.replace(',','') in blob.replace(',',''))/max(1,len(key_nums))
    quote_ok=any(c.get('quote') and len(c.get('quote'))>20 for c in claims)
    score=0.5*nums_ok + 0.3*(1 if page_ok else 0) + 0.2*(1 if quote_ok else 0)
    return {'score': round(score,3), 'nums_ok': nums_ok, 'page_ok': page_ok, 'quote_ok': quote_ok}

def main():
    ensure_dirs(); gts=read_json(config.EVAL_PATH); results=[]
    for gt in gts:
        pred=answer_question(gt['question'])
        sc=score_one(gt,pred)
        results.append({'id':gt['id'],'question':gt['question'],'prediction':pred,'score':sc,'expected_answer':gt.get('expected_answer'),'expected_page':gt.get('expected_page')})
        print(gt['id'], sc)
    summary={'run_name':config.RUN_NAME,'ts':time.time(),'n':len(results),'avg_score':round(sum(r['score']['score'] for r in results)/max(1,len(results)),3),'results':results}
    out=config.OUTPUT_DIR/f"results_{config.RUN_NAME}.json"
    write_json(out, summary); print('wrote', out)
if __name__=='__main__': main()
