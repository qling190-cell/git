import pathlib,sys,cv2,numpy as np
root=pathlib.Path('outputs/太古仙尊实验版').resolve()
sys.path.insert(0,str(root))
from assistant import Bot
from night_tasks import NightTasks
import night_tasks
b=Bot()
frame=cv2.imdecode(np.frombuffer(pathlib.Path('work/night_oppo_latest.png').read_bytes(),np.uint8),1)
buttons=b.night_buttons(frame)
print('Detected:',buttons)
latest=buttons[-4:]
assert len(latest)==4 and all(x['complete'] for x in latest)
assert [x['pos'][0]>350 for x in latest]==[True,False,True,False]
assert all('逆天' not in x['name'] and '证道' not in x['name'] for x in buttons)

class Fake(NightTasks):
    def __init__(self,running=False,already=False):
        self.pending={};self.ledger={'night_by_destination':{str(i):15 for i in range(4)} if already else {}}
        self.current=0;self.running={i:running for i in range(4)}
        self.claims={i:not running for i in range(4)};self.claimed=[];self.started=[];self.exited=False
        self.frame=cv2.cvtColor(np.full((1280,720,3),(60,200,200),np.uint8),cv2.COLOR_HSV2BGR)
    def realm(self,*a):pass
    def tap(self,x,y):
        if y==400:self.current=x
    def wait(self,*a):pass
    def adb(self,*a):pass
    def snap(self):pass
    def require(self,*a):pass
    def night_buttons(self):return [{'name':str(i),'pos':(i,400),'stationed':True,'complete':False} for i in range(4)]
    def log(self,*a):pass
    def record(self,*a):pass
    def find(self,name):return self.claims[self.current] if name=='night_claim' else not self.running[self.current]
    def click(self,name):
        if name=='night_claim':self.claimed.append(self.current);self.claims[self.current]=False
        if name=='night_start':
            self.started.append(self.current);self.running[self.current]=True
    def wait_gone(self,*a):pass
    def words(self,roi):
        if roi==(90,238,635,315):return f'尚可夜猎{60-15*len(self.started)}次'
        return '剩余夜猎时间00:15:00' if self.running[self.current] else ''
    def line(self,*a):return '15'
    def wait_words(self,page,roi,predicate):assert predicate(self.words(roi))
    def ledger_save(self):pass
    def close(self,*a):self.exited=True;assert len(self.claimed)==4 or len(self.started)==0
    def back(self,*a):pass
original=night_tasks.time.sleep;night_tasks.time.sleep=lambda seconds:None
try:
    b=Fake();b.night()
    assert b.claimed==[0,1,2,3] and b.started==[0,1,2,3]
    assert b.ledger['night_started']==60 and b.pending['night'] and b.exited
    b=Fake(running=True);b.night();assert not b.started and b.pending['night'] and b.exited
    b=Fake(already=True);b.night();assert len(b.claimed)==4 and not b.started and not b.pending['night']
finally:night_tasks.time.sleep=original
print('PASS: screenshot newest-four unlocked/completed; 4 claims then 4x15 starts; running skip; daily resume no duplicate.')
