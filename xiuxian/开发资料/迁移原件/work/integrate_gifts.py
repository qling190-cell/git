# -*- coding: utf-8 -*-
import pathlib,json
from PIL import Image
root=pathlib.Path('outputs/太古仙尊实验版')
meta=json.loads((root/'assets.json').read_text(encoding='utf-8'))
box=(295,270,435,310)
Image.open('work/gift_before.png').crop(box).save(root/'assets/gift_dialog.png')
meta['gift_dialog']={'box':list(box),'moving':False}
(root/'assets.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
p=root/'assistant.py';s=p.read_text(encoding='utf-8')
s=s.replace('from night_tasks import NightTasks','from night_tasks import NightTasks\nfrom gift_tasks import GiftTasks')
s=s.replace('class Bot(Navigation, NightTasks, ApprovedTasks, PalaceTasks):','class Bot(Navigation, NightTasks, GiftTasks, ApprovedTasks, PalaceTasks):')
s=s.replace("'palace_tasks','night_tasks')","'palace_tasks','night_tasks','gift_tasks')")
s=s.replace("'raid','provisions','pond'","'raid','provisions','gifts','pond'")
p.write_text(s,encoding='utf-8')
p=root/'ui.py';s=p.read_text(encoding='utf-8')
s=s.replace("'珍馐坊采购': 'provisions',","'珍馐坊采购': 'provisions',\n    '仙祠一键赠予': 'gifts',")
p.write_text(s,encoding='utf-8')
