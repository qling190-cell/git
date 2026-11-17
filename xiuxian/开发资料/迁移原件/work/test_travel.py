import sys,pathlib
sys.path.insert(0,str(pathlib.Path('outputs/太古仙尊实验版').resolve()))
from assistant import Bot
b=Bot();b.snap();b.close('wander_panel',610,190,'travel');b.back('travel','mortal_nav');b.travel()
