import sys,pathlib
sys.path.insert(0,str(pathlib.Path('outputs/太古仙尊实验版').resolve()))
from assistant import Bot
b=Bot();b.snap();b.close('family_panel',622,206,'family');b.back('family','immortal_home');b.back('immortal_home','void_nav')
