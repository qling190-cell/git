import sys,pathlib,time
sys.path.insert(0,str(pathlib.Path('outputs/太古仙尊实验版').resolve()))
from assistant import Bot
b=Bot()
for arg in sys.argv[1:]:
    if arg.startswith('wait:'):time.sleep(float(arg[5:]));continue
    if arg=='ocr':
        b.snap();print(b.text());continue
    x,y=map(int,arg.split(','));b.tap(x,y)
pathlib.Path('work/current.png').write_bytes(b.adb('exec-out','screencap','-p'))
