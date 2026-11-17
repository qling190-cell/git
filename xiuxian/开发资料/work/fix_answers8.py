import json,pathlib
p=pathlib.Path('outputs/太古仙尊实验版/quiz_answers.json');d=json.loads(p.read_text(encoding='utf-8'));d['pairs']['破茧']='舍弃';p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
