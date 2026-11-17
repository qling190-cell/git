import sys,pathlib,msvcrt
sys.path.insert(0,'E:/xiuxian')
root=pathlib.Path('E:/xiuxian')
lock=(root/'.running.lock').open('a+b');lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
from assistant import Bot
b=Bot();b.snap()
if not b.video_page('smallworld_map',b.frame):
    b.heaven_travel_open();b.tap(430,40);b.wait('smallworld_map')
b.video_button(('事件',),(250,940,460,1140));b.snap()
folder=pathlib.Path(__file__).parent
(folder/'smallworld_events_native.png').write_bytes(b.adb('exec-out','screencap','-p'))
print('OPTIONS',b.smallworld_event_options())
for box in b.smallworld_event_options():print(box,b.words(box))
print('BODY',b.words((40,0,680,1200)))
b.video_close('smallworld_map')
