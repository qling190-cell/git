# -*- coding: utf-8 -*-
import sys,pathlib,cv2,numpy as np
sys.path.insert(0,'E:/xiuxian')
from assistant import Bot,RapidOCR
from daily_tasks import ApprovedTasks,TaskStop
b=Bot.__new__(Bot);b.ocr=RapidOCR(intra_op_num_threads=2,inter_op_num_threads=2);b.find=lambda n:n=='practice'
for n,want in [(40,None),(42,'done')]:
 p=pathlib.Path(f'E:/xiuxian/logs/20261027-214105-402164/{n:04}.jpg');b.frame=cv2.imdecode(np.frombuffer(p.read_bytes(),np.uint8),1)
 assert b.normal_practice_outcome()==want,(n,b.normal_practice_outcome())
class Fake(ApprovedTasks):
 _v1_practice=Bot._v1_practice
 def __init__(self,result=None):self.cfg={};self.ledger={};self.state='ready';self.result=result;self.clicks=[]
 def mortal_sect_open(self):pass
 def tap(self,*a):pass
 def wait(self,*a):pass
 def find(self,n):return n in ('practice','practice_start','practice_cost')
 def normal_practice_outcome(self):return self.result if self.state=='clicked' else None
 def snap(self):pass
 def ledger_save(self):pass
 def record(self,*a):pass
 def close(self,*a):pass
 def back(self,*a):pass
 def click(self,n):self.clicks.append(n);self.state='clicked'
for status in ('running','done'):
 f=Fake(status);f._v1_practice();assert f.ledger['normal_practice_done'] and len(f.clicks)==1
 f._v1_practice();assert len(f.clicks)==1
f=Fake();f.ledger['normal_practice_phase']='submitted'
try:f._v1_practice();raise AssertionError('unconfirmed submission repeated')
except TaskStop:assert not f.clicks
print('PASS: native today-done toast, idle not falsely done; running/done results; daily dedup and unconfirmed submission blocks retry')
