from pathlib import Path
from PIL import Image
import json
root=Path('outputs/太古仙尊实验版');meta=json.loads((root/'assets.json').read_text(encoding='utf-8'));box=(294,662,419,692)
Image.open('work/quiz_none.png').crop(box).save(root/'assets/quiz_none.png');meta['quiz_none']={'box':box,'moving':False};(root/'assets.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
