# -*- coding: utf-8 -*-
import pathlib,shutil
root=pathlib.Path('outputs/太古仙尊实验版')
live=pathlib.Path('outputs/太古仙尊每日助手/太古仙尊每日助手')
note=('\n采购单项入口修复：单独运行珍馐坊采购也会接着执行仙祠一键赠予。'
      '名单采用放大识别、短距离慢速重叠滚动、跳过半露头像、等待选中动画并完整核对总人数。'
      '支持赠予后选择窗口自动关闭。实机核对22人，选择三角梅及7名甲中子嗣共8人，'
      '已完成今日赠予并保存每日记录，返回虚空主界面。实机日志：20261025-034105-490868。\n')
for name in ('任务顺序.md','验收记录.md'):
    with (root/name).open('a',encoding='utf-8') as f:f.write(note)
for name in ('assistant.py','gift_tasks.py','任务顺序.md','验收记录.md'):
    shutil.copy2(root/name,live/name)
