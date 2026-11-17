import sys,datetime as dt,py_compile
sys.path.insert(0,'E:/xiuxian')
from assistant import Bot
class Fake:
    sword_open=Bot.sword_open
    sword_defer=Bot.sword_defer
    def __init__(self,day,hour,body=''):
        self.now=dt.datetime(2026,10,day,hour,tzinfo=dt.timezone(dt.timedelta(hours=8)))
        self.ledger={};self.body=body;self.actions=[]
    def sword_local_now(self):return self.now
    def wait(self,*a):self.actions.append(('wait',a))
    def tap(self,*a):self.actions.append(('tap',a))
    def snap(self):pass
    def words(self,*a):return self.body
    def find(self,*a):return True
    def recover_to_main(self,*a):self.actions.append(('recover',a))
    def ledger_save(self):pass
    def record(self,*a):pass
b=Fake(26,11);assert not b.sword_open() and not b.actions and b.ledger['sword_deferred']
b=Fake(26,12);assert b.sword_open() and not b.ledger['sword_deferred']
b=Fake(26,12,'论剑尚未开放');assert not b.sword_open() and any(a[0]=='recover' for a in b.actions)
b=Fake(27,9);assert b.sword_open() and not b.ledger['sword_deferred']
for path in ('assistant.py','navigation.py'):py_compile.compile('E:/xiuxian/'+path,doraise=True)
print('PASS: Monday before noon skip, noon open, explicit closed recovery, Tuesday unrestricted')
