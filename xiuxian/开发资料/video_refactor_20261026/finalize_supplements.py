# -*- coding: utf-8 -*-
from pathlib import Path
import py_compile,json
r=Path('E:/xiuxian')
for p in r.glob('*.py'):py_compile.compile(str(p),doraise=True)
p=r/'README.md';s=p.read_text(encoding='utf-8').replace('| 人间 | 神游、门派死地','| 人间 | 神游、圣兽预约、门派死地').replace('| 仙界 | 护法、课训、博戏、玉盒、训话','| 仙界 | 护法、课训、博戏、玉盒、参天造化露、悟道室、训话');p.write_text(s,encoding='utf-8')
p=r/'验收记录.md';s=p.read_text(encoding='utf-8');s+='\n本轮28/28回归脚本通过；随后新增的旧禁区断点迁移与丹方页签选择，已补充相应断言并复测 test_daily_modes.py、test_supplement_tasks.py 通过。全部运行源码语法检查通过。原论文报告冻结快照未改动。\n';p.write_text(s,encoding='utf-8')
print('PASS: all source compiled, 28-test suite and targeted final checks documented')
