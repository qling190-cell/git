import cv2,subprocess,time,pathlib,numpy as np
adb=r'D:\雷电\leidian\LDPlayer9\adb.exe';root=pathlib.Path('work')
def shot():
 data=subprocess.check_output([adb,'-s','emulator-5554','exec-out','screencap','-p']);return data,cv2.imdecode(np.frombuffer(data,np.uint8),1)
src=cv2.imdecode(np.frombuffer((root/'progress_rewards.png').read_bytes(),np.uint8),1)
panel=src[165:207,285:435];button=src[440:490,272:426]
for i in range(20):
 data,im=shot();(root/f'claim_checked_{i:02}.png').write_bytes(data)
 def match(t):
  _,v,_,p=cv2.minMaxLoc(cv2.matchTemplate(im,t,cv2.TM_CCOEFF_NORMED));return v,p
 v,_=match(panel);b,p=match(button)
 if v<.97 or b<.97: print('No claim button. Stop.',i,flush=True);break
 x,y=p
 before=im[max(230,y-210):y-15,90:625].copy()
 subprocess.check_call([adb,'-s','emulator-5554','shell','input','tap',str(x+77),str(y+25)])
 time.sleep(1.2)
 data,after=shot();(root/f'claim_result_{i:02}.png').write_bytes(data)
 crop=after[max(230,y-210):y-15,90:625]
 diff=np.mean(np.abs(before.astype(float)-crop.astype(float)))
 if diff<2:print('No card change, stop. diff=',diff,flush=True);break
 print('Reward card changed:',i+1,'diff=',round(diff,2),flush=True)
