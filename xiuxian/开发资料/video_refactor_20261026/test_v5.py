import pathlib,sys,time as wall_time
import cv2,numpy as np
ROOT=pathlib.Path('E:/xiuxian');sys.path.insert(0,str(ROOT))
from assistant import Bot
from night_engine import NightTasks,destination_name
import night_engine
from daily_tasks import TaskStop
from workflow import DAILY_GROUPS,shared_parent,TASK_ENTRY
from hierarchy import Hierarchy
from navigation import Navigation

b=Bot()
fixtures=ROOT/'开发资料/work'
for name in ('night_selected_failed','night_oppo_stationed','night_oppo_latest'):
    frame=cv2.imdecode(np.frombuffer((fixtures/(name+'.png')).read_bytes(),np.uint8),1)
    found=b.night_buttons(frame)
    print(name,[p['name'] for p in found])
    assert len(found)==4,name
    assert all(p['stationed'] or p['complete'] for p in found)
frame=cv2.imdecode(np.frombuffer((ROOT/'开发资料/video_refactor_20261026/live_before.png').read_bytes(),np.uint8),1)
assert b.main_screen(frame)=='yuanji','appearance change must not block realm navigation'
assert destination_name('埋骨凶间')=='埋骨凶涧'
b.ledger['night_stationed']=['括苍洞天','死煞恶土','燃灭虚境','埋骨凶涧','消匿残域','陨神废墟','无矩虚境']
frame=cv2.imdecode(np.frombuffer((fixtures/'night_oppo_stationed.png').read_bytes(),np.uint8),1)
assert len(b.night_buttons(frame))==4,'cached but no longer stationed targets must not be selected'

class FakeNight(NightTasks):
    def __init__(self,count=4,blocked=None,quota=60):
        self.ledger={};self.pending={};self.current='A';self.names=list('ABCD')[:count]
        self.running={n:False for n in self.names};self.claims={n:False for n in self.names}
        self.started=[];self.claimed=[];self.checked=[];self.exited=False;self.quota=quota
        self.blocked=blocked
        self.good=cv2.cvtColor(np.full((1280,720,3),(60,200,200),np.uint8),cv2.COLOR_HSV2BGR)
        self.bad=cv2.cvtColor(np.full((1280,720,3),(0,200,200),np.uint8),cv2.COLOR_HSV2BGR)
        self.frame=self.good
    def snap(self):self.frame=self.bad if self.current==self.blocked else self.good
    def find(self,name):
        if name=='night_claim':return self.claims[self.current]
        return True
    def require(self,*a):pass
    def night_discover(self):return self.names
    def night_locate(self,name):self.current=name;self.checked.append(name);self.snap()
    def night_quota(self):return self.quota
    def night_rounds(self):return 15
    def night_running(self):return self.running[self.current]
    def tap(self,*a):pass
    def click(self,name):
        if name=='night_claim':
            self.claimed.append(self.current);self.claims[self.current]=False
        if name=='night_start':
            assert self.ledger['night_transactions'][self.current]['phase']=='reserved'
            self.started.append(self.current);self.running[self.current]=True;self.quota-=15
    def wait_gone(self,*a):pass
    def ledger_save(self):pass
    def log(self,*a):pass
    def record(self,*a):pass
    def close(self,*a):self.exited=True;assert self.checked==self.names
    def back(self,*a):pass

original=night_engine.time;night_engine.time=wall_time
try:
    n=FakeNight();assert n.night()
    assert n.started==list('ABCD') and n.quota==0 and n.ledger['night_started']==60 and n.pending['night']
    n.checked=[];assert n.night();assert len(n.started)==4,'running tasks must not restart'
    for key in n.names:n.running[key]=False;n.claims[key]=True
    n.checked=[];assert n.night();assert len(n.claimed)==4 and len(n.started)==4 and not n.pending['night']
    n=FakeNight(blocked='B');assert n.night() is False
    assert n.checked==list('ABCD') and n.started==list('ACD') and n.pending['night']
    n=FakeNight(count=3);assert n.night() is False and len(n.started)==3
    n=FakeNight(quota=40);assert n.night() is False and n.started==list('AB')
    n=FakeNight();n.running['A']=True;n.quota=45
    n.ledger['night_transactions']={'A':{'phase':'reserved','before_quota':60}}
    assert n.night() and n.started==list('BCD') and n.ledger['night_started']==60
finally:night_engine.time=original

assert [r for r,_,_ in DAILY_GROUPS]==['mortal','heaven','void','yuanji']
assert DAILY_GROUPS[0][2][0]=='travel'
assert [t for t in DAILY_GROUPS[1][2] if t not in ('creation_dew','enlightenment')][:12]==['guard','quiz','gamble','jade','lecture','forbidden','duel','tower','treasure','hunt','demon','smallworld']
assert DAILY_GROUPS[2][2].index('night')<DAILY_GROUPS[2][2].index('familycare')<DAILY_GROUPS[2][2].index('family')
assert DAILY_GROUPS[3][2][:3]==['palace_lamp','palace_cultivate','palace_court']
assert shared_parent('guard','quiz')=='teaching'
assert shared_parent('quiz','gamble')=='island'
assert shared_parent('gamble','jade')=='market'
assert shared_parent('jade','creation_dew')=='market_shop'
assert shared_parent('creation_dew','enlightenment')=='island'
assert shared_parent('travel','saint_beast')=='travel'
assert shared_parent('tower','treasure')=='heaven_travel'
assert shared_parent('treasure','hunt')=='secrets'
assert shared_parent('familycare','family')=='immortal_home'
assert shared_parent('provisions','gifts')=='immortal_home'
assert shared_parent('palace_cultivate','palace_court')=='palace_map'
assert shared_parent('night','familycare') is None
for _,_,tasks in DAILY_GROUPS:
    assert len(tasks)==len(set(tasks))
    assert all(hasattr(Bot,task) for task in tasks)

class Route(Navigation):
    def __init__(self):self.cfg={'realm_menu':True};self.pending={};self.calls=[];self.holds=[]
    def recover_to_main(self,*a):pass
    def realm(self,*a):pass
    def log(self,*a):pass
    def run_task(self,task):self.calls.append(task);self.holds.append(self._route_hold);return True
r=Route();assert r.run_groups(DAILY_GROUPS)
assert r.calls==[t for _,_,tasks in DAILY_GROUPS for t in tasks]
assert r.holds[r.calls.index('guard')]=='teaching'
assert r._route_hold is None

print('PASS v5: screenshots, new appearance, all-four 60 rounds, reservations, claims, partial failure, video order and hierarchy.')
