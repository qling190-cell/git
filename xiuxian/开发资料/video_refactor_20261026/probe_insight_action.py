# -*- coding: utf-8 -*-
import sys,pathlib,cv2,json
sys.path.insert(0,'E:/xiuxian')
from assistant import Bot
b=Bot();b.snap();b.video_button(('悟道',),(200,630,340,850));b.pause_animation(1);b.snap()
p=pathlib.Path('E:/xiuxian/开发资料/video_refactor_20261026/new_insight_action.png');p.write_bytes(cv2.imencode('.png',b.frame)[1].tobytes());print(b.words())
