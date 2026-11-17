import sys,pathlib,py_compile
sys.path.insert(0,'E:/xiuxian')
from daily_tasks import ApprovedTasks
assert ApprovedTasks.lecture_outcome('获得功德值×900!')=='reward'
assert ApprovedTasks.lecture_outcome('获得 功德值 x 900！')=='reward'
assert ApprovedTasks.lecture_outcome('今天已经训过话了')=='already'
assert ApprovedTasks.lecture_outcome('今日训话次数已满')=='already'
assert ApprovedTasks.lecture_outcome('掌门训话可获得功德') is None
assert ApprovedTasks.lecture_outcome('徒儿我给师父您请安了') is None
class Fake(ApprovedTasks):
    def __init__(self,msg):self.msg=msg;self.ledger={};self.events=[];self.backs=[];self.clicked=[]
    def snap(self):pass
    def find(self,*a):return True
    def require(self,*a):pass
    def click(self,name):self.clicked.append(name)
    def words(self,roi):return self.msg
    def record(self,*args):self.events.append(args)
    def ledger_save(self):pass
    def back(self,*args):self.backs.append(args)
for message in ('获得功德值×900!','今天已经训过话了'):
    b=Fake(message);b.lecture();assert b.ledger['lecture'] and b.clicked==['hall_lecture']
    assert b.backs==[('hall','island'),('island','heaven_nav')]
b=Fake('');b.ledger['lecture']=True;b.lecture();assert not b.clicked
class BottomAlready(Fake):
    def words(self,roi):return '你今天已经对弟子们训过话了。' if roi==(0,1045,720,1275) else '掌门训话'
b=BottomAlready('');b.lecture();assert b.ledger['lecture'] and b.events[0][1]=='本日已完成'

# Replay the real successful-but-misclassified screenshot without ADB.
from assistant import Bot,RapidOCR
import cv2,numpy as np
path=pathlib.Path('E:/xiuxian/logs/20261027-142345-454150/0218.jpg')
b=Bot.__new__(Bot);b.ocr=RapidOCR(intra_op_num_threads=2,inter_op_num_threads=2)
b.frame=cv2.imdecode(np.frombuffer(path.read_bytes(),np.uint8),1)
message=b.words((100,570,630,800))
assert ApprovedTasks.lecture_outcome(message)=='reward',message
other=pathlib.Path(__file__).parent/'lecture_now.png'
b.frame=cv2.imdecode(np.frombuffer(other.read_bytes(),np.uint8),1)
already=b.words((0,1045,720,1275))
assert ApprovedTasks.lecture_outcome(already)=='already',already
py_compile.compile('E:/xiuxian/daily_tasks.py',doraise=True)
print('PASS: central reward, already done, no inference from bare labels/chat, daily dedup, parent returns; actual screenshot:',message)
