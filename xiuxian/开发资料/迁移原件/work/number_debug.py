import sys,pathlib
sys.path.insert(0,str(pathlib.Path('outputs/太古仙尊实验版').resolve()))
from assistant import Bot
b=Bot();b.snap()
for roi in [(214,985,425,1034),(290,990,345,1028),(270,985,360,1032)]:
 x,y,r,d=roi;print(roi,b.ocr(b.frame[y:d,x:r],use_det=False,use_cls=False)[0],b.words(roi))
