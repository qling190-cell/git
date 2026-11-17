# -*- coding: utf-8 -*-
import sys,pathlib,cv2
sys.path.insert(0,'E:/xiuxian')
from assistant import Bot
b=Bot();b.snap();b.require('market_shop');b.tap(130,775);b.snap();p=pathlib.Path('E:/xiuxian/开发资料/video_refactor_20261026/new_dew_tooltip.png');p.write_bytes(cv2.imencode('.png',b.frame)[1].tobytes());print(b.words())
