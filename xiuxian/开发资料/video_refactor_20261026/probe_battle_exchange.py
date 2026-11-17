import pathlib,sys,msvcrt
root=pathlib.Path('E:/xiuxian');sys.path.insert(0,str(root))
lock=(root/'.running.lock').open('a+b');lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
for name in ('STOP','PAUSE','PAUSED'):(root/name).unlink(missing_ok=True)
from assistant import Bot
b=Bot();b.snap();b.journey_open();b.tap(220,995)
b.video_wait(('胜境','战境'),(0,0,720,150));b.tap(665,55);b.snap()
folder=pathlib.Path(__file__).resolve().parent
(folder/'battle_exchange_native.png').write_bytes(b.adb('exec-out','screencap','-p'))
print(b.text((70,150,650,1140)))
