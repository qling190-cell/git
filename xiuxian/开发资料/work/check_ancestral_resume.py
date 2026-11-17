import pathlib,sys
sys.path.insert(0,str(pathlib.Path('outputs/太古仙尊实验版').resolve()))
from navigation import Navigation
class Fake(Navigation):
    def __init__(self,open_page=True,done=False):
        self.daily_progress={'completed':['familycare'] if done else []}
        self.open_page=open_page;self.calls=[]
    def find(self,name):return name=='ancestral' and self.open_page
    def log(self,*a):pass
    def save_daily_progress(self,*a):pass
    def run_task(self,task):self.calls.append(task);return True
b=Fake();assert b.continue_open_daily_task()
assert b.calls==['familycare'] and b.daily_progress['completed']==['familycare']
assert b.continue_open_daily_task() and b.calls==['familycare']
b=Fake(False);assert b.continue_open_daily_task() and not b.calls
print('PASS: resume on ancestral directly, checkpoint completion, no repeated guidance on completed task.')
