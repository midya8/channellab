"""Hand-constructed controls, not an empirical evaluation set."""
from copy import deepcopy

def controls():
    task=[[1,0],[0,1]]
    def case(name,a,b,p=[1,2],payoffs=None):return {'id':name,'input':{'version':1,'prior':p,'a':a,'b':b,'payoffs':payoffs or task}}
    f=lambda n,d:[n,d]
    perfect=[[1,0],[0,1]];blind=[[1],[1]]
    out=[case('incomparable',[[1,0],[f(1,2),f(1,2)]],[[f(1,2),f(1,2)],[0,1]]),
         case('perfect_to_noisy',perfect,[[f(3,4),f(1,4)],[f(1,4),f(3,4)]]),
         case('noise_to_blind',[[f(3,4),f(1,4)],[f(1,4),f(3,4)]],blind),
         case('blind_to_perfect',blind,perfect),
         case('relabelled',[[f(3,4),f(1,4)],[f(1,4),f(3,4)]],[[f(1,4),f(3,4)],[f(3,4),f(1,4)]]),
         case('split_signal',perfect,[[f(1,3),f(2,3),0],[0,0,1]]),
         case('zero_signals',[[1,0,0],[0,1,0]],[[1,0],[1,0]]),
         case('all_blind',[[f(1,3),f(2,3)],[f(1,3),f(2,3)]],[[f(1,4),f(1,4),f(1,2)],[f(1,4),f(1,4),f(1,2)]]),
         case('skew_prior',[[1,0],[f(1,2),f(1,2)]],[[f(1,2),f(1,2)],[0,1]],p=f(1,5)),
         case('task_ignores_state',perfect,blind,payoffs=[[2,1],[2,1]]),
         case('three_signals',[[f(1,2),f(1,3),f(1,6)],[f(1,6),f(1,3),f(1,2)]],[[f(5,12),f(7,12)],[f(1,4),f(3,4)]]),
         case('tiny_prior',perfect,[[f(999,1000),f(1,1000)],[f(1,1000),f(999,1000)]],p=f(1,1000000))]
    # Seed-17029 development search candidate 0. Not a held-out result.
    out.append({'id': 'large_exact', 'input': {'version': 1, 'prior': [1, 2], 'a': [[[220424, 1000000], [65558, 1000000], [714018, 1000000]], [[407038, 1000000], [397763, 1000000], [195199, 1000000]]], 'b': [[[364125, 1000000], [439716, 1000000], [196159, 1000000]], [[322948, 1000000], [284423, 1000000], [392629, 1000000]]], 'payoffs': [[1, 0], [0, 1]]}})
    return deepcopy(out)
