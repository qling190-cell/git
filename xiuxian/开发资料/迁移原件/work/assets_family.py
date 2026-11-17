from pathlib import Path
from PIL import Image
import json
root=Path('outputs/太古仙尊实验版');meta=json.loads((root/'assets.json').read_text(encoding='utf-8'))
items={
'immortal_home':('immortal_home',(111,20,186,61)),
'family':('family',(86,20,236,61)),
'family_panel':('family_claim',(291,194,430,231)),
'family_claim':('family_claim',(286,996,434,1039)),
'family_start':('family_start_ready',(286,996,434,1039)),
}
for n,(src,box) in items.items():
 Image.open(Path('work')/(src+'.png')).crop(box).save(root/'assets'/(n+'.png'));meta[n]={'box':box,'moving':False}
(root/'assets.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
