# -*- coding: utf-8 -*-
import pathlib,cv2,numpy as np,json
r=pathlib.Path('E:/xiuxian');p=r/'assets.json';d=json.loads(p.read_text(encoding='utf-8'))
im=cv2.imdecode(np.frombuffer((r/'开发资料/video_refactor_20261026/new_market_scroll1.png').read_bytes(),np.uint8),1)
(r/'assets/creation_dew_item.png').write_bytes(cv2.imencode('.png',im[739:812,93:167])[1].tobytes())
d['creation_dew_item']={'box':[93,739,167,812],'moving':True};p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
p=r/'assistant.py';s=p.read_text(encoding='utf-8');s=s.replace("choices=['sect_deadland',", "choices=['enlightenment','creation_dew','saint_beast','sect_deadland',");p.write_text(s,encoding='utf-8')
print('Added item template and CLI entry points')
