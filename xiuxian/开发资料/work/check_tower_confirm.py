import pathlib,sys
sys.path.insert(0,str(pathlib.Path('outputs/太古仙尊实验版').resolve()))
from daily_tasks import ApprovedTasks
from navigation import Navigation

class Tower(ApprovedTasks):
    def __init__(self,batch,claimed=False):
        self._secrets_batch=batch;self.claimed=claimed;self.stage='tower';self.buttons=[];self.backs=[]
    def realm(self,*a):pass
    def tap(self,x,y):
        if (x,y)==(360,1190):self.stage='prompt'
    def wait(self,*a):pass
    def snap(self):pass
    def words(self,roi):
        if roi==(60,300,660,1000):return '每日只能领取一次，确定现在就领取吗' if self.stage=='prompt' else ''
        return '今日已领取' if self.claimed else '领取奖励'
    def text(self,*a):return [{'text':'领取奖励','confidence':1,'pos':(360,1190)}]
    def text_button(self,label,*a):
        assert self.stage=='prompt' and label=='确定'
        self.buttons.append(label);self.claimed=True;self.stage='tower'
    def find(self,name):return self.stage==name
    def reward_popup(self,*a):pass
    def wait_words(self,page,roi,predicate):assert predicate(self.words(roi))
    def record(self,*a):pass
    def back(self,page,target):self.backs.append((page,target))

b=Tower(True);b.tower()
assert b.buttons==['确定'] and b.backs==[('tower','heaven_travel')]
b=Tower(False);b.tower();assert len(b.backs)==2
b=Tower(True,True);b.tower();assert not b.buttons and len(b.backs)==1

class Entry(ApprovedTasks):
    def __init__(self):self.taps=[]
    def snap(self):pass
    def find(self,name):return name=='heaven_travel'
    def tap(self,*a):self.taps.append(a)
    def wait(self,name):assert name=='secrets'
    def realm(self,*a):raise AssertionError('must not return to main')
b=Entry();b.secrets_open();assert b.taps==[(500,995)]
print('PASS: tower claim then confirm, already claimed skip, batch stays in travel, direct travel-to-secrets route.')
