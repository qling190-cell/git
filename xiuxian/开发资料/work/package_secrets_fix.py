import pathlib,shutil
root=pathlib.Path('outputs/太古仙尊实验版')
live=pathlib.Path('outputs/太古仙尊每日助手/太古仙尊每日助手')
note='\n探秘流程修复：降妖启动按钮改为识别“寻宝”。魔域、仙猎、降妖连续执行时共用探秘界面，各项关闭子窗口回探秘，最后一项结束后返回仙界。断点续做、倒计时收尾同样适用；异常仍恢复主界面。已通过共用导航、单项返回、部分续做、寻宝按钮及确认流程测试。\n'
for name in ('任务顺序.md','验收记录.md'):
    with (root/name).open('a',encoding='utf-8') as f:f.write(note)
for name in ('daily_tasks.py','navigation.py','任务顺序.md','验收记录.md'):
    shutil.copy2(root/name,live/name)
