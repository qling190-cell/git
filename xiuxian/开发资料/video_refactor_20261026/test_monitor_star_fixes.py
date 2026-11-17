import pathlib,sys,json
sys.path.insert(0,'E:/xiuxian')
from assistant import Bot,RapidOCR
from video_tasks import VideoTasks
import cv2,numpy as np
root=pathlib.Path('E:/xiuxian');b=Bot.__new__(Bot)
b.cfg=json.loads((root/'config.json').read_text(encoding='utf-8-sig'))
b.meta=json.loads((root/'assets.json').read_text(encoding='utf-8'))
b.images={n:cv2.imdecode(np.frombuffer((root/'assets'/f'{n}.png').read_bytes(),np.uint8),1) for n in b.meta}
b.ocr=RapidOCR(intra_op_num_threads=2,inter_op_num_threads=2)
folder=root/'logs/20261027-151438-978291'
b.frame=cv2.imdecode(np.frombuffer((folder/'0044.jpg').read_bytes(),np.uint8),1)
assert b.seize_reward_observed(),'explicit already-collected centre toast missed'
b.frame=cv2.imdecode(np.frombuffer((folder/'0043.jpg').read_bytes(),np.uint8),1)
assert not b.seize_reward_observed(),'plain reward label must not imply collection'
b.frame=cv2.imdecode(np.frombuffer((folder/'0058.jpg').read_bytes(),np.uint8),1)
point=b.find('battle_exit');assert point and 330<point[0]<390 and 830<point[1]<900,point
class Recovery(VideoTasks):
    def __init__(self):self.tapped=[]
    def words(self,*a):return '神秘僧人受到伤害 紫灵击溃敌人取得胜利 退出'
    def find(self,*a):return (360,867)
    def tap(self,*p):self.tapped.append(p)
r=Recovery();assert r.recover_video_dialog() and r.tapped==[(360,867)]
print('PASS: real already-collected toast, no false success from label, real battle exit point, recovery uses observed exit')
