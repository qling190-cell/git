# -*- coding: utf-8 -*-
import pathlib,shutil
root=pathlib.Path('outputs/太古仙尊实验版')
live=pathlib.Path('outputs/太古仙尊每日助手/太古仙尊每日助手')
note=('\n夜猎返回识别修复：新增OPPO夜猎标题、专用红叉以及征程页圆形返回按钮样本。'
      '恢复流程先关闭夜猎弹窗，再点击征程左上角返回虚空主界面；仍不发送安卓系统返回。'
      '已实机完成红叉关闭与征程返回，截图测试同时确认遮罩下的背景返回按钮不会误判。\n')
for name in ('任务顺序.md','验收记录.md'):
    with (root/name).open('a',encoding='utf-8') as f:f.write(note)
    shutil.copy2(root/name,live/name)
