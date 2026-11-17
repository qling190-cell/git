from pathlib import Path
import json
p=Path('outputs/太古仙尊实验版/quiz_answers.json');d=json.loads(p.read_text(encoding='utf-8-sig'))
d['pairs'].update({'旋斗':'天度','幽篁':'鸣琴','魂魄':'玄冥','台清':'应变','太上':'应变','三界':'擎拳','天高':'行云','本根':'亿劫','神王':'诵经','落叶':'若谷','于渊':'外游','霹雳':'隐名','九天':'虎贲','自然':'分散','太虚':'浩劫','香传':'玉炉','情所困':'情劫','飞升后':'超脱','入魔':'护法'})
p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
