import pathlib,sys
sys.path.insert(0,'E:/xiuxian')
import cv2,numpy as np
from video_tasks import VideoTasks
class Fake(VideoTasks):
    def __init__(self,state='claim',started=0):
        self.state=state;self.ledger={'smallworld_started':started};self.pending={};self.actions=[]
    def snap(self):pass
    def video_button(self,*a):pass
    def video_wait(self,*a):return self.words()
    def words(self,*a):return {'claim':'探索结束，请领取奖励','ready':'还可探索3次','running':'探索中 00:10:00'}[self.state]
    def button_positions(self,labels,roi):
        if '领取' in labels and self.state=='claim':return [(300,900)]
        if '探索' in labels and self.state=='ready':return [(300,950)]
        return []
    def tap(self,*p):
        self.actions.append(self.state);self.state={'claim':'ready','ready':'running'}[self.state]
    def pause_animation(self,*a):pass
    def reward_popup(self,*a):return False
    def ledger_save(self):pass
    def record(self,*a):pass
    def video_close(self,*a):self.actions.append('close')
b=Fake();b.smallworld_explore();assert b.actions==['claim','ready','close'] and b.pending['smallworld'] and b.ledger['smallworld_started']==1
b=Fake(started=3);b.smallworld_explore();assert b.actions==['claim','close']
b=Fake(state='running');b.ledger['smallworld_unconfirmed']=True;b.smallworld_explore();assert b.ledger['smallworld_started']==1 and not b.ledger['smallworld_unconfirmed']
native=pathlib.Path(__file__).parent/'smallworld_events_native.png'
b=Fake();b.frame=cv2.imdecode(np.frombuffer(native.read_bytes(),np.uint8),1)
boxes=b.smallworld_event_options();assert len(boxes)==4 and boxes[1][1]==700,boxes
class EventFake(Fake):
    def video_wait(self,*a):return ''
    def smallworld_event_options(self):return [(100,400,600,450),(100,550,600,600),(100,700,600,750),(100,850,600,900)]
    def words(self,roi=None):return '使用2仙玉补充灵气' if roi==(100,550,600,600) else '事件'
b=EventFake();b.smallworld_events();assert b.actions==['close'],'Premium second option was clicked'
print('PASS: claim then explore, three-start cap, interrupted submission reconcile, native four options, premium second option blocked')
