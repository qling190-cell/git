# -*- coding: utf-8 -*-
import pathlib,json
r=pathlib.Path('E:/xiuxian')
p=r/'视频任务清单.json';d=json.loads(p.read_text(encoding='utf-8'))
for realm in d.get('realms',[]):
 for task in realm['tasks']:
  if task['code']=='battle_exchange':task['name']='胜境之喻兑换（仅第一项1个）'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
p=r/'任务顺序.md';p.write_text(p.read_text(encoding='utf-8').replace('战境材料兑换','胜境之喻兑换（仅第一项1个）'),encoding='utf-8')
for name in ['使用说明.txt','验收记录.md']:
 p=r/name;s=p.read_text(encoding='utf-8');s+='\n2026-10-27 胜境兑换：仅第一项胜境之喻，每次1个；不兑换第二项或第三、第四项经验。剩余0次或资源不足则跳过，不替换为其他商品。保留今日已处理记录并防止未确认提交重复执行。原生截图0次跳过及单次兑换、重复运行、资源不足等测试通过（test_battle_exchange_first.py）。\n';p.write_text(s,encoding='utf-8')
print('Updated UI/task list and documentation')
