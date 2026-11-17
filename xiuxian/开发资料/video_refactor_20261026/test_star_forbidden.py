import sys
sys.path.insert(0,'E:/xiuxian')
import forbidden_tasks as f
from workflow import DAILY_GROUPS,shared_parent
from video_tasks import VideoTasks
assert not any('star_orbit' in tasks for _,_,tasks in DAILY_GROUPS)
assert 'star_forbidden' not in DAILY_GROUPS[2][2] and shared_parent('stars','star_way')=='stars'
assert not f.material_shortage('在下实力不足无法斩杀')
assert f.material_shortage('晨露花不足')
class Disabled:
    def record(self,*a):self.result=a
b=Disabled();VideoTasks.star_orbit(b);assert b.result[1]=='已取消'
b=Disabled();VideoTasks.star_forbidden(b);assert b.result[1]=='已取消'
class Fake:
    def __init__(self,state):self.state=state;self.ledger={};self.actions=[]
    def snap(self):pass
    def find(self,*a):return (360,867)
    def pause_animation(self,*a):pass
    def words(self,roi):
        prefix='大苦灭境 '
        if roi==(65,0,390,100):return prefix
        return prefix+{'gift':'禁区修士 需要1000晨露花 给予灵草 委婉回绝',
          'shortage':'晨露花不足 确定','reject':'禁区修士 委婉回绝',
          'fight':'探索者 在下实力不足 战斗 爱莫能助',
          'combat':'战斗造成伤害 退出','done':'今日剩余探索次数0/4'}[self.state]
    def button_positions(self,labels,roi):
        label={'gift':'给予灵草','shortage':'确定','reject':'委婉回绝','fight':'战斗','combat':'退出'}.get(self.state)
        return [(label,)] if label in labels else []
    def tap(self,*point):
        self.actions.append('退出' if point==(360,867) else point[0]);self.state={'gift':'shortage','shortage':'reject','reject':'done','fight':'combat','combat':'done'}.get(self.state,'done')
    def video_button(self,labels,roi):self.tap(labels[0])
    def ledger_save(self):pass
    def record(self,*a):pass
    def wait(self,*a):pass
    def back(self,*a):pass
original=f.close_front;f.close_front=lambda b:b.actions.append('X')
try:
    b=Fake('gift');f.run_forbidden(b);assert b.actions[:3]==['给予灵草','确定','委婉回绝'] and b.ledger['star_forbidden_rules']==1
    b=Fake('fight');f.run_forbidden(b);assert b.actions[:2]==['战斗','退出'] and b.ledger['star_forbidden_rules']==1
finally:f.close_front=original
print('PASS: orbit and forbidden public entries disabled; legacy engine material, shortage, narrative, battle and exit regressions retained')
