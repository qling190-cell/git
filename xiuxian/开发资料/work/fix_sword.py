import pathlib,json,shutil,sys
from PIL import Image
root=pathlib.Path('outputs/太古仙尊实验版')
live=pathlib.Path('outputs/太古仙尊每日助手/太古仙尊每日助手')
image=Image.open('work/v42_sword_opponents.png')
assert image.size==(720,1280)
box=(611,183,642,215)
image.crop(box).save(root/'assets/sword_opponents_close.png')
meta=json.loads((root/'assets.json').read_text(encoding='utf-8'))
meta['sword_opponents_close']={'box':list(box),'moving':False}
(root/'assets.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
for name in ('assistant.py','navigation.py','assets.json'):
    shutil.copy2(root/name,live/name)
shutil.copy2(root/'assets/sword_opponents_close.png',live/'assets/sword_opponents_close.png')
shutil.copy2(live/'ledgers/oppo-ziling.json',root/'ledgers/oppo-ziling.json')
sys.path.insert(0,str(root.resolve()))
from assistant import Bot
import cv2,numpy as np
b=Bot()
b.frame=cv2.imdecode(np.frombuffer(pathlib.Path('work/v42_sword_opponents.png').read_bytes(),np.uint8),1)
print('popup:',b.find('sword_opponents'))
print('first challenge:',b.find('sword_challenge',roi=(495,294,625,350)))
print('specific X:',b.find('sword_opponents_close'))
print('old generic X:',[b.find(n,roi=(490,120,680,610)) for n in ('modal_close_white','modal_close_red')])
assert b.find('sword_opponents_close')
assert b.find('sword_challenge',roi=(495,294,625,350))
