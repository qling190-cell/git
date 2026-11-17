import pathlib,sys,tempfile,json
sys.path.insert(0,str(pathlib.Path('outputs/太古仙尊实验版').resolve()))
from navigation import Navigation

groups=[('mortal','凡间',['first','second']),('heaven','仙界',['third'])]
class Fake(Navigation):
    def __init__(self,folder,account='one',day='2026-10-25'):
        self.ledger_path=pathlib.Path(folder)/(account+'.json')
        self.day=day;self.cfg={};self.pending={};self.calls=[];self.stop=None
    def log(self,*a):pass
    def recover_to_main(self,*a):pass
    def realm(self,*a):pass
    def run_task(self,task):
        self.calls.append(task)
        if task==self.stop:raise InterruptedError('simulated forced stop')
        if task=='first':self.pending['first']=True
        return True

with tempfile.TemporaryDirectory() as folder:
    b=Fake(folder);b.prepare_daily_progress();b.stop='second'
    try:b.run_groups(groups)
    except InterruptedError:pass
    else:raise AssertionError('expected interruption')
    data=json.loads(b.progress_path.read_text(encoding='utf-8'))
    assert data['completed']==['first'] and data['current']=='second'
    b=Fake(folder);b.prepare_daily_progress(True)
    assert b.pending=={'first':True}
    assert b.run_groups(groups) and b.calls==['second','third']
    b.calls=[];assert b.run_groups(groups) and not b.calls
    b.run_groups([('mortal','凡间',['first'])],pending_only=True)
    assert b.calls==['first'],'pending rewards must remain eligible'
    b=Fake(folder,day='2026-10-26');b.prepare_daily_progress(True)
    assert not b.daily_progress['completed'] and not b.pending
    b=Fake(folder,account='other');b.prepare_daily_progress(True)
    assert not b.daily_progress['completed']
    b=Fake(folder);b.prepare_daily_progress(False)
    assert not b.daily_progress['completed'],'explicit full run resets progress'
print('PASS: forced interruption, resume at unfinished task, completed skip, pending rewards, date/account isolation, full restart.')
