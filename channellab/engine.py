"""Exact stop-loss comparison and a constructive finite signal garbling."""
from fractions import Fraction as F
from itertools import combinations,product
from .model import parse,encode

def reduced(rows,n):
    rows=[list(r)for r in rows];pivot=0
    for c in range(n):
        k=next((i for i in range(pivot,len(rows))if rows[i][c]),None)
        if k is None:continue
        rows[pivot],rows[k]=rows[k],rows[pivot];v=rows[pivot][c];rows[pivot]=[x/v for x in rows[pivot]]
        for i in range(len(rows)):
            if i!=pivot:
                v=rows[i][c];rows[i]=[a-v*b for a,b in zip(rows[i],rows[pivot])]
        pivot+=1
    if any(not any(r[:n])and r[n]for r in rows):return None
    return rows[:pivot]

def garbling(a,b):
    m,n=len(a[0]),len(b[0]);N=m*n
    rows=[]
    for j in range(m):rows.append([F(int(i//n==j))for i in range(N)]+[F(1)])
    for s in range(2):
        for k in range(n):rows.append([a[s][i//n]if i%n==k else F(0)for i in range(N)]+[b[s][k]])
    rr=reduced(rows,N)
    if rr is None:return None
    rank=len(rr)
    for basis in combinations(range(N),rank):
        ss=reduced([[r[i]for i in basis]+[r[-1]]for r in rr],rank)
        if ss is None or len(ss)!=rank:continue
        vals=[r[-1]for r in ss]
        if any(v<0 for v in vals):continue
        x=[F(0)]*N
        for i,v in zip(basis,vals):x[i]=v
        return [x[j*n:(j+1)*n]for j in range(m)]
    return None

def signals(c,p):
    return [{'signal':j,'state_joint':[(1-p)*c[0][j],p*c[1][j]],'mass':(1-p)*c[0][j]+p*c[1][j],'posterior':p*c[1][j]/((1-p)*c[0][j]+p*c[1][j])if (1-p)*c[0][j]+p*c[1][j] else None}for j in range(len(c[0]))]

def decision(c,p,u):
    n,k=len(c[0]),len(u[0]);rows=[]
    for j in range(n):
        vals=[(1-p)*c[0][j]*u[0][a]+p*c[1][j]*u[1][a]for a in range(k)];v=max(vals)
        rows.append({'signal':j,'action_joint_values':vals,'best_actions':[a for a in range(k)if vals[a]==v],'selected':vals.index(v),'value':v})
    policies=[]
    for choices in product(range(k),repeat=n):policies.append({'choices':list(choices),'value':sum(rows[j]['action_joint_values'][a]for j,a in enumerate(choices))})
    value=sum(r['value']for r in rows);prior_vals=[(1-p)*u[0][a]+p*u[1][a]for a in range(k)]
    return {'signals':rows,'policies':policies,'value':value,'optimal_policies':[i for i,v in enumerate(policies)if v['value']==value],'no_signal_values':prior_vals,'no_signal_value':max(prior_vals),'information_value':value-max(prior_vals)}

def certificate(a,b,p,ss,tt,hinges):
    bad=next((h for h in hinges if h['a_minus_b']<0),None)
    if bad:
        t=bad['threshold'];u=[[F(0),-t],[F(0),1-t]]
        return {'dominates':False,'garbling':None,'witness':{'threshold':t,'payoffs':u,'a':decision(a,p,u),'b':decision(b,p,u),'b_minus_a':-bad['a_minus_b']}}
    k=garbling(a,b)
    if k is None:raise ArithmeticError('stop-loss/garbling disagreement')
    m,n=len(a[0]),len(b[0]);reconstructed=[[sum(a[s][j]*k[j][i]for j in range(m))for i in range(n)]for s in range(2)]
    joint=[[ss[j]['mass']*k[j][i]for i in range(n)]for j in range(m)]
    # The zero-mass signal rows remain stochastic; their posterior is undefined.
    moments=[sum(p*a[1][j]*k[j][i]for j in range(m))for i in range(n)]
    return {'dominates':True,'witness':None,'garbling':{'kernel':k,'row_sums':[sum(r)for r in k],'reconstructed':reconstructed,'signal_joint':joint,'target_masses':[sum(joint[j][i]for j in range(m))for i in range(n)],'target_state1_joint':moments}}

def compare(data):
    p,a,b,u=parse(data);sa,sb=signals(a,p),signals(b,p)
    thresholds=sorted({F(0),F(1)}|{r['posterior']for r in sa+sb if r['posterior']is not None})
    hinges=[]
    for t in thresholds:
        va=sum(max(r['state_joint'][1]-t*r['mass'],F(0))for r in sa);vb=sum(max(r['state_joint'][1]-t*r['mass'],F(0))for r in sb)
        hinges.append({'threshold':t,'a':va,'b':vb,'a_minus_b':va-vb})
    ab=certificate(a,b,p,sa,sb,hinges)
    ba=certificate(b,a,p,sb,sa,[{'threshold':h['threshold'],'a_minus_b':-h['a_minus_b']}for h in hinges])
    relation='equivalent'if ab['dominates']and ba['dominates']else 'a_dominates_b'if ab['dominates']else 'b_dominates_a'if ba['dominates']else 'incomparable'
    return encode({'version':1,'input':data,'signals':{'a':sa,'b':sb},'hinges':hinges,'relation':relation,'a_to_b':ab,'b_to_a':ba,'task':{'a':decision(a,p,u),'b':decision(b,p,u)}})
