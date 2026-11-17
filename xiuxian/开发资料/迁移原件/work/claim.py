import cv2,subprocess,time,pathlib,numpy as np
adb=r'D:\雷电\leidian\LDPlayer9\adb.exe'
root=pathlib.Path('work'); src=cv2.imdecode(np.frombuffer((root/'progress_rewards.png').read_bytes(),np.uint8),1)
panel=src[165:207,285:435]; button=src[440:490,272:426]
for i in range(25):
 data=subprocess.check_output([adb,'-s','emulator-5554','exec-out','screencap','-p'])
 (root/f'claim_{i:02}.png').write_bytes(data)
 im=cv2.imdecode(np.frombuffer(data,np.uint8),1)
 def match(t):
  _,v,_,p=cv2.minMaxLoc(cv2.matchTemplate(im,t,cv2.TM_CCOEFF_NORMED));return v,p
 v,_=match(panel);b,p=match(button)
 if v<.97 or b<.97: print('Stopped',i,v,b);break
 x,y=p;subprocess.check_call([adb,'-s','emulator-5554','shell','input','tap',str(x+77),str(y+25)])
 time.sleep(.8)
 print('Claimed',i+1)
