# -*- coding: utf-8 -*-
import pathlib,json,csv,hashlib,re,zipfile,copy,datetime
from docx import Document
from docx.shared import Pt,Cm,Inches,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from vector_figures import generate

ROOT=pathlib.Path(__file__).parent;DATA=json.loads((ROOT/'审计资料/source_manifest.json').read_text(encoding='utf-8'))
FILES={f['file']:f for f in DATA['files']};IDS={f['file']:f'S{i:02d}' for i,f in enumerate(DATA['files'],1)}
TESTS=json.loads((ROOT/'审计资料/test_results.json').read_text(encoding='utf-8'))
generate();doc=Document();claims=[];figures=[]
sec=doc.sections[0];sec.page_width=Inches(8.5);sec.page_height=Inches(11)
sec.top_margin=Cm(2.3);sec.bottom_margin=Cm(2.3);sec.left_margin=Cm(2.54);sec.right_margin=Cm(2.54)
sec.header_distance=Cm(1.1);sec.footer_distance=Cm(1.1);sec.different_first_page_header_footer=True

def fonts(run,size=12,cn='宋体',bold=False):
    run.font.name='Times New Roman';run.font.size=Pt(size);run.bold=bold;run.font.color.rgb=RGBColor(0,0,0)
    p=run._element.get_or_add_rPr();f=p.rFonts
    if f is None:f=OxmlElement('w:rFonts');p.insert(0,f)
    for key,value in [('ascii','Times New Roman'),('hAnsi','Times New Roman'),('eastAsia',cn),('cs','Times New Roman')]:f.set(qn('w:'+key),value)

for name,size,cn,bold in [('Normal',12,'宋体',False),('Title',22,'黑体',True),('Heading 1',15,'黑体',True),('Heading 2',14,'黑体',True),('Heading 3',12,'黑体',True),('Caption',10.5,'宋体',False)]:
    s=doc.styles[name];s.font.name='Times New Roman';s.font.size=Pt(size);s.font.bold=bold;s.font.color.rgb=RGBColor(0,0,0)
    r=s.element.get_or_add_rPr();rf=r.rFonts
    if rf is None:rf=OxmlElement('w:rFonts');r.insert(0,rf)
    for k,v in [('ascii','Times New Roman'),('hAnsi','Times New Roman'),('eastAsia',cn)]:rf.set(qn('w:'+k),v)
    s.paragraph_format.space_after=Pt(6);s.paragraph_format.line_spacing=1.5
    if name.startswith('Heading'):s.paragraph_format.keep_with_next=True;s.paragraph_format.space_before=Pt(12)
for name in ('TOC 1','TOC 2','TOC 3','Header','Footer'):
    if name not in doc.styles:doc.styles.add_style(name,1)
    style=doc.styles[name];style.font.name='Times New Roman';style.font.size=Pt(12 if name.startswith('TOC') else 10.5)
    rr=style.element.get_or_add_rPr();rf=rr.rFonts
    if rf is None:rf=OxmlElement('w:rFonts');rr.insert(0,rf)
    for k,v in [('ascii','Times New Roman'),('hAnsi','Times New Roman'),('eastAsia','宋体')]:rf.set(qn('w:'+k),v)
doc.styles['Normal'].paragraph_format.first_line_indent=Pt(24)

def evidence(sources):
    return '；'.join(IDS.get(f,f)+(('，L'+loc) if loc else '') for f,loc in sources)
def p(text,sources=(),style=None,size=12,indent=True):
    para=doc.add_paragraph(style=style);para.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
    if not indent:para.paragraph_format.first_line_indent=Pt(0)
    suffix='〔'+evidence(sources)+'〕' if sources else ''
    fonts(para.add_run(text+suffix),size)
    if sources:
        claims.append({'claim_id':f'C{len(claims)+1:03d}','sha256':hashlib.sha256((text+suffix).encode()).hexdigest(),'evidence':evidence(sources),'human_verification':'pending'})
    return para
def h(text,level=1,new=False):
    para=doc.add_paragraph(text,'Heading '+str(level));para.paragraph_format.first_line_indent=Pt(0)
    if new and (text.startswith('1 研究') or text.startswith('参考文献') or text.startswith('附录')):para.paragraph_format.page_break_before=True
    for run in para.runs:fonts(run,15 if level==1 else 14,'黑体',True)
    return para
def code(text,label):
    cap=p(label,size=10.5,indent=False);cap.paragraph_format.keep_with_next=True
    for line in text.splitlines():
        para=doc.add_paragraph();para.paragraph_format.first_line_indent=Pt(0);para.paragraph_format.left_indent=Cm(.35)
        para.paragraph_format.space_after=Pt(0);para.paragraph_format.line_spacing=1.1
        fonts(para.add_run(line),10.5)
def table(headers,rows,widths=None,caption=None):
    if caption:
        pp=p(caption,size=10.5,indent=False);pp.paragraph_format.keep_with_next=True
    t=doc.add_table(rows=1,cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
    if widths is None:widths=[6.5/len(headers)]*len(headers)
    for i,wid in enumerate(widths):t.columns[i].width=Inches(wid)
    for i,txt in enumerate(headers):t.rows[0].cells[i].text=str(txt)
    for row in rows:
        cells=t.add_row().cells
        for i,txt in enumerate(row):cells[i].text=str(txt)
    for ri,row in enumerate(t.rows):
        trpr=row._tr.get_or_add_trPr()
        no=OxmlElement('w:cantSplit');trpr.append(no)
        if ri==0:
            repeat=OxmlElement('w:tblHeader');trpr.append(repeat)
        for ci,cell in enumerate(row.cells):
            cell.width=Inches(widths[ci]);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            cp=cell._tc.get_or_add_tcPr();borders=OxmlElement('w:tcBorders')
            for edge in ('top','left','bottom','right'):
                e=OxmlElement('w:'+edge);e.set(qn('w:val'),'single');e.set(qn('w:sz'),'4');e.set(qn('w:color'),'D9D9D9');borders.append(e)
            cp.append(borders)
            mar=OxmlElement('w:tcMar')
            for edge in ('top','left','bottom','right'):
                e=OxmlElement('w:'+edge);e.set(qn('w:w'),'85');e.set(qn('w:type'),'dxa');mar.append(e)
            cp.append(mar)
            if ri==0:
                sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'EDEDED');cp.append(sh)
            for para in cell.paragraphs:
                para.paragraph_format.first_line_indent=Pt(0);para.paragraph_format.space_after=Pt(2);para.paragraph_format.line_spacing=1.15
                for run in para.runs:fonts(run,10.5,bold=ri==0)
    doc.add_paragraph().paragraph_format.space_after=Pt(2)
    return t
def figure(name,caption,alt,width=6.5):
    para=doc.add_paragraph();para.paragraph_format.first_line_indent=Pt(0);para.alignment=WD_ALIGN_PARAGRAPH.CENTER;para.paragraph_format.keep_with_next=True
    inline=para.add_run().add_picture(str(ROOT/'矢量图'/(name+'.png')),width=Inches(width))
    inline._inline.docPr.set('descr',alt)
    figures.append((inline._inline.graphic.graphicData.pic.blipFill.blip.embed,name))
    pp=doc.add_paragraph(caption,'Caption');pp.alignment=WD_ALIGN_PARAGRAPH.CENTER;pp.paragraph_format.first_line_indent=Pt(0)
def ref(file):return [(file,'')]

# Front matter
for _ in range(3):doc.add_paragraph()
title=doc.add_paragraph('太古仙尊每日助手\n源码结构与运行机制分析','Title');title.alignment=WD_ALIGN_PARAGRAPH.CENTER
for run in title.runs:fonts(run,22,'黑体',True)
p('基于现有 Python 脚本的工程分析报告',indent=False).alignment=WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph();p('源码审计稿　供项目维护者复核',indent=False).alignment=WD_ALIGN_PARAGRAPH.CENTER
p('分析对象　E:\\xiuxian 根目录当前源码',indent=False).alignment=WD_ALIGN_PARAGRAPH.CENTER
p('快照日期　2026年10月26日',indent=False).alignment=WD_ALIGN_PARAGRAPH.CENTER
doc.add_paragraph();p('本文分析实际代码、离线回归结果与可追溯运行记录，不报告未测量的识别准确率、全流程成功率或性能提升。正文与表格可编辑；关系图以矢量格式嵌入，图源和审计资料随项目保存。',indent=False)
doc.add_page_break();h('摘要')
p('本报告研究一个在雷电模拟器中运行的安卓游戏日常助手，目的是说明各源码文件的职责、相互调用方式、页面层级控制和异常恢复边界，为后续独立维护提供依据。分析以本地15个Python文件、2821行物理源码为快照，采用抽象语法树提取、关键路径阅读、历史错误记录对照及12个离线回归脚本复跑，不新增游戏实机消耗实验。源码和测试结果均保留来源与定位。',ref('assistant.py'))
p('系统由Tkinter面板启动独立工作进程，工作进程通过ADB采集截图和发送触摸输入，以OpenCV模板匹配、颜色约束和RapidOCR文字识别判定页面。任务由区域列表排序，共同父页面计算与具体入口、退出函数共同实现页面复用。任务账本记录账号当日计数及提交状态，进度文件记录已处理任务和待收尾任务。',ref('workflow.py')+ref('navigation.py')+ref('ui.py'))
p('分析表明，程序具备面向当前界面的可追踪任务编排与部分防重复提交机制，但不能视为通用安卓自动化框架。完成标记、游戏侧领奖状态与运行日志之间仍存在语义差异；强制停止、分散的资源规则、固定识别区域和跨模块隐式依赖构成主要维护风险。复跑脚本均以退出码0结束，只能说明所覆盖样例及分支满足断言，不能推出全部日常、全部随机事件或其他渠道均可靠。',ref('navigation.py')+ref('runtime_control.py'))
p('关键词：安卓界面自动化；模板匹配；文字识别；页面层级；断点续跑；源码审计',indent=False)
h('阅读说明',2)
p('这是一份描述性工程报告，不属于临床试验、系统综述或统计推断研究，因而不套用CONSORT、PRISMA等研究设计清单。报告采用问题、方法、实现、验证与局限的结构。作者署名、投稿场所、资助及利益冲突未由项目维护者确认，不作补写；文本为AI辅助整理，尚需维护者进行最终技术核对。')
doc.add_page_break()
toc_title=doc.add_paragraph();toc_title.paragraph_format.first_line_indent=Pt(0);fonts(toc_title.add_run('目录'),15,'黑体',True)
para=doc.add_paragraph();para.paragraph_format.first_line_indent=Pt(0)
field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'TOC \\o "1-1" \\h \\z \\u');para._p.append(field)
p('目录由Word字段生成。修改正文后，在Word中更新整个目录即可同步页码。',size=10.5,indent=False)

h('1 研究对象与分析方法',new=True)
h('1.1 研究范围与证据类型',2)
p('研究对象是快照时刻根目录的15个Python源文件。vendor中的第三方库、assets中的识别素材、配置与日志作为运行依赖和旁证，不计入自有Python文件数量。物理行数包含空行、注释和文档字符串，不作为复杂度或质量评分。不同文件的行数与SHA-256散列记录在附录A及本地source_manifest.json。',ref('assistant.py'))
p('证据分为三类：S类为冻结的源码及行号，T类为本次复跑的脚本输出，H类为此前运行日志。S类能证明代码中存在某个分支，T类能证明给定样例满足断言，H类能证明某轮记录中出现过某种观察；三者都不能单独证明未覆盖场景下的可靠性。本文对建议与推断另作表述，不把建议写成已实现功能。')
h('1.2 分析步骤',2)
p('先复制源码并计算散列，再通过Python的ast模块提取顶层定义、类方法、行号和调用表达式。随后沿main、Bot初始化、run_groups、run_task及具体任务向下阅读，并核对识别、输入、保存和退出路径。静态调用表达式只用于定位，动态getattr、继承方法解析和模块级time替换仍需人工阅读解释，不能由导入图直接推断运行顺序。',ref('assistant.py')+ref('navigation.py'))
p('本次仅执行已识别为离线的12个回归脚本。它们使用截图或模拟对象，不启动游戏任务；个别脚本会启动隐藏的Tkinter测试窗口或读取本机样本。测试进程使用项目现有Python 3.9环境，文档构建使用独立的文档运行环境，两者不混同。运行结果保存在test_results.json，没有重置游戏次数、账本或购买额外次数。')
h('1.3 证据追溯和适用边界',2)
p('正文中的S编号对应附录A，L后数字为快照行号。例如S01的find段可直接定位模板判定逻辑。官方资料仅用于解释ADB、Tkinter、模板匹配和OCR的技术背景，具体阈值与业务规则以本地源码为准。写作过程采用Scientific Writing skill的证据与不确定性约束，并引用其软件说明和相关论文[5-6]；没有把工具审阅记为人类作者最终核验。')

h('2 系统架构与模块协作',new=True)
h('2.1 两个进程与一组控制文件',2)
p('ui.py负责展示任务菜单、资源开关和日志，不直接完成各项游戏操作。App.start读取并更新配置，使用subprocess.Popen启动assistant.py；后台线程读取子进程标准输出，写入线程安全队列，Tk主线程的poll再把消息显示到窗口。该结构把耗时的ADB、OCR和等待放到工作进程中。', [('ui.py','104-125'),('ui.py','154-167')])
figure('图1_系统协作','图1　系统进程与模块协作关系','面板进程启动工作进程；工作进程连接调度、任务、识别、ADB、日志和账本。')
p('图1区分了调用与数据流。配置、STOP、PAUSE和PAUSED是进程间文件约定，ledgers与logs保存运行结果，assets提供识别样本。箭头不表示所有对象都彼此直接调用：例如运行锁由工作进程入口获取，Tk面板主要通过进程对象和文件控制工作进程。',ref('ui.py')+ref('assistant.py'))
h('2.2 Bot是能力集合而非单一文件程序',2)
code('class Bot(Navigation, Hierarchy, NightTasks, GiftTasks,\n          StarRewards, VideoTasks, ApprovedTasks, PalaceTasks):\n    ...','代码1　Bot的继承次序　来源assistant.py L41')
p('多个Mixin类把方法汇入同一Bot实例，因此night_engine.py中的self.snap实际来自assistant.py，daily_tasks.py中的self.realm来自PalaceTasks。Python按方法解析顺序查找同名方法；方法定义在哪个文件，与调用时使用哪个对象是两件事。当前源码还通过night_tasks.py重导出NightTasks，旧入口可以保留而具体实现迁移到night_engine.py。', [('assistant.py','30-41'),('night_tasks.py','1-2')])
p('这种组织方式便于按任务拆分文件，却没有建立显式接口。某个任务依赖self.ocr、self.ledger、self.meta、self.pending和多个其他Mixin的方法，单独复制任务文件不能运行。新增同名方法还可能被继承顺序遮蔽，审查时应同时检查Bot及各基类。',ref('assistant.py')+ref('daily_tasks.py'))

h('3 入口与运行控制',new=True)
h('3.1 assistant.py的逻辑分段',2)
p('L1-39处理导入、根目录、点击名称和能力类引入；L42-69建立配置、模板、OCR、日志目录及账号账本；L71-175提供观察、识别和输入基础方法；L177-469保留部分任务和兼容实现；L471-517为命令行入口。这个文件既是基础设施，又仍包含征收、论剑、禁地、斗法和博戏等业务，职责未完全拆开。',ref('assistant.py'))
p('main首先解析task和--watch参数，再在.running.lock上申请Windows文件锁；拿不到锁则结束。取得锁后才清理旧控制标记、创建Bot并截图。all与resume都会读取当天断点，finish执行收尾任务组，普通任务通过run_task分派。默认task是all，所以调试时省略参数会进入全部日常，而不是只检查画面。', [('assistant.py','471-517')])
h('3.2 ui.py和启动脚本',2)
p('TASKS把中文菜单映射到命令代码；App初始化窗口，start验证神游目标并保存配置，然后启动工作进程。--watch只为菜单中列出的特定任务追加，不是任意单项都会自动收尾。面板使用CREATE_NO_WINDOW启动子进程，Bot.adb也采用隐藏控制台方式，减少ADB调用反复弹出终端。', [('ui.py','14-58'),('ui.py','104-125'),('assistant.py','76-82')])
p('打开每日助手.vbs与打开每日助手.bat都定位脚本目录，并使用写死的本机pythonw.exe路径启动ui.py；运行签到.bat进入daily.py；停止助手.bat写STOP。它们是启动与控制入口，不包含识别算法。daily.py只有参数转换：带--check-only时变成inspect，否则变成signin，并丢弃其他旧参数。迁移电脑时应同时检查启动器与config.json。', [('daily.py','1-8')])
h('3.3 runtime_control.py的暂停语义',2)
p('PauseClock.gate检查STOP；发现PAUSE时写PAUSED并等待，恢复后累计暂停耗时。monotonic返回扣除暂停时长的时间，sleep分段检查，所以点击与等待能响应暂停。Bot初始化把相关模块的time变量替换成这一对象，以较少改动覆盖原有等待代码；但这种替换属于模块级全局状态，不适合在同一进程中运行多个独立Bot。', [('runtime_control.py','6-39'),('assistant.py','42-48')])
p('暂停不会冻结游戏服务器倒计时。面板stop既写STOP又直接terminate工作进程，因此它不是保证每个收尾块都执行的优雅停止；即使JSON采用替换写入，也不能保证最后一次游戏操作已被记录。该区别解释了为什么“暂停继续”和“停止重启”不能视为同一种恢复机制。', [('ui.py','127-147'),('runtime_control.py','12-37')])

h('4 画面识别与输入闭环',new=True)
h('4.1 ADB连接和操作前置检查',2)
p('ADB是电脑与安卓设备通信的命令行工具，采用客户端、服务端与设备守护进程结构[1]。本项目把adb路径与设备标识放在配置中，Bot.adb以参数列表调用外部进程，设置20秒超时。snap先查询前台Activity，再获取PNG截图并解码；截图尺寸不是720×1280即停止。tap在发送输入前再次检查前台与北京时间日期，随后保存当前帧并发出input tap。', [('assistant.py','76-95'),('assistant.py','154-166')])
figure('图2_识别动作闭环','图2　从观察到结果核验的控制闭环','截图经识别和规则判断后发送输入，再观察页面或计数变化。')
p('图2是各模块共有的控制意图，不代表每个任务都使用统一状态机实现。当前输入保护主要集中在tap，滑动往往直接调用adb shell input swipe；这些路径会进入暂停门，但未全部复用tap的即时日期和前台复查。不能由tap存在保护就推断所有输入路径保护完全一致。', [('assistant.py','76-82'),('assistant.py','154-166'),('night_engine.py','61-65')])
h('4.2 OpenCV模板与颜色约束',2)
p('模板匹配是在较大的图像中搜索与小图相似的位置[3]。find根据assets.json选择固定邻域或全屏搜索，调用TM_CCOEFF_NORMED取得相关得分，再以像素平均绝对误差排除颜色差异过大的候选。代码要求得分不低于0.94且误差不高于15，不满足时转入fallback_find。这些数值是当前工程阈值，不是经标注数据集拟合的最优值，也不能换算成识别准确率。', [('assistant.py','103-125')])
p('night_buttons使用灰度模板寻找“已驻扎”标记，再用HSV中的橙色与白色像素约束过滤；绿色轮廓用于候选完成标记。御木园在文字状态之外检查红色，返回箭头则采用亮色前景匹配。颜色和形状提供补充证据，但分辨率、裁剪区域和界面色调仍影响结果。', [('night_engine.py','16-59'),('palace_tasks.py','253-285'),('navigation.py','143-163')])
h('4.3 RapidOCR与上下文判别',2)
p('RapidOCR负责把图像区域转换成文字、位置和识别置信度[4]。text对高度小于180像素的区域放大后识别，并把坐标换回原图；words过滤低于0.8的结果，line用于单行识别且阈值为0.9。button_positions进一步拼接同行或同列的分散字，以寻找横排或竖排按钮。置信度是模型输出，不能直接当作业务动作正确的概率。', [('assistant.py','127-148'),('daily_tasks.py','246-278')])
p('同修错误说明了上下文的重要性：历史聊天中的“获得奖励”可以被正确读出，却不是当前弹窗。palace_reward_popup因此把正文识别范围限制到聊天区上方，并要求存在独立“确定/确认”按钮后才处理。类似地，小世界仅从四个黄色选项条中读取第二项，避免把其下方奖励描述或其他选项的仙玉文字混入报价。', [('palace_tasks.py','146-165'),('video_tasks.py','256-311')])

h('5 任务顺序与页面层级',new=True)
h('5.1 workflow.py的三类数据',2)
p('DAILY_GROUPS规定人间、仙界、虚空、元极及其任务顺序；FINISH_GROUPS规定可以被倒计时收尾重复检查的任务；PALACE_TASKS统一燃心灯、同修、朝议和御木园的顺序。PARENTS描述子页面到父页面的关系，TASK_ENTRY把任务映射到入口页面。快照中的日常列表包含37项任务，任务总数只表示编排条目，并不意味着37项均在每次运行中实际执行。', [('workflow.py','2-37')])
figure('图3_页面层级与保留','图3　共同父页面与天阙同级关系','宗门、探秘及天阙三组页面关系；天阙三个建筑是同级，燃心灯位于天阙地图。')
h('5.2 共同父页面如何影响返回',2)
p('shared_parent先沿当前任务入口向上保存祖先列表，再沿下一个任务入口向上寻找第一个交点。若交点是以_nav结尾的角色主界面则返回None，否则返回该页面代码。它在声明的父关系上寻找最近共同祖先，不会读取游戏自行学习结构，也不负责具体点击路径。', [('workflow.py','40-49')])
code("following = selected[index + 1] if index + 1 < len(selected) else None\nself._route_hold = shared_parent(task, following)\nself._palace_batch = self._route_hold == 'palace_map'",'代码2　按相邻待执行任务设置保留页面　来源navigation.py L242-246')
p('run_groups过滤当天已处理项后，比较的是相邻实际选中任务。_route_hold交给back；retain_parent只在该页面已有模板元数据且当前截图确认匹配时才阻止返回。_secrets_batch、_palace_batch与_home_batch再控制特殊任务组的退出。任务结束后finally清空这些临时标记，避免影响下一组。', [('navigation.py','227-258'),('hierarchy.py','3-5'),('assistant.py','256-262')])
h('5.3 入口复用与专门退出函数',2)
p('teaching_open、market_open、journey_open等先截图检查是否已经位于目标父页面，已在则直接返回。因而护法后停在弟子院，课训就能直接开始。通天塔回游历后，secrets_open看到游历便直接进入探秘；珍馐坊采购回仙居后，gifts先复用仙居或仙祠。天阙四项统一返回palace_map，palace_finish只在组内最后一项退到元极。',ref('hierarchy.py')+[('daily_tasks.py','285-317'),('daily_tasks.py','180-225'),('gift_tasks.py','39-49'),('palace_tasks.py','38-68')])
p('页面表与业务函数必须共同维护。back会执行保留判断，但close和直接tap返回不会自动查询共同父页面；retain_parent也不接受只有语义检测、没有meta项的保留页。因此当前是部分声明式编排加手写导航，不能仅添加一个PARENTS条目就认为新页面的进入和退出全部完成。', [('hierarchy.py','3-5'),('assistant.py','256-262'),('video_tasks.py','42-60')])

h('6 各任务文件的功能与配合',new=True)
h('6.1 daily_tasks.py的通用日常',2)
p('ApprovedTasks承担常规日常与部分识别辅助。L14-110处理训话、护法、一键课训及掌门传功；L112-244提供账本保存、仙居任务、采购与钓鱼；L246-317实现文字按钮定位、探秘入口与通天塔；L319-500覆盖魔域、仙猎、寻宝、签到、斗法、神游、玉盒及凡间钓鱼。TaskStop是这些模块共享的业务中止异常，ScreenError在此基础上增加界面恢复语义。',ref('daily_tasks.py')+ref('navigation.py'))
p('这些任务采用不同的成功证据。护法检查弟子列表是否清空；讨伐检查剩余次数减一；玉盒检查购买计数增加；珍馐坊核对物品名称、数量、价格、余额以及扣费结果；钓鱼等待结束并核对剩余次数减少。规则由各方法分别实现，而不是统一交易接口，优点是贴合游戏页面，代价是修改政策时需要逐项查找。', [('daily_tasks.py','27-47'),('daily_tasks.py','163-225'),('daily_tasks.py','452-500')])
p('神游把当天目标限制在300次以内，按当前批次上限分配，开始前先保存wander_reservation，观察运行状态后再增加wander_started。仙猎每日按2次处理，但当前pending在count达到2时会清除，即使第二轮仍在倒计时，也可能不再进入自动收尾。该代码事实提示“已启动两次”与“第二轮奖励已收完”不能混为同一状态。', [('daily_tasks.py','334-366'),('daily_tasks.py','420-450')])
h('6.2 video_tasks.py的补充任务与共用弹窗',2)
p('这个文件包含门派死地、药谷、每日兑换、修真免费礼包、小世界、胜境兑换、观星台和探星封装。video_wait依据指定区域的文字等待，video_button要求目标按钮唯一，video_close先用模板找X，再用红色轮廓的对角线形状过滤。recover_video_dialog为已知弹窗提供恢复入口，但“已知”由一组文案与区域硬编码定义。', [('video_tasks.py','11-99'),('video_tasks.py','101-376')])
p('修真礼包会先检查入口存在与否；领取后可以用免费层消失作为结果证据，随后关闭礼包。这个判断适用于已观察到的列表上移行为，不足以应对所有加载失败。小世界先领取旧奖，再在当天启动次数低于3时探索；smallworld_unconfirmed记录未确认提交。事件条按纵坐标排序，只选索引1，即第二项；第二项出现仙玉则退出事件处理。', [('video_tasks.py','164-200'),('video_tasks.py','214-311')])
p('胜境兑换逐行核对资源报价，只操作三类基础材料；观星台要求识别到三个膜拜入口。stars方法只是组合入口，真正的夺道与供奉在StarRewards中。star_orbit目前只记录已取消，不再输入；star_forbidden将Bot传给run_forbidden。文件名“video_tasks”反映了功能加入的历史，不是长期稳定的领域边界，后续可按门派、小世界和探星分别拆分。', [('video_tasks.py','313-376')])
h('6.3 night_engine.py的驻扎识别与提交控制',2)
p('night_tasks.py只有重导入，不应在这里重复实现夜猎。NightTasks依次执行标记检测、滚动发现、按名字重新定位、配额读取、单处处理和整组收尾。缓存中的洞天名字只有伴随局部倒计时才重新采用，避免把曾经驻扎、现在已变化的亮色按钮当成目标。重新点击洞天后还要核对“选择洞天”的名字，降低错位风险。',ref('night_tasks.py')+[('night_engine.py','16-102')])
p('night_process先领取已有奖励，再判断倒计时或当天15次记录。开始前检查条件颜色、游戏总配额、全局累计预留，点击最大次数后读回并调整至15。预留在点击前保存，运行倒计时和总配额减15用于确认；一处失败时尽量继续剩余洞天，但名单少于四处不能把整项记为成功。整组检查后才关闭夜猎面板。', [('night_engine.py','104-194')])
p('该机制比单纯按四个坐标各点一次提供更多校验，但“完成”绿色轮廓只是候选标记，仍依赖区域与名字匹配。对reserved恢复为running的路径也并非每一处都重新验证同样完整的配额变化。当前机制降低了重复提交风险，不能称为服务器级事务或在任意中断下恰好执行一次。', [('night_engine.py','16-59'),('night_engine.py','104-159')])
h('6.4 star_rewards.py的两个独立奖励与五处供奉',2)
p('seize_rewards把夺道奖励和修炼加速分开保存。左侧读到已领取才记录seize_reward_done；加速要求识别“分身修炼加速”及非零倒计时，记录seize_boost_done，不等待整段加速结束。若当天两项都已确认则不重按。这一拆分避免把一次进入夺道页面等同于两项都已完成。', [('star_rewards.py','34-79')])
p('供奉按落日城、战争之门、斗技场、传承之地和不灭城的固定名单处理。模板先定位金色标记，但实际点击的是地点图像；进入详情后必须确认名字，再点击完整“领取供奉”文本并等待结果。各地点单独记录，缺一处则整项保留未完成。名字归一化允许唯一的一字偏差，是针对已有OCR问题的补偿，不应扩展为对任意相似名字的无条件接受。', [('workflow.py','3'),('star_rewards.py','9-32'),('star_rewards.py','81-147')])
h('6.5 forbidden_tasks.py的禁区事件循环',2)
p('当前只适配大苦灭境。run_forbidden在进入未知禁区后处理守门对话、战斗、剧情继续、探索详情、材料事件和结果页；以游戏“今日剩余探索次数”作为主要配额依据。点击探索前保存star_forbidden_transaction，下次观察到配额降低才释放提交记录。循环上限为80步，未知事件会中止，避免持续点击背后的探索按钮。', [('forbidden_tasks.py','26-116')])
p('材料策略允许给出已识别的灵草、矿石或灵石，但事件文案包含仙玉、神石时不自动接受；材料不足则确认提示并拒绝或关闭事件。战斗只在明确的战斗、迎战或挑战按钮唯一时执行。material_shortage排除了“实力不足”和“修为不足”，因为它们可能是人物台词；这种字符串规则仍不能覆盖全部叙事文案，其他材料名、事件排版和战败结果需要补样本。', [('forbidden_tasks.py','7-8'),('forbidden_tasks.py','41-90')])
h('6.6 palace_tasks.py的地图与领奖状态',2)
p('PalaceTasks同时负责境转与天阙。realm检查当前区域、打开境转菜单并选择目标；palace_open复用天阙地图。palace方法按PALACE_TASKS执行，各项结束通过palace_finish决定是否回元极。燃心灯只在愿力大于0时收取，并以归零确认；御木园先识别收获或种植，再判断健康、虫害、缺水、缺肥和养护机会。', [('palace_tasks.py','9-89'),('palace_tasks.py','212-285')])
p('同修和朝会共用timed_palace_task，但完成按钮不同：同修读取领取，朝会还接受完成。collect_palace_reward点击后等待独立奖励确认，确认按钮消失且原页面可见后写reward_done。phase为started或claiming时也会重新观察启动按钮；按钮仍在可触发游戏的今日完成提示，从而修复仅凭旧记录空等的情况。', [('palace_tasks.py','102-210')])
p('源码还存在一条不同语义的结束路径：游戏明确提示今天已经处理、等待后没有领取按钮时，代码把phase设为already_done，并同时写reward_done。这个标记说明脚本接受了游戏的今日结束提示，不等同于本轮亲眼看到奖励弹窗确认。维护与统计时应保留这一区别，不能把所有reward_done合并统计为本轮实际领奖。', [('palace_tasks.py','167-201')])
h('6.7 gift_tasks.py的名单选择与提交',2)
p('赠予任务先识别子嗣品质与姓名，再核对头像选中颜色。选择条件为姓名三角梅或品质甲中，滚动采用重叠区域，直到列表签名稳定；识别总人数还要与页面上限一致。三角梅未找到、品质冲突或人数不足时不提交。提交前写ancestral_gift_submitted，观察新的用药记录后写done与名单。', [('gift_tasks.py','10-101')])
p('赠予和珍馐坊采购通过仙居父页面衔接，单独运行provisions时入口专门把采购与赠予编成两项。赠予的成功证据来自新的聊天记录，因此仍有其他消息插入或OCR漏读的风险；与其无条件清除submitted重试，更合理的维护方式是先对照游戏状态和日志核实。', [('assistant.py','494-496'),('gift_tasks.py','39-101')])

h('7 进度保存与异常恢复',new=True)
h('7.1 账本与进度文件不是同一件事',2)
p('Bot按account_key选择ledgers下的账号JSON，并以北京时间日期判断是否建立新账本。ledger记录资源计数、单项状态与提交预留；同名.progress.json记录completed、pending、current及工作流版本。两者分别通过临时文件替换写入，不构成一次跨文件原子提交。若进程在两次保存之间结束，重启仍需用画面纠正记录。', [('assistant.py','60-69'),('daily_tasks.py','112-115'),('navigation.py','44-84')])
figure('图4_夜猎提交与恢复','图4　以夜猎为例的提交预留与重启恢复','先保存reserved，再发送开始，观察倒计时后进入running，完成后领取；结果不明时阻止重复提交。')
h('7.2 已处理与已完成的语义差异',2)
p('run_task把返回值不是False的正常结束视为成功，因此返回None的“跳过”“等待中”也可能加入completed。run_groups的completed更接近“本轮已经处理过”，不保证任务资源已全部消耗或奖励全部领取。pending用于再次检查倒计时，prepare_daily_progress则对夜猎、仙猎、供奉、小世界、禁区和周一论剑做迁移或重新检查。燃心灯即使已处理，继续当天流程仍优先检查新愿力。', [('navigation.py','44-76'),('navigation.py','213-258')])
p('这种双层状态可以表达“已启动、待领奖”，但需要每个任务正确设置pending。当前仙猎第二轮、部分异常中止和兼容任务不一定具有统一的收尾语义；main中的success采用累积与运算，一次失败即使后续收尾成功，最终退出码仍可能为2。日志、任务处理状态、奖励状态和进程退出码应分别解释。', [('daily_tasks.py','334-366'),('assistant.py','497-517')])
h('7.3 恢复策略与停止边界',2)
p('ScreenError表示页面不符合预期，run_task最多恢复后重试一次；普通TaskStop通常记录未完成、返回角色主界面并继续下一项。用户停止、应用离开前台、日期变化、分辨率错误等消息会向外抛出。recover_to_main有步数上限，优先处理已知弹窗和游戏内X，再使用可识别返回箭头；识别不到就停留现场，不发送安卓系统返回。', [('navigation.py','165-225')])
p('这是保守的有限恢复，不是完整的回滚。它不能撤销已经发生的材料扣除，也不保证所有未知弹窗可退出。业务错误可能触发回主界面，因而“同级任务不回主界面”只适用于正常路径。错误分类目前部分依赖异常文字的子串，建议逐步改为结构化异常类型和任务结果对象。', [('navigation.py','165-225')])

h('8 验证结果与证据解释',new=True)
h('8.1 本次离线复跑',2)
p(f'本次选择{len(TESTS)}个已知离线回归脚本，全部以退出码0结束。表1给出测试对象，完整标准输出与每脚本耗时保存在审计资料。耗时只用于运行追踪，没有控制硬件负载、重复次数或基线，故不作为性能测试结果。T编号按表中顺序对应test_results.json。')
test_purpose={
'test_contracts.py':'原任务归属、层级、暂停与面板入口', 'test_waiting_states.py':'寻宝直接启动与确认分支、仙猎零次数',
'test_star_rewards.py':'夺道两项、五处供奉、补漏与迁移','test_freegift.py':'修真入口缺失、免费层消失与关闭',
'test_smallworld.py':'先领取再探索、三次上限、第二项仙玉限制','test_sword_schedule.py':'周一午前跳过、开放及未开放恢复',
'test_palace_order.py':'燃心灯优先、天阙页面保留','test_palace_claim_v5.py':'完成与领取后确认奖励、聊天排除',
'test_palace_real_screens.py':'两张原始报错截图的启动按钮与弹窗判断','test_star_forbidden.py':'材料不足、战斗与星界停用',
'test_celestial_close.py':'用户天道截图的X定位','test_v5.py':'夜猎截图、四处60次、预留和单处失败'}
table(['编号与脚本','覆盖对象','本次结果'],[(f'T{i:02d}\n'+r['test'],test_purpose[r['test']],str(r['exit_code'])) for i,r in enumerate(TESTS,1)],[2.3,3.3,.9],caption='表1　本次离线回归结果　结果列为进程退出码')
h('8.2 历史运行记录能够证明什么',2)
p('日志20261026-071029-662574记录夜猎四处各15次以及总配额60至0的变化；20261026-083434-490343记录供奉补漏后的5/5确认；20261026-104208-694927记录天阙误判失败；20261026-105141-092193与105246-832682记录修复后游戏提示今日已结束。它们是不同时间、不同代码状态下的观察，不能合并成一轮当前版本完整日常成功实验。')
p('报告没有新增全流程实机复验，没有构建带人工标签的按钮数据集，也没有收集多账号、多渠道、跨分辨率样本。因此不报告召回率、精确率、每日任务总体完成率或节省时间比例。尤其不能把12个脚本通过写成“系统成功率100%”：测试脚本数量不是实际任务次数，断言通过也不是统计意义上的总体估计。')
h('8.3 后续应补充的验证',2)
p('建议为每个任务记录入口页面、初始配额、预期动作、结果证据、扣费与结束页面，并把正常、已完成、材料不足、弹窗遮挡、网络延迟和中断后恢复作为分离场景。识别能力应使用独立标注截图评估，业务正确性应以游戏状态和账本一致性评估；两类指标不能互相替代。该方案是后续建议，不是本次已完成的实验。')

h('9 当前问题与改进优先级',new=True)
h('9.1 已由源码确认的维护风险',2)
table(['问题','代码依据','影响与建议'],[
('完成语义混用','navigation.py run_task / run_groups','跳过和等待也可进入completed。建议返回明确的DONE、PENDING、SKIPPED、FAILED。'),
('第二轮仙猎收尾缺口','daily_tasks.py hunt','count达到2时pending变假。建议把启动配额和待领奖状态分开。'),
('停止不是优雅退出','ui.py stop','直接terminate可能中断写入与结果确认。建议先发停止请求，超时后再终止。'),
('输入保护不统一','assistant.py tap / adb','直接swipe不等同于tap保护。建议统一输入入口并复用前台、日期检查。'),
('层级表不能覆盖所有返回','hierarchy.py retain_parent','仅meta页可保留，close不检查保留。建议统一导航接口并记录实际页面状态。'),
('资源规则分散','daily / video / forbidden','不同模块独立报价与禁用词。建议建立按任务授权的结构化政策。'),
('全局time替换与Mixin耦合','assistant.py Bot.__init__','单进程多实例与测试隔离困难。建议注入时钟、识别器、设备和存储对象。'),
('兼容字段与版本不统一','config.json / workflow.py','不同版本字段承担不同含义。建议明确发布版本、规则版本和迁移版本。')
],[1.5,1.9,3.1],caption='表2　维护风险与建议　均为静态分析，不是已测故障发生率')
h('9.2 应先修正确性再抽象结构',2)
p('第一优先级是完成状态与资源提交的一致性，包括仙猎第二轮收尾、游戏已结束提示与实际领奖的区分，以及不明确提交的人工核对入口。第二优先级是统一输入保护和停止过程。接口拆分、任务注册和页面图扩展宜在这些语义稳定后进行，避免只移动文件而保留原有错误假设。',ref('daily_tasks.py')+ref('navigation.py')+ref('ui.py'))
p('结构上可把Bot拆成设备、识别、导航、存储、时钟和任务六类显式依赖，并让任务返回结构化结果。PARENTS可以继续保留，但需要与可执行转移及观测条件绑定。此处提出的是演进路线，当前代码仍是Mixin加手写流程，不能把目标结构画成当前实现。')

h('10 修改与调试的可复用方法',new=True)
h('10.1 从一个失败样例开始',2)
p('修改应从最新events.txt与对应截图定位，而不是先放宽阈值或延长所有等待。先确认游戏实际页面、模态层级、按钮区域与文字，再区分入口未到达、OCR漏读、目标不唯一、动作未生效和结果判定错误。把失败截图冻结为测试样本，最后才在游戏中运行单项，可减少重复资源消耗。')
code("# 在PowerShell中，先停止面板任务\n$py = 'C:\\Users\\21413\\AppData\\Local\\Programs\\Python\\Python39\\python.exe'\nSet-Location E:\\xiuxian\n& $py .\\assistant.py inspect\n& $py .\\assistant.py palace_court",'代码3　观察与单项验证示例　后一个命令会实际操作游戏')
p('VS Code使用.vscode中的debugpy配置可在单项任务设置断点，观察body、hits、phase、ledger和pending。断点暂停Python但不暂停游戏，因此长时间停住后继续执行，原先观察可能已经过期。截图识别的调试适合离线进行，动作时序则宜短断点或使用带时间戳的日志。',ref('assistant.py')+ref('runtime_control.py'))
h('10.2 添加一个任务需要同时修改什么',2)
p('首先编写带进入、观察、动作、结果确认和退出的任务方法；其次在命令行choices、中文TASKS和TASK_LABELS登记入口；再在DAILY_GROUPS、TASK_ENTRY与必要的PARENTS中声明顺序和层级；有倒计时的任务还要设置pending并加入FINISH_GROUPS。最后验证相邻任务复用、已完成跳过和中断恢复。只在菜单加一行不能完成整项接入。',ref('workflow.py')+ref('ui.py')+ref('navigation.py')+ref('assistant.py'))
p('维护源码时应保留ledgers与原始日志，不用删除账本来强行重跑。每次发布应保存源码散列、规则版本、测试结果和素材版本；打包程序与实际运行目录应核对一致。项目目前保留多种旧入口与开发脚本，probe和run命名的诊断脚本可能发送真实点击，不应按离线测试批量执行。')

h('11 结论',new=True)
p('现有助手是面向特定渠道、账号界面与720×1280截图的Python自动化系统。它通过ADB形成观察和输入通道，通过模板、颜色和OCR提供页面证据，再由区域顺序、共同父页面和各任务函数完成业务编排。账本预留、进度文件及有限恢复为中断处理提供了依据，但不同任务的结果语义和保护条件尚未完全统一。',ref('assistant.py')+ref('workflow.py')+ref('navigation.py'))
p('本报告的主要产物是对当前实现的文件职责、函数入口和证据链的可追溯说明。12个离线脚本通过支持已有回归样例，但不能替代当前版本的跨日全流程实测。后续维护应优先修正启动、领奖和完成标记之间的关系，再统一资源政策、输入保护与任务接口。报告没有证据支持“全部任务已稳定完成”或“可直接迁移任意游戏”的结论。')

h('参考文献',new=True)
references=[
'[1] Google. Android Debug Bridge (adb)[EB/OL]. Android Developers. https://developer.android.com/tools/adb. 访问日期：2026-10-26.',
'[2] Python Software Foundation. tkinter — Python interface to Tcl/Tk[EB/OL]. Python 3.9 documentation. https://docs.python.org/3.9/library/tkinter.html. 访问日期：2026-10-26.',
'[3] OpenCV. Template Matching[EB/OL]. OpenCV 4.13.0 documentation. https://docs.opencv.org/4.13.0/d4/dc6/tutorial_py_template_matching.html. 访问日期：2026-10-26.',
'[4] RapidAI. RapidOCR[CP/OL]. https://github.com/RapidAI/RapidOCR. 访问日期：2026-10-26. 本地代码使用rapidocr_onnxruntime接口；不据主仓库当前介绍推定本地包版本。',
'[5] K-Dense Inc. Scientific Writing skill, version 2.3[CP/OL]. https://github.com/K-Dense-AI/scientific-agent-skills/tree/main/skills/scientific-writing. 访问日期：2026-10-26.',
'[6] Kassis T, Agarwal V, He Y, Patel D, Brueckner A M. Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents[EB/OL]. arXiv:2609.00065, 2026, 当前记录v2. https://doi.org/10.48550/arXiv.2609.00065. 访问日期：2026-10-26.'
]
for text in references:p(text,size=10.5,indent=False).alignment=WD_ALIGN_PARAGRAPH.LEFT
h('材料与写作说明',2)
p('源码、截图与日志均在本机处理，没有为了生成报告上传项目源文件。公开资料只用于技术背景与写作方法。报告文字、结构化证据索引和矢量图由AI辅助整理；没有代填人类作者姓名、审批、经费或利益冲突。source_manifest中的人工复核状态保持pending，submission_ready保持false，供维护者后续确认。',size=10.5,indent=False)

h('附录A 源文件分段索引',new=True)
p('本附录按实际快照列出每个Python文件的职责和关键分段。S编号在正文中使用；短散列供快速核对，完整SHA-256与源码副本保存在审计资料。函数区间包含定义行与结束行。')
file_roles={
'assistant.py':('基础设施与命令入口','导入与常量1-39；Bot初始化42-69；识别和输入71-175；任务及兼容实现177-469；main入口471-517。'),
'daily.py':('旧签到启动兼容','1-8行检测--check-only并重写参数，再调用assistant.main，不实现签到算法。'),
'daily_tasks.py':('常规任务集合','14-110宗门与练功；112-244账本、仙居与钓鱼；246-317按钮与游历入口；319-500其余每日任务。'),
'forbidden_tasks.py':('探星禁区探索','7-8材料不足判别；10-24最上层X；26-28地图确认；30-116事件循环。'),
'gift_tasks.py':('仙祠赠予','10-28卡片识别；30-37选中状态；39-101名单核对、提交与结果确认。'),
'hierarchy.py':('父页面复用','3-5停留判断；7-33各入口复用；35-40练功结束与返回。'),
'navigation.py':('调度与安全恢复','34-84旧入口与进度；89-163画面、菜单与箭头；165-225恢复和异常；227-258任务组执行。'),
'night_engine.py':('夜猎核心','11-12名字归一化；16-102识别、发现与读取；104-159单洞天提交；161-194四处处理。'),
'night_tasks.py':('夜猎兼容导入','1-2行文档说明和NightTasks重导出。'),
'palace_tasks.py':('境转与天阙','9-100导航、燃心灯与等待；102-210奖励和定时任务；212-285御木园。'),
'runtime_control.py':('合作式暂停时钟','7-10状态；12-26控制门；28-37暂停感知时间；39其他time函数转发。'),
'star_rewards.py':('夺道与五处供奉','9-32名字与详情确认；34-79夺道；81-147地图定位、循环与单处领奖。'),
'ui.py':('图形面板','14-58菜单；62-97布局；99-147启动暂停停止；149-174状态与日志；末尾窗口启动。'),
'video_tasks.py':('新增任务与弹窗辅助','11-99弹窗；101-200门派与礼包；202-311小世界；313-376胜境与探星封装。'),
'workflow.py':('顺序与层级声明','2-15版本、名单与任务组；17-37页面和入口；40-49共同父页面计算。')}
for f in DATA['files']:
    role,blocks=file_roles[f['file']]
    h(IDS[f['file']]+' '+f['file'],2)
    p(f"职责：{role}。物理行数{f['lines']}；SHA-256前16位{f['sha256'][:16]}。{blocks}",indent=False)
    imports=[]
    for line in f['imports']:
        matched=re.match(r'(?:from|import) (\w+)',line)
        if matched and matched[1]+'.py' in FILES:imports.append(matched[1]+'.py')
    if imports:p('本地直接导入：'+'、'.join(dict.fromkeys(imports))+'。跨Mixin调用另见正文。',size=10.5,indent=False)

h('附录B 函数入口与直接调用索引',new=True)
p('本附录由快照的抽象语法树提取，覆盖顶层函数和类的直接方法；嵌套函数不另作为独立接口。调用列列出部分self方法或项目相关函数，按文本顺序排序，仅用于查找，不表示时序或完整动态调用图。没有项目调用的简单方法以返回值、外部库或文件操作为主。',size=10.5,indent=False)
for f in DATA['files']:
    entries=[]
    for symbol in f['symbols']:
        if symbol['kind']=='ClassDef':
            entries.extend((symbol['name']+'.'+m['name'],m['start'],m['end'],m['calls']) for m in symbol['methods'])
        else:entries.append((symbol['name'],symbol['start'],symbol['end'],symbol['calls']))
    if not entries:continue
    h(IDS[f['file']]+' '+f['file'],2)
    rows=[]
    for name,start,end,calls in entries:
        relevant=[x for x in calls if x.startswith('self.') or x in ('run_forbidden','close_front','forbidden_map','shared_parent','main','PauseClock')]
        relevant=[x.replace('self.','') for x in relevant]
        rows.append((name,f'{start}-{end}',' / '.join(relevant[:6])+(' 等' if len(relevant)>6 else '') if relevant else '文件、库调用或直接返回'))
    table(['函数或方法','行号','部分调用入口'],rows,[2.7,.65,3.15])

h('附录C 配套文件与目录的职责',new=True)
p('下表补充运行时读取的配置、启动文件和数据目录。它们不计入15个Python文件的源码行数。配置项、用户运行记录及第三方依赖不能与自有业务代码混为一类。',indent=False)
table(['文件或目录','作用与关系'],[
('config.json','Bot读取ADB路径、设备、渠道、账号标识和部分资源开关；ui.start会更新部分字段。不同版本字段不能直接等同。'),
('assets.json 与 assets','前者给出模板框与是否移动，后者保存对应PNG；Bot按名字加载，并应用渠道别名。缺失任一被引用图像会影响初始化或识别。'),
('quiz_answers.json','保留题库数据。当前quiz走一键课训流程，主源码中未见读取该文件的调用，不能据文件存在就声称仍按题库作答。'),
('ledger.json 与 ledgers','无account_key时使用根目录ledger.json；有账号标识时读取ledgers对应JSON，另有progress文件保存编排进度。'),
('ui-state.json 与 ui-error.log','面板状态文件记录UI进程、工作进程和当前任务；错误日志可供启动诊断。状态文件是快照，进程退出后可能滞后。'),
('打开每日助手.vbs / .bat','切换到脚本目录，按本机解释器路径启动ui.py；VBS通过隐藏窗口方式启动。'),
('运行签到.bat 与 daily.py','旧签到入口，通过daily.py兼容转交给assistant.main，不是第二套签到算法。'),
('停止助手.bat','写入STOP供工作进程检查；与面板stop中的直接terminate动作有所不同。'),
('.vscode','settings.json指定解释器，launch.json提供inspect及单项debugpy启动配置；调试运行仍受工作进程锁约束。'),
('vendor','包含被加入sys.path的第三方依赖。其代码、许可与版本需要单独管理，不计作项目自研算法。'),
('logs','每轮events.txt、report.json及JPG截图；用于还原当时观察，不是自动标注的准确率数据集。'),
('profiles 与 templates','保留适配或素材辅助目录。是否生效应沿具体读取路径确认，不能认为目录中每份文件都会被主程序加载。'),
('README及任务说明文档','帮助启动和维护。文档可能落后于代码，应以源码快照、配置和实际游戏状态对照核验。'),
('开发资料与发布包','前者保留历史脚本、诊断和测试；后者是发布快照。修改根目录源码不会自动同步旧ZIP。')
],[2.0,4.5],caption='表C1　配套文件与目录')

# Header, footer, document metadata and editable native content.
for part in (sec.header,sec.footer):
    for para in part.paragraphs:para.paragraph_format.first_line_indent=Pt(0)
hp=sec.header.paragraphs[0];hp.alignment=WD_ALIGN_PARAGRAPH.CENTER;fonts(hp.add_run('太古仙尊每日助手源码分析报告'),10.5)
fp=sec.footer.paragraphs[0];fp.alignment=WD_ALIGN_PARAGRAPH.CENTER
fonts(fp.add_run('第 '),10.5);fld=OxmlElement('w:fldSimple');fld.set(qn('w:instr'),'PAGE');fp._p.append(fld);fonts(fp.add_run(' 页'),10.5)
doc.core_properties.title='太古仙尊每日助手源码结构与运行机制分析'
doc.core_properties.subject='现有脚本工程分析与维护说明';doc.core_properties.author='';doc.core_properties.keywords='Python, ADB, OpenCV, OCR, 源码审计'
settings=doc.settings.element;upd=OxmlElement('w:updateFields');upd.set(qn('w:val'),'true');settings.append(upd)
# Theme fonts override explicit families in some Word installations.
for parent in (doc.styles.element,doc._element):
    for rf in parent.iter(qn('w:rFonts')):
        for key in list(rf.attrib):
            if 'theme' in key.lower():del rf.attrib[key]
    for border in list(parent.iter(qn('w:pBdr'))):border.getparent().remove(border)
out=ROOT/'太古仙尊每日助手源码分析报告.docx';doc.save(out)

# Replace PNG drawing payloads with native EMF vector payloads.
with zipfile.ZipFile(out) as z:members={n:z.read(n) for n in z.namelist()}
from lxml import etree as ET
rels=ET.fromstring(members['word/_rels/document.xml.rels']);types=ET.fromstring(members['[Content_Types].xml'])
for rid,name in figures:
    rel=next(r for r in rels if r.get('Id')==rid);old=rel.get('Target');new=old.rsplit('.',1)[0]+'.emf'
    rel.set('Target',new);members['word/'+new]=(ROOT/'矢量图'/(name+'.emf')).read_bytes();members.pop('word/'+old,None)
if not any(e.get('Extension')=='emf' for e in types):
    t=ET.SubElement(types,'{http://schemas.openxmlformats.org/package/2006/content-types}Default');t.set('Extension','emf');t.set('ContentType','image/x-emf')
members['word/_rels/document.xml.rels']=ET.tostring(rels,xml_declaration=True,encoding='UTF-8',standalone=True)
members['[Content_Types].xml']=ET.tostring(types,xml_declaration=True,encoding='UTF-8',standalone=True)
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for name,data in members.items():z.writestr(name,data)
with (ROOT/'审计资料/claims.csv').open('w',encoding='utf-8-sig',newline='') as stream:
    writer=csv.DictWriter(stream,fieldnames=['claim_id','sha256','evidence','human_verification']);writer.writeheader();writer.writerows(claims)
(ROOT/'审计资料/format_spec.json').write_text(json.dumps({'title_pt':22,'heading1_pt':15,'heading2_pt':14,'body_pt':12,'caption_reference_pt':10.5,'chinese_body':'宋体','chinese_heading':'黑体','latin':'Times New Roman','vector_diagrams':4,'source_file_count':len(FILES),'physical_lines':sum(f['lines'] for f in DATA['files']),'test_script_count':len(TESTS),'human_review':'pending','submission_ready':False},ensure_ascii=False,indent=2),encoding='utf-8')
print('Written editable DOCX with four EMF vectors:',out,'claims',len(claims))
