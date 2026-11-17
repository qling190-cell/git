import ctypes as c, pathlib, html, math,re
from ctypes import wintypes as w
from PIL import Image,ImageDraw,ImageFont
ROOT=pathlib.Path(__file__).parent/'矢量图';ROOT.mkdir(exist_ok=True)
g=c.WinDLL('gdi32');u=c.WinDLL('user32')
u.SetProcessDPIAware()
g.CreateEnhMetaFileW.argtypes=[w.HDC,w.LPCWSTR,c.POINTER(w.RECT),w.LPCWSTR];g.CreateEnhMetaFileW.restype=w.HDC
g.CloseEnhMetaFile.argtypes=[w.HDC];g.CloseEnhMetaFile.restype=w.HANDLE
g.DeleteEnhMetaFile.argtypes=[w.HANDLE]
g.SelectObject.argtypes=[w.HDC,w.HANDLE];g.SelectObject.restype=w.HANDLE
g.CreatePen.argtypes=[c.c_int,c.c_int,w.DWORD];g.CreatePen.restype=w.HANDLE
g.CreateSolidBrush.argtypes=[w.DWORD];g.CreateSolidBrush.restype=w.HANDLE
g.CreateFontW.argtypes=[c.c_int]*5+[w.DWORD]*8+[w.LPCWSTR];g.CreateFontW.restype=w.HANDLE
g.TextOutW.argtypes=[w.HDC,c.c_int,c.c_int,w.LPCWSTR,c.c_int]
g.GetTextExtentPoint32W.argtypes=[w.HDC,w.LPCWSTR,c.c_int,c.POINTER(w.SIZE)]
g.MoveToEx.argtypes=[w.HDC,c.c_int,c.c_int,c.c_void_p]
g.LineTo.argtypes=[w.HDC,c.c_int,c.c_int]
g.Rectangle.argtypes=[w.HDC,c.c_int,c.c_int,c.c_int,c.c_int]
g.SetBkMode.argtypes=[w.HDC,c.c_int];g.DeleteObject.argtypes=[w.HANDLE]
g.GetDeviceCaps.argtypes=[w.HDC,c.c_int];g.GetDeviceCaps.restype=c.c_int
g.SetMapMode.argtypes=[w.HDC,c.c_int]
g.SetWindowExtEx.argtypes=[w.HDC,c.c_int,c.c_int,c.c_void_p]
g.SetViewportExtEx.argtypes=[w.HDC,c.c_int,c.c_int,c.c_void_p]
u.GetDC.argtypes=[w.HWND];u.GetDC.restype=w.HDC;u.ReleaseDC.argtypes=[w.HWND,w.HDC]

class Fig:
    def __init__(self,name,width=1200,height=700):
        self.name=name;self.W=width;self.H=height;self.svg=[];self.ops=[]
        self.ref=u.GetDC(None);rect=w.RECT(0,0,18000,round(18000*height/width))
        self.dc=g.CreateEnhMetaFileW(self.ref,str(ROOT/(name+'.emf')),c.byref(rect),'xiuxian report\0vector diagram\0\0')
        if not self.dc:raise RuntimeError('EMF creation failed')
        # Fit logical drawing units into the explicit 0.01-mm EMF frame.
        px=round(180*g.GetDeviceCaps(self.ref,8)/g.GetDeviceCaps(self.ref,4))
        py=round(180*height/width*g.GetDeviceCaps(self.ref,10)/g.GetDeviceCaps(self.ref,6))
        g.SetMapMode(self.dc,8);g.SetWindowExtEx(self.dc,width,height,None);g.SetViewportExtEx(self.dc,px,py,None)
        self.pen=g.CreatePen(0,2,0x222222);self.brush=g.CreateSolidBrush(0xffffff)
        self.oldpen=g.SelectObject(self.dc,self.pen);self.oldbrush=g.SelectObject(self.dc,self.brush)
        g.SetBkMode(self.dc,1)
    def box(self,x,y,width,height,lines):
        g.Rectangle(self.dc,x,y,x+width,y+height)
        self.svg.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" fill="white" stroke="#222" stroke-width="2"/>')
        self.ops.append(('box',(x,y,x+width,y+height)))
        for i,line in enumerate(lines):
            units=sum(1 if '\u4e00'<=a<='\u9fff' else .52 for a in line)
            size=min(28,int(width*.91/max(1,units)))
            self.text(x+width/2,y+height/2+(i-(len(lines)-1)/2)*36,line,size)
    def text(self,x,y,text,size=28):
        parts=re.findall(r'[\u4e00-\u9fff]+|[^\u4e00-\u9fff]+',text);runs=[]
        for part in parts:
            family='SimSun' if '\u4e00'<=part[0]<='\u9fff' else 'Times New Roman'
            font=g.CreateFontW(-size,0,0,0,400,0,0,0,1,0,0,4,0,family)
            old=g.SelectObject(self.dc,font);dim=w.SIZE();g.GetTextExtentPoint32W(self.dc,part,len(part),c.byref(dim));g.SelectObject(self.dc,old)
            runs.append((part,family,font,dim.cx))
        left=x-sum(a[3] for a in runs)/2
        for part,family,font,width in runs:
            old=g.SelectObject(self.dc,font);g.TextOutW(self.dc,round(left),round(y-size*.58),part,len(part));g.SelectObject(self.dc,old);g.DeleteObject(font);left+=width
        spans=''.join(f'<tspan font-family="{family}">{html.escape(part)}</tspan>' for part,family,_,_ in runs)
        self.svg.append(f'<text x="{x}" y="{y+size*.32}" text-anchor="middle" font-size="{size}" fill="black">{spans}</text>')
        self.ops.append(('text',(x,y,text,size,'SimSun' if any('\u4e00'<=a<='\u9fff' for a in text) else 'Times New Roman')))
    def line(self,points,arrow=True):
        for i,(x,y) in enumerate(points):
            (g.MoveToEx(self.dc,round(x),round(y),None) if i==0 else g.LineTo(self.dc,round(x),round(y)))
        if arrow:
            x,y=points[-1];px,py=points[-2];angle=math.atan2(y-py,x-px)
            for a in (-.45,.45):
                tx=x-15*math.cos(angle+a);ty=y-15*math.sin(angle+a)
                g.MoveToEx(self.dc,round(x),round(y),None);g.LineTo(self.dc,round(tx),round(ty))
        pts=' '.join(f'{x},{y}' for x,y in points)
        self.svg.append(f'<polyline points="{pts}" fill="none" stroke="#222" stroke-width="2"'+(' marker-end="url(#arrow)"' if arrow else '')+'/>')
        self.ops.append(('line',(points,arrow)))
    def save(self):
        g.SelectObject(self.dc,self.oldpen);g.SelectObject(self.dc,self.oldbrush)
        handle=g.CloseEnhMetaFile(self.dc);g.DeleteEnhMetaFile(handle);g.DeleteObject(self.pen);g.DeleteObject(self.brush);u.ReleaseDC(None,self.ref)
        svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.W}" height="{self.H}" viewBox="0 0 {self.W} {self.H}"><defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8" fill="none" stroke="#222"/></marker></defs><rect width="100%" height="100%" fill="white"/>'+''.join(self.svg)+'</svg>'
        (ROOT/(self.name+'.svg')).write_text(svg,encoding='utf-8')
        im=Image.new('RGB',(self.W,self.H),'white');draw=ImageDraw.Draw(im)
        for op,args in self.ops:
            if op=='box':draw.rectangle(args,outline='#222',width=2)
            elif op=='text':
                x,y,text,size,family=args;font=ImageFont.truetype('C:/Windows/Fonts/simsun.ttc' if family=='SimSun' else 'C:/Windows/Fonts/times.ttf',size)
                draw.text((x,y),text,font=font,fill='black',anchor='mm')
            else:
                points,arrow=args;draw.line(points,fill='#222',width=2)
                if arrow:
                    x,y=points[-1];px,py=points[-2];angle=math.atan2(y-py,x-px)
                    for a in (-.45,.45):draw.line([(x,y),(x-15*math.cos(angle+a),y-15*math.sin(angle+a))],fill='#222',width=2)
        im.save(ROOT/(self.name+'.png'))

def generate():
    f=Fig('图1_系统协作',1200,750)
    f.box(30,40,310,105,['操作面板 ui.py','主进程与日志显示'])
    f.box(470,40,680,105,['工作进程 assistant.py','main → Bot → run_groups → run_task'])
    f.line([(340,90),(470,90)]);f.text(400,65,'Popen',24)
    f.box(30,240,310,125,['配置与控制文件','config / STOP / PAUSE'])
    f.box(470,235,310,140,['调度与导航','workflow / navigation','hierarchy'])
    f.box(840,235,310,140,['任务实现','daily / video / palace','night / star / gift / 禁区'])
    f.line([(810,145),(810,195),(625,195),(625,235)])
    f.line([(780,305),(840,305)]);f.line([(340,300),(470,300)])
    f.box(470,475,310,115,['识别与动作','OpenCV / OCR / ADB'])
    f.box(840,475,310,115,['本地状态与证据','ledgers / logs / assets'])
    f.line([(995,375),(995,425),(625,425),(625,475)])
    f.line([(995,375),(995,475)]);f.line([(780,530),(840,530)])
    f.box(470,650,310,75,['雷电模拟器游戏界面'])
    f.line([(625,590),(625,650)]);f.text(980,715,'箭头表示主要调用或数据流',22);f.save()
    f=Fig('图2_识别动作闭环',1200,450)
    for x,lines in [(25,['截图','snap']), (265,['页面与按钮','find / OCR']), (505,['规则判断','次数与资源']), (745,['输入操作','tap / swipe']), (985,['结果核验','页面与计数'])]:f.box(x,95,190,140,lines)
    for x in (215,455,695,935):f.line([(x,165),(x+50,165)])
    f.line([(1080,235),(1080,335),(120,335),(120,235)])
    f.text(600,370,'未满足结果条件时等待或记录未完成，不凭一次点击判定成功',28);f.save()
    f=Fig('图3_页面层级与保留',1200,790)
    for x,root,sub in [(20,'仙界主界面',['宗门 island','弟子院 teaching','护法 guard / 课训 quiz']),(420,'仙界主界面',['游历 heaven_travel','探秘 secrets','降妖 / 仙猎 / 魔域']),(820,'元极主界面',['天阙 palace_map','同修 / 朝议 / 御木园','燃心灯直接在天阙收取'])]:
        if x==820:
            f.box(x,40,360,85,[root]);f.box(x,195,360,130,['天阙 palace_map','燃心灯在此收取'])
            f.line([(1000,125),(1000,195)]);f.line([(1000,325),(1000,365)],False)
            f.line([(875,365),(1125,365)],False)
            for cx,label in [(875,'同修'),(1000,'朝议'),(1125,'御木园')]:
                f.box(cx-52,420,104,90,[label]);f.line([(cx,365),(cx,420)])
            f.text(1000,600,'三项分别返回天阙地图',26)
            continue
        f.box(x,40,360,85,[root]);f.box(x,195,360,95,[sub[0]]);f.line([(x+180,125),(x+180,195)])
        f.box(x,375,360,95,[sub[1]]);f.line([(x+180,290),(x+180,375)])
        f.box(x,555,360,100,[sub[2]]);f.line([(x+180,470),(x+180,555)])
    f.text(600,720,'同级任务完成后停在共同父页面；不同入口之间才继续返回',28)
    f.text(600,760,'方框表示页面或任务入口；分支表示同级关系',25);f.save()
    f=Fig('图4_夜猎提交与恢复',1200,680)
    f.box(50,60,310,105,['准备状态','目标与剩余次数已确认'])
    f.box(445,60,310,105,['reserved','点击前写入提交预留'])
    f.box(840,60,310,105,['running','倒计时与扣次核验'])
    f.line([(360,110),(445,110)]);f.line([(755,110),(840,110)])
    f.box(840,290,310,105,['claimed','奖励已领取'])
    f.line([(995,165),(995,290)])
    f.box(445,290,310,140,['重启后重新观察','有倒计时则恢复运行','结果不明则阻止重提'])
    f.line([(600,165),(600,290)])
    f.box(50,300,310,125,['确认未提交','开始按钮存在','且游戏配额未变化'])
    f.line([(445,355),(360,355)]);f.line([(205,300),(205,165)])
    f.text(600,520,'预留记录降低重复提交风险，但不是与游戏服务器共享的事务',28)
    f.text(600,565,'ledger写入与progress写入独立，仍存在进程终止和文件损坏窗口',27);f.save()
    print('Created four SVG / EMF vector diagrams and PNG previews')
if __name__=='__main__':generate()
