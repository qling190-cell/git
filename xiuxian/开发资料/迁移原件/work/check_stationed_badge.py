import pathlib,sys,cv2,numpy as np
sys.path.insert(0,str(pathlib.Path('outputs/太古仙尊实验版').resolve()))
from assistant import Bot
b=Bot()
frame=cv2.imdecode(np.frombuffer(pathlib.Path('work/night_oppo_stationed.png').read_bytes(),np.uint8),1)
buttons=b.night_buttons(frame)
selected=[v for v in buttons if v['stationed']]
print('Stationed:',selected)
print('All buttons:',buttons,'badge anywhere:',b.find('night_stationed',frame=frame))
assert len(selected)==4
assert [v['pos'][0]>350 for v in selected]==[True,False,True,False]
assert not next(v for v in buttons if '燃灭' in v['name'])['stationed']
assert not next(v for v in buttons if '死煞' in v['name'])['stationed']
print('PASS: four actual stationed badges; unlocked but unstationed buttons excluded.')
