import ast,copy,json,subprocess,sys,tempfile,unittest
from fractions import Fraction as F
from pathlib import Path
from channellab import prior_atlas,verify_atlas
from channellab.controls import controls
from channellab.engine import decision
from channellab.model import parse,encode
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from cases import cases

class AtlasTests(unittest.TestCase):
 def test_710_complete_atlases(self):
  rs=[prior_atlas(p)for p in cases()]
  self.assertEqual(len(rs),710)
  for r in rs:self.assertTrue(verify_atlas(r))
  print('ATLAS_COUNTS',len(rs),sum(sum(len(x)for x in r['policies'].values())for r in rs),sum(len(r['knots'])for r in rs),sum(len(r['intervals'])for r in rs))
 def test_exact_rank_reversal_not_just_supplied_prior_tie(self):
  r=prior_atlas(controls()[0]['input']);self.assertEqual([F(*x['prior'])for x in r['knots']],[F(0),F(1,3),F(1,2),F(2,3),F(1)])
  self.assertEqual([x['ranking']for x in r['intervals']],['a','a','b','b']);self.assertEqual([x['ranking']for x in r['knots']],['tie','a','tie','b','tie'])
 def test_rank_root_without_any_policy_change(self):
  p=json.loads((Path(__file__).resolve().parents[1]/'examples/prior_crossing.json').read_text());r=prior_atlas(p);self.assertTrue(verify_atlas(r));bounds={F(*x)for rows in r['policies'].values()for row in rows if row['optimal_range']for x in row['optimal_range']};self.assertNotIn(F(1,3),bounds);self.assertIn(F(1,3),[F(*x['prior'])for x in r['knots']]);self.assertEqual(next(x for x in r['knots']if F(*x['prior'])==F(1,3))['ranking'],'tie')
 def test_importing_checker_does_not_load_generator(self):
  code='from channellab import verify_atlas;import sys;assert "channellab.atlas" not in sys.modules and "channellab.engine" not in sys.modules'
  self.assertEqual(subprocess.run([sys.executable,'-c',code],capture_output=True).returncode,0)
 def test_values_at_every_knot_and_two_cell_points(self):
  for c in controls():
   r=prior_atlas(c['input']);_,a,b,u=parse(c['input'])
   for row in r['knots']:
    p=F(*row['prior'])
    for k,ch in [('a',a),('b',b),('none',[[F(1)],[F(1)]])]:
     d=decision(ch,p,u);self.assertEqual(row[k]['value'],encode(d['value']));self.assertEqual(row[k]['optimal_policies'],d['optimal_policies'])
   for row in r['intervals']:
    l,z=F(*row['left']),F(*row['right'])
    for p in [(2*l+z)/3,(l+2*z)/3]:
     for k,ch in [('a',a),('b',b),('none',[[F(1)],[F(1)]])]:
      d=decision(ch,p,u);x,y=map(lambda q:F(*q),row[k]['coefficients']);self.assertEqual(x+p*y,d['value']);self.assertEqual(row[k]['optimal_policies'],d['optimal_policies'])
 def test_policy_range_dominance_for_all_710(self):
  for data in cases():
   r=prior_atlas(data)
   for rows in r['policies'].values():
    for i,row in enumerate(rows):
     interval=row['optimal_range']
     if interval is None:continue
     l,h=[F(*q)for q in interval]
     self.assertTrue(0<=l<=h<=1)
     for p in [l,h,(l+h)/2]:
      x,y=map(lambda q:F(*q),row['coefficients'])
      self.assertTrue(all(x+p*y>=F(*v['coefficients'][0])+p*F(*v['coefficients'][1])for v in rows))
 def test_zero_mass_duplicate_actions_and_endpoint_only_policies(self):
  p=copy.deepcopy(controls()[6]['input']);p['payoffs']=[[1,0,0],[0,1,1]];r=prior_atlas(p);self.assertTrue(verify_atlas(r));self.assertEqual(len(r['policies']['a']),27)
  # The third signal is identically impossible; all its actions must remain tied.
  for x in r['knots']+r['intervals']:
   chosen=[r['policies']['a'][i]['choices']for i in x['a']['optimal_policies']]
   self.assertEqual({ch[2]for ch in chosen},{0,1,2})
  base=prior_atlas(controls()[0]['input']);self.assertEqual(base['policies']['a'][0]['optimal_range'],[[0,1],[0,1]])
 def test_all_tied_negative_payoffs_and_one_action(self):
  for payoffs in [[[-2,-2,-2],[-7,-7,-7]],[[-2],[-7]]]:
   p=copy.deepcopy(controls()[0]['input']);p['payoffs']=payoffs;r=prior_atlas(p);self.assertTrue(verify_atlas(r));self.assertEqual(len(r['knots']),2);self.assertEqual(r['intervals'][0]['ranking'],'tie')
   self.assertTrue(all(x['optimal_range']==[[0,1],[1,1]]for x in r['policies']['a']))
 def test_prior_independence_of_atlas_not_input(self):
  for c in controls():
   p=copy.deepcopy(c['input']);r=prior_atlas(p);r.pop('input');p['prior']=[1,5];s=prior_atlas(p);s.pop('input');self.assertEqual(r,s)
 def test_tiny_prior_cell_is_not_sampled_away(self):
  p=copy.deepcopy(controls()[0]['input']);p['a']=[[1,0],[0,1]];p['b']=[[1],[1]];p['payoffs']=[[[1,1000000],0],[0,1]];r=prior_atlas(p);self.assertTrue(verify_atlas(r));self.assertIn(F(1,1000001),[F(*x['prior'])for x in r['knots']]);self.assertTrue(all(x['ranking']=='a'for x in r['intervals']))
 def test_state_reflection(self):
  for c in controls():
   p=copy.deepcopy(c['input']);r=prior_atlas(p)
   for k in ['a','b','payoffs']:p[k]=p[k][::-1]
   s=prior_atlas(p);self.assertEqual([F(*x['prior'])for x in s['knots']],[1-F(*x['prior'])for x in r['knots'][::-1]])
   self.assertEqual([x['ranking']for x in s['knots']],[x['ranking']for x in r['knots'][::-1]])
 def test_all_noninput_primitives_rejected(self):
  r=prior_atlas(controls()[0]['input']);paths=[]
  def walk(x,path):
   if type(x)is dict:
    for k,v in x.items():
     if path or k!='input':walk(v,path+[k])
   elif type(x)is list:
    for i,v in enumerate(x):walk(v,path+[i])
   else:paths.append(path)
  walk(r,[])
  for path in paths:
   x=copy.deepcopy(r);o=x
   for k in path[:-1]:o=o[k]
   v=o[path[-1]];o[path[-1]]=not v if type(v)is bool else v+1 if type(v)is int else 'changed'
   with self.assertRaises(ValueError):verify_atlas(x)
  print('ATLAS_PRIMITIVE_FORGERIES',len(paths))
 def test_omissions_extras_noncanonical_and_type_confusion(self):
  original=prior_atlas(controls()[0]['input'])
  for key in ['knots','intervals']:
   x=copy.deepcopy(original);x[key].pop(1)
   with self.assertRaises(ValueError):verify_atlas(x)
  for path,value in [(['version'],True),(['extra'],0),(['knots',0,'prior'],[0,2]),(['policies','a',0,'optimal_range'],None)]:
   x=copy.deepcopy(original);o=x
   for k in path[:-1]:o=o[k]
   o[path[-1]]=value
   with self.assertRaises(ValueError):verify_atlas(x)
  for r in [None,{},[],{'input':{}},dict(original,intervals=None)]:
   with self.assertRaises(ValueError):verify_atlas(r)
 def test_verifier_imports_only_validation(self):
  tree=ast.parse((Path(__file__).resolve().parents[1]/'channellab/atlas_verify.py').read_text());local=[x.module for x in ast.walk(tree)if isinstance(x,ast.ImportFrom)and x.level];self.assertEqual(local,['model'])
 def test_cli_and_no_partial_stdout(self):
  with tempfile.TemporaryDirectory()as t:
   p=Path(t)/'input.json';p.write_text(json.dumps(controls()[0]['input']));cmd=[sys.executable,'-m','channellab'];r=subprocess.run(cmd+['atlas',str(p)],capture_output=True,text=True);self.assertEqual(r.returncode,0);self.assertEqual(json.loads(r.stdout),prior_atlas(controls()[0]['input']));p.write_text(r.stdout);v=subprocess.run(cmd+['verify-atlas',str(p)],capture_output=True,text=True);self.assertEqual(json.loads(v.stdout),{'valid':True});p.write_text('{}');v=subprocess.run(cmd+['verify-atlas',str(p)],capture_output=True,text=True);self.assertEqual(v.returncode,2);self.assertEqual(v.stdout,'')
if __name__=='__main__':unittest.main()
