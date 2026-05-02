import math
from collections import Counter
from util import tokens

class BM25:
    def __init__(self, docs, k1=1.5, b=0.75):
        self.docs=[tokens(d) for d in docs]; self.k1=k1; self.b=b
        self.avgdl=sum(map(len,self.docs))/max(1,len(self.docs)); self.df=Counter()
        for d in self.docs: self.df.update(set(d))
        self.N=len(self.docs)
    def scores(self, query):
        q=tokens(query); out=[]
        for d in self.docs:
            tf=Counter(d); dl=len(d); s=0.0
            for term in q:
                if term not in tf: continue
                idf=math.log(1+(self.N-self.df[term]+0.5)/(self.df[term]+0.5))
                s += idf * (tf[term]*(self.k1+1))/(tf[term]+self.k1*(1-self.b+self.b*dl/max(1,self.avgdl)))
            out.append(s)
        return out
