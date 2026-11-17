import pathlib,sys,msvcrt
root=pathlib.Path('E:/xiuxian');sys.path.insert(0,str(root))
lock=(root/'.running.lock').open('a+b');lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
from assistant import Bot
b=Bot();b.snap();b.mortal_sect_open();b.tap(230,675)
b.video_wait(('门派首徒','俸禄','切磋'));b.video_button(('兑换',),(300,400,580,850));b.snap()
folder=pathlib.Path(__file__).resolve().parent
(folder/'exchange_native.png').write_bytes(b.adb('exec-out','screencap','-p'))
print(b.text((70,200,650,1050)))
