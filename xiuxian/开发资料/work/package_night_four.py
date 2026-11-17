# -*- coding: utf-8 -*-
import pathlib,shutil
root=pathlib.Path('outputs/太古仙尊实验版')
live=pathlib.Path('outputs/太古仙尊每日助手/太古仙尊每日助手')
note=('\n夜猎规则更新：滚动到洞天列表底部，按排列顺序选择最新亮色已解锁的四个洞天，排除灰色未解锁按钮。'
      '绿色完成则先领奖，正在倒计时则跳过该洞天；可开始时将轮数确认为15，每处每日15次，共60次。'
      '逐洞天保存今日进度，不再使用全部洞天合计15次的旧限制；旧版完成标记会重新检查。'
      '四处全部检查后返回，倒计时完成后由自动收尾领取奖励。游戏次数或驻扎条件不足时记录并检查下一处。'
      '已通过当前OPPO真实截图的亮色/灰色和最新四处识别，以及四处领奖、60次启动、计时跳过、续做不重复的流程测试。\n')
for name in ('任务顺序.md','验收记录.md'):
    with (root/name).open('a',encoding='utf-8') as f:f.write(note)
for name in ('assistant.py','navigation.py','night_tasks.py','任务顺序.md','验收记录.md'):
    shutil.copy2(root/name,live/name)
