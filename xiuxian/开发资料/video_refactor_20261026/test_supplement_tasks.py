# -*- coding: utf-8 -*-
import pathlib,sys,json,cv2,numpy as np
sys.path.insert(0,'E:/xiuxian')
from assistant import Bot,RapidOCR
from supplement_tasks import SupplementTasks
from daily_tasks import TaskStop
from workflow import shared_parent,DAILY_GROUPS
class Fake(SupplementTasks):
 def __init__(self,used=0,money=10000):self.ledger={};self.used=used;self.money=money;self.actions=[];self.result=False
 def snap(self):pass
 def pause_animation(self,*a):pass
 def require(self,*a):pass
 def find(self,name,**kw):return (130,775) if name=='creation_dew_item' else True
 def words(self,roi):
  if roi==(190,715,635,865):return f'{self.money}/6000 {self.used}/2 兑换'
  if roi==(0,1020,720,1280):return '悟道成功 获得100修为' if self.result else ''
  return '已预约' if self.result else '预约封印'
 def button_positions(self,*a):return [(560,775)]
 def video_button(self,*a):self.actions.append(a[0]);self.result=True
 def tap(self,x,y):
  self.actions.append((x,y))
  if x==560:self.used+=1;self.money-=6000
 def video_wait(self,*a):self.actions.append('verify_name')
 def video_close(self,*a):self.actions.append('close')
 def reward_popup(self,*a):pass
 def ledger_save(self):pass
 def record(self,*a):pass
 def close(self,*a):self.actions.append('close_market')
 def back(self,*a):pass
for used,money,buy in [(0,10000,True),(1,10000,False),(2,10000,False),(0,5000,False)]:
 f=Fake(used,money);f.creation_dew();assert ((560,775) in f.actions)==buy
 if buy:
  assert f.used==1 and f.money==4000 and f.actions.index('verify_name')<f.actions.index((560,775))
  original=len(f.actions);f.creation_dew();assert len(f.actions)==original
f=Fake();f.ledger['creation_dew_phase']='submitted'
try:f.creation_dew();raise AssertionError('unconfirmed purchase repeated')
except TaskStop:assert f.actions==[('丹方',)],f.actions
f=Fake();f.enlightenment();assert f.ledger['enlightenment_done'] and f.actions==[('悟道',)]
f.enlightenment();assert len(f.actions)==1
f=Fake();f.saint_beast();assert f.ledger['saint_beast_done'] and f.actions[0]==('预约','预约封印')
f.saint_beast();assert f.actions.count(('预约','预约封印'))==1
class Way(Fake):
 def __init__(self,running):super().__init__();self.running=running;self.cfg={'allow_star_way_shenshi':True}
 def words(self,roi):return '神石：100' if roi==(120,1090,350,1130) else ''
 def log(self,*a):pass
 def tap(self,*a):self.actions.append('cultivate');self.running=True
 def star_way_running(self):return self.running
 def video_button(self,labels,roi):
  assert labels==('修炼','开始修炼') and roi==(90,980,380,1100)
  self.actions.append('cultivate');self.running=True
for running in (False,True):
 f=Way(running);f.star_way();assert f.ledger['star_way_done'] and f.actions.count('cultivate')==(0 if running else 1)
 f.star_way();assert f.actions.count('cultivate')==(0 if running else 1)
assert shared_parent('jade','creation_dew')=='market_shop'
assert shared_parent('creation_dew','enlightenment')=='island'
assert shared_parent('travel','saint_beast')=='travel'
assert shared_parent('stars','star_way')=='stars'
r=pathlib.Path('E:/xiuxian');b=Bot.__new__(Bot);b.ocr=RapidOCR(intra_op_num_threads=2,inter_op_num_threads=2)
b.cfg=json.loads((r/'config.json').read_text(encoding='utf-8-sig'));b.meta=json.loads((r/'assets.json').read_text(encoding='utf-8'))
b.images={n:cv2.imdecode(np.frombuffer((r/'assets'/f'{n}.png').read_bytes(),np.uint8),1) for n in b.meta}
for file,page in [('new_insight.png','enlightenment_room'),('new_saint_panel.png','saint_beast_panel')]:
 b.frame=cv2.imdecode(np.frombuffer((r/'开发资料/video_refactor_20261026'/file).read_bytes(),np.uint8),1);assert b.find(page),file
b.frame=cv2.imdecode(np.frombuffer((r/'开发资料/video_refactor_20261026/new_star_way.png').read_bytes(),np.uint8),1)
assert b.find('star_way_panel') and b.star_way_running()
for file,found in [('new_market_top.png',False),('new_market_scroll1.png',True)]:
 b.frame=cv2.imdecode(np.frombuffer((r/'开发资料/video_refactor_20261026'/file).read_bytes(),np.uint8),1)
 assert bool(b.find('creation_dew_item',roi=(85,265,180,1140)))==found
print('PASS: enlightenment receipt and daily dedup; beast confirmation and dedup; dew exact name before purchase, 6000 merit/one item, quota/manual/shortage/submission guards; native pages and item; shared-parent routes')
