# -*- coding: utf-8 -*-
import sys,pathlib,cv2
sys.path.insert(0,'E:/xiuxian')
from assistant import Bot
b=Bot();b.snap();body=b.words((0,1000,720,1280)).replace(' ','')
assert '悟道成功' in body and '获得' in body and '修为' in body,body
b.ledger['enlightenment_done']=True;b.ledger_save();b.tap(35,40);b.wait('island');b.market_open();b.tap(200,738);b.wait('market_shop');b.snap()
p=pathlib.Path('E:/xiuxian/开发资料/video_refactor_20261026/new_market_top.png');p.write_bytes(cv2.imencode('.png',b.frame)[1].tobytes());print(b.words())
