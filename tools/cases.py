"""Declared complete grid plus reproducible seeded rectangular controls."""
from fractions import Fraction as F
from random import Random
from channellab.model import encode
from channellab.controls import controls

def cases():
    yield from (c['input']for c in controls())
    channels=[[[[a,4],[4-a,4]],[[b,4],[4-b,4]]]for a in range(5)for b in range(5)]
    for a in channels:
        for b in channels:yield {'version':1,'prior':[1,2],'a':a,'b':b,'payoffs':[[1,0],[0,1]]}
    rng=Random(17023)
    for m in range(1,4):
        for n in range(1,4):
            for _ in range(8):
                def channel(k):
                    rows=[]
                    for s in range(2):
                        raw=[rng.randrange(5)for i in range(k)]
                        if not sum(raw):raw[0]=1
                        rows.append([F(v,sum(raw))for v in raw])
                    return rows
                yield encode({'version':1,'prior':F(rng.randrange(1,7),7),'a':channel(m),'b':channel(n),'payoffs':[[rng.randrange(-3,4)for _ in range(3)]for _ in range(2)]})
