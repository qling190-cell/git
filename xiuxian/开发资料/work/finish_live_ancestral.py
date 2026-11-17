import pathlib,sys,msvcrt
root=pathlib.Path('outputs/太古仙尊每日助手/太古仙尊每日助手').resolve()
sys.path.insert(0,str(root))
lock=(root/'.running.lock').open('a+b');lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
from assistant import Bot
b=Bot();b.snap();b.require('ancestral')
log=b.words((0,1040,720,1280))
assert '指点' in log and '提升' in log,log
b.ledger['ancestral']=True;b.ledger_save()
b.record('仙祠指点','实机确认完成',log)
b.back('ancestral','immortal_home')
print('Verified top-left return to immortal_home.')
pathlib.Path('work/ancestral_returned.png').write_bytes(b.adb('exec-out','screencap','-p'))
