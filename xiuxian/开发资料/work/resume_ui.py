import pathlib,sys,json,time,ctypes,subprocess
root=pathlib.Path('outputs/太古仙尊实验版').resolve()
end=time.monotonic()+60
while time.monotonic()<end:
 dirs=sorted((root/'logs').iterdir())
 latest=dirs[-1]/'events.txt'
 text=latest.read_text(encoding='utf-8') if latest.exists() else ''
 if text.rstrip().endswith('等待5分钟后继续领取和处理剩余任务；可在运行面板停止。'):break
 time.sleep(1)
else:raise SystemExit('Not at a stable wait; left current UI running.')
(root/'STOP').write_text('stop',encoding='utf-8')
for _ in range(20):
 state=json.loads((root/'ui-state.json').read_text(encoding='utf-8'))
 if state['state']!='running':break
 time.sleep(.5)
else:raise SystemExit('Old worker still active; no new UI launched.')
old_pid=int(state['ui_pid'])
WNDPROC=ctypes.WINFUNCTYPE(ctypes.c_bool,ctypes.c_void_p,ctypes.c_void_p)
def callback(hwnd,lparam):
 pid=ctypes.c_ulong();ctypes.windll.user32.GetWindowThreadProcessId(hwnd,ctypes.byref(pid))
 if pid.value==old_pid:ctypes.windll.user32.PostMessageW(hwnd,0x0010,0,0)
 return True
cb=WNDPROC(callback);ctypes.windll.user32.EnumWindows(cb,0)
time.sleep(1)
pythonw=r'C:\Users\21413\AppData\Local\Programs\Python\Python39\pythonw.exe'
with (root/'ui-error.log').open('ab') as err:
 p=subprocess.Popen([pythonw,str(root/'ui.py'),'--finish','--start'],cwd=str(root),stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=err,creationflags=subprocess.CREATE_NEW_PROCESS_GROUP|subprocess.DETACHED_PROCESS)
print('Resumed countdown UI:',p.pid)
