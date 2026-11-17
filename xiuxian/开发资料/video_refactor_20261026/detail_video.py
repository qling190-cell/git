import pathlib,cv2
from PIL import Image,ImageDraw
root=pathlib.Path(__file__).resolve().parent
cap=cv2.VideoCapture(r'E:/xwechat_files/wxid_j5khzxq275oh22_15f9/msg/video/2026-10/6d9bc3ae33f13a6a1305bf0ce995445b.mp4')
windows=[('mortal',range(16,45)),('heaven',range(56,72)),('travel',range(152,178)),('void',range(190,211)),('stars',range(211,248)),('palace',range(248,276))]
for name,times in windows:
    frames=[]
    for seconds in times:
        cap.set(cv2.CAP_PROP_POS_MSEC,seconds*1000);ok,frame=cap.read()
        if not ok:continue
        im=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB));im.save(root/f'detail_{seconds:03}.png')
        frames.append((seconds,im))
    for start in range(0,len(frames),12):
        sheet=Image.new('RGB',(896,1515),'#eee');draw=ImageDraw.Draw(sheet)
        for i,(seconds,im) in enumerate(frames[start:start+12]):
            x=i%4*224;y=i//4*505;sheet.paste(im.resize((224,480)),(x,y+25));draw.text((x+8,y+5),str(seconds),fill='black')
        sheet.save(root/f'detail_{name}_{start//12}.jpg')
print('Detailed contact sheets ready.')
