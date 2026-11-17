import pathlib,shutil,json
root=pathlib.Path('outputs/太古仙尊实验版')
live=pathlib.Path('outputs/太古仙尊每日助手/太古仙尊每日助手')
p=root/'ui.py'
s=p.read_text(encoding='utf-8').replace('v4.3','v4.4')
s=s.replace('停止后点击“继续今日”，从当天中断的任务接着执行。','开始会自动继续当天进度；暂停后点击“继续”，从当前位置接着执行。')
p.write_text(s,encoding='utf-8')
note='\n\n暂停与自动续做（v4.4）：普通“全部日常→开始”现在自动读取本角色当天断点，不再清空进度。暂停按钮保留进程与当前位置，当前操作结束后停止后续输入，显示已暂停后点击继续可恢复。识别超时不计暂停时间，游戏内倒计时照常运行。停止或关闭后重新开始仍读取当天任务断点；中断任务重新检查当前状态。\n'
for name in ('任务顺序.md','验收记录.md'):
    p=root/name;s=p.read_text(encoding='utf-8')
    s=s.replace('点击“全部日常→开始”会重新检查整套日常并建立新进度。','点击“全部日常→开始”也会自动继续当天进度。')
    p.write_text(s+note,encoding='utf-8')
for name in ('assistant.py','navigation.py','runtime_control.py','ui.py','任务顺序.md','验收记录.md'):
    shutil.copy2(root/name,live/name)
print('Both copies updated, including pause runtime.')
