import pathlib,sys,cv2,numpy as np
sys.path.insert(0,str(pathlib.Path('outputs/太古仙尊实验版').resolve()))
from assistant import Bot
b=Bot();folder=pathlib.Path('outputs/太古仙尊每日助手/太古仙尊每日助手/logs/20261025-033502-514426')
for index in range(11,16):
    p=folder/f'{index:04}.jpg';b.frame=cv2.imdecode(np.frombuffer(p.read_bytes(),np.uint8),1)
    print(index,[(c,b.gift_selected(c['pos'])) for c in b.gift_cards()])
