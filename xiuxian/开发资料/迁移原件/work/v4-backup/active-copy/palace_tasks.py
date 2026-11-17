"""境转导航及天阙每日任务。仅使用明确识别的状态，不补充付费次数。"""
import re
import time
from daily_tasks import TaskStop


class PalaceTasks:
    def realm(self,target):
        if not self.cfg.get('realm_menu'):
            return self._v1_realm(target)
        if target not in ('mortal','heaven','void','yuanji'):raise TaskStop('未知区域：'+target)
        self.wait('mortal_nav','heaven_nav','void_nav','yuanji_nav')
        if self.find(target+'_nav'):return
        self.require('main_anchor');self.tap(32,196)
        end=time.monotonic()+12
        while time.monotonic()<end:
            self.snap();menu=self.words((100,273,348,312))+' '+self.words((0,245,355,317))
            if sum(s in menu for s in ('凡间','仙界','虚空','元极'))>=2:break
            time.sleep(.3)
        else:raise TaskStop('境转菜单未识别，停止切换')
        # 点击文字中心，避开OPPO左侧浮标和背景中的仙职入口。
        self.tap({'mortal':43,'heaven':128,'void':218,'yuanji':309}[target],297)
        self.wait(target+'_nav',seconds=20)
        self.log('境转：'+{'mortal':'凡间','heaven':'仙界','void':'虚空','yuanji':'元极'}[target])

    def palace_open(self):
        if not self.cfg.get('realm_menu'):raise TaskStop('当前配置尚未适配元极/天阙')
        self.realm('yuanji');self.tap(360,995);self.wait('palace_map')

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
        self.palace_open()
        self._palace_lamp();self._palace_cultivate();self._palace_court();self._palace_garden()
        self.back('palace_map','yuanji_nav')

    def palace_lamp(self):
        self.palace_open();self._palace_lamp();self.back('palace_map','yuanji_nav')

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
        self.palace_open();self._palace_lamp();self._palace_cultivate();self.back('palace_map','yuanji_nav')

    def _palace_cultivate(self):
        if self.ledger.get('palace_cultivate_done'):
            self.pending['palace_cultivate']=False;self.record('萦云楼同修','今日已完成','按当前账号记录跳过');return
        self.palace_map_button('palace_cultivate_entry');self.wait('palace_cultivate')
        self.snap();state=self.words((110,505,620,810))
        rewards=[v for v in self.text((100,460,620,810)) if v['confidence']>=.85 and v['text'].replace(' ','') in ('领取','领取奖励')]
        if len(rewards)==1:
            self.tap(*rewards[0]['pos']);time.sleep(.8);self.snap()
            if not self.find('palace_cultivate'):
                body=self.words((80,260,640,1000))
                if '获得物品' not in body:raise TaskStop('同修领奖出现未知页面：'+body)
                self.text_button('确定',(180,620,550,1000));self.wait('palace_cultivate')
            self.snap();self.require('palace_cultivate')
            still=[v for v in self.text((100,460,620,810)) if v['text'].replace(' ','') in ('领取','领取奖励') and v['confidence']>=.85]
            if still:raise TaskStop('同修领取后奖励按钮未消失')
            self.ledger['palace_cultivate_done']=True;self.ledger_save();self.pending['palace_cultivate']=False
            self.record('萦云楼同修','已领奖','已领取完成的同修奖励')
        elif re.search(r'\d{1,2}[:：]\d{2}',state) or '同修中' in state:
            self.pending['palace_cultivate']=True;self.record('萦云楼同修','进行中',state+'；自动收尾等待后领取')
        else:
            self.click('palace_cultivate_start')
            end=time.monotonic()+15
            while time.monotonic()<end:
                self.snap();self.require('palace_cultivate');state=self.words((105,505,630,810))
                if self.find('palace_cultivate_done') or ('今日' in state and ('同修过' in state or '明日再来' in state)):
                    self.ledger['palace_cultivate_done']=True;self.ledger_save();self.pending['palace_cultivate']=False
                    self.record('萦云楼同修','今日已完成','游戏提示今日已同修过');break
                if re.search(r'\d{1,2}[:：]\d{2}',state) or '同修中' in state:
                    self.pending['palace_cultivate']=True;self.record('萦云楼同修','已开始',state+'；自动收尾等待后领取');break
                time.sleep(.4)
            else:raise TaskStop('点击同修后未确认倒计时或今日完成提示')
        self.back('palace_cultivate','palace_map')

    def palace_court(self):
        self.palace_open();self._palace_court();self.back('palace_map','yuanji_nav')

    def _palace_court(self):
        if self.ledger.get('palace_court_done'):
            self.record('朝会殿朝议','今日已完成','按当前账号记录跳过');return
        self.palace_map_button('palace_court_entry');self.wait('palace_court')
        before=self.words((0,1060,720,1245));self.click('palace_court_start')
        end=time.monotonic()+180;confirmed=False
        while time.monotonic()<end:
            self.snap()
            if self.find('palace_court'):
                state=self.words((105,510,630,820));after=self.words((0,1060,720,1245))
                done=self.find('palace_court_done') or ('朝议结束' in state) or (after!=before and '朝议' in after and any(s in after for s in ('获得','结束','愿力','奖励')))
                if done:confirmed=True
                if confirmed and self.find('palace_court_start'):
                    self.ledger['palace_court_done']=True;self.ledger_save()
                    self.record('朝会殿朝议','今日已完成','已确认朝议结束，等待动画完成后返回');break
            time.sleep(.7)
        else:raise TaskStop('朝议动画或结束状态未确认，停止而不重复点击')
        self.back('palace_court','palace_map')

    def palace_garden(self):
        self.palace_open();self._palace_garden();self.back('palace_map','yuanji_nav')

    def garden_state(self):
        state=self.words((485,846,652,890)).replace(' ','')
        s=self.words((255,1002,536,1047)).replace(' ','');m=re.search(r'养护次数[:：]?(\d+)',s)
        if not m:raise TaskStop('御木园自我养护次数未识别：'+s)
        return state,int(m[1])

    @staticmethod
    def garden_action(state):
        if '健康' in state:return None
        matches=[]
        for keywords,name in [(('虫害','害虫','生虫'),'除虫'),(('干旱','缺水','干渴'),'浇水'),(('缺肥','贫瘠','缺乏养分','营养不足'),'施肥')]:
            if any(k in state for k in keywords):matches.append(name)
        if len(matches)!=1:raise TaskStop('御木园灵树状态未知或有歧义：'+state)
        return matches[0]

    def _palace_garden(self):
        if self.ledger.get('palace_garden_done'):
            self.record('御木园','今日已完成','按当前账号记录跳过');return
        self.palace_map_button('palace_garden_entry');self.wait('palace_garden');self.snap()
        state,remaining=self.garden_state()
        if remaining==0:
            self.ledger['palace_garden_done']=True;self.ledger_save();self.record('御木园','今日已完成',state+'，自我养护次数0')
        else:
            action=self.garden_action(state)
            if action is None:self.record('御木园','无需养护',state+'；健康时不随意操作')
            else:
                self.text_button(action,(95,942,625,996))
                end=time.monotonic()+12
                while time.monotonic()<end:
                    self.snap();self.require('palace_garden');after,n=self.garden_state()
                    if n==remaining-1 and '健康' in after:break
                    time.sleep(.4)
                else:raise TaskStop('御木园操作后次数或健康状态未确认')
                self.ledger['palace_garden_done']=True;self.ledger_save();self.record('御木园','完成',state+'→'+action+'→'+after+'；今日只执行一次')
        self.back('palace_garden','palace_map')
