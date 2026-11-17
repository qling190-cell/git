import pathlib,shutil
root=pathlib.Path('outputs/太古仙尊实验版')
live=pathlib.Path('outputs/太古仙尊每日助手/太古仙尊每日助手')
note='\n通天塔领奖路线：点击领取奖励后识别每日只能领取一次的提示并点确定，确认今日已领取后返回游历；后续有探秘任务时直接从游历进入探秘，不再往返仙界主界面。已通过确认弹窗、已领取跳过、游历直达探秘及单项执行返回测试。\n'
for name in ('任务顺序.md','验收记录.md'):
    with (root/name).open('a',encoding='utf-8') as f:f.write(note)
for name in ('daily_tasks.py','navigation.py','任务顺序.md','验收记录.md'):
    shutil.copy2(root/name,live/name)
