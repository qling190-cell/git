import pathlib,sys
sys.path.insert(0,'E:/xiuxian')
from daily_tasks import ApprovedTasks

class Treasure(ApprovedTasks):
    def __init__(self,immediate):
        self.ledger={};self.pending={};self.phase='ready';self.immediate=immediate;self.actions=[]
    def secrets_open(self):pass
    def secrets_back(self):pass
    def tap(self,*a):pass
    def wait(self,*a):pass
    def snap(self):pass
    def text(self,*a):return []
    def words(self,roi):
        if roi==(105,520,615,735):return '确认开始寻宝' if self.phase=='confirm' else '已降伏全部妖兽'
        return '29:58' if self.phase=='running' else ''
    def find(self,name):return self.phase!='confirm'
    def text_button(self,label,*a):
        self.actions.append(label)
        if label=='寻宝':self.phase='running' if self.immediate else 'confirm'
        if label=='确定':self.phase='running'
    def wait_words(self,page,roi,predicate):assert predicate(self.words(roi))
    def ledger_save(self):pass
    def record(self,*a):pass
    def close(self,*a):pass
for immediate,actions in ((True,['寻宝']),(False,['寻宝','确定'])):
    b=Treasure(immediate);b.treasure()
    assert b.actions==actions and b.ledger['treasure_started'] and b.pending['treasure']

class Hunt(ApprovedTasks):
    def __init__(self):self.ledger={};self.pending={}
    def secrets_open(self):pass
    def secrets_back(self):pass
    def tap(self,*a):pass
    def wait(self,*a):pass
    def snap(self):pass
    def words(self,*a):return '每百年可游猎2次，剩余0次'
    def find(self,*a):return False
    def ledger_save(self):pass
    def record(self,*a):pass
    def log(self,*a):pass
    def close(self,*a):pass
b=Hunt();b.hunt();assert b.ledger['hunt_started']==2 and not b.pending['hunt']
print('PASS: direct-start and confirmation treasure flows; exhausted hunt with grey start button.')
