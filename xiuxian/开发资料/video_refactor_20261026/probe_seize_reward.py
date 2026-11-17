import pathlib,sys,msvcrt
root=pathlib.Path('E:/xiuxian');sys.path.insert(0,str(root))
lock=(root/'.running.lock').open('a+b');lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
from assistant import Bot
b=Bot();b.snap();body=b.words((80,200,650,1100))
assert '夺道奖励' in body and '修炼加速' in body
b.video_button(('夺道奖励',),(80,930,650,1055));b.pause_animation(.6);b.snap()
folder=pathlib.Path(__file__).resolve().parent
(folder/'seize_after_reward.png').write_bytes(b.adb('exec-out','screencap','-p'))
print(b.text((60,150,660,1240)))
