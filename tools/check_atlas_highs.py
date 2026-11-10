"""Optional floating reference for all complete-policy optimality ranges.

Not imported by the exact engine, checker or browser. Two independent HiGHS LPs
minimize/maximize the prior where a fixed policy dominates every alternative.
All inequalities are scaled before conversion to float; degenerate equalities
and numerically tiny ranges are still checked against exact expected endpoints.
"""
import json,sys
from pathlib import Path
from fractions import Fraction as F
from itertools import product
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import scipy
from scipy.optimize import linprog
from channellab import prior_atlas
from channellab.model import parse
from cases import cases
solves=feasible=policies=0;error=0.0
for data in cases():
    r=prior_atlas(data);_,a,b,u=parse(data)
    for k,c in [('a',a),('b',b),('none',[[F(1)],[F(1)]])]:
        lines=[]
        for ch in product(range(len(u[0])),repeat=len(c[0])):
            v=[sum(c[s][j]*u[s][i]for j,i in enumerate(ch))for s in range(2)]
            lines.append((v[0],v[1]-v[0]))
        for i,(v,w)in enumerate(lines):
            policies+=1;constraints=[];bounds=[]
            for x,y in lines:
                d,b=y-w,v-x;scale=max(abs(d),abs(b))
                if scale:constraints.append([float(d/scale)]);bounds.append(float(b/scale))
            results=[linprog([sign],A_ub=constraints or None,b_ub=bounds or None,bounds=[(0,1)],method='highs',options={'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9})for sign in [1,-1]];solves+=2
            expected=r['policies'][k][i]['optimal_range']
            if expected is None:
                assert all(z.status==2 for z in results),(data,k,i,results)
            else:
                assert all(z.success for z in results),(data,k,i,results)
                feasible+=1
                for result,target in zip(results,expected):
                    difference=abs(result.x[0]-float(F(*target)));error=max(error,difference);assert difference<1e-8,(difference,data,k,i)
print(json.dumps({'scipy':scipy.__version__,'policies':policies,'lp_solves':solves,'nonempty_ranges':feasible,'worst_endpoint_error':error,'tolerance':1e-8}))
