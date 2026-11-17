import pathlib,sys,msvcrt
root=pathlib.Path('outputs/太古仙尊每日助手/太古仙尊每日助手').resolve()
sys.path.insert(0,str(root))
lock=(root/'.running.lock').open('a+b');lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
for name in ('STOP','PAUSE','PAUSED'):(root/name).unlink(missing_ok=True)
from assistant import Bot
b=Bot();b.snap();b.require('night');b.click('night_close');b.snap()
pathlib.Path('work/journey_return.png').write_bytes(b.adb('exec-out','screencap','-p'))
print('Journey recognized:',b.find('journey'),'arrow:',b.return_arrow_visible())
