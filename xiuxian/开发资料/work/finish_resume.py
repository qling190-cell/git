import pathlib,shutil
root=pathlib.Path('outputs/太古仙尊实验版')
live=pathlib.Path('outputs/太古仙尊每日助手/太古仙尊每日助手')
p=root/'assistant.py'
s=p.read_text(encoding='utf-8')
s=s.replace("choices=['all','finish'","choices=['all','resume','finish'")
p.write_text(s,encoding='utf-8')
p=root/'ui.py'
s=p.read_text(encoding='utf-8').replace('v4.1','v4.3')
s=s.replace("in ['all','finish'","in ['all','resume','finish'")
s=s.replace("self.start_btn.configure(state='disabled');self.stop_btn", "self.resume_btn.configure(state='disabled');self.start_btn.configure(state='disabled');self.stop_btn")
s=s.replace("self.start_btn.configure(state='normal');self.stop_btn", "self.resume_btn.configure(state='normal');self.start_btn.configure(state='normal');self.stop_btn")
s=s.replace("self.output.insert('end','当前支持", "self.output.insert('end','停止后点击“继续今日”，从当天中断的任务接着执行。按角色与日期保存，已完成任务跳过，倒计时收尾会保留。\\n当前支持")
p.write_text(s,encoding='utf-8')
note='\n\n断点续做（v4.3）：新增“继续今日”按钮及“继续今日日常”任务。运行全部日常时按账号和北京时间日期原子保存进度；继续时跳过已处理任务，从中断或未完成任务重新检查状态，再执行后续任务。神游、禁地等倒计时收尾列表一并保存。点击“全部日常→开始”会重新检查整套日常并建立新进度。旧版本尚未保存的运行不能自动还原断点；更新后首次运行开始记录。\n'
for name in ('任务顺序.md','验收记录.md'):
    p=root/name
    s=p.read_text(encoding='utf-8')
    if note not in s:p.write_text(s+note,encoding='utf-8')
for name in ('assistant.py','navigation.py','ui.py','任务顺序.md','验收记录.md'):
    shutil.copy2(root/name,live/name)
print('Updated both copies; existing running process was not interrupted.')
