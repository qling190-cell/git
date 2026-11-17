import pathlib,sys,msvcrt
root=pathlib.Path('E:/xiuxian');sys.path.insert(0,str(root))
lock=(root/'.running.lock').open('a+b');lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
for name in ('STOP','PAUSE','PAUSED'):(root/name).unlink(missing_ok=True)
from assistant import Bot
b=Bot();b.snap();b.recover_to_main('视频层级核对');b.mortal_sect_open();b.snap()
folder=pathlib.Path(__file__).resolve().parent
(folder/'sect_native.png').write_bytes(b.adb('exec-out','screencap','-p'))
b.tap(360,995);b.snap()
(folder/'deadland_native.png').write_bytes(b.adb('exec-out','screencap','-p'))
print(b.text((70,140,650,1130)))
