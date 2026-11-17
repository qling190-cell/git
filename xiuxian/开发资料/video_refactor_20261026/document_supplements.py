# -*- coding: utf-8 -*-
import pathlib,json,sys,re
r=pathlib.Path('E:/xiuxian');sys.path.insert(0,str(r))
from workflow import DAILY_GROUPS,WORKFLOW_VERSION
from navigation import TASK_LABELS
p=r/'视频任务清单.json';d=json.loads(p.read_text(encoding='utf-8'));d['version']=WORKFLOW_VERSION
for realm,_,tasks in DAILY_GROUPS:
 data=next(x for x in d['realms'] if x['code']==realm);old={x['code']:x for x in data['tasks']}
 data['tasks']=[dict(old.get(t,{}),code=t,name=TASK_LABELS[t]) for t in tasks]
d.setdefault('user_supplements',{}).update(enlightenment={'daily':1},creation_dew={'daily':1,'price':6000,'currency':'功德'},saint_beast={'daily':1,'action':'预约封印'},star_way={'daily':1,'on_countdown':'退出，不等待，不点击神游天外'},star_forbidden={'enabled':False})
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
p=r/'任务顺序.md';s=p.read_text(encoding='utf-8')
for _,label,tasks in DAILY_GROUPS:
 s=re.sub(r'(## '+label+r'\s*\n\s*\n)[^\n]+',lambda m:m[1]+' → '.join(TASK_LABELS[t] for t in tasks),s,count=1)
s=s.replace('护法与课训共用弟子院；博戏与玉盒共用市肆；训话、禁地在宗门内直接切换。','护法与课训共用弟子院；玉盒与参天造化露共用市场窗口；造化露完成后回宗门地图，切换悟道室、训话与禁地。')
s=s.replace('观星台、探索奖励、禁区共用探星入口；星界运转已按最新要求取消。','观星台、探索奖励和游道共用探星入口；夺道与供奉后进入游道，看到倒计时退出。星界运转和禁区任务均已取消。')
s+='\n新增：凡间神游后直接在游历页预约圣兽；市场玉盒后向下寻找参天造化露，每日买1个（6000功德）；宗门悟道室每日悟道一次。\n';p.write_text(s,encoding='utf-8')
p=r/'README.md';s=p.read_text(encoding='utf-8').replace('禁区探索、讨伐','游道修炼、讨伐')
s=s.replace('- 探星禁区当前仅接入“大苦灭境”的每日探索，按游戏剩余次数执行；允许材料与战斗，材料不足跳过，不花仙玉、神石，不买次数。御敌、感悟与其他禁区尚未接入。','- 探星禁区与星界运转已取消；旧命令保留兼容，记录取消后返回，不发送点击。探索的夺道、供奉后进入游道，看到修炼倒计时即退出。')
s=s.replace('例如小世界、禁区的材料授权','例如小世界的材料授权').replace('| `forbidden_tasks.py` | 探星禁区探索、随机事件、材料不足跳过与战斗处理 |','| `forbidden_tasks.py` | 已停用禁区任务的旧实现，仅保留历史回归测试 |\n| `supplement_tasks.py` | 悟道室、参天造化露、圣兽预约、游道修炼及每天一次记录 |')
s=s.replace('& $py .\\assistant.py star_forbidden    # 探星禁区','& $py .\\assistant.py star_way          # 游道每日修炼')
s+='\n新增任务：人间游历圣兽每日预约；仙界市场参天造化露每日1个（6000功德），宗门悟道室每日悟道一次。具体位置与最新顺序见任务顺序.md。\n';p.write_text(s,encoding='utf-8')
entry='''
2026-10-27 新增每日任务与取消禁区：
人间：常羊山神游后在同一游历页进入圣兽，预约封印每天1次。
仙界：玉盒后复用市场窗口，向下查找并核对参天造化露，每天购买1个，价格6000功德；接着在宗门地图进入悟道室，悟道每天1次。
虚空：观星台、夺道奖励/修炼加速与供奉、游道共用探星入口；游道启动普通修炼一次，看到倒计时立即退出，不等待，不点击神游天外。
探星禁区已从全部日常移除，UI不再提供；旧CLI入口记录已取消，不执行探索或战斗。宗门禁地保持原任务。
全部/继续/暂停语义保持：全部从头；继续尊重当天断点，不回头插跑新增任务；当天已单独完成的任务保留记录。
'''
p=r/'使用说明.txt';p.write_text(p.read_text(encoding='utf-8')+'\n'+entry,encoding='utf-8')
p=r/'验收记录.md';p.write_text(p.read_text(encoding='utf-8')+'\n'+entry+'\n实机：悟道成功获得166750000修为（new_insight_result.png）；圣兽预约成功日志20261027-231747-632810；造化露确认限购从0/2变为1/2，消耗6000功德，日志20261027-232217-807414；游道已有倒计时，直接退出日志20261027-232540-903378。四项今日记录均保存。test_supplement_tasks.py覆盖原生页面、物品图标、购买/手动已购/不足/重复保护、悟道确认、圣兽预约、游道启动与已有倒计时退出、共用父级。\n',encoding='utf-8')
print('Updated structured task list, task order, README and verification notes')
