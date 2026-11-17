import pathlib,sys
sys.path.insert(0,'E:/xiuxian')
from video_tasks import VideoTasks
class Fake(VideoTasks):
    frame=None
    def __init__(self,footer):self.footer=footer
    def words(self,roi,frame=None):return '游历 小世界' if roi==(0,0,720,120) else self.footer
b=Fake('神游 通天塔 八卦 探秘 仙坊');assert not b.video_page('smallworld_map',None)
b=Fake('探索 事件 法宝');assert b.video_page('smallworld_map',None)
from assistant import Bot,RapidOCR
import cv2,numpy as np
b=Bot.__new__(Bot);b.ocr=RapidOCR(intra_op_num_threads=2,inter_op_num_threads=2)
def load(path):b.frame=cv2.imdecode(np.frombuffer(path.read_bytes(),np.uint8),1)
load(pathlib.Path('E:/xiuxian/logs/20261027-145459-505894/0046.jpg'))
assert not b.video_page('smallworld_map',b.frame),'unselected tab mistaken for loaded map'
load(pathlib.Path('E:/xiuxian/logs/20261027-150116-044652/0018.jpg'))
assert b.video_page('smallworld_map',b.frame),'loaded root footer not recognized'
assert len(b.button_positions(('探索',),(30,940,230,1140)))==1
load(pathlib.Path(__file__).parent/'smallworld_events_native.png')
assert b.smallworld_dialog_open(),'open event dialog must be recoverable even when footer covered'
print('PASS: unselected tab rejected, real footer required, captured travel frame rejected, open event dialog recovered')
