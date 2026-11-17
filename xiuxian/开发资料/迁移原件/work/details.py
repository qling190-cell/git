import cv2
from PIL import Image,ImageDraw
p=r'E:/xwechat_files/wxid_j5khzxq275oh22_15f9/temp/RWTemp/2026-10/9e20f478899dc29eb19741386f9343c8/51a41fdab13d96def1a4cbd52815a3a9.mp4'
c=cv2.VideoCapture(p);times=[28,36,160,168,187,198,220,242];out=Image.new('RGB',(448*4,985*2),'white');d=ImageDraw.Draw(out)
for i,t in enumerate(times):
 c.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,f=c.read()
 if ok:
  x=i%4*448;y=i//4*985;out.paste(Image.fromarray(cv2.cvtColor(f,cv2.COLOR_BGR2RGB)),(x,y+25));d.text((x+5,y+5),str(t)+'s',fill='black')
out.save('work/details.jpg')
