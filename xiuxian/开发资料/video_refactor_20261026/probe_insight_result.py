# -*- coding: utf-8 -*-
import sys,pathlib,cv2
sys.path.insert(0,'E:/xiuxian')
from assistant import Bot
b=Bot();b.snap();b.pause_animation(4);b.snap();p=pathlib.Path('E:/xiuxian/开发资料/video_refactor_20261026/new_insight_result.png');p.write_bytes(cv2.imencode('.png',b.frame)[1].tobytes());print(b.words())
