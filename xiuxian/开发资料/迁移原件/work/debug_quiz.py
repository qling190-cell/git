import sys,pathlib,cv2,numpy as np
root=pathlib.Path('outputs/太古仙尊实验版');sys.path.insert(0,str(root.resolve()))
from assistant import Bot
b=Bot()
for p in sorted((root/'logs/20261024-141525-022744').glob('*.png')):
 im=cv2.imdecode(np.frombuffer(p.read_bytes(),np.uint8),1)
 if b.find('quiz',frame=im):
  print(p.name,b.text((135,687,585,969),frame=im))
