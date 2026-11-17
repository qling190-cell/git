# -*- coding: utf-8 -*-
import pathlib,shutil
root=pathlib.Path('outputs/太古仙尊实验版')
live=pathlib.Path('outputs/太古仙尊每日助手/太古仙尊每日助手')
note=('\n新增仙祠一键赠予：珍馐坊三种丹药采购后返回一层仙居，进入仙祠赠予。'
      '滚动核对子嗣名单，选择三角梅（不限制品质）及其他甲中品质子嗣，排除其余子嗣。'
      '按角色与日期记录每日一次，提交前保存标记，未确认结果时不自动重复。'
      '赠予按游戏的一键赠予规则随机分配储物袋内丹药，直到没有可赠丹药或所选子嗣已吃满。'
      '已通过真实截图姓名品质配对、选中黄光，以及名单核对、取消误选、每日一次和中断防重复测试。\n')
for name in ('任务顺序.md','验收记录.md'):
    with (root/name).open('a',encoding='utf-8') as f:f.write(note)
for name in ('assistant.py','daily_tasks.py','navigation.py','gift_tasks.py','ui.py','assets.json','任务顺序.md','验收记录.md'):
    shutil.copy2(root/name,live/name)
shutil.copy2(root/'assets/gift_dialog.png',live/'assets/gift_dialog.png')
