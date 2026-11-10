"""Independent report replay. Imports validation, never the generator or its solver.

Feasible kernels need not be the generator's particular vertex. A failed direction
is checked by an exact binary-decision witness, not a failed numerical solve.
"""
from fractions import Fraction as F
from itertools import product
import json
from .model import parse,encode

def _rat(x):
    if type(x)is not list or len(x)!=2 or any(type(v)is not int for v in x)or x[1]<=0 or max(abs(x[0]),x[1])>10**100:raise ValueError('invalid report rational')
    v=F(*x)
    if [v.numerator,v.denominator]!=x:raise ValueError('noncanonical report rational')
    return v

def _signal(c,p):
    out=[]
    for j,(v,w)in enumerate(zip(*c)):
        x,y=(1-p)*v,p*w;mass=x+y
        out.append(dict(signal=j,state_joint=[x,y],mass=mass,posterior=None if mass==0 else y/mass))
    return out

def _decision(c,p,u):
    policies=[]
    for choices in product(range(len(u[0])),repeat=len(c[0])):
        v=F(0)
        for s in range(2):
            for j,a in enumerate(choices):v+=(p if s else 1-p)*c[s][j]*u[s][a]
        policies.append(dict(choices=list(choices),value=v))
    value=max(r['value']for r in policies);rows=[]
    for j in range(len(c[0])):
        vals=[sum((p if s else 1-p)*c[s][j]*u[s][a]for s in range(2))for a in range(len(u[0]))];w=max(vals);ties=[a for a,v in enumerate(vals)if v==w]
        rows.append(dict(signal=j,action_joint_values=vals,best_actions=ties,selected=ties[0],value=w))
    prior_vals=[sum((p if s else 1-p)*u[s][a]for s in range(2))for a in range(len(u[0]))]
    return dict(signals=rows,policies=policies,value=value,optimal_policies=[i for i,r in enumerate(policies)if r['value']==value],no_signal_values=prior_vals,no_signal_value=max(prior_vals),information_value=value-max(prior_vals))

def _certificate(c,d,p,signals,hinges,given,reverse=False):
    gaps=[(-h['a_minus_b']if reverse else h['a_minus_b'])for h in hinges]
    bad=next((i for i,g in enumerate(gaps)if g<0),None)
    if bad is not None:
        t=hinges[bad]['threshold'];u=[[F(0),-t],[F(0),1-t]]
        return dict(dominates=False,garbling=None,witness=dict(threshold=t,payoffs=u,a=_decision(c,p,u),b=_decision(d,p,u),b_minus_a=-gaps[bad]))
    g=given['garbling'];raw=g['kernel'];m,n=len(c[0]),len(d[0])
    if type(raw)is not list or len(raw)!=m or any(type(row)is not list or len(row)!=n for row in raw):raise ValueError('kernel shape')
    k=[[_rat(v)for v in row]for row in raw]
    if any(v<0 for row in k for v in row)or any(sum(row)!=1 for row in k):raise ValueError('nonstochastic kernel')
    out=[[F(0)]*n for _ in range(2)]
    for s in range(2):
        for i in range(n):
            for j in range(m):out[s][i]+=c[s][j]*k[j][i]
    if out!=d:raise ValueError('kernel does not reconstruct target')
    joint=[[signals[j]['mass']*k[j][i]for i in range(n)]for j in range(m)]
    return dict(dominates=True,witness=None,garbling=dict(kernel=k,row_sums=[sum(row)for row in k],reconstructed=out,signal_joint=joint,target_masses=[sum(row[i]for row in joint)for i in range(n)],target_state1_joint=[p*d[1][i]for i in range(n)]))

def verify(report):
    try:
        p,a,b,u=parse(report['input']);sa,sb=_signal(a,p),_signal(b,p)
        ts=sorted({F(0),F(1)}|{r['posterior']for r in sa+sb if r['mass']})
        hs=[]
        for t in ts:
            ca=sum(r['mass']*max(r['posterior']-t,F(0))for r in sa if r['mass']);cb=sum(r['mass']*max(r['posterior']-t,F(0))for r in sb if r['mass'])
            hs.append(dict(threshold=t,a=ca,b=cb,a_minus_b=ca-cb))
        ab=_certificate(a,b,p,sa,hs,report['a_to_b']);ba=_certificate(b,a,p,sb,hs,report['b_to_a'],True)
        rel='equivalent'if ab['dominates']and ba['dominates']else 'a_dominates_b'if ab['dominates']else 'b_dominates_a'if ba['dominates']else 'incomparable'
        expected=encode(dict(version=1,input=report['input'],signals=dict(a=sa,b=sb),hinges=hs,relation=rel,a_to_b=ab,b_to_a=ba,task=dict(a=_decision(a,p,u),b=_decision(b,p,u))))
        # JSON representation distinguishes booleans from integers and seals fields.
        if json.dumps(report,sort_keys=True,separators=(',',':'),allow_nan=False)!=json.dumps(expected,sort_keys=True,separators=(',',':'),allow_nan=False):raise ValueError('report mismatch')
        return True
    except (KeyError,TypeError,IndexError,ZeroDivisionError,OverflowError)as e:raise ValueError('malformed report')from e
