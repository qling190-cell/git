# -*- coding: utf-8 -*-
import sys,pathlib,cv2
sys.path.insert(0,'E:/xiuxian')
from assistant import Bot
b=Bot();b.snap();b.star_open('探索');b.video_button(('游道',),(270,900,440,1060));b.pause_animation(.6);b.snap()
p=pathlib.Path('E:/xiuxian/开发资料/video_refactor_20261026/new_star_way.png');p.write_bytes(cv2.imencode('.png',b.frame)[1].tobytes());print(b.words())
