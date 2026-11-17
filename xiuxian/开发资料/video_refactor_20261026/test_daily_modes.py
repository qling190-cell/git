import sys,pathlib,tempfile,json,ast
sys.path.insert(0,'E:/xiuxian')
from navigation import Navigation
from workflow import DAILY_GROUPS
class Fake(Navigation):
 def __init__(self,root):
  self.day='2026-10-27';self.ledger_path=root/'account.json';self.ledger={'buy_人参果':2,'hunt_started':1};self.pending={};self.cfg={'realm_menu':True};self.called=[];self.logs=[];self.halt=None
 def log(self,s):self.logs.append(s)
 def recover_to_main(self,*a):pass
 def realm(self,*a):pass
 def record(self,*a):pass
 def run_task(self,t):
  self.called.append(t)
  if t==self.halt:raise RuntimeError('interrupted')
  return True
G=[('mortal','人间',['travel','practice']),('heaven','仙界',['hunt','sword']),('yuanji','元极',['palace_lamp','palace_court'])]
old={'day':'2026-10-27','completed':['travel','practice','hunt'],'pending':{'hunt':True},'current':'sword'}
with tempfile.TemporaryDirectory() as d:
 r=pathlib.Path(d);p=r/'account.progress.json'
 p.write_text(json.dumps(old),encoding='utf-8');b=Fake(r);before=b.ledger.copy();b.prepare_daily_progress(False)
 assert b.daily_progress['completed']==[] and b.pending=={'hunt':True} and b.ledger==before
 b.run_groups(G);assert b.called==['travel','practice','hunt','sword','palace_lamp','palace_court'],b.called
 p.write_text(json.dumps(old),encoding='utf-8');b=Fake(r);b.prepare_daily_progress(True);assert b.daily_progress['current']=='sword'
 b.run_groups(G);assert b.called==['sword','palace_lamp','palace_court'],b.called
 # Even an earlier unfinished/deferred task must not move the resume cursor backwards.
 old['completed']=['travel'];p.write_text(json.dumps(old),encoding='utf-8');b=Fake(r);b.prepare_daily_progress(True);b.halt='palace_lamp'
 try:b.run_groups(G)
 except RuntimeError:pass
 assert b.called==['sword','palace_lamp'] and json.loads(p.read_text())['current']=='palace_lamp'
 b=Fake(r);b.prepare_daily_progress(True);b.run_groups(G);assert b.called==['palace_lamp','palace_court']
 assert json.loads(p.read_text())['current'] is None
 # Removed forbidden cursor migrates in place to the replacement, not back to earlier realms.
 p.write_text(json.dumps({'day':'2026-10-27','completed':[],'pending':{'star_forbidden':True},'current':'star_forbidden'}),encoding='utf-8')
 b=Fake(r);b.prepare_daily_progress(True);assert b.daily_progress['current']=='star_way' and 'star_forbidden' not in b.pending
 b.run_groups(DAILY_GROUPS);assert b.called[0]=='star_way' and 'star_forbidden' not in b.called
 # A process interrupted after one task saved the next task at a realm boundary.
 b=Fake(r);b.prepare_daily_progress(False);b.halt='hunt'
 try:b.run_groups(G)
 except RuntimeError:pass
 assert json.loads(p.read_text())['current']=='hunt'
 old['day']='2026-10-26';p.write_text(json.dumps(old),encoding='utf-8');b=Fake(r);b.prepare_daily_progress(True);b.run_groups(G);assert b.called[0]=='travel'
 # Entire main pass done: resume does not re-open the lamp or invalidate hunt progress.
 p.write_text(json.dumps({'day':'2026-10-27','completed':[t for _,_,ts in G for t in ts],'pending':{'hunt':True},'current':None}),encoding='utf-8')
 b=Fake(r);b.prepare_daily_progress(True);b.run_groups(G);assert not b.called
 b.run_groups(G,pending_only=True);assert b.called==['hunt']
s=pathlib.Path('E:/xiuxian/assistant.py').read_text(encoding='utf-8');assert "prepare_daily_progress(resume=args.task=='resume')" in s
print('PASS: all from first task; resume from exact cursor; no earlier deferred-task/lamp replay; interrupted and realm-boundary checkpoint; date reset; pending finish retained; consumption ledger untouched; CLI modes separate')
