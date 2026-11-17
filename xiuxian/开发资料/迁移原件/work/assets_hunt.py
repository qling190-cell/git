from pathlib import Path
from PIL import Image
import json
root=Path('outputs/太古仙尊实验版');meta=json.loads((root/'assets.json').read_text(encoding='utf-8'))
items={
'heaven_travel':('heaven_travel',(214,20,370,62)),
'secrets':('secrets',(128,24,213,67)),
'hunt':('hunt_ready',(326,176,394,212)),
'hunt_start':('hunt_ready',(297,1067,422,1100)),
'hunt_cost':('hunt_cost',(210,582,516,674)),
'hunt_cancel':('hunt_cost',(165,757,287,794)),
# Both selection windows share the title: transfer is distinguished by its cost labels below.
 'transfer_cost':('transfer',(144,795,279,826)),
}
for n,(src,box) in items.items():
 Image.open(Path('work')/(src+'.png')).crop(box).save(root/'assets'/(n+'.png'));meta[n]={'box':box,'moving':False}
(root/'assets.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
