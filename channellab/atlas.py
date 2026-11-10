"""Exact closed-prior task atlas by complete-policy half-space intersection.

The supplied model's prior remains full-support. This separate task atlas covers
all p in [0,1], including degenerate endpoints, without posterior division.
"""
from fractions import Fraction as F
from itertools import product
from .model import parse,encode


def _lines(c,u):
    out=[]
    for choices in product(range(len(u[0])),repeat=len(c[0])):
        v=[sum(c[s][j]*u[s][a]for j,a in enumerate(choices))for s in range(2)]
        out.append(dict(choices=list(choices),coefficients=[v[0],v[1]-v[0]]))
    for row in out:
        lo,hi=F(0),F(1);x,y=row['coefficients']
        for other in out:
            z,w=other['coefficients'];b,d=x-z,y-w
            if d>0:lo=max(lo,-b/d)
            elif d<0:hi=min(hi,-b/d)
            elif b<0:lo,hi=F(1),F(0)
        row['optimal_range']=[lo,hi]if lo<=hi else None
    return out


def prior_atlas(data):
    _,a,b,u=parse(data)
    ps={k:_lines(c,u)for k,c in [('a',a),('b',b),('none',[[F(1)],[F(1)]])]}
    cuts={F(0),F(1)}
    for rows in ps.values():
        for r in rows:
            if r['optimal_range']is not None:cuts.update(r['optimal_range'])
    def state(k,p):
        rows=ps[k];vs=[r['coefficients'][0]+p*r['coefficients'][1]for r in rows];v=max(vs)
        return dict(value=v,optimal_policies=[i for i,x in enumerate(vs)if x==v])
    def line(k,p):
        st=state(k,p)
        return dict(coefficients=ps[k][st['optimal_policies'][0]]['coefficients'],optimal_policies=st['optimal_policies'])
    # An affine gap may vanish strictly inside a policy cell. Split there too.
    initial=sorted(cuts)
    for l,r in zip(initial,initial[1:]):
        x,y=line('a',(l+r)/2)['coefficients'];z,w=line('b',(l+r)/2)['coefficients']
        if y!=w:
            root=-(x-z)/(y-w)
            if l<root<r:cuts.add(root)
    cuts=sorted(cuts);knots=[];cells=[]
    for p in cuts:
        st={k:state(k,p)for k in ps};gap=st['a']['value']-st['b']['value']
        knots.append(dict(prior=p,**st,a_minus_b=gap,ranking='a'if gap>0 else'b'if gap<0 else'tie'))
    for l,r in zip(cuts,cuts[1:]):
        p=(l+r)/2;st={k:line(k,p)for k in ps};gap=[x-y for x,y in zip(st['a']['coefficients'],st['b']['coefficients'])];v=gap[0]+p*gap[1]
        info={k:[x-y for x,y in zip(st[k]['coefficients'],st['none']['coefficients'])]for k in ['a','b']}
        cells.append(dict(left=l,right=r,**st,a_minus_b=gap,information_value=info,ranking='a'if v>0 else'b'if v<0 else'tie'))
    return encode(dict(version=1,kind='channellab-prior-atlas',input=data,policies=ps,knots=knots,intervals=cells))
