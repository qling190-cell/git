# -*- coding: utf-8 -*-
import pathlib,json,shutil,datetime,py_compile
r=pathlib.Path('E:/xiuxian');folder=r/'开发资料'/'star_way_authorize_20261028';folder.mkdir(exist_ok=True)
p=r/'supplement_tasks.py';s=p.read_text(encoding='utf-8')
old="""                cost = self.words((120, 1090, 350, 1130))
                if '神石' in cost or '仙玉' in cost:
                    raise TaskStop('修炼分身存在付费资源消耗：' + cost)
"""
new="""                cost = self.words((120, 1090, 350, 1130)).replace(' ', '')
                quote = re.fullmatch(r'神石[:：]?(\\d+)', cost)
                if not self.cfg.get('allow_star_way_shenshi', False):
                    raise TaskStop('游道修炼未开启神石授权')
                if not quote or int(quote[1]) != 100:
                    raise TaskStop('游道修炼仅授权每次100神石，报价不符：' + cost)
"""
assert old in s,'Current source differs; no changes made'
shutil.copy2(p,folder/'supplement_tasks.before.py')
p.write_text(s.replace(old,new,1),encoding='utf-8');py_compile.compile(str(p),doraise=True)
p=r/'config.json';shutil.copy2(p,folder/'config.before.json');d=json.loads(p.read_text(encoding='utf-8-sig'));d['allow_star_way_shenshi']=True;p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
p=r/'ledgers/oppo-ziling.json';shutil.copy2(p,folder/'ledger.before.json');d=json.loads(p.read_text(encoding='utf-8'))
assert d.get('day')=='2026-10-28',d.get('day')
if d.get('star_way_phase')=='submitted' and not d.get('star_way_done'):
 d.pop('star_way_phase');p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8');print('Removed only verified unclicked star_way submission marker')
print('Authorized only ordinary star-way cultivation at exactly 100 shenshi; other resource policies unchanged')
