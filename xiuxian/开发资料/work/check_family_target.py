import pathlib,sys
sys.path.insert(0,str(pathlib.Path('outputs/太古仙尊实验版').resolve()))
from assistant import Bot
class Fake(Bot):
    def __init__(self,running=False,claim=False,remaining=2):
        self.cfg={};self.pending={};self.running=running;self.claim=claim
        self.remaining=remaining;self.target='九尾狐宗';self.actions=[]
    def realm(self,*a):pass
    def tap(self,*a):pass
    def wait(self,*a):pass
    def snap(self):pass
    def require(self,*a):pass
    def find(self,name):
        return self.claim if name=='family_claim' else not self.running if name=='family_start' else False
    def click(self,name):
        self.actions.append(name)
        if name=='family_claim':self.claim=False
        if name=='family_start':self.running=True
    def wait_gone(self,*a):pass
    def line(self,*a):
        assert not self.running,'countdown must exit before quota OCR'
        return f'尚可征收{self.remaining}次'
    def words(self,roi):
        if roi==(92,899,470,940):return '征收地点：'+self.target
        return '00:14:54' if self.running else ''
    def text_button(self,label,*a):self.actions.append(label);self.target=label
    def wait_words(self,page,roi,predicate):assert predicate(self.words(roi))
    def record(self,*a):pass
    def log(self,*a):pass
    def close(self,*a):self.actions.append('exit')
    def back(self,*a):pass
b=Fake(running=True);b.family()
assert b.actions==['exit'] and b.target=='九尾狐宗' and b.pending['family']
b=Fake(claim=True);b.family()
assert b.actions==['family_claim','太上凰宗','family_start','exit'] and b.pending['family']
b=Fake(remaining=0);b.family();assert b.actions==['exit'] and not b.pending['family']
print('PASS: running countdown exits immediately; old reward claimed before new target; new levy at 太上凰宗; no extra attempts.')
