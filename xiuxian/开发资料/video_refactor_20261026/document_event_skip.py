# -*- coding: utf-8 -*-
from pathlib import Path
import py_compile
r=Path('E:/xiuxian')
for p in r.glob('*.py'):py_compile.compile(str(p),doraise=True)
entry='\n2026-11-11 探星事件跳过：决赛、恶龙等无法处理的事件，关闭游戏内X返回探索，不选择事件选项；供奉详情无法确认时关闭弹窗跳过该地点，未领取的供奉不写已领取。实机已跳过落日城、传承之地事件，其余3处确认领取，继续完成游道、讨伐、三种丹药采购、22人核对后赠予8人、剩余钓鱼与天阙。日志20261111-155020-250183于15:59:48进入5分钟收尾等待，御木园健康跳过。test_star_rewards.py与原生恶龙截图 test_blocked_star_event.py通过，全部源码语法检查通过。\n'
for name in ('验收记录.md','使用说明.txt'):
 p=r/name;p.write_text(p.read_text(encoding='utf-8')+entry,encoding='utf-8')
print('Compiled and recorded live validation')
