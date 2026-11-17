import pathlib,sys,cv2,numpy as np
root=pathlib.Path(__file__).resolve().parents[1]/'outputs'/'太古仙尊实验版'
sys.path.insert(0,str(root))
from assistant import Bot
from navigation import Navigation,ScreenError,DAILY_GROUPS,FINISH_GROUPS
from daily_tasks import TaskStop
from daily_tasks import ApprovedTasks
from palace_tasks import PalaceTasks

# Reproduce the user's actual failed frames, rather than refreshing templates.
b=Bot()
failed=root.parent/'太古仙尊每日助手'/'太古仙尊每日助手'/'logs'
for folder,file,realm in [('20261025-010333-739205','0006.jpg','mortal')]:
    frame=cv2.imdecode(np.frombuffer((failed/folder/file).read_bytes(),np.uint8),1)
    assert b.main_screen(frame)==realm
    assert b.find('sign_entry',frame=frame),'失败截图上的签到应由文字回退识别'
overlay=cv2.imdecode(np.frombuffer((failed/'20261025-010333-739205'/'0003.jpg').read_bytes(),np.uint8),1)
assert b.main_screen(overlay) is None,'境转菜单遮罩不可当作主界面'
assert [g[0] for g in DAILY_GROUPS]==['mortal','heaven','void','yuanji']
assert [g[0] for g in FINISH_GROUPS]==['mortal','heaven','void','yuanji']

class Recovery(Navigation):
    def __init__(self,error):self.calls=0;self.recovered=0;self.error=error
    def task(self):self.calls+=1;raise self.error('测试识别失败')
    def record(self,*a):pass
    def log(self,*a):pass
    def recover_to_main(self,*a):self.recovered+=1;return 'mortal'
r=Recovery(ScreenError);assert r.run_task('task') is False and r.calls==2 and r.recovered==2
r=Recovery(TaskStop);assert r.run_task('task') is False and r.calls==1,'消耗结果不明确时不能盲目重试'

class Timed(ApprovedTasks,PalaceTasks):
    def __init__(self,old_done=False,initial='ready'):
        self.ledger={'palace_court_done':old_done};self.pending={};self.phase=initial;self.claims=0;self.pauses=[]
    def palace_map_button(self,*a):pass
    def wait(self,*a,**k):pass
    def snap(self):pass
    def find(self,name):return self.phase not in ('animating','popup')
    def words(self,*a):return '获得物品' if self.phase=='popup' else ''
    def text(self,*a):
        text='领取奖励' if self.phase=='reward' else ('确定' if self.phase=='popup' else '')
        return [{'text':text,'confidence':1.,'pos':(360,700)}] if text else []
    def click(self,*a):self.phase='animating'
    def tap(self,*a):
        if self.phase=='reward':self.claims+=1;self.phase='popup'
        elif self.phase=='popup':self.phase='claimed'
    def pause_animation(self,n):
        self.pauses.append(n)
        if self.phase=='animating':self.phase='reward'
    def ledger_save(self):pass
    def log(self,*a):pass
    def record(self,*a):pass
    def back(self,*a):assert self.phase=='claimed'
for seconds in (8,10):
    t=Timed();t.timed_palace_task('page','entry','start','palace_court','测试奖励',seconds)
    assert t.claims==1 and t.ledger['palace_court_reward_done']
    assert max(t.pauses)>=seconds-.1,'必须先等动画，再领取'
t=Timed(old_done=True,initial='reward')
t.timed_palace_task('page','entry','start','palace_court','旧记录不应漏领',10)
assert t.claims==1

class Healthy(PalaceTasks):
    def __init__(self):self.ledger={};self.returned=False
    def palace_map_button(self,*a):pass
    def wait(self,*a):pass
    def garden_button(self,*a):return None
    def garden_state(self):return '状态：健康',None
    def record(self,*a):pass
    def back(self,*a):self.returned=True
    def text_button(self,*a):raise AssertionError('健康树不可养护')
h=Healthy();h._palace_garden();assert h.returned

class Harvest(Healthy):
    def __init__(self):super().__init__();self.phase='mature';self.actions=[]
    def garden_button(self,labels):
        if self.phase=='mature' and '收获' in labels:return (1,1)
        if self.phase=='empty' and '种植' in labels:return (2,2)
    def tap(self,x,y):
        self.actions.append((x,y));self.phase='empty' if (x,y)==(1,1) else 'planted'
    def pause_animation(self,*a):pass
    def reward_popup(self,*a):return False
    def ledger_save(self):pass
    def snap(self):pass
    def require(self,*a):pass
    def find(self,*a):return True
    def words(self,*a):return '状态：健康 距离成熟：500年'
h=Harvest();h._palace_garden();assert h.actions==[(1,1),(2,2)] and h.phase=='planted'
for filename in ('v4_mortal_sect','oppo_island'):
    b.frame=cv2.imdecode(np.frombuffer((root.parent.parent/'work'/f'{filename}.png').read_bytes(),np.uint8),1)
    assert b.return_arrow_visible(),filename
b.frame=cv2.imdecode(np.frombuffer((root.parent.parent/'work'/'oppo_mortal_main.png').read_bytes(),np.uint8),1)
assert not b.return_arrow_visible(),'角色头像不可识别成返回箭头'
class SpacedButton(ApprovedTasks):
    def snap(self):pass
    def text(self,*a):return [{'text':'传','confidence':1.,'pos':(344,797)},{'text':'功','confidence':1.,'pos':(376,797)}]
    def log(self,*a):pass
    def tap(self,*p):self.clicked=p
button=SpacedButton();button.text_button('传功',(285,770,435,825));assert button.clicked==(360,797)
print('通过：真实失败截图识别、遮罩保护、四区顺序、有限恢复重试、8/10秒领奖、旧记录漏领修复、健康跳过、收获后重种。')
print('通过：不同背景的返回箭头、头像防误识别、分字传功按钮。')
