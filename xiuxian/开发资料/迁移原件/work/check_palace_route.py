import pathlib,sys
sys.path.insert(0,str(pathlib.Path('outputs/太古仙尊实验版').resolve()))
from palace_tasks import PalaceTasks
from navigation import Navigation,DAILY_GROUPS
class Fake(Navigation,PalaceTasks):
    def __init__(self):
        self.cfg={'realm_menu':True};self.pending={};self.page='main'
        self.actions=[];self.entries=0;self.exits=0
    def snap(self):pass
    def find(self,name):return self.page==name
    def require(self,name):assert self.page==name
    def realm(self,*a):self.page='main'
    def recover_to_main(self,*a):self.page='main'
    def tap(self,*a):self.page='palace_map';self.entries+=1
    def wait(self,name):assert self.page==name
    def back(self,page,target):
        assert self.page==page
        self.page=target;self.exits+=1
    def log(self,*a):pass
    def _task(self,name):assert self.page=='palace_map';self.actions.append(name)
    def _palace_lamp(self):self._task('lamp')
    def _palace_garden(self):self._task('garden')
    def _palace_cultivate(self):self._task('cultivate')
    def _palace_court(self):self._task('court')

group=DAILY_GROUPS[-1]
assert group[2]==['palace_lamp','palace_garden','palace_cultivate','palace_court']
b=Fake();assert b.run_groups([group])
assert b.actions==['lamp','garden','cultivate','court'] and b.entries==1 and b.exits==1
b=Fake();assert b.palace()
assert b.actions==['lamp','garden','cultivate','court'] and b.entries==1 and b.exits==1
b=Fake();b.palace_garden();assert b.entries==1 and b.exits==1
b=Fake();b.resume_daily=True;b.daily_progress={'completed':['palace_lamp','palace_garden']}
b.save_daily_progress=lambda *a:None
assert b.run_groups([group])
assert b.actions==['cultivate','court'] and b.entries==1 and b.exits==1
print('PASS: lamp first; shared palace map; one final exit; standalone return; partial resume retains shared route.')
