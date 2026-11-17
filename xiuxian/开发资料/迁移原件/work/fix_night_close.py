# -*- coding: utf-8 -*-
import pathlib,json,shutil,sys
from PIL import Image
root=pathlib.Path('outputs/太古仙尊实验版')
live=pathlib.Path('outputs/太古仙尊每日助手/太古仙尊每日助手')
im=Image.open('work/current.png');im.save('work/night_return_failed.png')
meta=json.loads((root/'assets.json').read_text(encoding='utf-8'))
for name,box in [('oppo_night',(325,155,398,190)),('night_close',(612,150,645,185))]:
    im.crop(box).save(root/'assets'/f'{name}.png')
    meta[name]={'box':list(box),'moving':False}
(root/'assets.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
for folder in (root,live):
    p=folder/'config.json';cfg=json.loads(p.read_text(encoding='utf-8-sig'))
    if cfg.get('channel')=='oppo':cfg.setdefault('asset_aliases',{})['night']='oppo_night'
    p.write_text(json.dumps(cfg,ensure_ascii=False,indent=2),encoding='utf-8')
for name in ('assets.json','navigation.py'):shutil.copy2(root/name,live/name)
for name in ('oppo_night','night_close'):shutil.copy2(root/'assets'/f'{name}.png',live/'assets'/f'{name}.png')
sys.path.insert(0,str(live.resolve()))
from assistant import Bot
import cv2,numpy as np
b=Bot();b.frame=cv2.imdecode(np.frombuffer(pathlib.Path('work/night_return_failed.png').read_bytes(),np.uint8),1)
print('Night title:',b.find('night'),'close:',b.find('night_close'))
assert b.find('night') and b.find('night_close')
