import pathlib,sys,time as wall_time,tempfile,json
sys.path.insert(0,'E:/xiuxian')
from star_rewards import StarRewards,TRIBUTE_NAMES,tribute_name
from video_tasks import VideoTasks
import star_rewards
from navigation import Navigation
from daily_tasks import TaskStop

class Seize(StarRewards):
    def __init__(self,left=False,boost=False,flags=None):
        self.ledger=dict(flags or {});self.left=left;self.boost=boost;self.panel=True;self.actions=[]
    def snap(self):pass
    def words(self,roi):
        if roi==(100,950,625,1055):return ('已领取' if self.left else '夺道奖励')+' 修炼加速' if self.panel else ''
        if roi==(110,960,335,1045):return '已领取' if self.left else '夺道奖励'
        if roi==(120,840,610,940):return '59:57 分身修炼加速' if self.boost else ''
        return ''
    def star_open(self,*a):self.panel=False
    def require(self,*a):pass
    def tap(self,*a):self.panel=True
    def text(self,*a):return []
    def video_wait(self,labels,roi):assert any(s in self.words(roi) for s in labels)
    def video_button(self,labels,roi):
        label=labels[0];self.actions.append(label)
        if label=='夺道奖励':self.left=True
        if label=='修炼加速':self.boost=True
    def ledger_save(self):pass
    def record(self,*a):pass
    def video_close(self,*a):self.panel=False

class Tribute(StarRewards,VideoTasks):
    def __init__(self,already=None,fail=None):
        self.ledger={'seize_reward_done':True,'seize_boost_done':True,'star_tributes':dict(already or {})}
        self.server=set(already or {});self.mode='root';self.current=None;self.page=0
        self.claims=[];self.visits=[];self.root_exits=0;self.fail=fail
    def snap(self):pass
    def text(self,roi):
        if self.mode=='root':return []
        label='传參之地' if self.current=='传承之地' else self.current
        return [{'text':label,'confidence':.99,'pos':(360,337)}]
    def require(self,name):assert name=='stars' and self.mode=='root'
    def find(self,name):return name=='stars' and self.mode=='root'
    def seize_rewards(self):assert self.mode=='root'
    def star_tribute_targets(self):
        names=TRIBUTE_NAMES[:4] if self.page==0 else TRIBUTE_NAMES
        return [{'name':n,'pos':(TRIBUTE_NAMES.index(n),600),'has_badge':True} for n in names]
    def tap(self,x,y):self.current=TRIBUTE_NAMES[x];self.mode='city';self.visits.append(self.current)
    def pause_animation(self,*a):pass
    def words(self,*a):return '已供奉' if self.current in self.server else '领取供奉'
    def video_button(self,labels,roi):
        assert labels==('领取供奉',)
        self.claims.append(self.current)
        if self.current!=self.fail:self.server.add(self.current)
    def video_wait(self,labels,roi):
        if not any(s in self.words(roi) for s in labels):raise TaskStop('unconfirmed reward')
    def reward_popup(self,*a):return False
    def video_close(self,*a):self.mode='root'
    def ledger_save(self):pass
    def record(self,*a):pass
    def adb(self,*args):self.page=1 if args[4]==830 else 0
    def log(self,*a):pass
    def back(self,*a):
        self.root_exits+=1

class FastTime:
    monotonic=staticmethod(wall_time.monotonic)
    sleep=staticmethod(lambda seconds:None)
    time=staticmethod(wall_time.time)
original=star_rewards.time;star_rewards.time=FastTime
try:
    s=Seize();s.seize_rewards();assert s.actions==['夺道奖励','修炼加速']
    assert s.ledger['seize_reward_done'] and s.ledger['seize_boost_done']
    s.panel=True;s.left=False;s.seize_rewards();assert len(s.actions)==2,"yellow reward reset must not repeat today's reward"
    s=Seize(left=True);s.seize_rewards();assert s.actions==['修炼加速']
    assert tribute_name('传參之地')=='传承之地' and tribute_name('无关奖励') is None
    t=Tribute()
    t.stars();assert t.claims==list(TRIBUTE_NAMES) and t.root_exits==1
    assert all(t.ledger['star_tributes'].values())
    t=Tribute(already={n:True for n in TRIBUTE_NAMES[:-1]})
    t.stars();assert t.claims==['不灭城'] and t.root_exits==1
    t=Tribute(fail='斗技场')
    t.stars()
    assert t.claims==list(TRIBUTE_NAMES) and t.root_exits==1
    assert not t.ledger['star_tributes'].get('斗技场')
finally:star_rewards.time=original

class Progress(Navigation):
    def __init__(self,folder,complete):
        self.day='2026-10-26';self.ledger_path=pathlib.Path(folder)/'account.json';self.pending={}
        self.ledger={'seize_reward_done':True,'seize_boost_done':True,
                     'star_tributes':{n:True for n in TRIBUTE_NAMES} if complete else {}}
        self.ledger_path.with_suffix('.progress.json').write_text(json.dumps({'day':self.day,'completed':['stars'],'pending':{}}),encoding='utf-8')
    def log(self,*a):pass
with tempfile.TemporaryDirectory() as folder:
    p=Progress(folder,False);p.prepare_daily_progress(True);assert 'stars' in p.daily_progress['completed']
    p=Progress(folder,True);p.prepare_daily_progress(True);assert 'stars' in p.daily_progress['completed']
print('PASS: both seize actions, active boost, daily dedup, five exact collect buttons, last-city scroll; resume preserves completed checkpoint without replaying earlier tasks.')
