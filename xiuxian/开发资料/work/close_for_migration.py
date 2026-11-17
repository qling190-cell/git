import ctypes,pathlib,json
root=pathlib.Path('outputs/太古仙尊每日助手/太古仙尊每日助手')
state=json.loads((root/'ui-state.json').read_text(encoding='utf-8'))
assert state['state'] in ('finished','stopped'),state
pid=state['ui_pid'];assert pid==45108
user32=ctypes.windll.user32
callback=ctypes.WINFUNCTYPE(ctypes.c_bool,ctypes.c_void_p,ctypes.c_void_p)
@callback
def close(hwnd,param):
    owner=ctypes.c_ulong()
    user32.GetWindowThreadProcessId(ctypes.c_void_p(hwnd),ctypes.byref(owner))
    if owner.value==pid:user32.PostMessageW(ctypes.c_void_p(hwnd),0x0010,0,0)
    return True
user32.EnumWindows(close,0)
kernel=ctypes.windll.kernel32;kernel.OpenProcess.restype=ctypes.c_void_p
handle=kernel.OpenProcess(0x100000,False,pid)
if handle:
    assert kernel.WaitForSingleObject(ctypes.c_void_p(handle),5000)==0
    kernel.CloseHandle(ctypes.c_void_p(handle))
print('Old assistant panel closed; no game task was running.')
