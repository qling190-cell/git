import pathlib,sys,cv2,numpy as np
sys.path.insert(0,str(pathlib.Path('outputs/太古仙尊实验版').resolve()))
from daily_tasks import ApprovedTasks,TaskStop
class Fake(ApprovedTasks):
    def __init__(self,disabled=False,fail=False):
        self.ledger={'tree_claimed':True};self.phase='disabled' if disabled else 'ready'
        self.frame=cv2.cvtColor(np.full((1280,720,3),(25,180,220),dtype=np.uint8),cv2.COLOR_HSV2BGR)
        self.fail=fail;self.confirmed=False;self.next_task=False
    def home_open(self):pass
    def snap(self):pass
    def require(self,*a):pass
    def find(self,name):return name=='ancestral_disabled' and self.phase=='disabled'
    def wait(self,name):
        if name=='ancestral_disabled':assert self.confirmed
    def tap(self,x,y):
        if (x,y)==(567,705):
            assert not self.ledger.get('ancestral');self.phase='prompt'
        if (x,y)==(490,775):
            assert self.phase=='prompt' and not self.ledger.get('ancestral')
            self.confirmed=True;self.phase='disabled'
        if (x,y)==(530,585):
            assert self.phase=='disabled'
            self.next_task=True
    def button_positions(self,*a):
        if self.fail:raise TaskStop('simulated unreadable dialog')
        return [(490,775)] if self.phase=='prompt' else []
    def words(self,*a):return '确定要一键指点吗？' if self.phase=='prompt' else ''
    def ledger_save(self):assert self.confirmed
    def record(self,*a):pass
    def back(self,*a):pass
    def log(self,*a):pass
b=Fake();b.familycare();assert b.confirmed and b.ledger['ancestral'] and b.next_task
b=Fake(disabled=True);b.familycare();assert not b.confirmed and b.next_task
b=Fake(fail=True)
try:b.familycare()
except TaskStop:pass
else:raise AssertionError('unreadable confirmation must stop')
assert not b.ledger.get('ancestral') and not b.next_task
print('PASS: one-click guidance then confirm before next task; disabled skip; failed confirmation does not mark completion.')
