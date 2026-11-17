# -*- coding: utf-8 -*-
import sys,pathlib,cv2
sys.path.insert(0,'E:/xiuxian')
from assistant import Bot
b=Bot();b.snap();b.tap(360,150);b.snap();b.close('market_shop',618,150,'market');b.back('market','island');b.back('island','heaven_nav');b.realm('mortal');b.tap(630,995);b.wait('travel');b.snap()
p=pathlib.Path('E:/xiuxian/开发资料/video_refactor_20261026/new_mortal_travel.png');p.write_bytes(cv2.imencode('.png',b.frame)[1].tobytes());print(b.words())
