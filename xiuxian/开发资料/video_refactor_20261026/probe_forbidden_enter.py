import sys,pathlib,msvcrt
sys.path.insert(0,'E:/xiuxian')
root=pathlib.Path('E:/xiuxian');lock=(root/'.running.lock').open('a+b');lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
from assistant import Bot
b=Bot();b.snap();b.video_button(('硬闯',),(100,650,620,850));b.pause_animation(2);b.snap()
(pathlib.Path(__file__).parent/'star_forbidden_enter.png').write_bytes(b.adb('exec-out','screencap','-p'))
print(b.text((0,0,720,1280)))
