# -*- coding: utf-8 -*-
import sys,pathlib,cv2
sys.path.insert(0,'E:/xiuxian')
from assistant import Bot
b=Bot();b.snap();b.require('market_shop')
for n in range(1,5):
 b.adb('shell','input','swipe',400,990,400,480,650);b.pause_animation(.7);b.snap()
 p=pathlib.Path(f'E:/xiuxian/开发资料/video_refactor_20261026/new_market_scroll{n}.png');p.write_bytes(cv2.imencode('.png',b.frame)[1].tobytes());print(n,b.words((130,180,645,1130)))
