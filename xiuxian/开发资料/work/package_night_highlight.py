# -*- coding: utf-8 -*-
import pathlib,shutil
root=pathlib.Path('outputs/太古仙尊实验版')
live=pathlib.Path('outputs/太古仙尊每日助手/太古仙尊每日助手')
note=('\n夜猎漏识别修复：选中高亮边框会连接相邻按钮轮廓，新增独立竖排已驻扎模板扫描与去重，'
      '不依赖高亮按钮的外框分割。已用当前失败截图、普通驻扎截图及绿色完成截图验证均识别四处；'
      '每处15次、四处60次、倒计时跳过及领奖不重复的流程测试通过。\n')
for name in ('任务顺序.md','验收记录.md'):
    with (root/name).open('a',encoding='utf-8') as f:f.write(note)
    shutil.copy2(root/name,live/name)
shutil.copy2(root/'night_tasks.py',live/'night_tasks.py')
