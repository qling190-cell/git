# -*- coding: utf-8 -*-
import sys,pathlib,cv2,numpy as np
sys.path.insert(0,'E:/xiuxian')
from assistant import Bot,RapidOCR
from video_tasks import VideoTasks
from daily_tasks import TaskStop
class Fake(VideoTasks):
 def __init__(self,quota=1,money=100):self.quota=quota;self.money=money;self.ledger={};self.clicks=[]
 def snap(self):pass
 def words(self,roi):assert roi==(90,220,640,335);return f'兑换 剩余：{self.quota}次 {self.money}/50'
 def button_positions(self,labels,roi):assert roi==(470,230,640,300);return [(496,273)]
 def tap(self,*p):self.clicks.append(p);self.quota-=1;self.money-=50
 def reward_popup(self,*a):pass
 def ledger_save(self):pass
 def record(self,*a):pass
for quota,money,count in [(1,100,1),(5,100,1),(0,100,0),(1,20,0)]:
 f=Fake(quota,money);f.battle_exchange_first();assert len(f.clicks)==count
 if count:f.battle_exchange_first();assert len(f.clicks)==1
f=Fake();f.ledger['battle_exchange_rows']={'alchemy':True,'craft':True};f.battle_exchange_first();assert len(f.clicks)==1
f=Fake();f.ledger['battle_exchange_first_phase']='submitted'
try:f.battle_exchange_first();raise AssertionError('Repeated unconfirmed trade')
except TaskStop:assert not f.clicks
b=Bot.__new__(Bot);b.ocr=RapidOCR(intra_op_num_threads=2,inter_op_num_threads=2)
p=pathlib.Path('E:/xiuxian/开发资料/video_refactor_20261026/battle_exchange_current.png');b.frame=cv2.imdecode(np.frombuffer(p.read_bytes(),np.uint8),1)
b.snap=lambda:b.frame;b.ledger={};b.ledger_save=lambda:None;b.record=lambda *a:None;b.tap=lambda *a:(_ for _ in ()).throw(AssertionError('Quota zero must not click'))
b.battle_exchange_first();assert b.ledger['battle_exchange_rows']['basic']
print('PASS: first row only, one item, daily dedup, zero/insufficient skips, legacy experience records ignored, unconfirmed retry blocked; native quota zero skipped')
