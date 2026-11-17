import pathlib,cv2,json
from PIL import Image,ImageDraw
root=pathlib.Path(__file__).resolve().parent
source=r'E:/xwechat_files/wxid_j5khzxq275oh22_15f9/msg/video/2026-10/6d9bc3ae33f13a6a1305bf0ce995445b.mp4'
cap=cv2.VideoCapture(source)
duration=cap.get(cv2.CAP_PROP_FRAME_COUNT)/cap.get(cv2.CAP_PROP_FPS)
frames=[]
for seconds in range(0,int(duration)+1,5):
    cap.set(cv2.CAP_PROP_POS_MSEC,seconds*1000);ok,frame=cap.read()
    if not ok:continue
    im=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
    im.save(root/f'frame_{seconds:03}.png')
    frames.append((seconds,im))
for start in range(0,len(frames),12):
    sheet=Image.new('RGB',(224*4,505*3),'#eeeeee');draw=ImageDraw.Draw(sheet)
    for i,(seconds,im) in enumerate(frames[start:start+12]):
        x=(i%4)*224;y=(i//4)*505
        sheet.paste(im.resize((224,480)),(x,y+25))
        draw.text((x+8,y+5),f'{seconds//60:02}:{seconds%60:02}',fill='black')
    sheet.save(root/f'sheet_{start//12:02}.jpg')
print('seconds',duration,'frames',len(frames),'sheets',(len(frames)+11)//12)
