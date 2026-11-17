# -*- coding: utf-8 -*-
import pathlib,json
from PIL import Image
root=pathlib.Path('E:/xiuxian');folder=pathlib.Path(__file__).resolve().parent
meta=json.loads((root/'assets.json').read_text(encoding='utf-8'))
for name,source,box in [('seize_close','seize_native.png',(606,198,643,237)),
                       ('star_tribute_badge','stars_native.png',(291,431,326,481))]:
    Image.open(folder/source).crop(box).save(root/'assets'/f'{name}.png')
    meta[name]={'box':list(box),'moving':True}
(root/'assets.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
p=root/'assistant.py';s=p.read_text(encoding='utf-8')
s=s.replace('from gift_tasks import GiftTasks','from gift_tasks import GiftTasks\nfrom star_rewards import StarRewards')
s=s.replace('NightTasks, GiftTasks, VideoTasks','NightTasks, GiftTasks, StarRewards, VideoTasks')
s=s.replace("'video_tasks','night_engine')","'video_tasks','night_engine','star_rewards')")
s=s.replace("'star_forbidden','all'","'star_forbidden','seize','all'")
p.write_text(s,encoding='utf-8')
p=root/'video_tasks.py';s=p.read_text(encoding='utf-8')
s=s.replace("('sect_npc_close','modal_close_white'","('seize_close','sect_npc_close','modal_close_white'")
start=s.index('    def stars(self):');end=s.index('    def star_orbit(self):',start)
s=s[:start]+'''    def stars(self):
        self.seize_rewards()
        self.star_tributes()
        self.back('stars','void_nav')

'''+s[end:]
p.write_text(s,encoding='utf-8')
p=root/'navigation.py';s=p.read_text(encoding='utf-8')
s=s.replace("'stars':'探星护星与供奉'","'stars':'夺道奖励、修炼加速与供奉'")
needle="        if 'night' in data['completed']:"
s=s.replace(needle,"        if 'stars' in data['completed'] and not (self.ledger.get('seize_reward_done') and self.ledger.get('seize_boost_done')):\n            data['completed'].remove('stars')\n"+needle)
p.write_text(s,encoding='utf-8')
p=root/'ui.py';s=p.read_text(encoding='utf-8')
s=s.replace("'探星护星与供奉': 'stars',","'夺道奖励、加速与供奉': 'stars',\n    '夺道奖励与修炼加速': 'seize',")
p.write_text(s,encoding='utf-8')
print('Seize rewards and boost collection integrated; both daily flags kept separately.')
