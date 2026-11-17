import sys,pathlib
sys.path.insert(0,'E:/xiuxian')
from assistant import Bot,RapidOCR
from forbidden_tasks import event_positions
import cv2,numpy as np
b=Bot.__new__(Bot);b.ocr=RapidOCR(intra_op_num_threads=2,inter_op_num_threads=2)
p=pathlib.Path(__file__).parent/'forbidden_battle_button.png'
b.frame=cv2.imdecode(np.frombuffer(p.read_bytes(),np.uint8),1)
hits=event_positions(b,('战斗','迎战','挑战'))
assert len(hits)==1 and 320<hits[0][0]<410 and 810<hits[0][1]<880,hits
print('PASS: actual failed modal battle button confirmed through full-context OCR:',hits)
