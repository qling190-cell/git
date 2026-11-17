import pathlib,json,ctypes as c,subprocess,time,sys
from ctypes import wintypes as w
root=pathlib.Path('E:/xiuxian');status=json.loads((root/'ui-state.json').read_text(encoding='utf-8'))
assert status['state'] in ('stopped','finished','ready'),status
pid=status['ui_pid'];u=c.WinDLL('user32');windows=[]
CALLBACK=c.WINFUNCTYPE(w.BOOL,w.HWND,w.LPARAM)
u.GetWindowThreadProcessId.argtypes=[w.HWND,c.POINTER(w.DWORD)]
u.EnumWindows.argtypes=[CALLBACK,w.LPARAM]
u.PostMessageW.argtypes=[w.HWND,w.UINT,w.WPARAM,w.LPARAM]
u.IsWindow.argtypes=[w.HWND]
@CALLBACK
def enum(hwnd,param):
    found=w.DWORD();u.GetWindowThreadProcessId(hwnd,c.byref(found))
    if found.value==pid:windows.append(hwnd)
    return True
u.EnumWindows(enum,0)
for hwnd in windows:u.PostMessageW(hwnd,0x10,0,0)
end=time.monotonic()+8
while any(u.IsWindow(hwnd) for hwnd in windows) and time.monotonic()<end:time.sleep(.1)
assert not any(u.IsWindow(hwnd) for hwnd in windows),'old panel still open'
py=pathlib.Path('C:/Users/21413/AppData/Local/Programs/Python/Python39/pythonw.exe')
with (root/'ui-error.log').open('ab') as log:
    args=[str(py),str(root/'ui.py')]+([] if '--ready' in sys.argv else (['--start'] if '--all' in sys.argv else ['--resume','--start']))
    process=subprocess.Popen(args,cwd=str(root),stdin=subprocess.DEVNULL,stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW)
print('Restarted panel with updated code and current-day resume; UI pid',process.pid)
