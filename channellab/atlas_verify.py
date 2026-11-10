"""Independent atlas replay through per-signal Bayes decisions.

Never imports atlas.py, engine.py, or a policy-envelope solver. Every candidate
signal/action crossing is tested for optimality. On each resulting open cell,
all signal winners are constant; their Cartesian product gives all policies.
"""
from fractions import Fraction as F
from itertools import combinations,product
import json
from .model import parse,encode


def verify_atlas(report):
    try:
        _,a,b,u=parse(report['input']);channels={'a':a,'b':b,'none':[[F(1)],[F(1)]]}
        signal_lines={k:[[(c[0][j]*u[0][i],c[1][j]*u[1][i]-c[0][j]*u[0][i])for i in range(len(u[0]))]for j in range(len(c[0]))]for k,c in channels.items()}
        def winners(k,p):
            out=[]
            for lines in signal_lines[k]:
                vals=[v+p*w for v,w in lines];best=max(vals);out.append([i for i,v in enumerate(vals)if v==best])
            return out
        cuts={F(0),F(1)}
        for k,signals in signal_lines.items():
            for j,lines in enumerate(signals):
                for i,h in combinations(range(len(lines)),2):
                    v,w=lines[i];x,y=lines[h]
                    if w!=y:
                        p=(x-v)/(w-y)
                        if 0<=p<=1 and i in winners(k,p)[j] and h in winners(k,p)[j]:cuts.add(p)
        policies={}
        for k,signals in signal_lines.items():
            rows=[]
            for ch in product(range(len(u[0])),repeat=len(signals)):
                coeff=[sum(signals[j][i][s]for j,i in enumerate(ch))for s in range(2)]
                # A policy is optimal exactly when each chosen signal action is.
                lo,hi=F(0),F(1)
                for j,i in enumerate(ch):
                    v,w=signals[j][i]
                    for x,y in signals[j]:
                        if w>y:lo=max(lo,(x-v)/(w-y))
                        elif w<y:hi=min(hi,(x-v)/(w-y))
                        elif v<x:lo,hi=F(1),F(0)
                rows.append(dict(choices=list(ch),coefficients=coeff,optimal_range=[lo,hi]if lo<=hi else None))
            policies[k]=rows
        def value(k,p):
            return sum(max(v+p*w for v,w in ls)for ls in signal_lines[k])
        def ids(k,p):
            allowed=set(product(*winners(k,p)))
            return [i for i,r in enumerate(policies[k])if tuple(r['choices'])in allowed]
        def coefficients(k,p):
            return [sum(signal_lines[k][j][choices[0]][s]for j,choices in enumerate(winners(k,p)))for s in range(2)]
        base=sorted(cuts)
        for l,r in zip(base,base[1:]):
            p=(l+r)/2;gap=[x-y for x,y in zip(coefficients('a',p),coefficients('b',p))]
            if gap[1]:
                z=-gap[0]/gap[1]
                if l<z<r:cuts.add(z)
        cuts=sorted(cuts);knots=[];intervals=[]
        def rank(v):return'a'if v>0 else'b'if v<0 else'tie'
        for p in cuts:
            st={k:dict(value=value(k,p),optimal_policies=ids(k,p))for k in channels};gap=st['a']['value']-st['b']['value']
            knots.append(dict(prior=p,**st,a_minus_b=gap,ranking=rank(gap)))
        for l,r in zip(cuts,cuts[1:]):
            p=(l+r)/2;st={k:dict(coefficients=coefficients(k,p),optimal_policies=ids(k,p))for k in channels};gap=[x-y for x,y in zip(st['a']['coefficients'],st['b']['coefficients'])];info={k:[x-y for x,y in zip(st[k]['coefficients'],st['none']['coefficients'])]for k in ['a','b']}
            intervals.append(dict(left=l,right=r,**st,a_minus_b=gap,information_value=info,ranking=rank(gap[0]+p*gap[1])))
        expected=encode(dict(version=1,kind='channellab-prior-atlas',input=report['input'],policies=policies,knots=knots,intervals=intervals))
        if json.dumps(report,sort_keys=True,separators=(',',':'),allow_nan=False)!=json.dumps(expected,sort_keys=True,separators=(',',':'),allow_nan=False):raise ValueError('atlas mismatch')
        return True
    except (KeyError,TypeError,IndexError,ZeroDivisionError,OverflowError)as e:raise ValueError('malformed atlas')from e
