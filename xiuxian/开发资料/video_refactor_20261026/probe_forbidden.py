import sys,pathlib,msvcrt
sys.path.insert(0,'E:/xiuxian')
root=pathlib.Path('E:/xiuxian')
lock=(root/'.running.lock').open('a+b');lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
from assistant import Bot
b=Bot();b.snap()
print('BEFORE',b.words((30,0,690,1200)))
body=b.words((30,0,690,1200))
if '运转全部' in body and '天道' in body:b.video_close(None);b.snap()
print('AFTER_CLOSE',b.words((0,0,720,1280)))
b.star_open('禁区');b.snap()
folder=pathlib.Path(__file__).parent
(folder/'star_forbidden_native.png').write_bytes(b.adb('exec-out','screencap','-p'))
print('FORBIDDEN',b.text((0,0,720,1280)))
