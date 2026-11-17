# -*- coding: utf-8 -*-
import pathlib,json,py_compile
root=pathlib.Path('E:/xiuxian');folder=root/'开发资料/video_refactor_20261026'
rows=json.loads((folder/'regression_20261027_evening.json').read_text(encoding='utf-8'));assert len(rows)==26 and all(r['code']==0 for r in rows)
for p in root.glob('*.py'):py_compile.compile(str(p),doraise=True)
p=root/'验收记录.md';s=p.read_text(encoding='utf-8');s+='\n晚间最终检查结果：26/26回归脚本通过；根目录全部Python源码语法检查通过。练功与神游已完成上述实机验证。\n';p.write_text(s,encoding='utf-8')
print('PASS: 26/26 regression scripts; all runtime Python source compiled')
