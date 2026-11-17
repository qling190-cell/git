# -*- coding: utf-8 -*-
import pathlib,re,html,json,hashlib
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Table,TableStyle,Flowable,XPreformatted,KeepTogether
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT,TA_CENTER
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT=pathlib.Path(__file__).parent;ROOT.mkdir(exist_ok=True)
for name,path in [('Song','simsun.ttc'),('Hei','simhei.ttf'),('Times','times.ttf'),('TimesBold','timesbd.ttf')]:
    pdfmetrics.registerFont(TTFont(name,'C:/Windows/Fonts/'+path,subfontIndex=0))
pdfmetrics.registerFontFamily('Times',normal='Times',bold='TimesBold',italic='Times',boldItalic='TimesBold')
W,H=A4;CONTENT=W-100;story=[];chapter=[]
styles={
'body':ParagraphStyle('Body',fontName='Times',fontSize=12,leading=20,spaceAfter=9,wordWrap='CJK'),
'small':ParagraphStyle('Small',fontName='Times',fontSize=10.5,leading=16,spaceAfter=7,wordWrap='CJK'),
'title':ParagraphStyle('Title',fontName='TimesBold',fontSize=22,leading=33,alignment=TA_CENTER,spaceAfter=14),
'h1':ParagraphStyle('Heading',fontName='TimesBold',fontSize=16,leading=24,spaceAfter=13,wordWrap='CJK'),
'h2':ParagraphStyle('Subheading',fontName='TimesBold',fontSize=14,leading=21,spaceBefore=6,spaceAfter=8,wordWrap='CJK'),
'code':ParagraphStyle('Code',fontName='Times',fontSize=10.5,leading=14.5,spaceBefore=5,spaceAfter=10),
'cell':ParagraphStyle('Cell',fontName='Times',fontSize=10.5,leading=15,wordWrap='CJK'),
'caption':ParagraphStyle('Caption',fontName='Times',fontSize=10.5,leading=15,alignment=TA_CENTER,spaceAfter=12)}

def rich(text,cn='Song'):
    return ''.join('<font name="'+cn+'">'+html.escape(t)+'</font>' if any(ord(a)>127 for a in t) else html.escape(t)
                   for t in re.findall(r'[^\x00-\x7f]+|[\x00-\x7f]+',text))
def p(text,small=False):story.append(Paragraph(rich(text),styles['small' if small else 'body']))
def sub(text):story.append(Paragraph(rich(text,'Hei'),styles['h2']))
def page(title):
    first=not story
    if story:story.append(PageBreak())
    chapter.append(title);story.append(Paragraph(rich(title,'Hei'),styles['title' if first else 'h1']))
def code(text,where='Python示例'):
    p(where,True);story.append(XPreformatted(rich(text),styles['code']))
def table(headers,rows,widths=None):
    data=[[Paragraph(rich(str(t),'Hei'),styles['cell']) for t in headers]]
    data.extend([[Paragraph(rich(str(t)),styles['cell']) for t in row] for row in rows])
    widths=widths or [CONTENT/len(headers)]*len(headers)
    t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#ededed')),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#cccccc')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
    story.extend([t,Spacer(1,10)])

def drawtext(c,x,y,text,size=11,center=False):
    segments=re.findall(r'[^\x00-\x7f]+|[\x00-\x7f]+',text)
    parts=[(s,'Song' if any(ord(a)>127 for a in s) else 'Times') for s in segments]
    width=sum(pdfmetrics.stringWidth(s,f,size) for s,f in parts)
    xx=x-width/2 if center else x
    for s,f in parts:
        c.setFont(f,size);c.drawString(xx,y,s);xx+=pdfmetrics.stringWidth(s,f,size)
class Diagram(Flowable):
    def __init__(self,kind,height):Flowable.__init__(self);self.width=CONTENT;self.height=height;self.kind=kind
    def draw(self):
        c=self.canv;h=self.height;c.setStrokeColor(colors.HexColor('#333333'));c.setFillColor(colors.black);c.setLineWidth(.8)
        def box(x,y,w,hh,lines):
            c.rect(x,h-y-hh,w,hh,stroke=1,fill=0)
            for i,line in enumerate(lines):drawtext(c,x+w/2,h-y-hh/2+((len(lines)-1)/2-i)*15-4,line,10.5,True)
        def arrow(x1,y1,x2,y2):
            c.line(x1,h-y1,x2,h-y2)
            import math
            a=math.atan2(y2-y1,x2-x1)
            for d in (-.45,.45):c.line(x2,h-y2,x2-7*math.cos(a+d),h-y2+7*math.sin(a+d))
        if self.kind=='loop':
            labels=[['截图','ADB'],['识别','OpenCV / OCR'],['判断','Python'],['点击','ADB'],['确认结果','再截图']]
            for i,label in enumerate(labels):box(3+i*100,22,88,58,label)
            for i in range(4):arrow(91+i*100,51,103+i*100,51)
            c.line(447,h-80,447,h-106);c.line(447,h-106,47,h-106);arrow(47,106,47,80)
            drawtext(c,CONTENT/2,h-132,'程序每做一步，都要重新观察游戏是否按预期变化。',11,True)
        elif self.kind=='coords':
            x,y,pw,ph=35,15,162,288;c.rect(x,h-y-ph,pw,ph)
            drawtext(c,x,h-9,'(0, 0)',10)
            arrow(x,y,x+pw,y);arrow(x,y,x,y+ph)
            drawtext(c,x+pw+3,h-y,'X',10);drawtext(c,x-14,h-y-ph,'Y',10)
            rx=x+80/720*pw;ry=y+500/1280*ph;rw=(640-80)/720*pw;rh=(850-500)/1280*ph
            c.setDash(3,2);c.rect(rx,h-ry-rh,rw,rh);c.setDash()
            xx=x+360/720*pw;yy=y+800/1280*ph;c.circle(xx,h-yy,3,fill=1)
            drawtext(c,225,h-65,'原始截图：720 × 1280',12)
            drawtext(c,225,h-105,'虚线框是识别区域 ROI',12)
            drawtext(c,225,h-137,'(80, 500, 640, 850)',12)
            drawtext(c,225,h-177,'顺序：左、上、右、下',12)
            drawtext(c,225,h-217,'黑点：(360, 800)',12)
            drawtext(c,225,h-249,'示意图，不是实际游戏按钮位置',10.5)
        elif self.kind=='memory':
            for x,y,label in [(15,15,['内存变量','amount = 220','进程结束就丢失']),(265,15,['任务账本 ledger','已启动次数 / 提交预留','写入JSON后保留']),(15,130,['流程进度 progress','处理过什么 / 下项在哪','resume读取断点']),(265,130,['运行日志 logs','文字 / 截图 / 报告','供你回看，不自动学习'])]:box(x,y,210,90,label)
        elif self.kind=='state':
            box(10,25,135,65,['准备开始','先确认次数与目标']);box(180,25,135,65,['reserved','先保存提交预留']);box(350,25,135,65,['running','再确认倒计时'])
            arrow(145,58,180,58);arrow(315,58,350,58)
            box(180,145,135,65,['重启后核对','结果不明不再点'])
            arrow(247,90,247,145);arrow(315,178,417,90)
            drawtext(c,CONTENT/2,h-245,'预留记录是防重复的线索，不是游戏服务器的交易凭证。',11,True)
        elif self.kind=='debug':
            for y,lines in [(5,['1 看日志和截图','程序认为在哪？实际在哪？']),(95,['2 查看 body、hits、phase','识别错了？入口错了？记录错了？']),(185,['3 只修改一个原因','先测截图，再实机运行单项'])]:
                box(50,y,395,65,lines)
            arrow(247,70,247,95);arrow(247,160,247,185)
        elif self.kind=='vscode':
            c.rect(4,12,CONTENT-8,h-20)
            drawtext(c,15,h-28,'VS Code调试布局示意',12)
            c.line(155,12,155,h-42);c.line(4,h-42,CONTENT-4,h-42)
            for j,t in enumerate(['变量','amount = 220','phase = started','self.ledger = {...}']):drawtext(c,14,h-65-j*26,t,10.5)
            for j,t in enumerate(['amount = self.lamp_amount()','if amount > 0:','    self.click("palace_lamp_claim")']):drawtext(c,177,h-77-j*30,t,10.5)
            c.setFillColor(colors.HexColor('#b63232'));c.circle(166,h-102,4,fill=1,stroke=0);c.setFillColor(colors.black)
            drawtext(c,177,37,'红点是断点；停住后先检查变量再继续。',10.5)
def fig(kind,height,caption):story.append(Diagram(kind,height));story.append(Paragraph(rich(caption),styles['caption']))

page('太古仙尊助手项目介绍与手动调试教程')
p('从看懂任务流程，到自己定位和修复一个异常。',False)
p('适用对象：能够使用电脑和VS Code，但尚未系统学习Python的项目维护者。')
fig('loop',155,'图1　脚本完成游戏操作的基本闭环')
sub('你要逐步掌握的三件事')
p('第一，能把项目讲清楚：它做什么、你参与了什么、哪些地方使用AI辅助。第二，能看懂一个具体任务：从哪进入、如何判断、点击以后怎样确认。第三，遇到异常时能找截图、看变量、改一个条件，再验证。')
sub('本教程与旧报告的关系')
p('旧版37页报告解释项目结构；本教程解释怎样阅读、操作和调试。示例已对照2026年10月27日的源码核对。当前workflow版本为6，部分任务和“全部日常”的行为已更新，不能把昨天的报告当成永不变化的操作说明。')
p('本教程没有启动游戏任务，没有修改项目业务代码，也没有清空当天进度。插图为代码绘制的矢量示意，界面示意不冒充真实截图。',True)
p('阅读路线：第1—4节学介绍与语法，第5—10节看识别与动作，第11—15节看进度记忆，第16—22节练异常排查与调试。',True)

page('1 怎样向别人介绍这个项目')
sub('可以直接使用的介绍')
p('我正在开发和维护一个Python安卓游戏日常助手。它通过雷电模拟器截图识别按钮、文字和任务状态，再模拟点击完成重复任务。现在已经实现任务排序、暂停、当天进度记录和部分倒计时收尾。')
p('我主要负责梳理游戏操作、制定规则、实机测试和定位异常；代码使用AI辅助开发，我正在学习独立调试和维护。')
sub('被问到具体做了什么时')
p('我把手动日常拆成了签到、夜猎、同修、朝会等任务。每项都明确入口、条件、动作、成功证据和返回页面。例如天阙先收燃心灯，再做同修、朝议和御木园，任务之间只回天阙地图。夜猎需要识别四个已驻扎地点，每处15次，并保存次数避免重复提交。')
table(['你实际参与的工作','可以怎样表达'],[
('操作与规则设计','我整理了任务顺序、资源限制和不同状态的处理规则。'),
('测试与问题反馈','我用实际游戏画面检查结果，保留失败日志和截图。'),
('AI辅助实现','我使用AI帮助编写和修改，自己核对操作是否符合需求。'),
('正在学习维护','我开始学习读变量、设断点和修改判断，不把尚未掌握的能力说成已经熟练。')],[145,CONTENT-145])
p('不要把“有若干任务跑通”说成“全部任务永久稳定”，也不必把使用AI藏起来。能解释一个真实问题如何产生、如何确认修复，比背技术名词更有说服力。')

page('2 各种工具分别负责什么')
table(['工具','通俗解释','项目里的作用'],[
('Python','写规则和安排步骤的语言','如果有奖励就领取；若未开放则跳过。'),
('ADB','电脑与安卓设备通信的工具','截图、点击、滑动、检查前台应用。'),
('OpenCV','处理和比较图像的工具库','拿叉号小图到截图中寻找相似位置；辅助判断颜色。'),
('RapidOCR','把图片中的字读成文本','读取领取、倒计时、剩余次数和状态。'),
('Tkinter','制作Python桌面窗口','开始、暂停、停止、任务菜单与日志显示。'),
('JSON','一种保存结构化数据的文本格式','保存配置、当天计数和流程进度。')],[75,175,CONTENT-250])
sub('它们怎样配合')
p('Python先让ADB截图，再让OpenCV或OCR寻找目标。判断可以操作后，Python把坐标交给ADB；点完再截图核对，确认后把状态写进JSON。Tkinter只是给这套流程提供一个操作面板。')
p('ADB不会理解“领取”。它只知道在某个坐标点一下。OpenCV不会理解任务规则，它只比较图像。OCR能读出“获得奖励”，但不知道那是当前弹窗还是历史聊天。最后的判断仍然由你写的规则负责。')

page('3 Python语句是怎样从需求写出来的')
p('先把人的操作说清楚，再翻译成条件和动作。以燃心灯为例：进入天阙，读取愿力；大于0就收取，之后确认归零；等于0就跳过。')
code('self.snap()\nself.require("palace_map")\namount = self.lamp_amount()\n\nif amount > 0:\n    self.click("palace_lamp_claim")','现有任务中的核心语句，放在Bot方法内部使用')
table(['语句','读法'],[
('amount = ...','把右侧计算出的值，保存到名为amount的变量。'),
('if amount > 0:','如果amount大于0，就执行缩进部分。'),
('self.snap()','调用当前助手对象的截图方法。'),
('self.require(...)','确认当前页面符合预期，不符合就报告异常。'),
('self.click(...)','按素材名称查找按钮，再点击找到的位置。')],[170,CONTENT-170])
p('if、for、return、=是Python语法；snap、lamp_amount和click是本项目自己定义的方法。看到不认识的方法，可以先跳到定义查看，不必以为它是一种新的语言。self暂时理解为“当前这个助手对象”。')

page('4 先看懂最常用的语法')
table(['写法','意思','在脚本里常见的用途'],[
('def task(self):','定义一个方法','把一整项操作起名，供其他地方调用。'),
('if / elif / else','如果 / 否则如果 / 否则','判断领奖、倒计时、未开放等状态。'),
('for _ in range(3):','最多重复三轮','限制尝试次数；不是无限重试。'),
('return','结束当前函数','已经完成就退出，不再继续点击。'),
('raise TaskStop("原因")','抛出业务异常','结果不明确时停止当前操作。'),
('try / except','尝试执行并处理异常','记录失败，必要时恢复页面。'),
('列表 [a, b, c]','有顺序的一组值','保存每日任务顺序。'),
('字典 {"key": value}','名称对应数值或状态','保存次数、日期和完成标志。')],[145,145,CONTENT-290])
code('remaining = 3\nfor _ in range(3):\n    if remaining == 0:\n        break\n    remaining = remaining - 1','教学示例：最多处理三次。它不会操作游戏。')
p('Python靠缩进表示哪些语句属于同一个分支。修改时保留现有缩进，不要随意混用Tab与空格。==用来比较是否相等，=用来赋值；两者用途不同。')

page('5 运行前准备与只检查画面')
p('用VS Code打开整个E:\\xiuxian文件夹，先停止助手面板中的旧任务。下面是PowerShell命令，不是放进.py文件的Python代码。')
code("Set-Location E:\\xiuxian\n$py = 'C:\\Users\\21413\\AppData\\Local\\Programs\\Python\\Python39\\python.exe'\n$adb = 'D:\\雷电\\leidian\\LDPlayer9\\adb.exe'\n& $adb devices\n& $py .\\assistant.py --help\n& $py .\\assistant.py inspect",'PowerShell：检查设备、查看帮助、读取当前画面')
p('$py与$adb是当前终端里的临时变量，关闭终端后就没有了。&表示运行变量指向的程序。devices列出ADB设备；inspect读取截图和识别结果，不执行日常任务，但会创建运行日志。')
sub('先排查环境，再排查识别')
p('设备必须连接，游戏必须在前台，原始截图必须是720×1280。config.json中的ADB路径、device、package和账号标识要与当前环境相符。否则应先解决连接或配置，不能靠修改按钮坐标补救。')
p('如果提示“已有助手正在运行”，从面板停止旧任务。不要通过删除.running.lock绕过运行锁，否则两个进程可能争抢同一画面。')

page('6 截图命令怎样实现')
code('& $adb -s emulator-5554 shell screencap -p /sdcard/learn.png\n& $adb -s emulator-5554 pull /sdcard/learn.png E:\\xiuxian\\学习资料\\learn.png','PowerShell：保存安卓截图，再拉到电脑；两步都不点击游戏')
p('emulator-5554是设备标识，若本机配置不同要替换。/sdcard/learn.png位于模拟器；最后的E盘路径位于电脑。不要把这两个位置混为一谈。')
sub('项目内采用的是直接读取PNG字节')
code('import subprocess\nimport cv2\nimport numpy as np\n\nraw = subprocess.check_output([\n    adb_path, "-s", device,\n    "exec-out", "screencap", "-p"\n])\nframe = cv2.imdecode(np.frombuffer(raw, np.uint8), 1)\nprint(frame.shape)','Python教学片段：需先给adb_path和device赋值，不是可直接独立运行的完整文件')
p('raw是PNG文件的二进制内容；frombuffer把字节交给图像库；imdecode把它解码成像素数组。shape通常是(1280, 720, 3)，顺序是高度、宽度、通道数。项目snap还会检查前台应用与尺寸。')
p('在旧版PowerShell中用“>”重定向二进制截图可能损坏文件。初学时使用上面的screencap加pull，或用Python接收字节，更容易排查。',True)

page('7 坐标与识别区域ROI')
fig('coords',320,'图2　720×1280画面的坐标和局部识别区域')
code('roi = (80, 500, 640, 850)\nx1, y1, x2, y2 = roi\ncrop = frame[y1:y2, x1:x2]','Python：从已读取的frame中裁剪区域，不操作游戏')
p('ROI是“只看哪一块”的范围。项目常用左、上、右、下四个值，不是左、上、宽、高。图像数组先写y，再写x，所以裁剪是frame[y1:y2, x1:x2]。上例宽560像素，高350像素。')
p('按钮在底部而ROI只看到1055行，就可能漏掉1250行的“领取”。相反，区域太大又可能读到聊天记录或别的“领取”。先在截图上确认区域，通常比盲目降低识别阈值有效。')

page('8 模板匹配怎样找到按钮')
p('模板就是从游戏截下来的小图，例如叉号或“收取”。OpenCV把模板在大图上逐个位置比较，返回每个位置的相似程度。它比较外观，不理解按钮的用途。')
code('result = cv2.matchTemplate(\n    crop, template, cv2.TM_CCOEFF_NORMED\n)\n_, score, _, location = cv2.minMaxLoc(result)\nx, y = location','Python教学片段：crop和template必须已经读取，且模板不能比搜索区域大')
p('location是模板左上角，不是按钮中心。若模板宽w、高h，且裁剪区域起点是(a, b)，点击中心为(a+x+w/2, b+y+h/2)。忘了加裁剪偏移，就会点到错误位置。')
sub('项目已有方法把这些步骤封装好了')
code('self.snap()\npoint = self.find("palace_lamp_claim")\nself.log(f"调试：找到的位置 = {point}")\nif point is None:\n    self.log("没找到，先检查截图和素材")','在Bot方法或断点上下文中使用；这段不点击')
p('assets.json里保存模板框和moving标志，assets里保存对应PNG。当前find常规模板要求score至少0.94，还检查颜色平均差异；不满足时部分目标会走文字等回退。不同模块有自己的阈值，不能把一个数当成全项目通用规则。')
sub('怎样准备一个模板')
p('先从同尺寸截图裁出稳定的小图，确认文字和边框完整，再保存PNG。学习时先存到学习资料，不直接覆盖正式assets。正式接入时，素材名、PNG文件名和assets.json中的键必须对应。',True)
code('patch = frame[842:882, 559:685]\nPath("E:/xiuxian/学习资料/claim_sample.png").write_bytes(\n    cv2.imencode(".png", patch)[1].tobytes()\n)','离线裁图示例：frame与Path须已定义；坐标来自当前收取素材框')

page('9 文字识别怎样读出状态')
p('RapidOCR返回的不是只有一句话，而是文字、置信度和位置。下面的数据是教学示例，不是读取你的账号。')
code('{\n    "text": "领取",\n    "confidence": 0.97,\n    "pos": (360, 1245)\n}','OCR结果示例')
table(['项目方法','返回什么','适合什么'],[
('self.text(roi)','包含文字、置信度、位置的列表','检查究竟读到了哪些候选。'),
('self.words(roi)','把合格结果拼成字符串','判断有没有倒计时或状态文字。'),
('self.line(roi)','单行识别结果字符串','读数量、余额等较短的单行。'),
('self.button_positions(labels, roi)','匹配文字的坐标列表','找到唯一按钮后再决定是否点击。')],[145,175,CONTENT-320])
code('self.snap()\nroi = (70, 200, 650, 1050)\nbody = self.words(roi)\nhits = self.button_positions(("确定", "确认"), roi)\nself.log(f"调试：body={body}")\nself.log(f"调试：hits={hits}")','在Bot内部加入临时日志：先观察，不点击')
p('置信度不是“按钮点击正确率”。OCR读对了“获得奖励”，但它若来自历史聊天，仍然不应按当前奖励弹窗处理。文字、位置、页面和按钮要一起判断。')

page('9A 完整的离线OCR练习')
p('下面保存为E:\\xiuxian\\学习资料\\ocr_demo.py，读取第6节保存的learn.png。它只打开电脑上的图片，不连接ADB、不调用Bot，不会操作游戏。这个文件也已随教程放在学习资料目录。')
ocr_demo='''from pathlib import Path
import sys
sys.path.insert(0, "E:/xiuxian/vendor")
import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR

p = Path("E:/xiuxian/学习资料/learn.png")
if not p.exists():
    raise SystemExit("先按第6节保存learn.png")
frame = cv2.imdecode(np.frombuffer(p.read_bytes(), np.uint8), 1)
if frame is None:
    raise SystemExit("图片无法解码")
ocr = RapidOCR()
result, _ = ocr(frame)
for box, text, confidence in result or []:
    x = sum(point[0] for point in box) / len(box)
    y = sum(point[1] for point in box) / len(box)
    print(text, round(confidence, 3), (int(x), int(y)))'''
code(ocr_demo,'完整Python程序：按现有项目Python 3.9环境运行')
code('& $py E:\\xiuxian\\学习资料\\ocr_demo.py','PowerShell运行命令，先定义第5节的$py')
p('每行输出文字、置信度、文字框中心。先检查目标文字是否存在，再看坐标有没有落在按钮附近。读错时可以裁小区域或放大截图，不要急着把程序改成见到任何相似字就点击。')

page('10 点击滑动与等待命令')
code('& $adb -s emulator-5554 shell input tap 360 800\n& $adb -s emulator-5554 shell input swipe 350 900 350 500 600','PowerShell：这两条会实际点击和滑动，坐标仅为示例')
p('tap后面是x、y。swipe后面是起点x、起点y、终点x、终点y、持续毫秒数。第二条表示手指从下向上移动，不保证游戏内容一定按你想的方向或距离滚动。')
table(['项目代码','实际含义'],[
('self.tap(x, y)','点击坐标，并执行项目里的前台、停止及日期等检查。'),
('self.click("素材名")','反复截图寻找素材，找到后再调用tap。'),
('self.wait("页面名")','等待识别到页面；不等于等待奖励到账。'),
('self.wait_words(...)','等待指定区域文字满足条件。'),
('self.adb("shell", "input", "swipe", ...)','直接发送滑动；不等同于tap的所有保护。')],[230,CONTENT-230])
p('固定等待8秒只是在估计动画时长。更可靠的写法是等待“完成”或“领取”出现，点击以后再验证弹窗、次数或按钮变化。代码里已有多种等待方法，改动时先看现有任务怎样确认结果。')
p('这个渠道的安卓系统返回可能弹出退出引导，所以项目优先点击游戏里的叉号和返回箭头，不把系统返回当通用修复办法。')

page('11 所谓记忆操作到底记住了什么')
fig('memory',240,'图3　变量、账本、流程进度和日志是四种不同记录')
p('这里的“记忆”不是AI训练，也不是自动录下你所有鼠标动作。程序依靠你写好的规则操作，把需要保留的状态写进文件。下次启动时再读取，决定哪些不应重复。')
code('amount = 220\nself.ledger["night_started"] = 15\nself.ledger_save()','前一句只改内存；后两句修改账本并保存到文件')
p('只写self.ledger里的值而不保存，进程结束后可能丢失。反过来，文件里写着已完成，也不代表游戏侧必定领奖成功；还要看这个标志是在什么证据出现以后写入的。')
p('日志保存“发生过什么”，不负责自动重新学习。截图保存“当时看见什么”，可以作为离线回归样本。它们能帮你分析异常，但不会自己生成正确的操作流程。')

page('12 账本和流程进度怎样配合')
code('{\n  "day": "2026-10-27",\n  "night_started": 15,\n  "palace_cultivate_phase": "claiming"\n}','账本结构示意：字段仅用于讲解，不能覆盖真实账本')
code('{\n  "day": "2026-10-27",\n  "completed": ["signin"],\n  "pending": {"night": true},\n  "current": "palace_court"\n}','progress结构示意：JSON布尔值写true，Python代码中则写True')
p('账本更像“次数和操作记录”，progress更像“日常清单执行到了哪里”。current用来定位正在处理的任务，completed用于筛选已处理项，pending用于倒计时收尾。不同任务的完成定义并不完全相同，要看具体代码。')
sub('当前版本的重要区别')
p('all会重新建立流程清单，但保留当天消耗与游戏次数记录；resume读取当天流程断点。单独重建清单不等于恢复游戏次数，也不表示每项都会再次花资源。旧报告里对all与resume的共同处理说明，不能原样套到今天的代码。')
p('账号标识决定读取哪份账本。换号时要检查配置，不能把另一角色的记录当成当前角色状态。')

page('13 JSON怎样读取和保存')
p('下面用单独的学习文件演示，避免触碰真实ledgers。可以保存为E:\\xiuxian\\学习资料\\memory_demo.py后运行；它只写教学数据，不操作游戏。')
code('import json\nfrom pathlib import Path\n\np = Path("E:/xiuxian/学习资料/示例数据.json")\ndata = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}\ndata["练习次数"] = int(data.get("练习次数", 0)) + 1\n\ntmp = p.with_suffix(".tmp")\ntmp.write_text(\n    json.dumps(data, ensure_ascii=False, indent=2),\n    encoding="utf-8"\n)\ntmp.replace(p)\nprint(data)','完整Python教学程序：每次运行将练习次数加一')
p('read_text把文件读成字符串，json.loads把字符串变成字典。json.dumps把字典变回JSON文字，write_text写文件。ensure_ascii=False让中文以可读形式保存，indent=2让缩进容易看。')
p('先写临时文件再replace，可以减少直接覆盖时留下半个JSON的风险。但这不是数据库事务，也不能保证游戏动作与文件写入同步完成；真实记录不能通过随意改数字来“修复”。')

page('14 为什么点击前还要保存预留')
fig('state',270,'图4　以夜猎为例理解提交预留与重启核对')
p('考虑一种中断：游戏已经接受“开始夜猎”，但Python还没来得及保存，电脑就重启了。如果下次只看本地旧计数，可能再次点击。')
p('所以部分任务先写“准备提交”，再点击，最后用倒计时和配额变化确认。重启后看到预留，先核对游戏状态：已运行就恢复记录；结果不明确就停止重复提交，等待核查。')
p('这是一种防重复思路，并不保证任意时刻中断都能自动修复。你要区分：准备提交、游戏已运行、奖励可领取、奖励已确认。只有把这些状态说清楚，断点续跑才不只是“跳过前几步”。')

page('15 任务顺序与返回层级怎样写')
code('PALACE_TASKS = (\n    "palace_lamp",\n    "palace_cultivate",\n    "palace_court",\n    "palace_garden"\n)','workflow.py中的天阙顺序：燃心灯、同修、朝会、御木园')
p('任务列表决定先后，PARENTS描述页面关系，TASK_ENTRY描述任务入口。shared_parent比较当前任务和下一项，找到可以保留的共同父页面。')
code('self._route_hold = shared_parent(task, following)\nself._palace_batch = self._route_hold == "palace_map"','任务调度器中的关键思路，需在其原上下文使用')
p('如果下一个仍是天阙任务，当前任务结束后只回天阙地图。下一个入口函数先检查是否已经在这里，已经在就直接使用。最后一项结束后再回元极。')
p('但只改任务列表不一定能修好返回：具体方法可能直接tap返回，或用close关弹窗。新增任务还要检查进入和退出代码，避免一边声明保留、一边又手动退到了主界面。')
table(['想改什么','先看哪里'],[('任务先后','workflow.py'),('识别与点击基础方法','assistant.py'),('返回与断点','navigation.py、hierarchy.py'),('天阙领奖','palace_tasks.py'),('夜猎','night_engine.py')],[155,CONTENT-155])

page('16 遇到异常时按什么顺序查')
fig('debug',265,'图5　定位问题先看证据，再修改一个原因')
table(['现象','优先检查'],[
('页面没进去','前面入口点对了吗？有没有弹窗或过渡动画？'),
('按钮看得见但找不到','ROI覆盖了吗？模板尺寸对吗？OCR读成什么？'),
('点击了却无变化','按钮能点吗？坐标是全图还是裁剪区域坐标？'),
('一直等领取','动画没结束，还是程序从未真正点击开始？'),
('已领奖仍等待','成功条件是否把历史聊天或别的文字算进去了？'),
('重启后重复操作','提交前后有没有保存？读取的是正确账号和日期吗？')],[150,CONTENT-150])
p('在VS Code按Ctrl+Shift+F搜索完整报错文字，通常能直接找到抛异常的位置。再向上看它依赖哪些变量，向前看这些变量从哪里来。不要一开始就把所有等待都改成60秒。')

page('17 一个真实例子 同修奖励误判')
p('之前同修页面底部聊天出现“获得奖励”，程序把它当成当前奖励弹窗，于是一直找确认按钮。问题不是OCR读错，而是把正确文字放进了错误的业务语境。')
code('self.snap()\nbody = self.words((70, 200, 650, 1050))\nhits = self.button_positions(\n    ("确定", "确认"), (120, 400, 610, 1200)\n)\nself.log(f"调试：body={body}; hits={hits}")','先加入日志观察；不要看到获得奖励就直接点击')
sub('修复条件为什么这样加')
p('把大部分底部聊天排除在识别区外，并要求真正存在独立“确定/确认”按钮。底部“领取”是任务页动作，不能自动当成奖励弹窗确认。领取以后还要截图检查弹窗是否消失、原页面是否恢复。')
sub('另一个例子 朝议一直等待')
p('旧记录写着started，但画面仍显示朝议启动按钮。如果只相信旧记录，程序会等一个根本没有启动的动画。修复时既要读取记录，也要识别当前按钮和游戏“今天已完成”提示。')
p('这些修复针对具体证据。不要为了让异常消失，就直接把reward_done写成True；那样只是把错误藏起来。')

page('18 看懂识别结果与常见报错')
code('point = self.find("palace_lamp_claim")\nprint(point)\n\nif point is None:\n    print("没有找到")\nelse:\n    x, y = point\n    print(x, y)','示例：find通常返回坐标元组或None，不是百分比')
table(['报错或现象','通常意味着什么'],[
('NameError','名字没定义，或你把函数内部变量拿到外部直接用。'),
('ModuleNotFoundError','解释器不对或缺依赖；先核对Python环境。'),
('IndentationError','缩进有问题，检查if、def、for下方。'),
('等待页面超时','预期页面未被识别；不等于只是网络慢。'),
('按钮不能唯一确认','识别出零个或多个候选，不宜随便取第一个。'),
('JSON读取失败','可能文件内容不完整或格式被改坏，应先备份并查原因。')],[170,CONTENT-170])
p('重要区别：None表示没有结果，0是一个数字，False是布尔值。它们在if里都可能被当成假，但含义不同。调试时先打印实际值和类型，不要凭猜测改变条件。')

page('19 在VS Code里启动已有调试配置')
p('1. 打开整个E:\\xiuxian文件夹。2. 停止助手面板中的任务。3. 按Ctrl+Shift+D打开运行和调试。4. 选择已有配置，再按F5。')
table(['配置名称','适合什么时候用'],[
('检查当前画面（不执行任务）','先核对设备、页面、识别结果；不会执行日常点击。'),
('调试单项任务（会操作游戏）','选定一个任务，设断点观察；会真实消耗已授权次数或资源。')],[235,CONTENT-235])
p('解释器应选择C:\\Users\\21413\\AppData\\Local\\Programs\\Python\\Python39\\python.exe。不要因为电脑还有Python 3.12，就默认它具备同样的依赖。')
code('"program": "${workspaceFolder}/assistant.py",\n"args": ["palace_court"],\n"cwd": "${workspaceFolder}"','launch.json中的片段：指定主文件、任务参数和工作目录，不是完整JSON文件')
p('program不是要你正在编辑的每个模块；多数情况下仍启动assistant.py，再通过args选择任务。直接运行palace_tasks.py通常不会完成天阙任务，因为它主要定义类，还需要Bot、配置和其他模块。')
p('配置里的单项菜单可能随项目更新而落后。拿不准任务名时运行assistant.py --help，再对照实际choices；不要把旧名字当成永远有效。')

page('20 设置断点后应该看什么')
fig('vscode',235,'图6　调试窗口示意，不是实际VS Code截图')
p('在if amount > 0这一行左侧点出红点。运行燃心灯单项后停住，把鼠标放到amount上，检查程序读到的数字是不是游戏里显示的愿力。没到断点就失败，说明问题在更前面。')
table(['按键','作用'],[('F5','继续运行。'),('F10','执行下一行，不进入函数内部。'),('F11','进入当前函数，查看它的实现。'),('Shift+F11','从当前函数返回调用处。'),('Shift+F5','停止本次调试。')],[110,CONTENT-110])
p('调试控制台可以输入amount、type(amount)、self.ledger等表达式查看状态。但控制台也能真实执行方法；输入self.tap或self.click会点击游戏。断点暂停Python，不暂停游戏倒计时，停很久以后要重新截图。')

page('21 暂停继续停止与当天恢复的命令')
p('优先使用面板按钮。下面是在另一个PowerShell终端里操作控制文件的方式，只用于理解实现。不要在日常运行前批量执行这些命令。')
code('New-Item -ItemType File E:\\xiuxian\\PAUSE -Force\nRemove-Item -LiteralPath E:\\xiuxian\\PAUSE\nNew-Item -ItemType File E:\\xiuxian\\STOP -Force','PowerShell：三行分别是请求暂停、请求继续、请求停止；按需要单独执行')
p('暂停到达控制检查点才生效。PAUSED是工作进程写出的响应，不应自己创建它来冒充已暂停。STOP让工作进程在下一检查点退出；面板停止还可能直接结束进程，因此不保证最后一次操作已写入记录。')
code('& $py .\\assistant.py resume --watch\n& $py .\\assistant.py all --watch\n& $py .\\assistant.py finish','PowerShell：三种运行方式，都会实际执行所选流程')
p('当前版本：resume读取当天断点；all从人间重建流程清单但不清空消耗账本；finish检查收尾任务组。--watch按待处理状态每5分钟再检查，最长24小时且不跨北京时间日期。每次新启动取得锁后会清理旧控制标记。')
p('不要删除ledgers来达到“从头跑”的效果。那可能丢掉次数、赠予或夜猎预留记录，导致重复操作。')

page('22 跟着做的三个练习')
sub('练习一 看懂变量和日志')
p('在燃心灯读取amount后加一行日志，在if语句设断点；运行单项，比较变量、日志和游戏画面。验证后把临时日志移除或保留为明确的调试信息。')
code('amount = self.lamp_amount()\nself.log(f"调试：当前愿力为 {amount}")','在现有方法内添加，不要把整段任务重复粘贴')
sub('练习二 只识别保存截图')
p('先用第6节命令保存learn.png，再裁剪ROI、查看OCR结果。此练习不需要反复领取或购买。不要把“重新截图”与“读取旧截图”混为一谈。')
code('from pathlib import Path\nimport cv2\nimport numpy as np\n\np = Path("E:/xiuxian/学习资料/learn.png")\nframe = cv2.imdecode(np.frombuffer(p.read_bytes(), np.uint8), 1)\nprint(frame.shape)\ncrop = frame[500:850, 80:640]\nout = p.with_name("learn_crop.png")\nout.write_bytes(cv2.imencode(".png", crop)[1].tobytes())','完整离线Python示例：只读已保存图片并输出裁剪图')
sub('练习三 验证记忆文件')
p('运行第13节教学程序两次，查看示例数据.json的练习次数是否增加。然后关闭终端重新运行，理解为什么内存变量不在了，文件里的数字仍在。')

page('23 如何逐步减少对AI修复的依赖')
p('先让AI解释一个函数，不要求它立刻改全项目。你自己复述“输入是什么、返回什么、何时点击、怎样确认”，再用日志或断点验证自己的理解。')
table(['学习阶段','你应该能自己完成什么'],[
('读基础语句','看懂变量、条件、循环、列表和字典。'),
('看一个任务','解释入口、识别、动作、结果和返回。'),
('定位异常','找到对应日志截图，打印body和hits。'),
('修改一个条件','说明改前为何错误，改后如何验证。'),
('补离线回归','保留失败样本，确认同类问题不再出现。'),
('维护完整模块','考虑已完成、材料不足、重启、未知弹窗等边界。')],[135,CONTENT-135])
p('向AI提问可以这样写：“我在某页面，期望找到领取，但body读到了这些文字，hits为空；这是ROI还是匹配条件的问题？先解释，不要替我改其他模块。”这样你控制问题范围，也能判断回答是否靠谱。')
p('你不必先独立重写全部代码。先独立完成一次“看日志—提出原因—验证原因—修改—回归”，就已经从只接受修复，走向实际维护。')

page('24 常用命令和文件速查')
table(['目的','命令或文件'],[
('看设备','& $adb devices'),('只检查画面','& $py .\\assistant.py inspect'),
('调试燃心灯','& $py .\\assistant.py palace_lamp'),('调试朝会','& $py .\\assistant.py palace_court'),
('读当天断点继续','& $py .\\assistant.py resume --watch'),
('重新建立流程清单','& $py .\\assistant.py all --watch'),
('查任务名','& $py .\\assistant.py --help'),
('看当前任务顺序','& $py .\\assistant.py order'),
('连接与角色配置','config.json'),('识别图片及位置','assets / assets.json'),
('当天次数与状态','ledgers'),('错误现场','logs中最新一轮的events.txt与截图')],[155,CONTENT-155])
p('上表中的$py与$adb要先按第5节定义。inspect和order也需要项目环境与ADB可连接；单项及all、resume、finish会实际操作游戏。')
sub('使用范围与资料来源')
p('教程依据本地assistant.py、navigation.py、workflow.py、runtime_control.py、daily_tasks.py、palace_tasks.py、assets.json和.vscode配置核对，并参考2026年10月26日的源码分析报告。这里没有承诺所有任务、渠道或随机事件均已覆盖。源码继续变化时，以实际帮助信息、任务实现和日志为准。',True)
p('插图为原创代码绘制的矢量示意；字体采用宋体、黑体和Times New Roman。教程生成日期：2026年10月27日。',True)

def footer(c,doc):
    c.saveState();c.setFillColor(colors.HexColor('#333333'))
    drawtext(c,W/2,H-28,'太古仙尊助手项目介绍与手动调试教程',9.5,True)
    drawtext(c,W/2,28,str(doc.page),10.5,True);c.restoreState()
out=ROOT/'太古仙尊助手项目介绍与手动调试教程.pdf'
class TutorialDoc(SimpleDocTemplate):
    def afterFlowable(self,flowable):
        if isinstance(flowable,Paragraph) and flowable.style.name in ('Heading','Title'):
            text=flowable.getPlainText();key='topic'+str(self.page)
            self.canv.bookmarkPage(key);self.canv.addOutlineEntry(text,key,level=0,closed=False)
document=TutorialDoc(str(out),pagesize=A4,rightMargin=50,leftMargin=50,topMargin=55,bottomMargin=50,title='太古仙尊助手项目介绍与手动调试教程',author='')
document.build(story,onFirstPage=footer,onLaterPages=footer)
(ROOT/'ocr_demo.py').write_text(ocr_demo+'\n',encoding='utf-8')
compile(ocr_demo,'ocr_demo.py','exec')
snap={n:hashlib.sha256((ROOT.parent/n).read_bytes()).hexdigest() for n in ['assistant.py','navigation.py','workflow.py','palace_tasks.py','runtime_control.py']}
(ROOT/'教程依据.json').write_text(json.dumps({'date':'2026-10-27','source_hashes':snap,'notes':'No game task executed; only read current code and wrote teaching document.'},ensure_ascii=False,indent=2),encoding='utf-8')
print('Written',out)
