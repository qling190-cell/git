import sys,pathlib
sys.path.insert(0,str(pathlib.Path('outputs/太古仙尊实验版').resolve()))
from assistant import Bot
b=Bot();b.island();b.island_label('island_teaching');b.wait('teaching');b.tap(194,738)
