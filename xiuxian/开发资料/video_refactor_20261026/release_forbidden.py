# -*- coding: utf-8 -*-
import pathlib,sys,json,runpy
root=pathlib.Path('E:/xiuxian');sys.path.insert(0,str(root))
from workflow import DAILY_GROUPS
from navigation import TASK_LABELS
p=root/'视频任务清单.json';data=json.loads(p.read_text(encoding='utf-8'))
data['realms']=[{'code':r,'name':name,'tasks':[{'code':t,'name':TASK_LABELS[t]} for t in tasks]} for r,name,tasks in DAILY_GROUPS]
data.setdefault('user_supplements',{})['star_forbidden']={'star_orbit':'已取消，旧入口也不点击','area':'大苦灭境','daily':'按游戏剩余探索次数完成，不购买次数','materials':'允许所有材料；不足跳过','battle':'允许','premium':'不花仙玉、神石','hierarchy':'探索/事件的X逐层关闭，再从禁区回探星'}
p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
p=root/'任务顺序.md';s=p.read_text(encoding='utf-8')
lines=s.splitlines()
for i,line in enumerate(lines):
    if '观星台膜拜 →' in line:lines[i]=' → '.join(TASK_LABELS[t] for r,_,tasks in DAILY_GROUPS if r=='void' for t in tasks)
s='\n'.join(lines)+'\n'
s=s.replace('- 观星台、探星、星界共用探星入口。','- 观星台、探索奖励、禁区共用探星入口；星界运转已按最新要求取消。')
s+='\n禁区更新：只在探星禁区“大苦灭境”处理每日探索；按游戏剩余次数执行。允许材料和战斗，材料不足跳过，不花仙玉、神石，不买次数。其他禁区及御敌、感悟尚未接入自动任务。视频时间对照中的星界仅为历史演示，不再执行。\n'
p.write_text(s,encoding='utf-8')
p=root/'使用说明.txt';s=p.read_text(encoding='utf-8')
s+='\n2026-10-26 探星更新：星界运转取消；新增禁区每日探索（大苦灭境）。允许材料和战斗，材料不足跳过；仙玉、神石及额外次数不花。forbidden_tasks.py负责探索与随机事件。其他禁区、御敌、感悟未接入。\n'
p.write_text(s,encoding='utf-8')
p=root/'验收记录.md';s=p.read_text(encoding='utf-8')
entry='''## 禁区接入与星界取消（2026-10-26）

- 每日列表与面板移除星界运转；旧CLI入口保持兼容但不再操作游戏。
- 用户天道截图验证：右上角X准确定位(645,55)；关闭后不再强等错误的stars目标。
- 禁区实际经过守门战斗、剧情进入大苦灭境；游戏每日4次探索已用完并返回探星，日志20261026-101405-640694。
- 部分探索在用户补充材料授权之前按拒绝处理；当前代码已改为允许材料、允许战斗、材料不足跳过。该策略用控制流测试验证，今天次数已用完，未重置次数或追加购买来测试。
- 测试覆盖：停用星界、共享探星层级、材料赠予、材料不足跳过、实力不足台词排除、战斗及退出；原有天阙顺序与领奖回归通过。
- 当前仅大苦灭境每日探索已接入；其他禁区、御敌、感悟不自动执行。

'''
p.write_text(entry+s,encoding='utf-8')
runpy.run_path(str(pathlib.Path(__file__).parent/'release_smallworld.py'),run_name='__main__')
print('Forbidden release updated')
