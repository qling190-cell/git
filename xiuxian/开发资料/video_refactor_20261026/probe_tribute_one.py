import pathlib,sys,msvcrt
root=pathlib.Path('E:/xiuxian');sys.path.insert(0,str(root))
lock=(root/'.running.lock').open('a+b');lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
from assistant import Bot
b=Bot();b.snap();b.star_open('探索');b.tap(230,510);b.snap()
folder=pathlib.Path(__file__).resolve().parent
(folder/'tribute_city_native.png').write_bytes(b.adb('exec-out','screencap','-p'))
print('root-match:',b.find('stars'));print(b.text((80,150,650,1220)))
