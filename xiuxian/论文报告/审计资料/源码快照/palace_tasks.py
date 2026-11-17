"""境转导航及天阙每日任务。仅使用明确识别的状态，不补充付费次数。"""
import re
import time
from daily_tasks import TaskStop
from workflow import PALACE_TASKS


class PalaceTasks:
    def realm(self,target):
        if not self.cfg.get('realm_menu'):return self._v1_realm(target)
        if target not in ('mortal','heaven','void','yuanji'):raise TaskStop('未知区域：'+target)
        for attempt in range(3):
            self.snap()
            current=self.main_screen()
            if not current:current=self.recover_to_main('境转前恢复')
            if current==target:return
            self.tap(32,196)
            end=time.monotonic()+10
            while time.monotonic()<end:
                self.snap()
                if self.menu_visible():break
                time.sleep(.3)
            else:
                self.recover_to_main('境转菜单未打开');continue
            time.sleep(.7)
            self.tap({'mortal':43,'heaven':128,'void':218,'yuanji':309}[target],272)
            end=time.monotonic()+8
            while time.monotonic()<end:
                self.snap()
                if self.main_screen()==target:
                    self.log('境转：'+{'mortal':'凡间','heaven':'仙界','void':'虚空','yuanji':'元极'}[target]);return
                time.sleep(.35)
            self.log('境转尚未切换成功，返回主界面重试')
            self.recover_to_main('境转重试')
        from navigation import ScreenError
        raise ScreenError('境转三次未能到达目标区域：'+target)

    def palace_open(self):
        if not self.cfg.get('realm_menu'):raise TaskStop('当前配置尚未适配元极/天阙')
        self.snap()
        if self.find('palace_map'):return
        self.realm('yuanji');self.tap(360,995);self.wait('palace_map')

    def palace_finish(self):
        self.snap();self.require('palace_map')
        if not getattr(self,'_palace_batch',False):self.back('palace_map','yuanji_nav')

    def palace_map_button(self,name):
        for direction in (None,'left','right'):
            self.snap();self.require('palace_map');p=self.find(name,roi=(0,95,720,790))
            if p:self.tap(*p);return
            if direction in (None,'left'):self.adb('shell','input','swipe',650,550,130,550,500)
            else:self.adb('shell','input','swipe',130,550,650,550,500)
            time.sleep(1)
        self.snap();p=self.find(name,roi=(0,95,720,790))
        if not p:raise TaskStop('天阙建筑入口未识别：'+name)
        self.tap(*p)

    def palace(self):
        if not self.cfg.get('realm_menu'):
            self.record('天阙','跳过','当前渠道尚未配置境转导航');return
        success=True
        tasks=PALACE_TASKS
        for index,task in enumerate(tasks):
            self._palace_batch=index<len(tasks)-1
            try:success=self.run_task(task) and success
            finally:self._palace_batch=False
        return success

    def palace_lamp(self):
        self.palace_open();self._palace_lamp();self.palace_finish()

    def lamp_amount(self):
        s=self.words((25,868,365,911));m=re.search(r'当前积累愿力[:：]?(\d+)/\d+',s.replace(' ',''))
        if not m:raise TaskStop('燃心灯积累愿力未识别：'+s)
        return int(m[1])

    def _palace_lamp(self):
        self.snap();self.require('palace_map');amount=self.lamp_amount()
        if amount>0:
            self.click('palace_lamp_claim')
            end=time.monotonic()+12
            while time.monotonic()<end:
                self.snap();self.require('palace_map')
                if self.lamp_amount()==0:break
                time.sleep(.4)
            else:raise TaskStop('燃心灯收取后积累愿力未归零')
            self.record('天阙燃心灯','已收取',f'收取积累愿力{amount}，已确认归零')
        else:self.record('天阙燃心灯','跳过','积累愿力为0')

    def palace_cultivate(self):
        self.palace_open();self._palace_cultivate();self.palace_finish()

    def pause_animation(self,seconds):
        from pathlib import Path
        end=time.monotonic()+seconds
        while time.monotonic()<end:
            if (Path(__file__).resolve().parent/'STOP').exists():raise TaskStop('用户已停止运行。')
            time.sleep(min(.3,max(0,end-time.monotonic())))
        self.snap()

    def reward_button(self,page):
        self.snap()
        if not self.find(page):return None
        labels=('领取','领取奖励','领奖','完成') if page=='palace_court' else ('领取','领取奖励','领奖')
        hits=self.button_positions(labels,(75,350,650,1275))
        if len(hits)>1:raise TaskStop('奖励按钮不唯一，不猜测点击')
        return hits[0] if hits else None

    def reward_popup(self,page):
        handled=False
        for _ in range(3):
            self.snap();body=self.words((80,250,645,1050))
            context=any(t in body for t in ('获得物品','获得奖励','领取成功','收获成功','朝议奖励','同修奖励'))
            if not context:return handled
            choices=self.button_positions(('确定','确认','领取','领取奖励'),(160,500,570,1030))
            if len(choices)==1:
                self.tap(*choices[0]);self.pause_animation(.5);handled=True
            elif self.find(page):return True
            else:raise TaskStop('奖励弹窗未识别到领取或确认按钮')
        self.wait(page)
        return handled

    def collect_palace_reward(self,page,key,label):
        popup=self.palace_reward_popup(page)
        button=self.reward_button(page)
        if not popup and not button:return False
        if button:
            self.ledger[key+'_phase']='claiming';self.ledger_save()
            self.log(label+'：点击完成/领取，等待奖励并确认')
            self.tap(*button);self.pause_animation(.8)
            end=time.monotonic()+15
            while time.monotonic()<end:
                popup=self.palace_reward_popup(page) or popup
                self.snap()
                if popup and self.find(page) and not self.reward_button(page):break
                time.sleep(.4)
            else:raise TaskStop(label+'点击后尚未确认奖励弹窗，保留待领奖状态')
        self.wait(page)
        if self.reward_button(page):raise TaskStop(label+'领取后奖励按钮未消失')
        self.ledger[key+'_reward_done']=True;self.ledger[key+'_phase']='claimed'
        self.ledger[key+'_done']=True;self.ledger_save();self.pending[key]=False
        self.record(label,'已领奖','已点击领取并确认奖励到账页面；随后继续下一任务')
        return True

    def palace_reward_popup(self,page):
        """A reward is confirmed only after tapping its actual confirmation."""
        self.snap();body=self.words((70,200,650,1050)).replace(' ','')
        contexts=('获得物品','获得奖励','领取成功','朝议奖励','同修奖励')
        if not any(s in body for s in contexts):return False
        # Historical chat says "获得奖励" too. A real modal must have its own
        # confirmation button; the page's bottom "领取" is a separate action.
        if not self.button_positions(('确定','确认'),(120,400,610,1200)):return False
        end=time.monotonic()+10
        while time.monotonic()<end:
            self.snap()
            choices=self.button_positions(('确定','确认'),(120,400,610,1200))
            if len(choices)==1:
                self.tap(*choices[0]);self.pause_animation(.5)
                self.snap()
                remaining=self.button_positions(('确定','确认'),(120,400,610,1200))
                if not remaining and self.find(page):return True
            elif len(choices)>1:raise TaskStop('天阙奖励确认按钮不唯一，不退出任务')
            time.sleep(.3)
        raise TaskStop('天阙奖励弹窗尚未确认，不返回地图')

    def timed_palace_task(self,page,entry,start,key,label,seconds):
        self.palace_map_button(entry);self.wait(page)
        # Always inspect the actual page first: v3 completion flags did not prove
        # a reward had been claimed and must not suppress an unclaimed reward.
        if self.collect_palace_reward(page,key,label):
            self.back(page,'palace_map');return
        if self.ledger.get(key+'_reward_done'):
            self.pending[key]=False;self.record(label,'今日已完成','本日已确认领取奖励，当前无可领按钮')
            self.back(page,'palace_map');return
        phase=self.ledger.get(key+'_phase')
        self.snap();start_visible=bool(self.find(start))
        if phase not in ('started','claiming') or start_visible:
            self.ledger[key+'_phase']='started';self.ledger[key+'_start_time']=time.time();self.ledger_save()
            self.click(start);self.snap()
            hint=self.words((75,250,650,1050)).replace(' ','')
            already=('今日' in hint or '今天' in hint) and any(x in hint for x in ('明日再来','已同修过','朝议结束','已经','已完成','用尽','用完','上限','已朝议','已同修'))
            self.ledger[key+'_already_hint']=already;self.ledger_save()
        elapsed=time.time()-float(self.ledger.get(key+'_start_time',0))
        remaining=max(0,seconds-elapsed)
        if remaining:
            self.log(label+f'：等待约{remaining:.0f}秒，之后先领奖')
            self.pause_animation(remaining)
        end=time.monotonic()+60
        while time.monotonic()<end:
            if self.collect_palace_reward(page,key,label):break
            self.snap()
            if self.ledger.get(key+'_already_hint') and self.find(page) and self.find(start):
                self.ledger[key+'_reward_done']=True;self.ledger[key+'_done']=True;self.ledger[key+'_phase']='already_done';self.ledger_save()
                self.pending[key]=False;self.record(label,'今日已完成','游戏提示今日已结束，等待后确认无待领奖励');break
            time.sleep(.5)
        else:
            self.pending[key]=True
            self.record(label,'等待领奖','动画等待已结束，尚未出现可确认的领取按钮；后续只检查领奖，不重复启动')
            raise TaskStop(label+'等待完成/领取按钮超时，未领奖不主动返回地图')
        self.back(page,'palace_map')

    def _palace_cultivate(self):
        self.timed_palace_task('palace_cultivate','palace_cultivate_entry','palace_cultivate_start','palace_cultivate','萦云楼同修',8)

    def palace_court(self):
        self.palace_open();self._palace_court();self.palace_finish()

    def _palace_court(self):
        self.timed_palace_task('palace_court','palace_court_entry','palace_court_start','palace_court','朝会殿朝议',10)

    def palace_garden(self):
        self.palace_open();self._palace_garden();self.palace_finish()

    def garden_state(self):
        self.snap();self.require('palace_garden')
        state=self.words((485,846,652,890)).replace(' ','')
        s=self.words((255,1002,536,1047)).replace(' ','');m=re.search(r'养护次数[:：]?(\d+)',s)
        return state,int(m[1]) if m else None

    @staticmethod
    def garden_action(state):
        clean=state.replace('状态','').replace('：','').replace(':','').replace(' ','')
        if clean=='健康':return None
        matches=[]
        rules=[(('虫害','害虫','生虫','虫蛀'),'除虫'),(('干旱','缺水','干渴','干燥','干涸'),'浇水'),(('缺肥','贫瘠','缺乏养分','营养不足','肥力不足','营养不良'),'施肥')]
        for keywords,name in rules:
            if any(k in state for k in keywords):matches.append(name)
        if len(matches)!=1:raise TaskStop('御木园灵树状态未知或有歧义：'+state)
        return matches[0]

    def garden_button(self,labels):
        self.snap();self.require('palace_garden')
        hits=self.button_positions(labels,(65,320,655,1060))
        if len(hits)>1:raise TaskStop('御木园按钮有歧义：'+str(labels))
        return hits[0] if hits else None

    def garden_replant(self):
        button=self.garden_button(('种植','重新种植','种下灵树'))
        if not button:raise TaskStop('御木园收获后未找到重新种植按钮，已保留现场')
        self.tap(*button);self.pause_animation(.7);self.snap()
        if not self.find('palace_garden'):
            body=self.words((75,350,645,920))
            if not any(k in body for k in ('种植','灵树')) or any(k in body for k in ('仙玉','神石','充值','购买')):
                raise TaskStop('重新种植出现未确认费用或未知弹窗：'+body)
            self.text_button('确定',(150,600,590,1000));self.wait('palace_garden')
        self.snap();self.require('palace_garden')
        state=self.words((45,830,675,1048))
        if '健康' not in state and '距离成熟' not in state:raise TaskStop('重新种植结果未确认')
        self.ledger['palace_garden_harvest_phase']='planted';self.ledger_save()
        self.record('御木园','已收获并重新种植','已确认新树状态或成熟倒计时')

    def _palace_garden(self):
        self.palace_map_button('palace_garden_entry');self.wait('palace_garden')
        harvest=self.garden_button(('收获',))
        if harvest:
            self.ledger['palace_garden_harvest_phase']='harvesting';self.ledger_save()
            self.tap(*harvest);self.pause_animation(.7);self.reward_popup('palace_garden');self.wait('palace_garden')
            self.garden_replant();self.back('palace_garden','palace_map');return
        if self.garden_button(('种植','重新种植','种下灵树')):
            self.garden_replant();self.back('palace_garden','palace_map');return
        state,remaining=self.garden_state()
        # Healthy is checked before quota parsing, per the requested daily rule.
        action=self.garden_action(state)
        if action is None:
            self.record('御木园','健康跳过','灵树健康，直接返回，不点击养护')
        elif remaining==0 or self.ledger.get('palace_garden_action_done'):
            self.record('御木园','今日无养护机会',state+'；不购买额外次数')
        else:
            if remaining is None:raise TaskStop('异常树的自我养护次数未确认，不执行消耗')
            import cv2
            import numpy as np
            hsv=cv2.cvtColor(self.frame[845:891,555:640],cv2.COLOR_BGR2HSV)
            red=cv2.countNonZero(cv2.inRange(hsv,np.array([0,80,80]),np.array([12,255,255])))+cv2.countNonZero(cv2.inRange(hsv,np.array([168,80,80]),np.array([179,255,255])))
            if red<8:raise TaskStop('灵树文字显示异常但红色状态未确认：'+state)
            self.text_button(action,(95,942,625,996))
            end=time.monotonic()+12
            while time.monotonic()<end:
                after,n=self.garden_state()
                if n==remaining-1 and self.garden_action(after) is None:break
                time.sleep(.4)
            else:raise TaskStop('御木园操作后次数或健康状态未确认')
            self.ledger['palace_garden_action_done']=True;self.ledger_save()
            self.record('御木园','完成',state+'→'+action+'→'+after+'；今日只养护一次')
        self.back('palace_garden','palace_map')
