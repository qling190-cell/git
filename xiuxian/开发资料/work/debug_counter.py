import pathlib,sys,cv2
sys.path.insert(0,str(pathlib.Path('outputs/太古仙尊实验版').resolve()))
from assistant import Bot
b=Bot();b.snap();print(b.text((260,1012,480,1060)))
for scale in [2,3,4]:
 im=cv2.resize(b.frame[1012:1060,260:480],None,fx=scale,fy=scale)
 r,_=b.ocr(im);print(scale,[(x[1],round(x[2],3)) for x in r or []])
