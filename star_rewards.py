"""Exploration rewards: 夺道奖励, 修炼加速 and existing cities' daily tribute."""
import re
import time
import cv2
import numpy as np
from daily_tasks import TaskStop
from workflow import TRIBUTE_NAMES

def tribute_name(text):
    text=text.replace(' ','').replace('傳','传').replace('传參之地','传承之地')
    if text in TRIBUTE_NAMES:return text
    if re.fullmatch('[\u4e00-\u9fff]{3,4}',text):
        matches=[name for name in TRIBUTE_NAMES if len(name)==len(text)
                 and sum(a!=b for a,b in zip(name,text))<=1]
        if len(matches)==1:return matches[0]
    return None


class StarRewards:
    def tribute_panel_name(self):
        for item in self.text((150,150,570,410)):
            name=tribute_name(item['text'])
            if item['confidence']>=.8 and name in TRIBUTE_NAMES:return name
        return None

    def wait_tribute_panel(self,name):
        end=time.monotonic()+12
        while time.monotonic()<end:
            self.snap()
            if self.skip_blocked_star_event():
                raise TaskStop('探星事件无法处理，已关闭并跳过')
            if self.tribute_panel_name()==name:return
            time.sleep(.3)
        raise TaskStop('地点详情未确认为'+name+'；读取到：'+self.words((150,150,570,410)))

    def skip_blocked_star_event(self):
        body=self.words((80,140,650,1040)).replace(' ','')
        if ('决赛' in body and '手下留情' in body) or ('恶龙' in body and '就这' in body):
            self.video_close('stars')
            self.record('探星事件','跳过','当前事件无法处理，关闭弹窗继续后续任务')
            return True
        return False

    def seize_panel_open(self):
        text=self.words((100,950,625,1055)).replace(' ','')
        return '修炼加速' in text and ('夺道奖励' in text or '已领取' in text)

    def seize_boost_active(self):
        text=self.words((120,840,610,940)).replace(' ','')
        clock=re.search(r'(\d{1,2})[:：](\d{2})',text)
        return bool('分身修炼加速' in text and clock and (int(clock[1]) or int(clock[2])))

    def seize_reward_observed(self):
        receipt=self.words((130,580,610,730)).replace(' ','')
        if '获得' in receipt and any(s in receipt for s in ('玲珑精石','蛮荒遗骨')):return True
        if '已领取' in self.words((110,960,335,1045)).replace(' ',''):return True
        toast=self.words((130,550,610,800)).replace(' ','')
        return '夺道奖励' in toast and any(s in toast for s in ('已领','领取成功'))

    def seize_rewards(self):
        self.snap()
        if not self.seize_panel_open():
            if self.tribute_panel_name():self.video_close('stars')
            self.star_open('探索')
            if self.ledger.get('seize_reward_done') and self.ledger.get('seize_boost_done'):
                self.record('夺道奖励与修炼加速','今日已完成','两项已有分别确认的记录，不重复点击');return
            self.require('stars');self.tap(245,995)
            self.video_wait(('夺道奖励','修炼加速'),(90,900,630,1070))
        left=(110,960,335,1045)
        if not self.ledger.get('seize_reward_done'):
            if not self.seize_reward_observed():
                self.video_button(('夺道奖励',),left)
                end=time.monotonic()+12
                while time.monotonic()<end:
                    self.snap()
                    if self.seize_reward_observed():break
                    time.sleep(.3)
                else:raise TaskStop('夺道奖励未确认按钮已领取或中部已领提示')
            self.ledger['seize_reward_done']=True;self.ledger_save()
            self.record('夺道奖励','今日已领取','已确认按钮已领取或游戏中部明确提示夺道奖励已领')
        else:self.record('夺道奖励','今日已处理','保留今日领取记录')
        self.snap()
        if not self.ledger.get('seize_boost_done'):
            if not self.seize_boost_active():
                self.video_button(('修炼加速',),(400,950,625,1055))
                end=time.monotonic()+12
                while time.monotonic()<end:
                    self.snap()
                    if self.seize_boost_active():break
                    body=self.words((100,450,620,1055))
                    if any(k in body for k in ('消耗神石','消耗仙玉','充值','购买加速')):
                        raise TaskStop('修炼加速出现额外费用，未确认：'+body)
                    time.sleep(.4)
                else:raise TaskStop('修炼加速后未确认分身加速倒计时，保留待处理')
            self.ledger['seize_boost_done']=True;self.ledger_save()
            self.record('修炼加速','今日已开启','已确认分身修炼加速与非零倒计时；无需等待一小时')
        else:self.record('修炼加速','今日已处理','保留今日加速记录')
        self.video_close('stars')

    def seize(self):
        self.seize_rewards();self.back('stars','void_nav')

    def star_tribute_targets(self):
        crop=self.frame[410:915,100:625]
        targets=[]
        for key in ('star_tribute_badge','star_tribute_badge_right'):
            template=self.images[key];h,w=template.shape[:2]
            scores=cv2.matchTemplate(crop,template,cv2.TM_CCOEFF_NORMED)
            for _ in range(12):
                _,score,_,(x,y)=cv2.minMaxLoc(scores)
                if score<.84:break
                scores[max(0,y-28):y+29,max(0,x-23):x+24]=-1
                cx=x+100+w//2;cy=y+410+h//2
                if cy+145>915:continue
                if any(abs(t['pos'][0]-cx)<25 and abs(t['pos'][1]-cy)<25 for t in targets):continue
                name=tribute_name(self.words((cx-160,cy+85,cx+20,cy+145)))
                if name in TRIBUTE_NAMES:targets.append({'name':name,'pos':(cx-78,cy+50),'has_badge':True})
        for item in self.text((100,490,620,910)):
            name=tribute_name(item['text'])
            if item['confidence']<.8 or name not in TRIBUTE_NAMES or any(t['name']==name for t in targets):continue
            x,y=item['pos']
            targets.append({'name':name,'pos':(x,y-80),'has_badge':False})
        return sorted(targets,key=lambda item:(round(item['pos'][1]/20),item['pos'][0]))

    def star_tributes(self):
        self.snap();self.require('stars')
        done=self.ledger.setdefault('star_tributes',{})
        if all(done.get(name) for name in TRIBUTE_NAMES):
            self.record('探星每日供奉','今日已完成','五处5/5已分别确认领取，不重复点击');return
        for _ in range(3):
            self.adb('shell','input','swipe',350,480,350,830,600);time.sleep(.4)
        checked=set();claimed=0;scrolls=0
        for _ in range(16):
            self.snap();self.require('stars')
            targets=[t for t in self.star_tribute_targets() if t['name'] not in checked and not done.get(t['name'])]
            if not targets:
                if scrolls>=4:break
                scrolls+=1
                self.adb('shell','input','swipe',350,830,350,650,650)
                time.sleep(1);continue
            target=targets[0];name=target['name'];checked.add(name)
            try:
                self.tap(*target['pos']);self.pause_animation(.5)
                self.wait_tribute_panel(name)
                self.collect_tribute(name);claimed+=1
            except TaskStop as exc:
                if any(s in str(exc) for s in ('用户已停止','不在前台','前台应用','跨北京时间','分辨率必须')):raise
                self.record('探星供奉'+name,'本处未完成',str(exc))
                self.snap()
                if self.tribute_panel_name():self.video_close('stars')
                elif not self.find('stars'):
                    # A city can open an event instead of its tribute detail.
                    # Close the observed modal; never choose an unknown event option.
                    self.video_close('stars')
        else:raise TaskStop('探星供奉列表检查达到上限，保留未完成')
        total=sum(bool(done.get(name)) for name in TRIBUTE_NAMES)
        self.record('探星每日供奉','本轮结束',f'本次确认{claimed}处；今日已确认{total}/5处；全部处理后再返回')
        missing=[name for name in TRIBUTE_NAMES if not done.get(name)]
        if missing:self.record('探星供奉','跳过未完成地点','本轮不再重试，继续下一任务：'+'、'.join(missing))

    def collect_tribute(self,name):
        self.snap()
        if self.tribute_panel_name()!=name:raise TaskStop('供奉详情未确认为目标地点：'+name)
        roi=(150,700,600,1180)
        body=self.words(roi)
        if not any(s in body for s in ('已供奉','已领取','今日已领取')):
            self.video_button(('领取供奉',),roi)
            self.pause_animation(.6);self.reward_popup('stars')
            self.video_wait(('已供奉','已领取','今日已领取','领取成功'),roi)
        self.ledger.setdefault('star_tributes',{})[name]=True;self.ledger_save()
        self.record('探星供奉'+name,'今日已领取','已在地点详情点击领取供奉并确认结果，或游戏显示本日已供奉')
        self.video_close('stars')
