import pathlib,shutil
root=pathlib.Path('outputs/太古仙尊实验版')
live=pathlib.Path('outputs/太古仙尊每日助手/太古仙尊每日助手')
note='\n仙祠返回修复：补充OPPO仙祠左上角圆形返回按钮；停留仙祠时续做会先直接处理一键指点、确定，再左上角返回仙居执行后续任务。确认弹窗关闭并恢复仙祠后记录指点完成，不再强制匹配旧版变灰按钮。已实机确认子嗣属性提升及返回仙居，并保留今日已指点记录。\n'
for name in ('任务顺序.md','验收记录.md'):
    p=root/name;s=p.read_text(encoding='utf-8')
    s=s.replace('确认一键指点按钮变灰后才记录完成','确认弹窗关闭并恢复仙祠页面后才记录完成')
    p.write_text(s+note,encoding='utf-8')
for name in ('assistant.py','daily_tasks.py','navigation.py','assets.json','任务顺序.md','验收记录.md'):
    shutil.copy2(root/name,live/name)
