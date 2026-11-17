import sys
sys.path.insert(0,'E:/xiuxian')
from video_tasks import VideoTasks
class Fake(VideoTasks):
    def __init__(self,entry=True,opened=False,claim=True):
        self.entry=entry;self.opened=opened;self.claim=claim;self.ledger={};self.taps=[];self.closed=0
    def snap(self):pass
    def freegift_panel(self):return self.opened
    def realm(self,*a):pass
    def button_positions(self,labels,roi):
        if labels==('修真',):return [(50,280)] if self.entry else []
        return [(300,600)] if self.claim else []
    def tap(self,*point):
        self.taps.append(point)
        if point==(50,280):self.opened=True
        else:self.claim=False
    def words(self,*a):return '修真礼包 超值礼包 68仙玉'
    def video_wait(self,*a):pass
    def reward_popup(self,*a):return False
    def pause_animation(self,*a):pass
    def video_close(self,*a):self.closed+=1;self.opened=False
    def ledger_save(self):pass
    def record(self,*a):pass
    def log(self,*a):pass
b=Fake(entry=False);b.freegift();assert not b.taps and not b.closed and not b.ledger
b=Fake();b.freegift();assert len(b.taps)==2 and b.closed==1 and b.ledger['freegift_done']
b=Fake(opened=True,claim=False);b.freegift();assert b.closed==1 and not b.taps and not b.ledger
b=Fake(opened=True);b.ledger['freegift_done']=True;b.freegift();assert b.closed==1 and not b.taps
print('PASS: missing entry skip, disappearing claimed tier, already-open paid tiers close, done panel close')
