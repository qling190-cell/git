# -*- coding: utf-8 -*-
from pathlib import Path
r=Path('E:/xiuxian');p=r/'验收记录.md';s=p.read_text(encoding='utf-8')
s+='''

## 2026-10-27 晚间练功与神游修复

根因：普通练功只等 practice_running，没有处理居中“今日已经修炼过了”提示；自动页面恢复因此重复提交。证据 logs/20261027-214105-402164/0042.jpg。

修复：普通练功增加当前页今日完成提示与修炼中判断；提交前保存 phase，结果未确认则保留提交记录且禁止再次点击；确认后记录今日已处理，不重复消耗。掌门传功仍独立检查已有次数，不购买。

实机：logs/20261027-214908-896583，普通练功正常识别今日完成；掌门提示仅购买入口，关闭X正常返回。未购买掌门次数。

额外修复：同一日志神游数量曾瞬时读空，增加4秒内重读和检测OCR回退，要求唯一数字、范围0至300。实机 logs/20261027-215048-640512 正确读取20，启动20次消耗8000食物，今日累计300/300；当前批次仍待完成领取。

测试：test_practice_outcome.py 覆盖原生今日完成提示、空闲页反例、修炼中、今日已完成、重复调用去重及未确认提交拦截。test_wander_count.py 覆盖原生20、过渡空白与检测OCR回退。完整回归详情见开发资料/video_refactor_20261026/regression_20261027_evening.json。离线测试通过不等于所有游戏功能在当前账号重新完成一遍。
'''
p.write_text(s,encoding='utf-8')
p=r/'使用说明.txt';s=p.read_text(encoding='utf-8');s+='\n练功修复（2026-10-27晚）：支持游戏“今日已经修炼过了”提示；结果不明时不重复点击开始。确认后保存今日记录。神游数量切换时允许短暂等待，仍严格确认数量后才启动。\n';p.write_text(s,encoding='utf-8')
print('Recorded root cause, safeguards, native screenshots and real verification logs')
