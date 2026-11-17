# -*- coding: utf-8 -*-
import sys,pathlib,cv2,numpy as np
sys.path.insert(0,'E:/xiuxian')
from assistant import Bot,RapidOCR
from daily_tasks import ApprovedTasks
b=Bot.__new__(Bot);b.ocr=RapidOCR(intra_op_num_threads=2,inter_op_num_threads=2)
p=pathlib.Path('E:/xiuxian/logs/20261027-214105-402164/0007.jpg');b.frame=cv2.imdecode(np.frombuffer(p.read_bytes(),np.uint8),1);b.snap=lambda:b.frame;b.require=lambda *a:None
assert b.wander_batch_count()==20
class Fake(ApprovedTasks):
 def __init__(self):self.n=0
 def snap(self):self.n+=1
 def require(self,*a):pass
 def line(self,*a):return ''
 def text(self,*a):return [] if self.n==1 else [{'text':'20','confidence':.99}]
f=Fake();assert f.wander_batch_count()==20 and f.n==2
print('PASS: native 20 count; transient empty value retried; detection OCR fallback succeeds')
