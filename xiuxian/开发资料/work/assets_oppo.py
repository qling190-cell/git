from pathlib import Path
from PIL import Image
import json
r=Path('outputs/太古仙尊实验版');p=r/'assets.json'
meta=json.loads(p.read_text(encoding='utf-8'))
def add(name,src,box,moving=False):
    Image.open('work/'+src+'.png').crop(box).save(r/'assets'/f'{name}.png')
    meta[name]={'box':box,'moving':moving}
add('oppo_mortal_nav','oppo_mortal_main',(238,1000,302,1040))
add('oppo_heaven_nav','oppo_heaven_main',(38,1000,109,1040))
add('oppo_void_nav','oppo_void_main',(331,1000,398,1040))
add('oppo_sign_entry','oppo_heaven_main',(79,177,119,229))
add('oppo_island','oppo_island',(115,22,232,64))
add('oppo_sign_panel','oppo_sign_ready',(137,203,366,261))
add('oppo_sign_ready','oppo_sign_ready',(155,510,281,595))
add('oppo_sign_done','oppo_sign_done',(155,510,281,595))
add('oppo_sign_close','oppo_sign_ready',(605,258,641,296))
add('oppo_sign_draw','oppo_sign_done',(467,519,542,549))
add('yuanji_nav','oppo_yuanji_main',(329,1002,392,1039))
add('palace_map','oppo_palace_map',(139,21,244,65))
add('palace_cultivate_entry','oppo_palace_map',(18,357,50,441),True)
add('palace_court_entry','oppo_palace_map',(147,135,180,214),True)
add('palace_garden_entry','oppo_palace_map',(328,359,359,439),True)
add('palace_cultivate','oppo_cultivate_ready',(132,23,237,68))
add('palace_cultivate_start','oppo_cultivate_ready',(312,646,408,685))
add('palace_cultivate_done','oppo_cultivate_done',(227,661,495,688))
add('palace_court','oppo_court_ready',(125,23,229,64))
add('palace_court_start','oppo_court_ready',(208,658,244,742))
add('palace_court_done','oppo_court_done',(230,662,490,690))
add('palace_garden','oppo_garden_healthy',(127,20,229,67))
add('palace_lamp_claim','oppo_palace_map',(559,842,685,882))
p.write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
cfg=json.loads((r/'config.json').read_text(encoding='utf-8-sig'))
cfg['asset_aliases']={'mortal_nav':'oppo_mortal_nav','heaven_nav':'oppo_heaven_nav','void_nav':'oppo_void_nav','sign_entry':'oppo_sign_entry','island':'oppo_island',**{n:'oppo_'+n for n in ('sign_panel','sign_ready','sign_done','sign_close','sign_draw')}}
cfg.update(rules_version=3,account_label='紫灵')
(r/'config.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2),encoding='utf-8')
