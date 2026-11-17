# -*- coding: utf-8 -*-
import pathlib,shutil
root=pathlib.Path('outputs/太古仙尊实验版')
live=pathlib.Path('outputs/太古仙尊每日助手/太古仙尊每日助手')
note=('\n天阙同级任务路线调整：燃心灯优先，然后御木园、萦云楼、朝会殿。'
      '各建筑任务结束只返回一层到天阙地图，直接进入下一建筑，不再重复返回元极主界面。'
      '最后一项结束后统一返回；单项执行仍正常返回，断点续做和自动收尾也复用地图。'
      '已通过灯优先、四任务共用地图、最后统一退出、单项执行和部分续做测试。\n')
for name in ('任务顺序.md','验收记录.md'):
    with (root/name).open('a',encoding='utf-8') as f:f.write(note)
for name in ('navigation.py','palace_tasks.py','任务顺序.md','验收记录.md'):
    shutil.copy2(root/name,live/name)
