import pathlib,sys,msvcrt
root=pathlib.Path('outputs/太古仙尊每日助手/太古仙尊每日助手').resolve()
sys.path.insert(0,str(root))
lock=(root/'.running.lock').open('a+b');lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
from assistant import Bot
b=Bot();b.snap()
assert '指点' in b.words((80,300,645,1000))
b.text_button('确定',(100,350,620,1000));b.snap()
print('title:',b.find('ancestral'),'disabled:',b.find('ancestral_disabled'))
print(b.words((0,1040,720,1280)))
pathlib.Path('work/ancestral_after_confirm.png').write_bytes(b.adb('exec-out','screencap','-p'))
