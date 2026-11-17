import json,pathlib
p=pathlib.Path('outputs/太古仙尊实验版/quiz_answers.json');d=json.loads(p.read_text(encoding='utf-8'));d['pairs'].pop('飞升后',None);d['pairs']['飞升']='超脱';p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
