import pathlib,sys,msvcrt
root=pathlib.Path('E:/xiuxian');sys.path.insert(0,str(root))
lock=(root/'.running.lock').open('a+b');lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
from assistant import Bot
b=Bot();b.snap();assert '已领取' in b.words((110,960,330,1040))
b.ledger['seize_reward_done']=True;b.ledger_save()
b.video_button(('修炼加速',),(400,950,620,1055));b.pause_animation(.6);b.snap()
folder=pathlib.Path(__file__).resolve().parent
(folder/'seize_after_boost.png').write_bytes(b.adb('exec-out','screencap','-p'))
print(b.text((60,150,660,1240)))
