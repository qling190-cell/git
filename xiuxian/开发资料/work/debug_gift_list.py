import pathlib,sys,cv2,numpy as np
sys.path.insert(0,str(pathlib.Path('outputs/太古仙尊实验版').resolve()))
from assistant import Bot
b=Bot();seen={}
folder=pathlib.Path('outputs/太古仙尊每日助手/太古仙尊每日助手/logs/20261025-033030-589581')
for p in sorted(folder.glob('*.jpg')):
    b.frame=cv2.imdecode(np.frombuffer(p.read_bytes(),np.uint8),1)
    if not b.find('gift_dialog'):continue
    cards=b.gift_cards()
    for c in cards:seen[c['name']]=c['quality']
    print(p.name,[(c['name'],c['quality']) for c in cards])
print('All:',len(seen),seen)
