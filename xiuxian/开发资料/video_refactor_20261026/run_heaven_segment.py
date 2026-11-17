import pathlib,sys,msvcrt
root=pathlib.Path('E:/xiuxian');sys.path.insert(0,str(root))
lock=(root/'.running.lock').open('a+b');lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
for name in ('STOP','PAUSE','PAUSED'):(root/name).unlink(missing_ok=True)
from assistant import Bot
b=Bot();b.snap()
ok=b.run_groups([('heaven','仙界',['guard','quiz','gamble','jade','lecture','forbidden'])])
print('Heaven segment:',ok,'log:',b.out)
raise SystemExit(0 if ok else 2)
