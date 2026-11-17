import json,pathlib
p=pathlib.Path('outputs/太古仙尊实验版/quiz_answers.json');d=json.loads(p.read_text(encoding='utf-8'));d['pairs']['天地不仁']='以万物';d['pairs'].pop('草木',None);d['pairs']['对木']='灵性';p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
