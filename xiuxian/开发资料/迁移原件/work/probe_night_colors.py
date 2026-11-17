import cv2,numpy as np,pathlib,sys
sys.path.insert(0,str(pathlib.Path('outputs/太古仙尊实验版/vendor').resolve()))
frame=cv2.imdecode(np.frombuffer(pathlib.Path('work/night_oppo_latest.png').read_bytes(),np.uint8),1)
hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
for x,y in [(230,375),(470,445),(230,585),(470,585),(230,655)]:
    crop=hsv[y-20:y+20,x-80:x+80]
    print(x,y,np.median(crop.reshape(-1,3),axis=0))
mask=cv2.inRange(hsv[325:690,120:600],np.array([12,70,170]),np.array([40,255,255]))
mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,np.ones((7,11),np.uint8))
contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
print([cv2.boundingRect(c) for c in contours if cv2.boundingRect(c)[2]>150])
