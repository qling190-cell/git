# -*- coding: utf-8 -*-
import sys,pathlib,cv2,numpy as np
sys.path.insert(0,'E:/xiuxian')
from assistant import Bot,RapidOCR
b=Bot.__new__(Bot);b.ocr=RapidOCR(intra_op_num_threads=2,inter_op_num_threads=2)
p=pathlib.Path('E:/xiuxian/logs/20261027-214105-402164/0007.jpg');b.frame=cv2.imdecode(np.frombuffer(p.read_bytes(),np.uint8),1)
for roi in [(215,950,425,1005),(240,950,400,1005),(200,920,445,1020)]:
 print(roi,'line=',b.line(roi),'text=',b.text(roi))
