import pathlib,sys
root=pathlib.Path('outputs/太古仙尊实验版').resolve();(root/'STOP').unlink(missing_ok=True);sys.path.insert(0,str(root))
from assistant import Bot
b=Bot();b.island();b.island_label('island_market');b.wait('market');b.tap(200,738)
