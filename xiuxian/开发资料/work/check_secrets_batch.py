import pathlib,sys
sys.path.insert(0,str(pathlib.Path('outputs/太古仙尊实验版').resolve()))
from navigation import Navigation
from daily_tasks import ApprovedTasks

class Route(Navigation,ApprovedTasks):
    def __init__(self):
        self.cfg={};self.pending={};self.page='main';self.entries=0;self.exits=0;self.stays=[]
    def log(self,*a):pass
    def recover_to_main(self,*a):self.page='main'
    def realm(self,*a):self.page='main'
    def snap(self):pass
    def find(self,name):return self.page==name
    def tap(self,x,y):
        if x==650:self.page='heaven_travel'
        elif x==500:self.page='secrets';self.entries+=1
    def wait(self,name):assert self.page==name
    def require(self,name):assert self.page==name
    def back(self,page,target):
        assert self.page==page
        self.page=target
        if page=='secrets':self.exits+=1
    def run_task(self,task):
        self.secrets_open();self.secrets_back();self.stays.append(self.page);return True

b=Route();b.run_groups([('heaven','仙界',['demon','hunt','treasure'])])
assert b.entries==1 and b.exits==1
assert b.stays==['secrets','secrets','heaven_nav']
b=Route();b.run_groups([('heaven','仙界',['hunt','treasure'])])
assert b.entries==1 and b.exits==1
b=Route();b.run_groups([('heaven','仙界',['treasure'])])
assert b.entries==1 and b.exits==1 and b.page=='heaven_nav'

class Treasure(ApprovedTasks):
    def __init__(self):self.ledger={};self.pending={};self.buttons=[]
    def secrets_open(self):pass
    def secrets_back(self):pass
    def snap(self):pass
    def tap(self,*a):pass
    def wait(self,*a):pass
    def words(self,roi):return '确认寻宝' if roi==(105,520,615,735) else ''
    def text(self,*a):return []
    def text_button(self,label,*a):self.buttons.append(label)
    def wait_words(self,*a):pass
    def ledger_save(self):pass
    def record(self,*a):pass
    def close(self,*a):pass
b=Treasure();b.treasure()
assert b.buttons==['寻宝','确定'] and b.pending['treasure']
print('PASS: shared secrets navigation, partial resume, single task return, treasure label and confirmation.')
