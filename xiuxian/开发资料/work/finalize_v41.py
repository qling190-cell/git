# -*- coding: utf-8 -*-
from pathlib import Path
import json,shutil,ctypes,subprocess
r=Path('outputs/太古仙尊实验版').resolve()
active=Path('outputs/太古仙尊每日助手/太古仙尊每日助手').resolve()
p=r/'ui.py';s=p.read_text(encoding='utf-8').replace('v4','v4.1')
p.write_text(s,encoding='utf-8')
p=r/'config.json';cfg=json.loads(p.read_text(encoding='utf-8-sig'))
cfg['build_revision']='4.1'
p.write_text(json.dumps(cfg,ensure_ascii=False,indent=2),encoding='utf-8')
(r/'profiles/oppo-ziling.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2),encoding='utf-8')
for filename in ('任务顺序.md','使用说明.txt'):
    p=r/filename;s=p.read_text(encoding='utf-8')
    s=s.replace('必要时使用系统返回','只使用游戏内X和返回按钮，不发送系统返回')
    p.write_text(s,encoding='utf-8')
p=r/'验收记录.md';s=p.read_text(encoding='utf-8')+'''

### v4.1 掌门传功与OPPO返回修复

OCR将传功分成“传”和“功”，现支持同一按钮分字合并。
使用已有机会后已看到“传功中”倒计时，记录当日已执行，不重复扣机会。
内层提示自动关闭，再点击外层X，最后返回凡间，已完成实测。
OPPO系统返回会弹游戏中心退出引导，现已完全取消系统返回。
优先关闭识别到的白色/红色X，再使用游戏内返回箭头。
补充菱形、白云、圆形三种箭头；未知状态停留现场，不调用退出确认。
回归验证涵盖失败截图、返回、分字传功、健康跳过、收获后重种及领奖流程。
'''
p.write_text(s,encoding='utf-8')
user=ctypes.windll.user32
callback=ctypes.WINFUNCTYPE(ctypes.c_bool,ctypes.c_void_p,ctypes.c_void_p)
@callback
def close(hwnd,_):
    pid=ctypes.c_ulong();user.GetWindowThreadProcessId(hwnd,ctypes.byref(pid))
    if pid.value==47128:user.PostMessageW(hwnd,0x0010,0,0)
    return True
user.EnumWindows(close,0)
names=('assistant.py','daily_tasks.py','palace_tasks.py','navigation.py','ui.py',
       'config.json','assets.json','使用说明.txt','验收记录.md','任务顺序.md')
for name in names:shutil.copy2(r/name,active/name)
for f in (r/'assets').glob('*.png'):shutil.copy2(f,active/'assets'/f.name)
shutil.copy2(r/'ledgers/oppo-ziling.json',active/'ledgers/oppo-ziling.json')
shutil.copy2(r/'profiles/oppo-ziling.json',active/'profiles/oppo-ziling.json')
(active/'STOP').unlink(missing_ok=True)
pythonw=r'C:\Users\21413\AppData\Local\Programs\Python\Python39\pythonw.exe'
with (active/'ui-error.log').open('ab') as err:
    child=subprocess.Popen([pythonw,str(active/'ui.py'),'--start'],cwd=str(active),
        stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=err,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP|subprocess.DETACHED_PROCESS)
print('v4.1 UI pid',child.pid)
