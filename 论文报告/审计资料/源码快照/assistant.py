"""太古仙尊 OPPO/vivo / LDPlayer 720x1280. Run from the logged-in main screen."""
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
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from daily_tasks import ApprovedTasks, TaskStop as Stop
from palace_tasks import PalaceTasks
from night_tasks import NightTasks
from gift_tasks import GiftTasks
from star_rewards import StarRewards
from hierarchy import Hierarchy
from video_tasks import VideoTasks
from navigation import Navigation, ScreenError, DAILY_GROUPS, FINISH_GROUPS, TASK_LABELS

class Bot(Navigation, Hierarchy, NightTasks, GiftTasks, StarRewards, VideoTasks, ApprovedTasks, PalaceTasks):
    def __init__(self):
        global time
        from runtime_control import PauseClock
        time=PauseClock(ROOT,Stop)
        for module in ('navigation','daily_tasks','palace_tasks','night_tasks','gift_tasks','video_tasks','night_engine','star_rewards','forbidden_tasks'):
            sys.modules[module].time=time
        self.cfg = json.loads((ROOT/'config.json').read_text(encoding='utf-8-sig'))
        self.meta = json.loads((ROOT/'assets.json').read_text(encoding='utf-8'))
        self.images = {n: cv2.imdecode(np.frombuffer((ROOT/'assets'/f'{n}.png').read_bytes(), np.uint8), 1) for n in self.meta}
        for name,target in self.cfg.get('asset_aliases',{}).items():
            self.meta[name]=self.meta[target];self.images[name]=self.images[target]
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
        account=self.cfg.get('account_key','')
        if account and not re.fullmatch(r'[a-zA-Z0-9_-]+',account):raise Stop('账号记录标识格式错误')
        ledger_path=ROOT/'ledgers'/f'{account}.json' if account else ROOT/'ledger.json'
        ledger_path.parent.mkdir(exist_ok=True)
        self.ledger_path=ledger_path
        self.ledger=json.loads(ledger_path.read_text(encoding='utf-8-sig')) if ledger_path.exists() else {}
        if self.ledger.get('day')!=self.day:self.ledger={'day':self.day,'night_started':0}

    def log(self, message):
        print(message, flush=True)
        with (self.out/'events.txt').open('a', encoding='utf-8') as f:
            f.write(f'{dt.datetime.now():%H:%M:%S} {message}\n')

    def adb(self, *parts):
        time.gate()
        # pythonw has no console; Windows otherwise creates one for each adb.exe.
        return subprocess.check_output(
            [self.cfg['adb'], '-s', self.cfg['device'], *map(str,parts)],
            timeout=20, stdin=subprocess.DEVNULL, stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW)

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
        if name=='main_anchor' and self.cfg.get('realm_menu'):
            return (360,1000) if self.main_screen(frame) else None
        if name in ('mortal_nav','heaven_nav','void_nav','yuanji_nav') and self.cfg.get('realm_menu'):
            return (360,1000) if self.main_screen(frame)==name[:-4] else None
        if name not in self.meta:return self.video_page(name,frame)
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
            return self.fallback_find(name,frame,roi)
        return a+x+w//2,b+y+h//2

    def text(self, roi=(0,0,720,1280), frame=None):
        im = self.frame if frame is None else frame
        if getattr(self,'_ocr_frame',None) is not im:self._ocr_frame=im;self._ocr_cache={}
        if roi in self._ocr_cache:return self._ocr_cache[roi]
        x,y,r,b=roi
        crop=im[y:b,x:r]
        if crop.shape[0]<180:
            crop=cv2.resize(crop,None,fx=2,fy=2); scale=2
        else:
            scale=1
        result,_=self.ocr(crop)
        values=[{'text':s,'confidence':float(conf),'pos':(int(x+np.mean([p[0] for p in box])/scale),int(y+np.mean([p[1] for p in box])/scale))} for box,s,conf in (result or [])]
        self._ocr_cache[roi]=values
        return values

    def words(self, roi=(0,0,720,1280), frame=None):
        return ' '.join(v['text'] for v in self.text(roi,frame) if v['confidence']>=.8)

    def line(self,roi):
        x,y,r,b=roi
        result,_=self.ocr(self.frame[y:b,x:r],use_det=False,use_cls=False)
        return ''.join(s for s,confidence in (result or []) if confidence>=.9)

    def require(self, name):
        if not self.find(name):
            raise ScreenError(f'当前页面不符合预期：{name}。已保存截图。')

    def tap(self,x,y):
        time.gate()
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

    def _v1_practice(self):
        if not self.cfg.get('allow_practice_lingshi',True):
            self.record('门派练功','跳过','未启用1000灵石消耗');return
        self.mortal_sect_open()
        self.tap(70,995);self.wait('practice')
        if self.find('practice_running'):
            self.record('门派练功','进行中','已在练功，不重复启动')
        elif self.find('practice_start') and self.find('practice_cost'):
            self.click('practice_start');self.wait('practice_running')
            self.record('门派练功','已启动','消耗1000灵石，已确认修炼中；不购买掌门传功次数')
        else:raise Stop('门派练功状态未知')
        self.close('practice',605,270,'mortal_sect');self.back('mortal_sect','mortal_nav')

    def family(self):
        self.home_open()
        self.tap(530,945);self.wait('family');self.tap(360,995);self.wait('family_panel')
        claimed=0;started=0;self.pending['family']=False
        # First resolve any previously selected collection, without changing its destination.
        if self.find('family_claim'):
            self.click('family_claim');self.wait_gone('family_panel','family_claim');claimed+=1
        self.snap();self.require('family_panel')
        state=self.words((105,984,605,1044))
        if re.search(r'\d{1,2}[:：]\d{2}',state):
            self.pending['family']=True
            self.log('家族征收：已识别倒计时，保留当前地点并退出执行下一项')
        else:
            text=self.line((278,1046,439,1086));m=re.search(r'征收\s*(\d+)次',text)
            if not m:raise Stop('无法读取家族征收次数：'+text)
            if int(m[1])>0:
                if not self.find('family_start'):raise Stop('家族征收状态未知：'+state)
                target=self.cfg.get('family_target','太上凰宗')
                self.text_button(target,(90,280,630,885));self.snap();self.require('family_panel')
                selected=self.words((92,899,470,940))
                if target not in selected:raise Stop('家族征收目标未确认：'+selected)
                self.click('family_start');started+=1
                self.wait_words('family_panel',(105,984,605,1044),lambda s:bool(re.search(r'\d{2}[:：]\d{2}',s)))
                self.pending['family']=True
                self.log('家族征收：已启动'+target+'并识别倒计时，退出执行下一项')
        self.record('家族征收','进行中' if self.pending['family'] else '本日完成',f'新增征收{started}次，领取{claimed}次；自动收尾可等待后续征收')
        self.close('family_panel',622,206,'family');self.back('family','immortal_home');self.back('immortal_home','void_nav')

    def transfer(self):
        # Cultivation is outside the approved food/lingshi budget. Inspect only.
        self.teaching_open();self.tap(194,738);self.wait('guard')
        costs=self.words((126,787,598,829))
        if '修为' not in costs:raise Stop('传功消耗类型未确认，停止。')
        self.record('宗门传功','按资源范围跳过',costs+'；未消耗修为')
        self.close('guard',615,404,'teaching');self.back('teaching','island');self.back('island','heaven_nav')


    def click(self,name,roi=None):
        end=time.monotonic()+12
        p=None
        while time.monotonic()<end:
            self.snap();p=self.find(name,roi=roi)
            if p is not None:break
            time.sleep(.3)
        if p is None:raise ScreenError(f'未识别按钮：{name}')
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
        raise ScreenError('等待页面超时：'+','.join(names))

    def wait_gone(self,page,name,seconds=12):
        end=time.monotonic()+seconds
        while time.monotonic()<end:
            self.snap();self.require(page)
            if not self.find(name):return
            time.sleep(.5)
        raise Stop('操作后按钮未变化，停止：'+name)

    def back(self,page,target):
        self.snap()
        if self.retain_parent():return
        self.require(page);self.tap(35,40);self.wait(target)

    def close(self,page,x,y,target):
        self.snap();self.require(page);self.tap(x,y);self.wait(target)

    def _v1_realm(self,target):
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
        self.snap()
        if self.find('island'):return
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

    def sword_local_now(self):
        return dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))

    def sword_defer(self,detail,entered=False):
        if entered:self.recover_to_main('周一论剑未开放')
        self.ledger['sword_deferred']=True;self.ledger_save()
        self.record('论剑','暂时跳过',detail+'；继续下一项任务，再次运行时重新检查')

    def sword_open(self):
        now=self.sword_local_now();monday=now.weekday()==0
        if monday and now.hour<12:
            self.sword_defer('周一北京时间中午12点后开放，目前未到开放时间');return False
        self.wait('main_anchor');self.tap(662,152)
        if monday:
            end=time.monotonic()+12
            while time.monotonic()<end:
                self.snap()
                body=self.words((60,120,660,1100)).replace(' ','')
                if any(s in body for s in ('未开放','未开启','尚未开始','暂未开始','尚未开放','尚未开启')):
                    self.sword_defer('周一识别到论剑尚未开放：'+body[:150],entered=True);return False
                if self.find('sword'):break
                time.sleep(.3)
            else:raise Stop('论剑页面未确认，未识别到明确的未开放提示')
        else:self.wait('sword')
        self.ledger['sword_deferred']=False;self.ledger_save()
        return True

    def sword(self):
        if not self.sword_open():return
        done=0
        for _ in range(10):
            self.snap();self.require('sword')
            remaining=self.sword_remaining()
            if not remaining:break
            self.click('sword_match');self.wait('sword_opponents')
            # Always challenge the first matched opponent; names/power are irrelevant.
            self.log('论剑：挑战匹配列表第一位')
            self.click('sword_challenge',roi=(495,294,625,350))
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
            best,cy=max(candidates)
            if not 1<=best<=3:raise Stop('禁地星级未能确认为1至3星，停止派遣。')
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


    def _v1_duel(self):
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
        self.market_open()
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
    parser.add_argument('--watch',action='store_true',help='本轮结束后每5分钟自动收尾，最长24小时且不跨北京时间日期')
    parser.add_argument('task',choices=['sect_deadland', 'sect_herbs', 'sect_exchange', 'freegift', 'smallworld', 'battle_exchange', 'observatory', 'star_orbit','star_forbidden','seize','all','resume','finish','signin','forbidden','travel','duel','gamble','sword','guard','quiz','practice','night','stars','family','transfer','hunt','jade','fishing_mortal','familycare','raid','provisions','gifts','pond','tower','demon','treasure','lecture','palace','palace_cultivate','palace_court','palace_garden','palace_lamp','recover','order','inspect'],default='all',nargs='?')
    args=parser.parse_args()
    lock=(ROOT/'.running.lock').open('a+b')
    lock.write(b'0');lock.flush();lock.seek(0)
    try:msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
    except OSError:
        print('已有助手正在运行。请先停止上一轮。',flush=True);return
    (ROOT/'STOP').unlink(missing_ok=True)
    (ROOT/'PAUSE').unlink(missing_ok=True)
    (ROOT/'PAUSED').unlink(missing_ok=True)
    bot=Bot()
    try:
        bot.snap()
        if args.task=='inspect':
            bot.log('已识别：'+','.join(n for n in bot.meta if bot.find(n)))
            bot.log(bot.words());return
        success=True
        if args.task=='order':
            for _,label,tasks in DAILY_GROUPS:bot.log(label+'：'+' → '.join(TASK_LABELS.get(t,t) for t in tasks))
            return
        if args.task in ('all','resume'):
            bot.prepare_daily_progress(resume=True)
            success=bot.run_groups(DAILY_GROUPS)
        elif args.task=='finish':success=bot.run_groups(FINISH_GROUPS)
        elif args.task=='provisions':
            success=bot.run_groups([('void','虚空',['provisions','gifts'])])
        else:success=bot.run_task(args.task)
        if args.watch:
            end=time.monotonic()+24*3600
            while any(bot.pending.values()) and time.monotonic()<end:
                bot.log('等待5分钟后继续领取和处理剩余任务；可在运行面板停止。')
                for _ in range(300):
                    if (ROOT/'STOP').exists():raise Stop('用户已停止运行。')
                    if dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).date().isoformat()!=bot.day:
                        raise Stop('已跨北京时间日期，停止，避免自动消耗下一天的资源。')
                    time.sleep(1)
                success=bot.run_groups(FINISH_GROUPS,pending_only=True) and success
            if any(bot.pending.values()):bot.log('已达到24小时上限，尚有倒计时任务。')
        bot.log(('本次流程结束。' if success else '本轮结束，部分任务未完成，请查看报告。')+'报告目录：'+str(bot.out))
        if not success:raise SystemExit(2)
    except (Stop,subprocess.SubprocessError) as exc:
        bot.record(args.task,'停止',str(exc));raise SystemExit(1)
    except KeyboardInterrupt:
        bot.record(args.task,'已停止','用户按下Ctrl+C');raise SystemExit(130)

if __name__=='__main__':main()





