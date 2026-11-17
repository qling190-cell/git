import pathlib,sys,msvcrt
root=pathlib.Path('outputs/太古仙尊每日助手/太古仙尊每日助手').resolve()
sys.path.insert(0,str(root))
lock=(root/'.running.lock').open('a+b');lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
for name in ('STOP','PAUSE','PAUSED'):(root/name).unlink(missing_ok=True)
from assistant import Bot
b=Bot();b.snap()
assert '选择子嗣' in b.words((250,260,470,320))
pathlib.Path('work/gift_before.png').write_bytes(b.adb('exec-out','screencap','-p'))
b.tap(190,475);b.snap()
pathlib.Path('work/gift_selected.png').write_bytes(b.adb('exec-out','screencap','-p'))
print(b.text((110,400,610,905)))
