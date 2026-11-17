import pathlib,sys
sys.path.insert(0,str(pathlib.Path('outputs/太古仙尊实验版').resolve()))
from daily_tasks import ApprovedTasks,TaskStop
class Fake(ApprovedTasks):
    def __init__(self,body):self.body=body;self.buttons=[];self.records=[]
    def island(self):pass
    def island_label(self,*a):pass
    def wait(self,*a):return a[0]
    def tap(self,*a):pass
    def snap(self):pass
    def words(self,*a):return self.body
    def text_button(self,label,*a):self.buttons.append(label)
    def text(self,*a):return []
    def record(self,*a):self.records.append(a)
    def close(self,*a):pass
    def back(self,*a):pass
for amount in (0,80,100,10000):
    body=f'全部护法会一次性为所有入魔的弟子护法，需要消耗{amount}灵石。确定要全部护法吗？'
    b=Fake(body);b.guard()
    assert b.buttons==['全部护法','确定']
    assert body in b.records[-1][-1]
b=Fake('其他操作消耗80灵石')
try:b.guard()
except TaskStop:pass
else:raise AssertionError('unrelated dialog confirmed')
assert b.buttons==['全部护法']
print('PASS: any spirit-stone amount, actual prompt logged, unrelated dialog rejected.')
