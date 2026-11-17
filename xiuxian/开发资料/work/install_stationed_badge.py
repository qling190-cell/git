# -*- coding: utf-8 -*-
import pathlib,json
from PIL import Image
root=pathlib.Path('outputs/太古仙尊实验版')
Image.open('work/current.png').save('work/night_oppo_stationed.png')
box=(559,415,576,469)
Image.open('work/night_oppo_stationed.png').crop(box).save(root/'assets/night_stationed.png')
meta=json.loads((root/'assets.json').read_text(encoding='utf-8'))
meta['night_stationed']={'box':list(box),'moving':True}
(root/'assets.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
