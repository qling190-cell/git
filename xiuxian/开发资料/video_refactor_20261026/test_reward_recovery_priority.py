import sys,pathlib
sys.path.insert(0,'E:/xiuxian')
from assistant import Bot,RapidOCR
import cv2,numpy as np
b=Bot.__new__(Bot);b.ocr=RapidOCR(intra_op_num_threads=2,inter_op_num_threads=2)
p=pathlib.Path(__file__).parent/'monitor_close.png'
b.frame=cv2.imdecode(np.frombuffer(p.read_bytes(),np.uint8),1)
b.snap=lambda:b.frame;b.pause_animation=lambda *a:None;b.log=lambda *a:None
clicked=[];b.tap=lambda *point:clicked.append(point)
assert b.recover_video_dialog()
assert len(clicked)==1 and 330<clicked[0][0]<390 and 740<clicked[0][1]<810,clicked
print('PASS: foreground obtained-items modal confirms before trying background X:',clicked)
