import pathlib,sys,msvcrt
root=pathlib.Path('outputs/太古仙尊每日助手/太古仙尊每日助手').resolve()
sys.path.insert(0,str(root))
lock=(root/'.running.lock').open('a+b');lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
(root/'STOP').unlink(missing_ok=True)
from assistant import Bot
b=Bot();b.snap();b.require('ancestral');b.tap(567,705);b.snap()
print(b.words((60,300,660,1000)))
pathlib.Path('work/ancestral_prompt.png').write_bytes(b.adb('exec-out','screencap','-p'))
