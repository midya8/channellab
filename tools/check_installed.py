"""Fresh wheel and two installed CLI paths, outside the checkout."""
import json,os,subprocess,sys,tempfile,venv
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root))
from channellab import compare
from channellab.controls import controls
expected=[compare(c['input'])for c in controls()]
def run(args,**kw):
 p=subprocess.run(args,capture_output=True,text=True,**kw)
 if p.returncode:raise RuntimeError(str(args)+'\n'+p.stdout+'\n'+p.stderr)
 return p
with tempfile.TemporaryDirectory(prefix='channellab-installed-')as t:
 d=Path(t);w=d/'wheel';w.mkdir();run([sys.executable,'-m','pip','wheel','--no-deps','--no-build-isolation',str(root),'-w',str(w)],cwd=d)
 venv.EnvBuilder(with_pip=True).create(d/'venv');py=d/'venv/bin/python';entry=d/'venv/bin/channellab';wheel=next(w.glob('*.whl'));run([str(py),'-m','pip','install','--no-deps','--force-reinstall',str(wheel)],cwd=d)
 env=os.environ.copy();env.pop('PYTHONPATH',None)
 code='import channellab,channellab.model,channellab.engine,channellab.verify,channellab.controls,channellab.__main__;import importlib;ms=[importlib.import_module("channellab"+s)for s in ["",".model",".engine",".verify",".controls",".__main__"]];assert all("site-packages"in m.__file__ for m in ms);print(len(ms))'
 origins=int(run([str(py),'-c',code],cwd=d,env=env).stdout);direct=cli=0
 for c,expected_report in zip(controls(),expected):
  src=d/'input.json';src.write_text(json.dumps(c['input']));report=d/'report.json'
  for cmd in [[str(entry)],[str(py),'-m','channellab']]:
   raw=run(cmd+['run',str(src)],cwd=d,env=env).stdout;assert json.loads(raw)==expected_report;report.write_text(raw);assert json.loads(run(cmd+['verify',str(report)],cwd=d,env=env).stdout)=={'valid':True}
  for mode in ['relation','hinge']:
   r=json.loads(json.dumps(expected_report))
   if mode=='relation':r['relation']='changed'
   else:r['hinges'][0]['a'][0]+=1
   report.write_text(json.dumps(r));run([str(py),'-c','import json,sys;from channellab import verify\ntry:verify(json.load(open(sys.argv[1])))\nexcept ValueError:pass\nelse:raise AssertionError("forgery accepted")',str(report)],cwd=d,env=env);direct+=1
   for cmd in [[str(entry)],[str(py),'-m','channellab']]:
    x=subprocess.run(cmd+['verify',str(report)],cwd=d,env=env,capture_output=True,text=True);assert x.returncode==2 and x.stdout=='';cli+=1
 assert json.loads(run([str(entry),'demo'],cwd=d,env=env).stdout)==expected[0]
 print(json.dumps({'wheel':wheel.name,'origins':origins,'controls':len(expected),'entrypoints':2,'direct_forgery_rejections':direct,'cli_forgery_rejections':cli}))
