# -*- coding: utf-8 -*-
import pathlib,json,sys,py_compile,zipfile,subprocess
root=pathlib.Path('E:/xiuxian');sys.path.insert(0,str(root))
from workflow import DAILY_GROUPS,TRIBUTE_NAMES
from navigation import TASK_LABELS
for path in root.glob('*.py'):py_compile.compile(str(path),doraise=True)
section='''
## 探星探索奖励与五处供奉

探索内先进入夺道，分别处理“夺道奖励”和“修炼加速”，两项单独保存当天状态。
再分别进入落日城、战争之门、斗技场、传承之地、不灭城，在各自详情内点击“领取供奉”。
地图金色供奉标记仅用于定位，不视为领取成功；第五处需滚动查找。
每处确认领取结果后才记录完成，只回探索页面；五处全部处理后再退出。
中断后只补未确认地点；领取失败不会把整项标记为完成。
'''
p=root/'任务顺序.md';s=p.read_text(encoding='utf-8').replace('探星护星与已有世界供奉','探星探索奖励与五处供奉')
if '## 探星探索奖励与五处供奉' not in s:s+=section
p.write_text(s,encoding='utf-8')
p=root/'视频任务清单.json';data=json.loads(p.read_text(encoding='utf-8'))
data['realms']=[{'code':r,'name':name,'tasks':[{'code':t,'name':TASK_LABELS[t]} for t in tasks]} for r,name,tasks in DAILY_GROUPS]
data['user_supplements']={'stars':{'seize':['夺道奖励','修炼加速'],'tributes':list(TRIBUTE_NAMES),'action':'分别进入五处详情，点击领取供奉，确认结果后返回探索'}}
for item in data.get('video_timeline',[]):
    if '探星护星' in item['operation']:item['operation']='探星探索奖励与供奉（具体领取项按用户补充）'
p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
p=root/'使用说明.txt';s=p.read_text(encoding='utf-8')
if 'star_rewards.py' not in s:s+='\n探星：探索→夺道→分别领取夺道奖励、修炼加速；逐一进入五个地点点击领取供奉。\n单项菜单可选择“夺道奖励与修炼加速”或“夺道奖励、加速与供奉”。\nstar_rewards.py：夺道与五处供奉、逐项确认、防重复和中断补领。\n'
p.write_text(s,encoding='utf-8')
p=root/'验收记录.md';s=p.read_text(encoding='utf-8')
proof='''
## 探星补充验收（2026-10-26）

- 夺道奖励与修炼加速分别实机确认；日志20261026-081738-128799。
- 五处均进入详情并点击领取供奉，今日确认5/5；日志20261026-083016-687670、20261026-083434-490343。
- 修正传承之地标题OCR误字；断点补领仅处理最后未确认的一处。
- 四套回归通过：截图与夜猎、四区层级与界面、寻宝仙猎计时、夺道与五处供奉；根目录Python语法检查通过。
- 高级星界等资源操作未全部实机消耗验证，仍按识别结果与游戏提示保留未完成状态。

'''
if '## 探星补充验收' not in s:s=proof+s
p.write_text(s,encoding='utf-8')
dest=root/'发布包'/'太古仙尊每日助手_v5.0.zip';dest.parent.mkdir(exist_ok=True)
folders=('assets','vendor','profiles','templates','ledgers')
files=[p for p in root.iterdir() if p.is_file() and p.suffix.lower() in ('.py','.json','.md','.txt','.bat','.vbs') and p.name not in ('ui-state.json','迁移核验.json')]
for name in folders:
    files.extend(p for p in (root/name).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc')
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
    for p in files:z.write(p,p.relative_to(root).as_posix())
with zipfile.ZipFile(dest) as z:
    assert z.testzip() is None
    for name in ('assistant.py','workflow.py','hierarchy.py','night_engine.py','star_rewards.py','video_tasks.py','runtime_control.py','ui.py'):assert name in z.namelist(),name
print('PASS compile + ZIP CRC:',str(dest),'files',len(files),'bytes',dest.stat().st_size)
proc=subprocess.Popen([str(pathlib.Path(sys.executable).with_name('pythonw.exe')),str(root/'ui.py')],cwd=str(root),creationflags=subprocess.CREATE_NO_WINDOW,stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
print('UI launched without starting tasks; pid',proc.pid)
