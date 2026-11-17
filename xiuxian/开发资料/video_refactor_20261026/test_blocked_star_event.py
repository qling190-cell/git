import sys,pathlib,cv2,numpy as np
sys.path.insert(0,'E:/xiuxian')
from assistant import Bot,RapidOCR
b=Bot.__new__(Bot);b.ocr=RapidOCR(intra_op_num_threads=2,inter_op_num_threads=2)
p=pathlib.Path('E:/xiuxian/logs/20261111-154754-270895/0024.jpg');b.frame=cv2.imdecode(np.frombuffer(p.read_bytes(),np.uint8),1)
clicked=[];b.video_close=lambda target:clicked.append(target);b.record=lambda *a:None
assert b.skip_blocked_star_event() and clicked==['stars']
print('PASS: native blocked dragon event closes to stars; no event option clicked')
