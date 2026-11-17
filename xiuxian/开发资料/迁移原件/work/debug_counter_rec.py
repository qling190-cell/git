import pathlib,sys,cv2
sys.path.insert(0,str(pathlib.Path('outputs/太古仙尊实验版').resolve()))
from assistant import Bot
b=Bot();b.snap()
for box in [(280,1018,445,1048),(413,1020,442,1047),(270,1012,460,1058)]:
 x,y,r,d=box;im=b.frame[y:d,x:r];res,_=b.ocr(im,use_det=False,use_cls=False);print(box,res)
