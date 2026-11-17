import json,pathlib
p=pathlib.Path('outputs/太古仙尊实验版/config.json');d=json.loads(p.read_text(encoding='utf-8-sig'));d.update(allow_food=True,wander_rounds=100,allow_gamble_lingshi=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
