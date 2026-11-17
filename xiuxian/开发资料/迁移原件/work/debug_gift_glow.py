import pathlib,cv2,numpy as np
p=pathlib.Path('outputs/太古仙尊每日助手/太古仙尊每日助手/logs/20261025-033502-514426/0013.jpg')
frame=cv2.imdecode(np.frombuffer(p.read_bytes(),np.uint8),1);hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
for x,y in [(192,576),(360,576),(529,576)]:
    print(x,[(s,sum(cv2.countNonZero(cv2.inRange(hsv[y-15:y+20,left:right],np.array([18,s,185]),np.array([40,255,255]))) for left,right in [(x-72,x-52),(x+52,x+72)])) for s in (35,40,45,50,60)])
