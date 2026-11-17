"""太古仙尊 vivo / LDPlayer 720x1280. Run from the logged-in main screen."""
import argparse
import datetime as dt
import json
import msvcrt
import pathlib
import re
import subprocess
import sys
import time

import cv2
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent
CLICK_LABELS={
 'sign_entry':'签到入口','sign_ready':'免费签到','sign_close':'关闭签到',
 'forbidden_progress_button':'禁地进度','forbidden_auto':'自动选择弟子','forbidden_start':'开始禁地探索','forbidden_reward':'领取禁地奖励',
 'wander_button':'神游','wander_start':'开始神游','duel_tab':'斗法','duel_join':'加入斗法','duel_fight':'参加斗法','duel_confirm':'确认斗法奖励',
 'gamble_button':'博戏','gamble_start':'试试手气','sword_match':'匹配论剑对手','sword_challenge':'挑战论剑对手',
 'battle_exit':'结束战斗','guard_one':'单人护法','practice_start':'开始门派练功','night_claim':'领取夜猎奖励','night_start':'开始夜猎',
 'family_claim':'领取征收奖励','family_start':'开始征收','hunt_start':'检查仙猎消耗','hunt_cancel':'取消仙猎消耗'
}
sys.path.insert(0, str(ROOT / 'vendor'))
from rapidocr_onnxruntime import RapidOCR

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

class Stop(RuntimeError):
    pass

class Bot:
    def __init__(self):
        self.cfg = json.loads((ROOT/'config.json').read_text(encoding='utf-8-sig'))
        self.meta = json.loads((ROOT/'assets.json').read_text(encoding='utf-8'))
        self.images = {n: cv2.imdecode(np.frombuffer((ROOT/'assets'/f'{n}.png').read_bytes(), np.uint8), 1) for n in self.meta}
        self.ocr = RapidOCR(intra_op_num_threads=2, inter_op_num_threads=2)
        self.out = ROOT/'logs'/dt.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        self.out.mkdir(parents=True)
        self.seq = 0
        self.report = []
        self.frame = None
        self.last_saved=0
        self.save_next=True
        self.pending={}
        self.day=dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).date().isoformat()
        ledger_path=ROOT/'ledger.json'
        self.ledger=json.loads(ledger_path.read_text(encoding='utf-8-sig')) if ledger_path.exists() else {}
        if self.ledger.get('day')!=self.day:self.ledger={'day':self.day,'night_started':0}

    def log(self, message):
        print(message, flush=True)
        with (self.out/'events.txt').open('a', encoding='utf-8') as f:
            f.write(f'{dt.datetime.now():%H:%M:%S} {message}\n')

    def adb(self, *parts):
        return subprocess.check_output([self.cfg['adb'], '-s', self.cfg['device'], *map(str,parts)], timeout=20)

    def snap(self):
        if (ROOT/'STOP').exists():raise Stop('用户已停止运行。')
        s = self.adb('shell','dumpsys','activity','activities').decode('utf-8','replace')
        if not any(self.cfg['package']+'/' in line for line in s.splitlines() if 'mResumedActivity' in line):
            raise Stop('游戏不在前台，停止操作。')
        raw = self.adb('exec-out','screencap','-p')
        self.frame = cv2.imdecode(np.frombuffer(raw,np.uint8),1)
        if self.frame is None or self.frame.shape[:2] != (1280,720):
            raise Stop('分辨率必须为720×1280。')
        if self.save_next or time.monotonic()-self.last_saved>=10:
            self.save_frame()
        return self.frame

    def save_frame(self):
        if self.frame is None:return
        self.seq+=1
        (self.out/f'{self.seq:04}.jpg').write_bytes(cv2.imencode('.jpg',self.frame,[cv2.IMWRITE_JPEG_QUALITY,90])[1].tobytes())
        self.last_saved=time.monotonic();self.save_next=False

    def find(self, name, frame=None, roi=None):
        frame = self.frame if frame is None else frame
        spec = self.meta[name]
        x1,y1,x2,y2 = spec['box']
        if roi is None:
            roi = (0,0,720,1280) if spec['moving'] else (max(0,x1-8),max(0,y1-8),min(720,x2+8),min(1280,y2+8))
        a,b,c,d = roi
        t = self.images[name]; h,w = t.shape[:2]
        crop = frame[b:d,a:c]
        if crop.shape[0]<h or crop.shape[1]<w:
            return None
        _,score,_,pos = cv2.minMaxLoc(cv2.matchTemplate(crop,t,cv2.TM_CCOEFF_NORMED))
        x,y = pos; sample=crop[y:y+h,x:x+w]
        # Correlation alone also matches dimmed backgrounds. Check absolute color too.
        error = float(np.mean(np.abs(sample.astype(float)-t.astype(float))))
        if score < .94 or error > 15:
            return None
        return a+x+w//2,b+y+h//2

    def text(self, roi=(0,0,720,1280), frame=None):
        im = self.frame if frame is None else frame
        x,y,r,b=roi
        crop=im[y:b,x:r]
        if crop.shape[0]<180:
            crop=cv2.resize(crop,None,fx=2,fy=2); scale=2
        else:
            scale=1
        result,_=self.ocr(crop)
        return [{'text':s,'confidence':float(conf),'pos':(int(x+np.mean([p[0] for p in box])/scale),int(y+np.mean([p[1] for p in box])/scale))} for box,s,conf in (result or [])]

    def words(self, roi=(0,0,720,1280), frame=None):
        return ' '.join(v['text'] for v in self.text(roi,frame) if v['confidence']>=.8)

    def line(self,roi):
        x,y,r,b=roi
        result,_=self.ocr(self.frame[y:b,x:r],use_det=False,use_cls=False)
        return ''.join(s for s,confidence in (result or []) if confidence>=.9)

    def require(self, name):
        if not self.find(name):
            raise Stop(f'当前页面不符合预期：{name}。已保存截图。')

    def tap(self,x,y):
        if (ROOT/'STOP').exists():raise Stop('用户已停止运行。')
        if dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).date().isoformat()!=self.day:
            raise Stop('已跨北京时间日期，停止，避免自动消耗下一天的资源。')
        # Recheck the foreground immediately before dispatching any input.
        s=self.adb('shell','dumpsys','activity','activities').decode('utf-8','replace')
        if not any(self.cfg['package']+'/' in z for z in s.splitlines() if 'mResumedActivity' in z):
            raise Stop('点击前发现前台应用变化，停止。')
        self.save_frame()
        self.adb('shell','input','tap',x,y)
        self.save_next=True
        time.sleep(.45)

    def wait_words(self,page,roi,predicate,seconds=12):
        end=time.monotonic()+seconds
        while time.monotonic()<end:
            self.snap();self.require(page)
            text=self.words(roi)
            if predicate(text):return text
            time.sleep(.4)
        raise Stop('页面文字未出现预期变化：'+page)

    def practice(self):
        if not self.cfg.get('allow_practice_lingshi',True):
            self.record('门派练功','跳过','未启用1000灵石消耗');return
        self.realm('mortal');self.tap(270,995);self.wait('mortal_sect')
        self.tap(70,995);self.wait('practice')
        if self.find('practice_running'):
            self.record('门派练功','进行中','已在练功，不重复启动')
        elif self.find('practice_start') and self.find('practice_cost'):
            self.click('practice_start');self.wait('practice_running')
            self.record('门派练功','已启动','消耗1000灵石，已确认修炼中；不购买掌门传功次数')
        else:raise Stop('门派练功状态未知')
        self.close('practice',605,270,'mortal_sect');self.back('mortal_sect','mortal_nav')

    def night(self):
        self.realm('void');self.tap(650,995);self.wait('journey');self.tap(360,995);self.wait('night')
        claimed=0
        # Inspect destinations to collect completed hunts. Selecting a destination has no cost.
        for row in range(5):
            for col in range(2):
                self.snap();self.require('night');self.tap(238+238*col,371+70*row)
                self.snap()
                if self.find('night_claim'):
                    self.click('night_claim')
                    self.wait_words('night',(105,980,605,1120),lambda s:'夜猎收获' not in s)
                    claimed+=1
        # Keep the previously established destination; no relocation or new occupation.
        self.snap();self.require('night');self.tap(478,650);self.snap();self.require('night')
        selection=self.words((110,715,525,785))
        if '丽晶异域' not in selection:raise Stop('夜猎目标未确认为丽晶异域')
        state=self.words((100,970,610,1125))
        if '剩余夜猎' in state or '本轮夜猎' in state:
            self.pending['night']=True
            self.record('虚空夜猎','进行中',f'已领取{claimed}处奖励；保留现有夜猎任务')
        elif self.find('night_start'):
            self.pending['night']=False
            budget=max(0,15-int(self.ledger.get('night_started',0)))
            condition=self.frame[856:962,160:570];hsv=cv2.cvtColor(condition,cv2.COLOR_BGR2HSV)
            red=cv2.countNonZero(cv2.inRange(hsv,np.array([0,130,130]),np.array([10,255,255])))
            green=cv2.countNonZero(cv2.inRange(hsv,np.array([35,100,80]),np.array([90,255,255])))
            if not budget:
                self.record('虚空夜猎','今日上限',f'已领取{claimed}处奖励；今天已使用15次夜猎预算，不继续消耗共享征战次数')
            elif red>20 or green<50:
                self.record('虚空夜猎','条件不足',f'已领取{claimed}处奖励；不调整驻扎弟子')
            else:
                # Use the game max control then cap to 15 to preserve shared expedition attempts.
                self.tap(541,1009);self.snap();self.require('night')
                value=self.line((270,985,365,1033))
                if not value.isdigit():raise Stop('无法读取夜猎轮数：'+value)
                maximum=int(value);count=min(maximum,budget)
                for _ in range(maximum-count):
                    self.snap();self.require('night');self.tap(179,1009)
                self.click('night_start')
                self.wait_words('night',(95,975,610,1135),lambda s:'剩余夜猎' in s or '本轮夜猎' in s)
                self.ledger['night_started']=int(self.ledger.get('night_started',0))+count
                (ROOT/'ledger.json').write_text(json.dumps(self.ledger,ensure_ascii=False,indent=2),encoding='utf-8')
                self.pending['night']=True
                self.record('虚空夜猎','已启动',f'领取{claimed}处奖励，新启动丽晶异域{count}轮；消耗共享征战次数')
        else:
            self.record('虚空夜猎','未启动',f'已领取{claimed}处奖励；当前不是可启动状态')
        self.close('night',628,166,'journey');self.back('journey','void_nav')

    def stars(self):
        self.realm('void');self.tap(213,995);self.wait('stars');self.tap(437,118);self.wait('stars_locked','stars')
        time.sleep(.6);self.snap()
        locked=self.words((300,265,355,419))
        if '未知' in locked:
            self.record('探星禁区供奉','未解锁','当前vivo号禁区显示未知；不使用录屏高等级账号的坐标领取')
        else:
            self.record('探星禁区供奉','需要适配','当前禁区状态与本次已验证模板不同')
        self.back('stars','void_nav')

    def family(self):
        self.realm('void');self.tap(360,995);self.wait('immortal_home')
        self.tap(530,945);self.wait('family');self.tap(360,995);self.wait('family_panel')
        claimed=0;started=0;self.pending['family']=False
        # First resolve any previously selected collection, without changing its destination.
        if self.find('family_claim'):
            self.click('family_claim');self.wait_gone('family_panel','family_claim');claimed+=1
        self.snap();self.require('family_panel')
        text=self.line((278,1046,439,1086));m=re.search(r'征收\s*(\d+)次',text)
        if not m:raise Stop('无法读取家族征收次数：'+text)
        state=self.words((105,984,605,1044))
        if not self.find('family_start') and re.search(r'\d{2}[:：]\d{2}',state):
            self.pending['family']=True
        elif int(m[1])==0:
            pass
        elif not self.find('family_start'):
            raise Stop('家族征收状态未知：'+state)
        else:
            if int(m[1])>0:
                self.tap(230,683);self.snap();self.require('family_panel')
                selected=self.words((92,899,470,940))
                if '九尾狐宗' not in selected:raise Stop('家族征收目标未确认：'+selected)
                self.click('family_start');started+=1
                self.wait_words('family_panel',(105,984,605,1044),lambda s:bool(re.search(r'\d{2}[:：]\d{2}',s)))
                self.pending['family']=True
        self.record('家族征收','进行中' if self.pending['family'] else '本日完成',f'新增征收{started}次，领取{claimed}次；自动收尾可等待后续征收')
        self.close('family_panel',622,206,'family');self.back('family','immortal_home');self.back('immortal_home','void_nav')

    def transfer(self):
        # Cultivation is outside the approved food/lingshi budget. Inspect only.
        self.island();self.island_label('island_teaching');self.wait('teaching');self.tap(194,738);self.wait('guard')
        costs=self.words((126,787,598,829))
        if '修为' not in costs:raise Stop('传功消耗类型未确认，停止。')
        self.record('宗门传功','按资源范围跳过',costs+'；未消耗修为')
        self.close('guard',615,404,'teaching');self.back('teaching','island');self.back('island','heaven_nav')

    def hunt(self):
        self.realm('heaven');self.tap(650,995);self.wait('heaven_travel')
        self.tap(500,995);self.wait('secrets');self.tap(360,600);self.wait('hunt')
        if self.find('hunt_start'):
            self.click('hunt_start');self.wait('hunt_cost')
            text=self.words((115,577,607,680))
            self.click('hunt_cancel');self.wait('hunt')
            self.record('仙猎','按资源范围跳过',text+'；未确认消耗')
        else:
            self.record('仙猎','未启动','保留当前状态；不花木材、陨铁或其他材料')
        self.close('hunt',610,184,'secrets');self.back('secrets','heaven_travel');self.back('heaven_travel','heaven_nav')

    def click(self,name,roi=None):
        self.snap()
        p=self.find(name,roi=roi)
        if p is None:
            raise Stop(f'未识别按钮：{name}')
        self.log('点击：'+CLICK_LABELS.get(name,name))
        self.tap(*p)

    def wait(self,*names,seconds=12):
        end=time.monotonic()+seconds
        while time.monotonic()<end:
            self.snap()
            for n in names:
                if self.find(n):
                    return n
            time.sleep(.5)
        raise Stop('等待页面超时：'+','.join(names))

    def wait_gone(self,page,name,seconds=12):
        end=time.monotonic()+seconds
        while time.monotonic()<end:
            self.snap();self.require(page)
            if not self.find(name):return
            time.sleep(.5)
        raise Stop('操作后按钮未变化，停止：'+name)

    def back(self,page,target):
        self.snap();self.require(page);self.tap(35,40);self.wait(target)

    def close(self,page,x,y,target):
        self.snap();self.require(page);self.tap(x,y);self.wait(target)

    def realm(self,target):
        self.wait('mortal_nav','heaven_nav','void_nav')
        for _ in range(3):
            if self.find(target+'_nav'):
                return
            self.require('main_anchor');self.tap(96 if target=='void' else 32,196)
            # Switching realms has a long visual transition.
            time.sleep(1.8)
            self.wait('mortal_nav','heaven_nav','void_nav')
        raise Stop('无法切换到'+target)

    def island(self):
        self.realm('heaven');self.tap(70,995);self.wait('island')

    def island_label(self,name):
        for direction in (None,'left','right'):
            self.snap();self.require('island')
            p=self.find(name,roi=(0,75,720,920))
            if p:
                self.tap(*p);return
            if direction is None or direction=='left':
                self.adb('shell','input','swipe',650,550,130,550,450)
            else:
                self.adb('shell','input','swipe',130,550,650,550,450)
            time.sleep(.8)
        self.snap();p=self.find(name,roi=(0,75,720,920))
        if not p:raise Stop('宗门入口未找到：'+name)
        self.tap(*p)

    def record(self,task,status,detail):
        self.report.append(dict(task=task,status=status,detail=detail))
        self.log(f'[{task}] {status}：{detail}')
        (self.out/'report.json').write_text(json.dumps(self.report,ensure_ascii=False,indent=2),encoding='utf-8')

    def battle(self,target):
        # Battles close automatically. Waiting avoids tapping a page behind a fading dialog.
        try:
            self.wait(target,seconds=30)
        except Stop:
            self.snap()
            if not self.find('battle_exit'):raise
            self.click('battle_exit');self.wait(target)

    def sword_remaining(self):
        whole=self.line((210,1017,560,1050))
        if '购买' in whole:
            return 0
        text=self.line((280,1018,445,1048))
        m=re.search(r'次数[:：]?\s*(\d+)',text)
        if not m:raise Stop('无法读取论剑次数：'+text)
        return int(m[1])

    def sword(self):
        self.wait('main_anchor');self.tap(662,152);self.wait('sword')
        done=0
        for _ in range(10):
            self.snap();self.require('sword')
            remaining=self.sword_remaining()
            if not remaining:break
            self.click('sword_match');self.wait('sword_opponents')
            rows=[]
            for top,bottom,y in [(270,374,322),(386,490,437),(500,604,551),(616,720,667),(731,835,782)]:
                s=self.words((293,top,486,bottom));m2=re.search(r'战力[:：]?\s*(\d+)',s)
                if not m2:raise Stop('无法读取论剑对手战力：'+s)
                rows.append((int(m2[1]),y))
            # Prefer the highest listed rank among opponents weaker than this character.
            own=self.words((300,1127,528,1166));own_m=re.search(r'战力[:：]?\s*(\d+)',own)
            # Own power is behind a dark overlay; OCR can still read it. If missing, choose lowest power.
            viable=[r for r in rows if own_m and r[0]<int(own_m[1])]
            power,y=(viable[0] if viable else min(rows))
            self.click('sword_challenge',roi=(495,y-28,625,y+28))
            end=time.monotonic()+120;verified=False
            while time.monotonic()<end:
                time.sleep(.5);self.snap()
                if not self.find('sword'):continue
                if self.sword_remaining()==remaining-1:
                    verified=True;break
            if not verified:raise Stop('论剑次数未减少，停止。')
            done+=1
        self.record('论剑','完成本次处理',f'完成{done}场，不购买次数，不花论剑币')
        self.back('sword','main_anchor')

    def guard(self):
        self.island();self.island_label('island_teaching');self.wait('teaching')
        self.tap(527,735)
        if self.wait('guard','guard_none')=='guard_none':
            self.record('宗门护法','已完成','当前没有弟子需要护法')
            self.back('teaching','island');self.back('island','heaven_nav');return
        done=0
        for _ in range(45):
            self.snap();self.require('guard')
            names=self.text((100,556,600,600))
            names=[n for n in names if n['confidence']>.85 and len(n['text'])>=2]
            if not names:break
            before='|'.join(n['text'] for n in names)
            x=names[0]['pos'][0]
            self.tap(x,525);self.click('guard_one');self.battle('guard')
            after='|'.join(n['text'] for n in self.text((100,556,600,600)) if n['confidence']>.85)
            if before==after:raise Stop('护法后弟子列表未变化，停止。')
            done+=1
        self.record('宗门护法','完成本次处理',f'免费逐个护法{done}名弟子；不使用付费全部护法')
        self.close('guard',615,404,'teaching');self.back('teaching','island');self.back('island','heaven_nav')

    def quiz(self):
        self.island();self.island_label('island_teaching');self.wait('teaching')
        self.tap(359,738)
        if self.wait('questions','quiz_none')=='quiz_none':
            self.record('宗门答疑','本日完成','游戏提示没有疑惑了')
            self.back('teaching','island');self.back('island','heaven_nav');return
        self.tap(480,867)
        state=self.wait('quiz','questions')
        if state=='questions':
            self.record('宗门答疑','已完成或无题目','没有出现答题页面')
            self.close('questions',601,460,'teaching')
        else:
            db=json.loads((ROOT/'quiz_answers.json').read_text(encoding='utf-8-sig'))['pairs']
            answered=0;unknown=[];seen=set()
            for _ in range(60):
                self.snap();self.require('quiz')
                question=self.words((108,466,614,635))
                identity=self.words((355,350,520,440))+'|'+question
                if identity in seen:raise Stop('答题后题目未变化，停止重复作答。')
                seen.add(identity)
                options=self.text((135,687,585,969))
                keys=[k for k in db if k in question]
                answers=[v for v in options if v['confidence']>=.7 and any(db[k] in v['text'] for k in keys)]
                if len(answers)==1:
                    # Rare characters lower the line confidence. Require the same known suffix twice.
                    self.snap();self.require('quiz')
                    verify=self.text((135,687,585,969))
                    same=[v for v in verify if any(db[k] in v['text'] for k in keys)]
                    if len(same)!=1 or abs(same[0]['pos'][1]-answers[0]['pos'][1])>8:
                        raise Stop('答题选项两次识别不一致。')
                    self.log('答疑：'+question+' -> '+answers[0]['text'])
                    self.tap(*answers[0]['pos'])
                    changed=False
                    for attempt in range(10):
                        time.sleep(.35);self.snap()
                        if not self.find('quiz'):
                            changed=True;break
                        new_identity=self.words((355,350,520,440))+'|'+self.words((108,466,614,635))
                        if new_identity!=identity:
                            changed=True;break
                    if not changed:raise Stop('答题后未切换弟子或题目，停止。')
                    answered+=1
                    if not self.find('quiz'):break
                else:
                    unknown.append(question)
                    self.log('未匹配答疑：'+question)
                    # Close this question, then reopen the next disciple only when supported.
                    break
            (self.out/'unknown_questions.json').write_text(json.dumps(unknown,ensure_ascii=False,indent=2),encoding='utf-8')
            self.record('宗门答疑','完成已知题' if not unknown else '有未知题',f'作答{answered}题，未知{len(unknown)}题，未猜答案')
            self.snap()
            if self.find('quiz'):self.close('quiz',610,248,'questions')
            if self.find('questions'):self.close('questions',601,460,'teaching')
            elif not self.find('teaching'):raise Stop('答题后出现未知页面，需要适配。')
        self.back('teaching','island');self.back('island','heaven_nav')

    def signin(self):
        self.wait('main_anchor');self.click('sign_entry');self.wait('sign_panel')
        if self.find('sign_done'):
            self.record('签到','已完成','今天已签到')
        elif self.find('sign_ready'):
            self.click('sign_ready');self.wait('sign_done')
            self.record('签到','成功','已确认请明日再来')
        else:raise Stop('签到状态未知')
        self.click('sign_close');self.wait('main_anchor')

    def forbidden(self):
        self.island();self.island_label('island_forbidden');self.wait('forbidden')
        self.click('forbidden_progress_button');self.wait('forbidden_progress')
        claims=0
        for _ in range(45):
            self.snap();self.require('forbidden_progress')
            p=self.find('forbidden_reward',roi=(90,225,630,1110))
            if not p:break
            x,y=p;box=(90,max(230,y-215),625,y-45)
            before=self.words(box)
            self.tap(x,y)
            changed=False
            for attempt in range(4):
                time.sleep(.5);self.snap();self.require('forbidden_progress')
                if self.find('bag_full') or '储物袋已满' in self.words((180,450,540,750)):
                    raise Stop('储物袋已满，领取停止。请清理后重跑。')
                after=self.words(box)
                if before!=after:
                    changed=True;break
            if not changed:raise Stop('领取后任务卡未变化，停止重复点击。')
            claims+=1;self.log(f'已验证领取禁地奖励 {claims} 组')
        self.pending['forbidden']=not bool(self.find('forbidden_empty_progress'))
        self.close('forbidden_progress',625,178,'forbidden')
        sent=0
        for _ in range(min(15,self.cfg['forbidden_limit'])):
            self.snap();self.require('forbidden')
            text=self.line((250,306,479,360))
            m=re.search(r'(\d+)\s*/\s*(\d+)',text)
            if not m:raise Stop('无法读取禁地次数：'+text)
            used,total=map(int,m.groups())
            if used>=min(total,15):break
            # Rank the visible destinations by star count, never refresh with currency.
            candidates=[]
            for top,bottom,cy in [(390,445,450),(548,606,608),(704,761,763)]:
                crop=self.frame[top:bottom,80:370]
                hsv=cv2.cvtColor(crop,cv2.COLOR_BGR2HSV)
                mask=cv2.inRange(hsv,np.array([12,120,190]),np.array([35,255,255]))
                count,_,stats,_=cv2.connectedComponentsWithStats(mask)
                stars=sum(1 for x,y,w,h,a in stats[1:] if 9<w<45 and 9<h<45 and a>40)
                candidates.append((stars,cy))
            _,cy=max(candidates)
            self.tap(330,cy);self.wait('forbidden_detail')
            self.click('forbidden_auto');time.sleep(.6);self.snap();self.require('forbidden_detail')
            condition=self.frame[565:630,175:545]
            hsv=cv2.cvtColor(condition,cv2.COLOR_BGR2HSV)
            green=cv2.countNonZero(cv2.inRange(hsv,np.array([35,100,80]),np.array([90,255,255])))
            red=cv2.countNonZero(cv2.inRange(hsv,np.array([0,130,130]),np.array([10,255,255])))
            if red>20 or green<50:
                self.close('forbidden_detail',625,178,'forbidden')
                self.record('禁地派遣','暂停','没有足够合适的空闲弟子；未刷新或购买次数')
                break
            self.click('forbidden_start');self.wait('forbidden')
            new=self.line((250,306,479,360));n=re.search(r'(\d+)\s*/\s*(\d+)',new)
            if not n or int(n[1])!=used+1:raise Stop('派遣后次数未增加，停止。')
            sent+=1;self.log(f'禁地已派遣：{n[1]}/{n[2]}')
            self.pending['forbidden']=True
        self.record('宗门禁地','完成本次处理',f'已领取{claims}组，已新增派遣{sent}队；探索完成后需再次领取')
        self.back('forbidden','island');self.back('island','heaven_nav')

    def travel(self):
        if not self.cfg['allow_food']:
            self.pending['travel']=False
            self.record('凡间历练','跳过','食物消耗未开启');return
        self.realm('mortal');self.tap(630,995);self.wait('travel')
        self.click('wander_button');self.wait('wander_panel')
        if self.find('wander_running'):
            self.pending['travel']=True
            self.record('凡间神游','进行中','已有神游任务，不中断、不重复启动')
        else:
            self.require('wander_map');self.require('wander_food');self.require('wander_start')
            text=self.words((110,840,610,920));m=re.search(r'次数\s*(\d+)',text)
            if not m:raise Stop('无法读取神游剩余次数：'+text)
            remaining=int(m[1])
            self.tap(541,978);self.snap();self.require('wander_panel')
            cap_text=self.line((215,950,425,1005))
            if not cap_text.isdigit():raise Stop('无法识别神游单批上限：'+cap_text)
            cap=int(cap_text)
            count=min(remaining,int(self.cfg['wander_rounds']),cap)
            if count<=0:
                self.pending['travel']=False
                self.record('凡间神游','已完成','没有剩余次数')
            else:
                # This Unity field is not editable. Use the verified max/minus controls.
                for _ in range(cap-count):
                    self.snap();self.require('wander_panel');self.tap(179,978)
                self.snap();self.require('wander_panel')
                value=self.line((215,950,425,1005))
                if not re.fullmatch(r'\s*'+str(count)+r'\s*',value):raise Stop('神游轮数输入后未确认：'+value)
                self.click('wander_start');self.wait('wander_running')
                self.pending['travel']=True
                self.record('凡间神游','已启动',f'常羊山{count}轮，每轮400食物；不使用仙玉加速')
        self.close('wander_panel',610,190,'travel');self.back('travel','mortal_nav')

    def duel(self):
        self.realm('heaven');self.tap(213,995);self.wait('heaven_arena','duel')
        if not self.find('duel'):
            self.click('duel_tab');self.wait('duel')
        if self.find('duel_join'):
            self.click('duel_join');self.wait('duel_joined')
        done=0
        for _ in range(min(5,self.cfg['duel_limit'])):
            self.snap();self.require('duel')
            text=self.line((570,75,720,113));m=re.search(r'(\d+)次',text)
            if not m:raise Stop('无法读取斗法次数：'+text)
            remaining=int(m[1])
            if remaining==0:break
            self.click('duel_fight');self.wait('battle_exit',seconds=25)
            self.click('battle_exit');self.wait('duel_reward');self.click('duel_confirm');self.wait('duel_joined')
            after=self.line((570,75,720,113));m2=re.search(r'(\d+)次',after)
            if not m2 or int(m2[1])!=remaining-1:raise Stop('斗法次数未减少，停止。')
            done+=1
        self.record('仙界斗法','完成本次处理',f'本次战斗{done}场，已确认每场结算')
        self.back('duel','heaven_nav')

    def gamble(self):
        if not self.cfg['allow_gamble_lingshi']:
            self.record('市肆博戏','跳过','未启用每次2000灵石的消耗');return
        self.island();self.island_label('island_market');self.wait('market')
        self.click('gamble_button');self.wait('gamble')
        count=0
        for _ in range(min(10,self.cfg['gamble_limit'])):
            self.snap();self.require('gamble');self.require('gamble_cost')
            text=self.line((285,835,435,867));m=re.search(r'(\d+)\s*/\s*10',text)
            if not m:raise Stop('无法读取博戏次数：'+text)
            used=int(m[1])
            if used>=10:break
            self.click('gamble_start');time.sleep(.8);self.snap();self.require('gamble')
            new=self.line((285,835,435,867));n=re.search(r'(\d+)\s*/\s*10',new)
            if not n or int(n[1])!=used+1:raise Stop('博戏次数未变化，可能储物袋满或灵石不足。')
            count+=1
        self.record('市肆博戏','完成本次处理',f'本次{count}次，消耗{count*2000}灵石')
        self.close('gamble',619,384,'market');self.back('market','island');self.back('island','heaven_nav')

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--watch',action='store_true',help='本轮结束后每5分钟自动收尾，最长8小时且不跨北京时间日期')
    parser.add_argument('task',choices=['all','finish','signin','forbidden','travel','duel','gamble','sword','guard','quiz','practice','night','stars','family','transfer','hunt','inspect'],default='all',nargs='?')
    args=parser.parse_args()
    lock=(ROOT/'.running.lock').open('a+b')
    lock.write(b'0');lock.flush();lock.seek(0)
    try:msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
    except OSError:
        print('已有助手正在运行。请先停止上一轮。',flush=True);return
    (ROOT/'STOP').unlink(missing_ok=True)
    bot=Bot()
    try:
        bot.snap()
        if args.task=='inspect':
            bot.log('已识别：'+','.join(n for n in bot.meta if bot.find(n)))
            bot.log(bot.words());return
        tasks=['signin','practice','guard','quiz','transfer','forbidden','duel','sword','gamble','hunt','night','family','stars','travel'] if args.task=='all' else [args.task]
        if args.task=='finish':tasks=['family','night','forbidden','travel']
        for task in tasks:
            getattr(bot,task)()
        if args.watch:
            end=time.monotonic()+8*3600
            while any(bot.pending.values()) and time.monotonic()<end:
                bot.log('等待5分钟后继续领取和处理剩余任务；可在运行面板停止。')
                for _ in range(300):
                    if (ROOT/'STOP').exists():raise Stop('用户已停止运行。')
                    if dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).date().isoformat()!=bot.day:
                        raise Stop('已跨北京时间日期，停止，避免自动消耗下一天的资源。')
                    time.sleep(1)
                for task in ['family','night','forbidden','travel']:
                    if bot.pending.get(task):getattr(bot,task)()
            if any(bot.pending.values()):bot.log('已达到8小时上限，尚有倒计时任务。')
        bot.log('本次流程结束。报告目录：'+str(bot.out))
    except (Stop,subprocess.SubprocessError) as exc:
        bot.record(args.task,'停止',str(exc));raise SystemExit(1)
    except KeyboardInterrupt:
        bot.record(args.task,'已停止','用户按下Ctrl+C');raise SystemExit(130)

if __name__=='__main__':main()





