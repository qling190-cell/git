import json,pathlib
from PIL import Image
root=pathlib.Path('outputs/太古仙尊实验版'); dest=root/'assets';dest.mkdir(exist_ok=True)
# fixed coordinates are verified by visual matching before each action
spec={
'main_anchor':('heaven',(148,105,311,166)),
'mortal_nav':('mortal',(240,958,311,1044)),
'heaven_nav':('heaven',(28,958,115,1043)),
'void_nav':('main',(317,954,410,1045)),
'sign_panel':('sign_before',(93,282,363,354)),
'sign_entry':('main',(140,170,184,225)),
'sign_ready':('sign_before',(155,510,281,595)),
'sign_done':('sign_after',(155,510,281,595)),
'sign_close':('sign_before',(603,257,642,296)),
'island':('island',(115,22,232,64)),
'island_forbidden':('island_right',(504,179,539,284)),
'island_teaching':('island',(210,198,246,290)),
'island_market':('island',(293,370,330,463)),
'forbidden':('forbidden_list',(104,25,250,65)),
'forbidden_progress_button':('forbidden_list',(225,955,310,1044)),
'forbidden_detail':('forbidden_empty',(292,164,426,201)),
'forbidden_auto':('forbidden_empty',(147,1030,298,1077)),
'forbidden_start':('forbidden_empty',(421,1030,570,1077)),
'forbidden_progress':('progress_rewards',(288,165,434,204)),
'forbidden_empty_progress':('progress_empty',(204,624,521,656)),
'forbidden_reward':('progress_rewards',(272,440,426,490)),
'forbidden_running':('progress_running',(245,467,474,493)),
'bag_full':('claim_24',(305,520,413,545)),
'forbidden_success':('forbidden_dispatched',(197,660,521,693)),
'star':('forbidden_list',(222,414,251,443)),
'travel':('travel',(76,17,166,60)),
'wander_button':('travel',(170,954,257,1045)),
'wander_panel':('wander_ready',(323,177,393,215)),
'wander_start':('wander_ready',(285,1020,434,1064)),
'wander_running':('wander_running',(480,1019,604,1057)),
'wander_map':('wander_ready',(156,728,344,753)),
'wander_food':('wander_ready',(157,779,366,804)),
'heaven_arena':('arena',(211,27,345,61)),
'duel_tab':('arena',(362,23,498,65)),
'duel':('duel',(365,24,494,65)),
'duel_join':('duel_join',(260,627,461,683)),
'duel_joined':('duel',(291,721,429,752)),
'duel_fight':('duel',(239,957,313,1044)),
'battle_exit':('battle_result',(298,849,422,888)),
'duel_reward':('duel_reward',(323,309,398,345)),
'duel_confirm':('duel_reward',(286,888,433,936)),
'market':('market',(126,25,202,66)),
'gamble_button':('market',(330,654,389,829)),
'gamble':('gamble',(326,363,394,399)),
'gamble_cost':('gamble',(289,739,432,765)),
'gamble_start':('gamble',(286,781,435,826)),
'teaching':('teaching',(116,24,223,64)),
'questions':('questions',(290,462,428,501)),
'quiz':('quiz',(327,246,395,281)),
}
meta={}
for name,(src,box) in spec.items():
 im=Image.open(pathlib.Path('work')/(src+'.png')); im.crop(box).save(dest/(name+'.png'))
 meta[name]={'box':box,'moving':name in ['island_forbidden','island_teaching','island_market','forbidden_reward','star','bag_full','battle_exit']}
(root/'assets.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
print(len(meta),'templates')
