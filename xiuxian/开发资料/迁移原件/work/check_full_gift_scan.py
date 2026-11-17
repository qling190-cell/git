import pathlib,sys,cv2,numpy as np
sys.path.insert(0,str(pathlib.Path('outputs/太古仙尊实验版').resolve()))
from assistant import Bot
b=Bot();seen={}
folder=pathlib.Path('outputs/太古仙尊每日助手/太古仙尊每日助手/logs/20261025-033903-448823')
for p in sorted(folder.glob('*.jpg')):
    b.frame=cv2.imdecode(np.frombuffer(p.read_bytes(),np.uint8),1)
    if not b.find('gift_dialog'):continue
    for c in b.gift_cards():seen[c['name']]=c['quality']
print(len(seen),seen)
assert len(seen)==22
