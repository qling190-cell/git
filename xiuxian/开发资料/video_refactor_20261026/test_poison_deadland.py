import pathlib,sys,py_compile
sys.path.insert(0,'E:/xiuxian')
import video_tasks
from video_tasks import VideoTasks
class Fake(VideoTasks):
    def __init__(self,state):self.state=state;self.pending={'sect_deadland':True};self.ledger={};self.actions=[]
    def snap(self):pass
    def words(self,roi):
        if self.state=='prompt':return '万毒蛊坑 物品不足 闯荡需要避毒甲 是否前往查看'
        if self.state=='poison':return '万毒蛊坑 闯荡需要避毒甲'
        return '涅元结界 剩余闯荡 00:10:00'
    def button_positions(self,labels,roi):return [(200,800)] if self.state=='prompt' and labels==('取消',) else []
    def tap(self,*point):assert self.state=='prompt';self.actions.append('取消');self.state='poison'
    def wait(self,target):assert target=='mortal_sect' and self.state=='sect'
    def ledger_save(self):pass
    def record(self,*a):pass
    def log(self,*a):pass
    def back(self,*a):self.actions.append('正常返回')
original=video_tasks.close_front
def close(b):assert b.state=='poison';b.actions.append('毒坑X');b.state='sect'
video_tasks.close_front=close
try:
    b=Fake('prompt');b.sect_deadland();assert b.actions==['取消','毒坑X','正常返回'] and not b.pending['sect_deadland']
    b=Fake('poison');b.sect_deadland();assert b.actions==['毒坑X','正常返回'] and not b.ledger.get('sect_deadland_started')
    b=Fake('normal');assert not b.skip_poison_deadland() and not b.actions
    b=Fake('prompt');assert b.recover_video_dialog() and b.actions==['取消','毒坑X']
finally:video_tasks.close_front=original
py_compile.compile('E:/xiuxian/video_tasks.py',doraise=True)
print('PASS: poison skip, cancel before X, never start/click confirm, pending cleared, normal deadland unchanged, recovery handles layers')

# Real native screenshot: OCR detection and foreground red-X geometry, no ADB.
from assistant import Bot,RapidOCR
import cv2,numpy as np,json
root=pathlib.Path('E:/xiuxian');b=Bot.__new__(Bot)
b.ocr=RapidOCR(intra_op_num_threads=2,inter_op_num_threads=2)
b.frame=cv2.imdecode(np.frombuffer((pathlib.Path(__file__).parent/'poison_native.png').read_bytes(),np.uint8),1)
b.snap=lambda:b.frame
assert b.poison_deadland_visible()
clicked=[];b.tap=lambda *p:clicked.append(p)
original(b)
assert len(clicked)==1 and 600<clicked[0][0]<650 and 350<clicked[0][1]<410,clicked
print('PASS native poison screenshot OCR and red X:',clicked)
src=pathlib.Path('C:/Users/21413/AppData/Local/Temp/codex-clipboard-7b9f7f2d-c0fe-4ed6-aeca-db69e56c83ac.png')
im=cv2.imdecode(np.frombuffer(src.read_bytes(),np.uint8),1)
im=cv2.resize(im,(720,round(im.shape[0]*720/im.shape[1])))
b.frame=np.zeros((1280,720,3),np.uint8);b.frame[180:180+len(im)]=im
assert b.poison_deadland_visible()
hits=b.button_positions(('取消',),(90,500,620,1000));assert len(hits)==1,hits
print('PASS supplied shortage screenshot: cancel OCR',hits)
