import sys,pathlib,json
sys.path.insert(0,'E:/xiuxian')
from assistant import Bot,RapidOCR
import cv2,numpy as np
root=pathlib.Path('E:/xiuxian');b=Bot.__new__(Bot)
b.cfg=json.loads((root/'config.json').read_text(encoding='utf-8-sig'))
b.meta=json.loads((root/'assets.json').read_text(encoding='utf-8'))
b.images={n:cv2.imdecode(np.frombuffer((root/'assets'/f'{n}.png').read_bytes(),np.uint8),1) for n in b.meta}
b.ocr=RapidOCR(intra_op_num_threads=2,inter_op_num_threads=2)
b.snap=lambda:b.frame
b.tap=lambda *p:(_ for _ in ()).throw(AssertionError('historical chat must not cause any click'))
for file,page,start in [('0027.jpg','palace_cultivate','palace_cultivate_start'),('0036.jpg','palace_court','palace_court_start')]:
    b.frame=cv2.imdecode(np.frombuffer((root/'logs/20261026-104208-694927'/file).read_bytes(),np.uint8),1)
    assert b.find(page) and b.find(start),(page,'page/start not recognized')
    assert not b.palace_reward_popup(page),'historical chat mistaken for reward dialog'
print('PASS actual failing screenshots: both start buttons detected; reward history does not trigger modal handling')
