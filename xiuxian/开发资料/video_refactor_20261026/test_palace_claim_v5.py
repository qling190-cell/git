import pathlib,sys,py_compile
sys.path.insert(0,'E:/xiuxian')
from palace_tasks import PalaceTasks
class Fake(PalaceTasks):
    def __init__(self):self.ledger={};self.pending={};self.actions=[];self.phase='ready'
    def snap(self):pass
    def find(self,page):return True
    def button_positions(self,labels,roi):
        if '完成' in labels or ('领取' in labels and '确认' not in labels):assert roi[3]>=1250,'bottom button excluded'
        if self.phase=='ready' and ('完成' in labels or '领取' in labels):return [(360,1250)]
        if self.phase=='popup' and '确认' in labels:return [(360,900)]
        return []
    def words(self,*a):return '获得奖励 玲珑木 天阙石 百炼金' if self.phase=='popup' else ''
    def tap(self,*point):
        self.actions.append(point);self.phase={'ready':'popup','popup':'done'}[self.phase]
    def pause_animation(self,*a):pass
    def ledger_save(self):pass
    def wait(self,*a):pass
    def log(self,*a):pass
    def record(self,*a):pass
for page in ('palace_court','palace_cultivate'):
    b=Fake();assert b.collect_palace_reward(page,page,page)
    assert b.actions==[(360,1250),(360,900)] and b.ledger[page+'_reward_done']
b=Fake();b.phase='done';assert not b.collect_palace_reward('palace_court','palace_court','court') and not b.ledger
class Chat(Fake):
    def words(self,*a):return '历史聊天：额外获得奖励功德3000'
b=Chat();b.phase='done';assert not b.palace_reward_popup('palace_cultivate') and not b.actions
py_compile.compile('E:/xiuxian/palace_tasks.py',doraise=True)
print('PASS: court finish -> reward confirm; cultivate claim -> reward confirm; bottom buttons included; no button means no completion')
