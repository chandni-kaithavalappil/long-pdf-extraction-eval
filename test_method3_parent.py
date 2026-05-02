#!/usr/bin/env python3
import sys
sys.path.insert(0, 'pipeline')
from chunk import build_chunks
pages=[
 {'page':1,'text':'Ministry of X Demand No. 1 1. Scheme Alpha 100 ... 200','section':'Demand No. 1','ministry':'Ministry of X','demand':{'number':'1','name':'X'}},
 {'page':2,'text':'1. Scheme Alpha: prose explaining Scheme Alpha and benefits','section':'Demand No. 1','ministry':'Ministry of X','demand':{'number':'1','name':'X'}},
]
chunks=build_chunks(pages)
assert all('parent_section_id' in c and c['parent_section_id'] for c in chunks)
assert all(c['parent_section_id'].startswith('1-ministry-of-x') for c in chunks), chunks
print('parent_section_id metadata ok')
