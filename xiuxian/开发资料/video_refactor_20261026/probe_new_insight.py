# -*- coding: utf-8 -*-
import sys,pathlib,json,cv2
sys.path.insert(0,'E:/xiuxian')
from assistant import Bot
r=pathlib.Path('E:/xiuxian');status=json.loads((r/'ui-state.json').read_text(encoding='utf-8'));assert status['state'] in ('stopped','ready','finished')
(r/'STOP').unlink(missing_ok=True);b=Bot();b.snap();b.island()
for i in range(4):
 b.snap();hits=b.button_positions(('悟道室',),(0,80,720,920))
 if len(hits)==1:b.tap(*hits[0]);break
 b.adb('shell','input','swipe',650,550,130,550,500);b.pause_animation(.7)
else:raise RuntimeError('悟道室入口未找到')
b.pause_animation(1);b.snap();p=r/'开发资料/video_refactor_20261026/new_insight.png';p.write_bytes(cv2.imencode('.png',b.frame)[1].tobytes());print(b.words());print(p)
