"""Disclosed seed17029 development search. large_exact is candidate0.

Find a feasible garbling with a serialized kernel component beyond2**53.
Not held-out evaluation or a data-derived probability model.
"""
import json,sys
from pathlib import Path
from random import Random
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from channellab import compare
rng=Random(17029)
for i in range(1000):
 def channel():
  rows=[]
  for s in range(2):
   x=sorted(rng.sample(range(1,1000000),2));rows.append([[x[0],1000000],[x[1]-x[0],1000000],[1000000-x[1],1000000]])
  return rows
 p={'version':1,'prior':[1,2],'a':channel(),'b':channel(),'payoffs':[[1,0],[0,1]]};r=compare(p)
 if any(abs(v)>2**53 for key in ['a_to_b','b_to_a']if r[key]['dominates']for row in r[key]['garbling']['kernel']for q in row for v in q):
  print(json.dumps({'candidate':i,'input':p}));break
else:raise RuntimeError('no control found')
