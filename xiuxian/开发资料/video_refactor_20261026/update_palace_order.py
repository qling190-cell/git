# -*- coding: utf-8 -*-
import pathlib,json,sys
root=pathlib.Path('E:/xiuxian');sys.path.insert(0,str(root))
from workflow import PALACE_TASKS
from navigation import TASK_LABELS
p=root/'任务顺序.md';s=p.read_text(encoding='utf-8')
s=s.replace('萦云楼同修领奖 → 朝会殿朝议领奖 → 燃心灯收取 → 御木园状态与收获重种','燃心灯收取 → 萦云楼同修领奖 → 朝会殿朝议领奖 → 御木园状态与收获重种')
s=s.replace('- 天阙按本次视频：同修 → 朝议 → 燃心灯；御木园留在元极模块最后补做。各项只回天阙地图。','- 天阙按最新要求：燃心灯优先 → 同修领奖 → 朝议领奖 → 御木园。四项同属天阙地图，各项之间不回元极主界面。')
p.write_text(s,encoding='utf-8')
p=root/'视频任务清单.json';data=json.loads(p.read_text(encoding='utf-8'))
for realm in data['realms']:
    if realm['code']=='yuanji':realm['tasks']=[{'code':t,'name':TASK_LABELS[t]} for t in PALACE_TASKS]
data.setdefault('user_supplements',{})['palace']={'order':list(PALACE_TASKS),'parent':'palace_map','lamp_recheck_on_resume':True,'note':'最新要求覆盖视频中天阙的原始先后；各任务之间只回天阙地图'}
p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
p=root/'使用说明.txt';s=p.read_text(encoding='utf-8')
line='天阙最新顺序：燃心灯收取→萦云楼领奖→朝会殿领奖→御木园。全部日常与天阙每日共用这一顺序；任务之间只回天阙地图，最后一次才回元极。继续当天任务也优先检查新积累愿力。'
if line not in s:p.write_text(s+'\n'+line+'\n',encoding='utf-8')
p=pathlib.Path(__file__).parent/'test_v5.py';s=p.read_text(encoding='utf-8').replace("['palace_cultivate','palace_court','palace_lamp']","['palace_lamp','palace_cultivate','palace_court']")
p.write_text(s,encoding='utf-8')
print('Updated current order, documentation and regression expectation')
