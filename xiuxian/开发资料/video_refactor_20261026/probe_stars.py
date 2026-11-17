import pathlib,sys,msvcrt
root=pathlib.Path('E:/xiuxian');sys.path.insert(0,str(root))
lock=(root/'.running.lock').open('a+b');lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
from assistant import Bot
b=Bot();b.snap();b.star_open('探索');b.snap()
folder=pathlib.Path(__file__).resolve().parent
(folder/'stars_native.png').write_bytes(b.adb('exec-out','screencap','-p'))
print(b.text((60,100,710,1120)))
b.tap(650,230);b.snap()
(folder/'star_guard_native.png').write_bytes(b.adb('exec-out','screencap','-p'))
print('After guard click:',b.words((70,100,650,1120)))
