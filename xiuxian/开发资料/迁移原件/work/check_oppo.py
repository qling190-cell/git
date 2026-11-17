import pathlib,sys,cv2,numpy as np
workspace=pathlib.Path(__file__).resolve().parents[1]
root=workspace/'outputs'/'太古仙尊实验版';sys.path.insert(0,str(root))
from assistant import Bot,Stop
from palace_tasks import PalaceTasks
b=Bot()
assert b.ledger_path==root/'ledgers'/'oppo-ziling.json'
assert b.ledger.get('night_started')==0
assert (root/'ledger.json').read_text(encoding='utf-8').find('"night_started": 15')>=0
for realm in ('mortal','heaven','void','yuanji'):
    p=workspace/'work'/f'oppo_{realm}_main.png'
    frame=cv2.imdecode(np.frombuffer(p.read_bytes(),np.uint8),1)
    assert b.find(realm+'_nav',frame=frame),realm
    assert b.find('main_anchor',frame=frame),realm
overlay=cv2.imdecode(np.frombuffer((workspace/'work'/'oppo_realm_menu.png').read_bytes(),np.uint8),1)
assert not b.find('main_anchor',frame=overlay),'菜单遮罩不应匹配角色主界面'
assert PalaceTasks.garden_action('状态：健康') is None
for state,action in [('状态：虫害','除虫'),('状态：干旱','浇水'),('状态：缺肥','施肥')]:
    assert PalaceTasks.garden_action(state)==action
for state in ('状态：未知','状态：缺水并有虫害'):
    try:PalaceTasks.garden_action(state)
    except Stop:pass
    else:raise AssertionError('未知或冲突的灵树状态应停止')
print('通过：四区主界面及菜单遮罩识别；OPPO/vivo日记隔离；灵树状态决策和未知状态停止。')
