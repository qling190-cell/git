import pathlib,sys,ast,tempfile,threading,time,json,shutil
ROOT=pathlib.Path('E:/xiuxian');sys.path.insert(0,str(ROOT))
from workflow import DAILY_GROUPS,PARENTS,shared_parent
from assistant import Bot
from hierarchy import Hierarchy
from runtime_control import PauseClock

old=ast.parse((pathlib.Path(__file__).parent/'before/navigation.py').read_text(encoding='utf-8'))
assignment=next(n for n in old.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='DAILY_GROUPS' for t in n.targets))
old_groups=ast.literal_eval(assignment.value)
new={realm:set(tasks) for realm,_,tasks in DAILY_GROUPS}
for realm,_,tasks in old_groups:assert set(tasks)<=new[realm],realm
for name in PARENTS:
    seen=set();node=name
    while node:
        assert node not in seen;seen.add(node);node=PARENTS.get(node)

class Back(Hierarchy):
    back=Bot.back
    def __init__(self,page,hold):
        self.page=page;self._route_hold=hold;self.meta={'teaching':{},'island':{},'mortal_sect':{}};self.taps=[]
    def snap(self):pass
    def find(self,name):return self.page==name
    def require(self,name):assert self.page==name
    def wait(self,name):assert self.page==name
    def tap(self,*a):self.taps.append(a);self.page=PARENTS[self.page]
b=Back('teaching','teaching');b.back('teaching','island');b.back('island','heaven_nav')
assert b.page=='teaching' and not b.taps
b=Back('teaching','island');b.back('teaching','island');b.back('island','heaven_nav')
assert b.page=='island' and len(b.taps)==1
b=Back('island',None);b.back('island','heaven_nav');assert b.page=='heaven_nav'

with tempfile.TemporaryDirectory() as folder:
    p=pathlib.Path(folder);clock=PauseClock(p);result=[]
    (p/'PAUSE').touch();started=time.monotonic()
    thread=threading.Thread(target=lambda:(clock.sleep(.1),result.append(clock.monotonic())))
    thread.start();time.sleep(.25);assert not result
    (p/'PAUSE').unlink();thread.join(2)
    assert result and clock.paused_seconds>=.2

import ui
with tempfile.TemporaryDirectory() as folder:
    ui.ROOT=pathlib.Path(folder);shutil.copy2(ROOT/'config.json',ui.ROOT/'config.json')
    app=ui.App();app.root.withdraw()
    assert 'v5.0' in app.root.title() and app.pause_btn.cget('text')=='暂停'
    status=json.loads((ui.ROOT/'ui-state.json').read_text(encoding='utf-8'))
    assert status['state']=='ready'
    for code in ui.TASKS.values():
        assert code in ('all','resume','finish','inspect','order') or hasattr(Bot,code),code
    tree=ast.parse((ROOT/'assistant.py').read_text(encoding='utf-8'))
    task_argument=next(n for n in ast.walk(tree) if isinstance(n,ast.Call)
                       and isinstance(n.func,ast.Attribute) and n.func.attr=='add_argument'
                       and n.args and isinstance(n.args[0],ast.Constant) and n.args[0].value=='task')
    choices=ast.literal_eval(next(k.value for k in task_argument.keywords if k.arg=='choices'))
    assert set(ui.TASKS.values())<=set(choices),'UI task missing CLI handler'
    app.root.destroy()

print('PASS: original tasks kept in their realms, acyclic hierarchy, no repeated root returns, pause/resume, v5 UI and handlers.')
