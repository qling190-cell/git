import pathlib,sys,tempfile,threading,time,shutil
root=pathlib.Path('outputs/太古仙尊实验版').resolve()
sys.path.insert(0,str(root))
from runtime_control import PauseClock
with tempfile.TemporaryDirectory() as folder:
    path=pathlib.Path(folder);clock=PauseClock(path)
    result=[];start=clock.monotonic()
    (path/'PAUSE').touch()
    t=threading.Thread(target=lambda:(clock.sleep(.15),result.append(clock.monotonic()-start)))
    t.start()
    for _ in range(100):
        if (path/'PAUSED').exists():break
        time.sleep(.01)
    assert (path/'PAUSED').exists()
    time.sleep(.25);assert not result
    (path/'PAUSE').unlink();t.join(2)
    assert not t.is_alive() and .14<=result[0]<.4,result
    assert not (path/'PAUSED').exists()
    (path/'PAUSE').touch();errors=[]
    def blocked():
        try:clock.gate()
        except RuntimeError as exc:errors.append(str(exc))
    t=threading.Thread(target=blocked);t.start();time.sleep(.15)
    (path/'STOP').touch();t.join(2)
    assert errors and not t.is_alive()

import ui
with tempfile.TemporaryDirectory() as folder:
    ui.ROOT=pathlib.Path(folder)
    shutil.copy2(root/'config.json',ui.ROOT/'config.json')
    app=ui.App();app.root.withdraw()
    class Proc:
        pid=123
        def poll(self):return None
    app.proc=Proc()
    app.pause();assert (ui.ROOT/'PAUSE').exists()
    assert app.pause_btn.cget('text')=='继续'
    app.pause();assert not (ui.ROOT/'PAUSE').exists()
    assert app.pause_btn.cget('text')=='暂停'
    app.proc=None;app.root.destroy()
print('PASS: pause blocks work, resume preserves active timeout, stop interrupts pause, UI pause/resume toggles.')
