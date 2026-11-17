from pathlib import Path
from PIL import Image
import json
root=Path('outputs/太古仙尊实验版');meta=json.loads((root/'assets.json').read_text(encoding='utf-8'))
items={
'mortal_sect':('sect',(75,17,168,60)),
'practice':('practice_ready',(110,301,609,350)),
'practice_start':('practice_ready',(152,893,302,936)),
'practice_cost':('practice_ready',(174,945,281,976)),
'practice_running':('practice_running',(146,898,308,935)),
'journey':('journey',(113,22,202,65)),
'night':('night_ready',(325,155,398,190)),
'night_start':('night_ready',(284,1048,435,1093)),
'night_claim':('night_claim_ready',(285,984,434,1030)),
'stars':('stars_avatar',(110,21,203,63)),
'stars_locked':('stars_locked',(307,284,345,405)),
'star_rebuild':('starworld_locked',(277,190,449,231)),
}
for n,(src,box) in items.items():
 Image.open(Path('work')/(src+'.png')).crop(box).save(root/'assets'/(n+'.png'));meta[n]={'box':box,'moving':False}
(root/'assets.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
