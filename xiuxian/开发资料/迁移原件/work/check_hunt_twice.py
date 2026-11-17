import sys,pathlib
sys.path.insert(0,str(pathlib.Path('outputs/太古仙尊实验版').resolve()))
from daily_tasks import ApprovedTasks
class Fake(ApprovedTasks):
    def __init__(self,count,remaining=1,running=False):
        self.ledger={'hunt_started':count};self.pending={};self.starts=0
        self.remaining=remaining;self.running=running
    def secrets_open(self):pass
    def secrets_back(self):pass
    def tap(self,*a):pass
    def wait(self,*a):pass
    def snap(self):pass
    def close(self,*a):pass
    def find(self,*a):return not self.running
    def words(self,roi):
        if roi==(115,575,607,685):return '75000陨铁125000木材'
        return '14:58' if self.running else f'每百年可游猎2次，剩余{self.remaining}次'
    def click(self,*a):pass
    def text_button(self,*a):self.starts+=1;self.running=True
    def ledger_save(self):pass
    def record(self,*a):pass
    def log(self,*a):pass
    def wait_words(self,page,roi,predicate):assert predicate(self.words(roi))
b=Fake(True);b.hunt();assert b.starts==1 and b.ledger['hunt_started']==2 and not b.pending['hunt']
b.running=False;b.hunt();assert b.starts==1
b=Fake(0,2);b.hunt();assert b.ledger['hunt_started']==1 and b.pending['hunt']
b.hunt();assert b.starts==1 and b.pending['hunt']
b=Fake(0,0);b.hunt();assert b.starts==0 and b.ledger['hunt_started']==2
print('PASS: two daily starts, legacy boolean migration, countdown retained, zero quota, no third start.')
