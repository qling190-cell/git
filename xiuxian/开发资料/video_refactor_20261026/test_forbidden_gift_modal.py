import pathlib,sys
sys.path.insert(0,'E:/xiuxian')
from assistant import Bot,RapidOCR
from forbidden_tasks import accept_free_event,front_x_points,run_forbidden
from daily_tasks import TaskStop
import cv2,numpy as np
folder=pathlib.Path(__file__).parent
b=Bot.__new__(Bot);b.ocr=RapidOCR(intra_op_num_threads=2,inter_op_num_threads=2)
gift=cv2.imdecode(np.frombuffer((folder/'monitor_forbidden.png').read_bytes(),np.uint8),1)
root=cv2.imdecode(np.frombuffer((folder/'star_forbidden_now.png').read_bytes(),np.uint8),1)
b.frame=gift;b.snap=lambda:b.frame;b.pause_animation=lambda *a:None;clicked=[]
def tap(*point):clicked.append(point);b.frame=root
b.tap=tap;b.record=lambda *a:None
assert len(front_x_points(b))==1
body=b.words((50,100,670,1200)).replace(' ','')
assert accept_free_event(b,body) and len(clicked)==1,body
class Unknown:
    frame=gift
    def snap(self):pass
    def pause_animation(self,*a):pass
    def words(self,*a):return '大苦灭境 神秘来客 尚未支持的事件'
    def button_positions(self,*a):return []
    def tap(self,*a):raise AssertionError('Must not click background')
    def video_button(self,*a):raise AssertionError('Must not click background')
try:run_forbidden(Unknown());raise AssertionError('Unknown overlay must stop')
except TaskStop as e:assert '前景弹窗' in str(e),e
print('PASS: real gift modal collected at',clicked,'unknown front dialog blocks background exploration')
