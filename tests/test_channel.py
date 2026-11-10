import copy,json,subprocess,sys,tempfile,unittest
from pathlib import Path
from fractions import Fraction as F
from channellab import compare,verify
from channellab.controls import controls
from channellab.model import loads,parse
from channellab.engine import garbling
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from cases import cases

class Tests(unittest.TestCase):
 def test_controls_and_complete_grid(self):
  self.reports=[compare(p)for p in cases()]
  self.assertEqual(len(self.reports),710)
  for r in self.reports:self.assertTrue(verify(r))
 def test_equal_accuracy_does_not_order(self):
  r=compare(controls()[0]['input']);self.assertEqual(r['relation'],'incomparable');self.assertEqual(r['task']['a']['value'],r['task']['b']['value'])
  for k in ['a_to_b','b_to_a']:self.assertGreater(F(*r[k]['witness']['b_minus_a']),0)
 def test_twelve_classes(self):
  expected=['incomparable','a_dominates_b','a_dominates_b','b_dominates_a','equivalent','equivalent','a_dominates_b','equivalent','incomparable','a_dominates_b','a_dominates_b','a_dominates_b','a_dominates_b']
  self.assertEqual([compare(c['input'])['relation']for c in controls()],expected)
 def test_zero_mass_null_and_all_action_ties(self):
  r=compare(controls()[6]['input']);self.assertIsNone(r['signals']['a'][2]['posterior']);self.assertEqual(r['task']['a']['signals'][2]['best_actions'],[0,1]);self.assertTrue(verify(r))
 def test_prior_does_not_change_order(self):
  for c in controls():
   rel=compare(c['input'])['relation']
   for p in [[1,4],[1,2],[3,4]]:
    x=copy.deepcopy(c['input']);x['prior']=p;self.assertEqual(compare(x)['relation'],rel)
 def test_relabel_signals(self):
  for c in controls():
   x=copy.deepcopy(c['input']);rel=compare(x)['relation'];x['a']=[r[::-1]for r in x['a']];x['b']=[r[::-1]for r in x['b']];self.assertEqual(compare(x)['relation'],rel)
 def test_state_relabel(self):
  for c in controls():
   x=copy.deepcopy(c['input']);rel=compare(x)['relation'];p=F(*x['prior']);x['prior']=[(1-p).numerator,(1-p).denominator]
   for k in ['a','b','payoffs']:x[k]=x[k][::-1]
   r=compare(x);self.assertEqual(r['relation'],rel);self.assertEqual(r['task']['a']['value'],compare(c['input'])['task']['a']['value'])
 def test_alternative_feasible_kernel(self):
  r=compare(controls()[7]['input']);g=r['a_to_b']['garbling'];k=[[F(1,4),F(1,4),F(1,2)]]*2
  from channellab.model import encode
  g['kernel']=encode(k);g['row_sums']=encode([F(1),F(1)]);g['signal_joint']=encode([[F(1,3)*v for v in k[0]],[F(2,3)*v for v in k[1]]]);self.assertTrue(verify(r))
 def test_information_value_nonnegative(self):
  for c in controls():
   r=compare(c['input'])
   for k in ['a','b']:self.assertGreaterEqual(F(*r['task'][k]['information_value']),0)
 def test_all_primitives_tamper(self):
  r=compare(controls()[0]['input']);paths=[]
  def walk(x,path):
   if type(x)is dict:
    for k,v in x.items():
     if path or k!='input':walk(v,path+[k])
   elif type(x)is list:
    for i,v in enumerate(x):walk(v,path+[i])
   else:paths.append(path)
  walk(r,[]);rejected=0
  for path in paths:
   x=copy.deepcopy(r);o=x
   for k in path[:-1]:o=o[k]
   v=o[path[-1]];o[path[-1]]=not v if type(v)is bool else v+1 if type(v)is int else 'changed'
   with self.assertRaises(ValueError):verify(x)
   rejected+=1
  print('PRIMITIVE_FORGERIES',rejected)
 def test_extra_fields_and_type_confusion(self):
  r=compare(controls()[1]['input']);r['extra']=1
  with self.assertRaises(ValueError):verify(r)
  r=compare(controls()[0]['input']);r['version']=True
  with self.assertRaises(ValueError):verify(r)
  r=compare(controls()[1]['input']);r['a_to_b']['garbling']['kernel'][0][0][1]=True
  with self.assertRaises(ValueError):verify(r)
 def test_invalid_schema(self):
  base=controls()[0]['input']
  for path,v in [('version',True),('prior',0),('prior',1),('prior',True),('prior',[1,-2]),('prior',[1,1000001]),('a',[[1],[0]]),('b',[[1,-1],[0,1]]),('payoffs',[[101],[0]])]:
   x=copy.deepcopy(base);x[path]=v
   with self.assertRaises(ValueError):compare(x)
  x=copy.deepcopy(base);x['unknown']=1
  with self.assertRaises(ValueError):compare(x)
 def test_strict_json(self):
  for s in ['{"a":1,"a":2}','{"x":1e0}','{"x":0.5}','NaN','[1,]']:
   with self.assertRaises(ValueError):loads(s)
 def test_input_not_mutated(self):
  for c in controls():
   p=c['input'];old=copy.deepcopy(p);compare(p);self.assertEqual(p,old)
 def test_cli(self):
  with tempfile.TemporaryDirectory()as t:
   p=Path(t)/'x.json';p.write_text(json.dumps(controls()[0]['input']));r=subprocess.run([sys.executable,'-m','channellab','run',str(p)],text=True,capture_output=True);self.assertEqual(r.returncode,0);p.write_text(r.stdout);v=subprocess.run([sys.executable,'-m','channellab','verify',str(p)],text=True,capture_output=True);self.assertEqual(json.loads(v.stdout),{'valid':True});p.write_text('{"bad":true}');bad=subprocess.run([sys.executable,'-m','channellab','run',str(p)],text=True,capture_output=True);self.assertEqual(bad.returncode,2);self.assertEqual(bad.stdout,'')
if __name__=='__main__':unittest.main()
