import sys,pathlib,cv2,numpy as np
root=pathlib.Path('outputs/太古仙尊实验版');sys.path.insert(0,str(root.resolve()))
from assistant import Bot
b=Bot(); dirs=sorted(p for p in (root/'logs').iterdir() if (p/'events.txt').exists()); prev=dirs[-1]
for p in reversed(sorted(prev.glob('*.png'))):
 im=cv2.imdecode(np.frombuffer(p.read_bytes(),np.uint8),1)
 if b.find('quiz',frame=im):
  print(b.text((135,687,585,969),frame=im));break
