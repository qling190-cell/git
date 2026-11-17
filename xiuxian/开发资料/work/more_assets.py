from pathlib import Path
from PIL import Image
import json
root=Path('outputs/太古仙尊实验版'); meta=json.loads((root/'assets.json').read_text(encoding='utf-8'))
items={
'sword':('sword',(76,18,160,61),False),
'sword_match':('sword',(286,962,431,1006),False),
'sword_opponents':('sword_opponents',(302,190,416,222),False),
'sword_challenge':('sword_opponents',(504,306,613,339),True),
'guard':('guard',(262,394,458,431),False),
'guard_one':('guard',(140,824,288,866),False),
}
for n,(src,box,moving) in items.items():
 Image.open(Path('work')/(src+'.png')).crop(box).save(root/'assets'/(n+'.png'));meta[n]={'box':box,'moving':moving}
(root/'assets.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
