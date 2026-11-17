# -*- coding: utf-8 -*-
import pathlib,shutil
root=pathlib.Path('outputs/太古仙尊实验版')
live=pathlib.Path('outputs/太古仙尊每日助手/太古仙尊每日助手')
note=('\n夜猎选择规则修订：以橙色竖排“已驻扎”标记识别目标，不再取最新四个亮色按钮。'
      '绿色完成表示已有夜猎已结束，先领奖。四个目标逐个设置15次并开始，倒计时则跳过，全部处理后返回。'
      '每个洞天每日最多15次、共60次，保留各洞天的续做记录。'
      '已通过OPPO实图四个驻扎标记识别、亮色未驻扎项排除、完成领奖及60次流程测试。\n')
for name in ('任务顺序.md','验收记录.md'):
    with (root/name).open('a',encoding='utf-8') as f:f.write(note)
for name in ('night_tasks.py','assets.json','任务顺序.md','验收记录.md'):
    shutil.copy2(root/name,live/name)
shutil.copy2(root/'assets/night_stationed.png',live/'assets/night_stationed.png')
