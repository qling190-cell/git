import sys,pathlib
sys.path.insert(0,str(pathlib.Path('outputs/太古仙尊实验版').resolve()))
from assistant import Bot
b=Bot();b.snap();b.close('guard',615,404,'teaching');b.back('teaching','island');b.back('island','heaven_nav');b.guard()
