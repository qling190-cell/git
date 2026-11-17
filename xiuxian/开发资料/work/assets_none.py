from pathlib import Path
from PIL import Image
import json
root=Path('outputs/太古仙尊实验版');meta=json.loads((root/'assets.json').read_text(encoding='utf-8'));box=(251,662,469,692)
Image.open('work/guard_none.png').crop(box).save(root/'assets/guard_none.png');meta['guard_none']={'box':box,'moving':False};(root/'assets.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
