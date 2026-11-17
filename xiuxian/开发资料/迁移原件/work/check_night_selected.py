import pathlib,sys,cv2,numpy as np
sys.path.insert(0,str(pathlib.Path('outputs/太古仙尊实验版').resolve()))
from assistant import Bot
b=Bot()
for name in ('night_selected_failed','night_oppo_stationed','night_oppo_latest'):
    frame=cv2.imdecode(np.frombuffer(pathlib.Path(f'work/{name}.png').read_bytes(),np.uint8),1)
    buttons=b.night_buttons(frame)
    selected=[v for v in buttons if v['stationed'] or v['complete']]
    print(name,selected)
    assert len(selected)==4,name
print('PASS: selected highlight, normal stationed ribbons, completed badges all identify four targets.')
