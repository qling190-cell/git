import sys
sys.path.insert(0,'E:/xiuxian')
import daily_tasks
from daily_tasks import ApprovedTasks,TaskStop
class Clock:
 n=0
 @classmethod
 def monotonic(c):c.n+=1;return c.n
 @staticmethod
 def sleep(s):pass
daily_tasks.time=Clock
class Fake(ApprovedTasks):
 def __init__(self,reward=True,changed=False):self.clicked=0;self.reward=reward;self.changed=changed;self.checked=False
 def snap(self):pass
 def words(self,*a):return '\u83b7\u5f97\u7389\u76d2x1' if self.clicked and self.reward else ''
 def click(self,*a):self.clicked+=1
 def log(self,*a):pass
 def line(self,*a):return '2/20' if self.changed else '1/20'
 def wait_market_counter(self,*a):assert self.reward and self.clicked;self.checked=True;return 2
f=Fake();assert f.market_click_with_receipt('jade_exchange',(0,0,1,1),20,1)==2 and f.checked
f=Fake(False,True)
try:f.market_click_with_receipt('jade_exchange',(0,0,1,1),20,1);raise AssertionError()
except TaskStop:assert f.clicked==1 and not f.checked
f=Fake(False)
try:f.market_click_with_receipt('jade_exchange',(0,0,1,1),20,1);raise AssertionError()
except TaskStop:assert f.clicked==3 and not f.checked
print('PASS: receipt before count; quota change without receipt blocks duplicate; unchanged quota retries at most three times')
