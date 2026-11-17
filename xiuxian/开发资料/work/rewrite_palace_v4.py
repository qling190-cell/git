from pathlib import Path
p=Path('outputs/太古仙尊实验版/palace_tasks.py')
s=p.read_text(encoding='utf-8')
s=s.replace('self._palace_lamp();self._palace_cultivate();self._palace_court();self._palace_garden()', 'self._palace_garden();self._palace_cultivate();self._palace_court();self._palace_lamp()')
a=s.index('    def _palace_cultivate(self):');b=s.index('    def palace_court(self):',a)
s=s[:a]+'''    def pause_animation(self,seconds):
        from pathlib import Path
        end=time.monotonic()+seconds
        while time.monotonic()<end:
            if (Path(__file__).resolve().parent/'STOP').exists():raise TaskStop('用户已停止运行。')
            time.sleep(min(.3,max(0,end-time.monotonic())))
        self.snap()

    def reward_button(self,page):
        self.snap()
        if not self.find(page):return None
        hits=[v for v in self.text((75,350,650,1055)) if v['confidence']>=.85 and v['text'].replace(' ','') in ('领取','领取奖励','领奖')]
        if len(hits)>1:raise TaskStop('奖励按钮不唯一，不猜测点击')
        return hits[0]['pos'] if hits else None

    def reward_popup(self,page):
        self.snap();body=self.words((80,250,645,1050))
        if not any(t in body for t in ('获得物品','获得奖励','领取成功')):return False
        choices=[v for v in self.text((180,580,550,1030)) if v['confidence']>=.85 and v['text'].replace(' ','') in ('确定','确认')]
        if len(choices)==1:self.tap(*choices[0]['pos']);self.wait(page)
        elif not self.find(page):raise TaskStop('奖励弹窗未识别到确认按钮')
        return True

    def collect_palace_reward(self,page,key,label):
        popup=self.reward_popup(page)
        button=self.reward_button(page)
        if not popup and not button:return False
        if button:
            self.ledger[key+'_phase']='claiming';self.ledger_save()
            self.tap(*button);self.pause_animation(.8);self.reward_popup(page)
        self.wait(page)
        if self.reward_button(page):raise TaskStop(label+'领取后奖励按钮未消失')
        self.ledger[key+'_reward_done']=True;self.ledger[key+'_phase']='claimed'
        self.ledger[key+'_done']=True;self.ledger_save();self.pending[key]=False
        self.record(label,'已领奖','已点击领取并确认奖励到账页面；随后继续下一任务')
        return True

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
        if phase not in ('started','claiming'):
            self.ledger[key+'_phase']='started';self.ledger[key+'_start_time']=time.time();self.ledger_save()
            self.click(start);self.snap()
            hint=self.words((95,500,635,820))
            already=('今日' in hint or '今天' in hint) and any(x in hint for x in ('明日再来','已同修过','朝议结束','已经'))
            self.ledger[key+'_already_hint']=already;self.ledger_save()
        elapsed=time.time()-float(self.ledger.get(key+'_start_time',0))
        remaining=max(0,seconds-elapsed)
        if remaining:
            self.log(label+f'：等待约{remaining:.0f}秒，之后先领奖')
            self.pause_animation(remaining)
        end=time.monotonic()+15
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
        self.back(page,'palace_map')

    def _palace_cultivate(self):
        self.timed_palace_task('palace_cultivate','palace_cultivate_entry','palace_cultivate_start','palace_cultivate','萦云楼同修',8)

'''+s[b:]
a=s.index('    def _palace_court(self):');b=s.index('    def palace_garden(self):',a)
s=s[:a]+'''    def _palace_court(self):
        self.timed_palace_task('palace_court','palace_court_entry','palace_court_start','palace_court','朝会殿朝议',10)

'''+s[b:]
a=s.index('    def garden_state(self):')
s=s[:a]+'''    def garden_state(self):
        self.snap();self.require('palace_garden')
        state=self.words((485,846,652,890)).replace(' ','')
        s=self.words((255,1002,536,1047)).replace(' ','');m=re.search(r'养护次数[:：]?(\\d+)',s)
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
        hits=[v for v in self.text((65,320,655,1060)) if v['confidence']>=.85 and v['text'].replace(' ','') in labels]
        if len(hits)>1:raise TaskStop('御木园按钮有歧义：'+str(labels))
        return hits[0]['pos'] if hits else None

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
'''
p.write_text(s,encoding='utf-8')
