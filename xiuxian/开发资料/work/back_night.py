import sys,pathlib
sys.path.insert(0,str(pathlib.Path('outputs/太古仙尊实验版').resolve()))
from assistant import Bot
b=Bot();b.snap();b.close('night',628,166,'journey');b.back('journey','void_nav')
