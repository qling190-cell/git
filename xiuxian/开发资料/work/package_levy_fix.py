# -*- coding: utf-8 -*-
import pathlib,shutil
root=pathlib.Path('outputs/太古仙尊实验版')
live=pathlib.Path('outputs/太古仙尊每日助手/太古仙尊每日助手')
note=('\n征收与仙猎倒计时：新征收目标改为太上凰宗，按文字定位并确认选中地点。'
      '已有九尾狐宗征收若仍计时则保留，结束后先领奖再选择新地点。'
      '征收优先检测倒计时，有倒计时直接退出执行后续任务；自动收尾检查奖励及剩余次数。'
      '仙猎启动后识别倒计时即退出，每日最多2次。已通过计时退出、先领奖再切目标及次数上限测试。\n')
for name in ('任务顺序.md','验收记录.md'):
    with (root/name).open('a',encoding='utf-8') as f:f.write(note)
for name in ('assistant.py','daily_tasks.py','任务顺序.md','验收记录.md'):
    shutil.copy2(root/name,live/name)
