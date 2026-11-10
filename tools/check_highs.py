"""Actual external numerical feasibility check, never used by production."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from channellab import compare
from channellab.model import parse
from cases import cases
import numpy as np,scipy
from scipy.optimize import linprog
count=0;feasible=0;worst=0.
for p in cases():
 r=compare(p);prior,a,b,u=parse(p)
 for key,c,d in [('a_to_b',a,b),('b_to_a',b,a)]:
  m,n=len(c[0]),len(d[0]);N=m*n;A=[];rhs=[]
  for j in range(m):A.append([float(i//n==j)for i in range(N)]);rhs.append(1.)
  for s in range(2):
   for k in range(n):A.append([float(c[s][i//n])if i%n==k else 0. for i in range(N)]);rhs.append(float(d[s][k]))
  x=linprog(np.zeros(N),A_eq=A,b_eq=rhs,bounds=(0,None),method='highs')
  assert x.status in [0,2],x.message
  assert x.success==r[key]['dominates'],(p,key,x.message)
  if x.success:
   feasible+=1;err=float(np.max(np.abs(np.array(A)@x.x-np.array(rhs))));worst=max(worst,err);assert err<1e-8
  count+=1
print(json.dumps({'scipy':scipy.__version__,'highs_feasibility_solves':count,'feasible':feasible,'worst_abs_equality_residual':worst,'tolerance':1e-8}))
