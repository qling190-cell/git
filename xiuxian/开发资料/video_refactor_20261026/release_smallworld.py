# -*- coding: utf-8 -*-
import pathlib,json,py_compile,zipfile
root=pathlib.Path('E:/xiuxian')
for p in root.glob('*.py'):py_compile.compile(str(p),doraise=True)
section='''
小世界更新（2026-10-26）：
探索：有领取先领取，再继续探索；每天最多启动三次，倒计时交给自动收尾。
事件：识别四个黄色选项，仅选择第二项；本模块允许材料与灵石，不允许仙玉。
事件结果页点右上角X回小世界，再进入事件处理下一件；无事件则退出。
探索与事件共用小世界地图，各自点X关闭，全部处理后才返回上一级。
材料与灵石授权仅适用于小世界，不改变其他任务原有资源限制。
修真礼包：无修真入口即跳过；免费领取后支持礼包移除判断，并点击金色X关闭。
'''
for name in ('使用说明.txt','任务顺序.md'):
    p=root/name;s=p.read_text(encoding='utf-8')
    if '小世界更新（2026-10-26）' not in s:p.write_text(s+'\n'+section,encoding='utf-8')
p=root/'视频任务清单.json';data=json.loads(p.read_text(encoding='utf-8'))
data.setdefault('user_supplements',{})['smallworld']={'exploration_limit':3,'claim_first':True,'event_option':2,'allow':['材料','灵石'],'forbid':['仙玉'],'return':'右上角叉号返回小世界地图'}
for realm in data.get('realms',[]):
    for task in realm['tasks']:
        if task['code']=='smallworld':task['name']='小世界探索与事件'
p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
p=root/'验收记录.md';s=p.read_text(encoding='utf-8')
entry='''
## 小世界与修真礼包修复（2026-10-26）

- 修真礼包在实际停留页面识别金色X并退出；缺入口、已领层消失、已打开付费层测试通过。
- 小世界实际先领取旧奖励并启动后续探索；累计启动1次并检测倒计时，保留自动收尾。
- 事件首轮1件、补齐奖励页处理后连续7件，均选第二项，消耗材料或灵石；日志20261026-091739-035911、20261026-092003-289026。
- 无事件后点击X退出成功；未消耗仙玉。
- 测试覆盖：三次上限、领取后继续、未确认启动恢复、原生截图四选项、第二项仙玉禁止点击。
- 原有四区层级、UI任务入口、探星奖励与供奉、寻宝仙猎回归通过；源码语法检查通过。

'''
if '## 小世界与修真礼包修复' not in s:p.write_text(entry+s,encoding='utf-8')
dest=root/'发布包'/'太古仙尊每日助手_v5.0.zip'
files=[p for p in root.iterdir() if p.is_file() and p.suffix.lower() in ('.py','.json','.md','.txt','.bat','.vbs') and p.name not in ('ui-state.json','迁移核验.json')]
for folder in ('assets','vendor','profiles','templates','ledgers'):
    files.extend(p for p in (root/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc')
with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
    for p in files:z.write(p,p.relative_to(root).as_posix())
with zipfile.ZipFile(dest) as z:assert z.testzip() is None and 'assets/freegift_close.png' in z.namelist()
print('PASS: compiled, documented, updated release ZIP with latest code/assets and preserved ledgers')
