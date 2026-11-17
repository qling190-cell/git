import sys
sys.path.insert(0,'E:/xiuxian')
from workflow import DAILY_GROUPS,PALACE_TASKS,shared_parent
from palace_tasks import PalaceTasks
from navigation import Navigation
assert tuple(DAILY_GROUPS[3][2])==PALACE_TASKS
assert PALACE_TASKS[0]=='palace_lamp'
assert all(shared_parent(a,b)=='palace_map' for a,b in zip(PALACE_TASKS,PALACE_TASKS[1:]))
class Fake(PalaceTasks):
    cfg={'realm_menu':True}
    def __init__(self):self.page='yuanji_nav';self.entries=0;self.exits=0;self.order=[]
    def palace_open(self):
        if self.page!='palace_map':self.entries+=1;self.page='palace_map'
    def snap(self):pass
    def require(self,page):assert self.page==page
    def back(self,page,target):
        assert self.page==page;self.page=target
        if target=='yuanji_nav':self.exits+=1
    def run_task(self,task):self.order.append(task);getattr(self,task)();return True
    def _palace_lamp(self):assert self.page=='palace_map'
    def building(self):
        assert self.page=='palace_map';self.page='building';self.back('building','palace_map')
    _palace_cultivate=building
    _palace_court=building
    _palace_garden=building
b=Fake();assert b.palace();assert tuple(b.order)==PALACE_TASKS and b.entries==1 and b.exits==1
class Groups(Navigation):
    cfg={'realm_menu':True};resume_daily=True
    def __init__(self):self.daily_progress={'completed':list(PALACE_TASKS)};self.pending={};self.called=[]
    def recover_to_main(self,*a):pass
    def realm(self,*a):pass
    def log(self,*a):pass
    def save_daily_progress(self,*a):pass
    def run_task(self,t):self.called.append(t);return True
b=Groups();b.run_groups([DAILY_GROUPS[3]]);assert b.called==[]
print('PASS: lamp first in complete palace flow; shared map throughout; one entry/exit; resume does not replay completed palace tasks')
