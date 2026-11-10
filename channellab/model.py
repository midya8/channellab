"""Strict finite binary experiment input. No floats or inferred probabilities."""
from fractions import Fraction as F
from math import lcm
import json

def rational(x):
    if type(x) is int: n,d=x,1
    elif type(x) is list and len(x)==2 and all(type(v)is int for v in x): n,d=x
    else: raise ValueError('expected exact integer or [integer,positive denominator]')
    if abs(n)>1000000 or not 1<=d<=1000000: raise ValueError('rational component bound')
    return F(n,d)

def parse(data):
    if type(data)is not dict or set(data)!={'version','prior','a','b','payoffs'} or type(data['version'])is not int or data['version']!=1: raise ValueError('expected version 1, prior, a, b, payoffs')
    prior=rational(data['prior'])
    if not 0<prior<1: raise ValueError('prior P(state1) must have full support')
    matrices=[]
    for name in ['a','b','payoffs']:
        x=data[name]
        if type(x)is not list or len(x)!=2 or any(type(row)is not list for row in x) or not 1<=len(x[0])<=3 or len(x[1])!=len(x[0]): raise ValueError('two equally sized rows, one to three columns')
        mat=[[rational(v)for v in row]for row in x]
        if name!='payoffs':
            if any(v<0 for row in mat for v in row)or any(sum(row)!=1 for row in mat): raise ValueError('channel rows must be nonnegative probability laws')
        elif any(abs(v)>100 for row in mat for v in row):raise ValueError('payoff magnitude <=100')
        matrices.append(mat)
    if lcm(*(v.denominator for mat in matrices for row in mat for v in row),prior.denominator)>1000000:raise ValueError('normalized denominator LCM bound')
    return prior,*matrices

def encode(x):
    if isinstance(x,F):return [x.numerator,x.denominator]
    if type(x)is dict:return {k:encode(v)for k,v in x.items()}
    if type(x)is list or type(x)is tuple:return [encode(v)for v in x]
    return x

def loads(s):
    def pairs(items):
        out={}
        for k,v in items:
            if k in out:raise ValueError('duplicate key')
            out[k]=v
        return out
    def nope(x):raise ValueError('noninteger JSON number')
    return json.loads(s,object_pairs_hook=pairs,parse_float=nope,parse_constant=nope)
