import pathlib,json,shutil,sys
from PIL import Image
root=pathlib.Path('outputs/太古仙尊实验版')
live=pathlib.Path('outputs/太古仙尊每日助手/太古仙尊每日助手')
meta=json.loads((root/'assets.json').read_text(encoding='utf-8'))
box=(10,5,74,70)
Image.open('work/ancestral_oppo_ready.png').crop(box).save(root/'assets/back_ancestral.png')
meta['back_ancestral']={'box':list(box),'moving':False}
(root/'assets.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
for name in ('daily_tasks.py','navigation.py','assets.json'):
    shutil.copy2(root/name,live/name)
shutil.copy2(root/'assets/back_ancestral.png',live/'assets/back_ancestral.png')
sys.path.insert(0,str(live.resolve()))
from assistant import Bot
import cv2,numpy as np
b=Bot();b.frame=cv2.imdecode(np.frombuffer(pathlib.Path('work/ancestral_oppo_ready.png').read_bytes(),np.uint8),1)
print('Ancestral title:',b.find('ancestral'),'new return:',b.find('back_ancestral'))
assert b.find('ancestral') and b.return_arrow_visible()
