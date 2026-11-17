import sys,pathlib,cv2,numpy as np
root=pathlib.Path('outputs/太古仙尊实验版');sys.path.insert(0,str(root.resolve()))
from assistant import Bot
b=Bot()
for src,label in [('work/mortal_stable.png','mortal_nav'),('work/heaven.png','heaven_nav'),('work/sign_before.png','main_anchor'),('work/forbidden_empty.png','forbidden'),('work/progress_rewards.png','forbidden_progress')]:
 im=cv2.imdecode(np.frombuffer(pathlib.Path(src).read_bytes(),np.uint8),1)
 found=b.find(label,frame=im)
 expected=label not in ['main_anchor','forbidden']
 assert bool(found)==expected,(src,label,found)
print('通过：两个主界面可识别；签到遮罩和禁地详情不会误识别为可操作的底层页面。')
