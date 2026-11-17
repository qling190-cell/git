import sys,pathlib
sys.path.insert(0,'E:/xiuxian')
import cv2,numpy as np
from video_tasks import VideoTasks
p=pathlib.Path('C:/Users/21413/AppData/Local/Temp/codex-clipboard-e707ffa8-3d8b-4489-a30f-ae6a095d60c5.png')
im=cv2.imdecode(np.frombuffer(p.read_bytes(),np.uint8),1)
scaled=cv2.resize(im,(720,round(im.shape[0]*720/im.shape[1])))
frame=np.zeros((1280,720,3),np.uint8);frame[:min(1280,len(scaled))]=scaled[:1280]
class Fake(VideoTasks):
    meta={}
    def snap(self):pass
    def tap(self,*p):self.clicked=p
b=Fake();b.frame=frame;b.video_close(None)
assert 620<b.clicked[0]<680 and b.clicked[1]<100,b.clicked
print('PASS: supplied celestial modal screenshot X detected:',b.clicked)
