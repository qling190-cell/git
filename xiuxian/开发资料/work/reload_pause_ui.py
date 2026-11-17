import pathlib,json,ctypes,time,subprocess
root=pathlib.Path('outputs/太古仙尊每日助手/太古仙尊每日助手').resolve()
state=json.loads((root/'ui-state.json').read_text(encoding='utf-8'))
pid=state['ui_pid']
assert pid==46160,'Unexpected UI; recheck before closing'
progress=root/'ledgers/oppo-ziling.progress.json'
before=json.loads(progress.read_text(encoding='utf-8'))
pathlib.Path('work/progress-before-ui-reload.json').write_text(json.dumps(before,ensure_ascii=False,indent=2),encoding='utf-8')
user32=ctypes.windll.user32
callback_type=ctypes.WINFUNCTYPE(ctypes.c_bool,ctypes.c_void_p,ctypes.c_void_p)
@callback_type
def close_window(hwnd,param):
    owner=ctypes.c_ulong()
    user32.GetWindowThreadProcessId(ctypes.c_void_p(hwnd),ctypes.byref(owner))
    if owner.value==pid:user32.PostMessageW(ctypes.c_void_p(hwnd),0x0010,0,0)
    return True
user32.EnumWindows(close_window,0)
kernel=ctypes.windll.kernel32
kernel.OpenProcess.restype=ctypes.c_void_p
for target in (pid,state.get('worker_pid')):
    if not target:continue
    handle=kernel.OpenProcess(0x100000,False,target)
    if handle:
        result=kernel.WaitForSingleObject(ctypes.c_void_p(handle),5000)
        kernel.CloseHandle(ctypes.c_void_p(handle))
        assert result==0,'Old UI/worker still active'
after=json.loads(progress.read_text(encoding='utf-8'))
assert set(before['completed'])<=set(after['completed'])
exe=pathlib.Path(r'C:/Users/21413/AppData/Local/Programs/Python/Python39/pythonw.exe')
p=subprocess.Popen([str(exe),str(root/'ui.py')],cwd=root,
    creationflags=subprocess.CREATE_NO_WINDOW,stdin=subprocess.DEVNULL,
    stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
time.sleep(1)
assert p.poll() is None
print('New v4.4 panel PID:',p.pid)
print('Preserved progress:',after)
