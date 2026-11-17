import cv2
from PIL import Image,ImageDraw
p=r'E:/xwechat_files/wxid_j5khzxq275oh22_15f9/temp/RWTemp/2026-10/9e20f478899dc29eb19741386f9343c8/51a41fdab13d96def1a4cbd52815a3a9.mp4'
c=cv2.VideoCapture(p)
fps=c.get(cv2.CAP_PROP_FPS); n=c.get(cv2.CAP_PROP_FRAME_COUNT); dur=n/fps
print(f'fps={fps}, frames={n}, duration={dur}, size={c.get(3)}x{c.get(4)}')
times=list(range(0,int(dur),max(1,int(dur/24))))[:25]
w=240; h=540
sheet=Image.new('RGB',(w*6,(h+25)*((len(times)+5)//6)), 'white');d=ImageDraw.Draw(sheet)
for i,t in enumerate(times):
 c.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,f=c.read()
 if not ok:continue
 im=Image.fromarray(cv2.cvtColor(f,cv2.COLOR_BGR2RGB)); im.thumbnail((w,h))
 x=(i%6)*w;y=(i//6)*(h+25)
 sheet.paste(im,(x,y+25));d.text((x+5,y+5),str(t)+'s',fill='black')
sheet.save('work/contact.jpg')
