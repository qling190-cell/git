import pathlib,json,shutil,sys
from PIL import Image
root=pathlib.Path('outputs/太古仙尊实验版')
live=pathlib.Path('outputs/太古仙尊每日助手/太古仙尊每日助手')
box=(10,15,65,78)
Image.open('work/journey_return.png').crop(box).save(root/'assets/back_journey.png')
meta=json.loads((root/'assets.json').read_text(encoding='utf-8'))
meta['back_journey']={'box':list(box),'moving':False}
(root/'assets.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
shutil.copy2(root/'assets.json',live/'assets.json')
shutil.copy2(root/'assets/back_journey.png',live/'assets/back_journey.png')
sys.path.insert(0,str(live.resolve()))
from assistant import Bot
import cv2,numpy as np
b=Bot()
for name,expected in [('journey_return',True),('night_return_failed',False)]:
    b.frame=cv2.imdecode(np.frombuffer(pathlib.Path(f'work/{name}.png').read_bytes(),np.uint8),1)
    assert bool(b.find('back_journey'))==expected
print('PASS: journey return recognized, dimmed arrow behind night modal rejected.')
