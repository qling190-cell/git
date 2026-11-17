# -*- coding: utf-8 -*-
from pathlib import Path
r=Path('E:/xiuxian');p=r/'README.md';s=p.read_text(encoding='utf-8')
s=s.replace('4. 选择“全部日常”或单项任务，点击“开始”。','4. 选择“全部日常”（从第一项重跑）、“继续今日日常”（读取当天断点）或单项任务，点击“开始”。')
s=s.replace('开始时读取当前配置角色的当天进度；暂停保留进程，停止后再启动会重新加载代码并读取已保存进度。','“全部日常”重新建立流程进度，从人间第一项依次执行所有任务；“继续今日日常”读取本角色当天断点，中断的任务重新检查，已结束的步骤不回头执行。任务完成时立即保存下一项位置，跨区域也能续跑。暂停保留进程，点击“继续”恢复原位置。\n\n两种模式均保留当天已确认的购买、消耗和游戏次数记录；游戏已完成或次数用尽的任务仍按模块规则跳过，不重复购买、不增加额外次数。倒计时任务保留给自动收尾，不会让续跑跳回前面的区域。')
s=s.replace('# 全部日常：自动读取当天断点；--watch开启倒计时收尾','# 全部日常：从第一项重跑完整流程；--watch开启倒计时收尾')
s=s.replace('& $py .\\assistant.py all --watch','& $py .\\assistant.py all --watch\n\n# 继续今日日常：从当天断点继续\n& $py .\\assistant.py resume --watch')
p.write_text(s,encoding='utf-8')
p=r/'使用说明.txt';s=p.read_text(encoding='utf-8').replace('继续当天任务也优先检查新积累愿力。','完整流程中燃心灯优先；继续当天任务遵守断点，不回头重做燃心灯。')
s+='\n运行模式区分（2026-10-27）：\n全部日常 / all：清空流程完成列表，从人间第一项依次检查执行全部任务。\n继续今日日常 / resume：保留当天完成列表与任务断点，中断项继续处理，完成项不回头重做；没有当天断点则从第一项开始。\n任务之间保存下一项位置；暂停“继续”只恢复原进程。两种模式均保留今日资源消耗与次数记录，倒计时由自动收尾继续处理。\n';p.write_text(s,encoding='utf-8')
p=r/'验收记录.md';s=p.read_text(encoding='utf-8');s+='\n2026-10-27 两种日常模式分离：all 使用 resume=False，从第一项执行全部模块；resume 使用 resume=True，只执行断点后的未完成项。不再强制回查前面的仙猎或燃心灯。每项开始前保存当前项，结束后保存下一项，跨区域也保存。重新开始只重置流程进度，保留今日资源、次数与倒计时。test_daily_modes.py 覆盖从头、精确续跑、中断、跨区、跨日、收尾和消耗记录不变；全部通过。\n';p.write_text(s,encoding='utf-8')
print('Updated mode instructions and verification record')
