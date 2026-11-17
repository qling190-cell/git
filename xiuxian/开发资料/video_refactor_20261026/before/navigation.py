"""主界面识别、返回恢复与按区域执行。"""
import time
import json
import cv2
import numpy as np
from daily_tasks import TaskStop


class ScreenError(TaskStop):
    """可返回主界面后重新检查的界面错误。"""


DAILY_GROUPS=[
    ('mortal','凡间',['signin','practice','travel','fishing_mortal']),
    ('heaven','仙界',['lecture','guard','quiz','transfer','forbidden','duel','sword','gamble','jade','tower','demon','hunt','treasure']),
    ('void','虚空',['familycare','family','night','raid','provisions','gifts','pond','stars']),
    ('yuanji','元极',['palace_lamp','palace_garden','palace_cultivate','palace_court']),
]
FINISH_GROUPS=[
    ('mortal','凡间',['travel']),
    ('heaven','仙界',['forbidden','hunt','treasure']),
    ('void','虚空',['family','night']),
    ('yuanji','元极',['palace_cultivate','palace_court']),
]
TASK_LABELS={
    'signin':'签到与抽奖','practice':'门派练功与掌门传功','travel':'常羊山神游',
    'fishing_mortal':'幻海之心钓鱼','lecture':'掌门大殿训话','guard':'全部护法',
    'quiz':'一键课训','transfer':'检查宗门传功','forbidden':'宗门禁地',
    'duel':'斗法','sword':'论剑','gamble':'市肆博戏','jade':'购买玉盒',
    'tower':'通天塔每日奖励','demon':'魔域埋骨地扫荡','hunt':'仙猎',
    'treasure':'降妖寻宝','familycare':'仙祠指点与玄灵树','family':'家族征收',
    'night':'丽晶异域夜猎','raid':'鸿胪台讨伐','provisions':'珍馐坊采购',
    'gifts':'仙祠一键赠予','pond':'游心塘钓鱼','stars':'探星禁区','palace':'天阙每日',
    'palace_cultivate':'萦云楼同修领奖','palace_court':'朝会殿朝议领奖',
    'palace_garden':'御木园状态与收获重种','palace_lamp':'燃心灯收取',
}


class Navigation:
    def continue_open_daily_task(self):
        # Resume an already-open ancestral page before trying generic recovery.
        if 'familycare' in self.daily_progress['completed'] or not self.find('ancestral'):return True
        self.log('当前停留仙祠：直接继续一键指点，再返回处理后续任务')
        self.save_daily_progress('familycare')
        result=self.run_task('familycare')
        if result:self.daily_progress['completed'].append('familycare')
        self.save_daily_progress()
        return result

    def prepare_daily_progress(self,resume=False):
        self.progress_path=self.ledger_path.with_suffix('.progress.json')
        data={}
        if resume and self.progress_path.exists():
            data=json.loads(self.progress_path.read_text(encoding='utf-8'))
        if data.get('day')!=self.day:
            data={'day':self.day,'completed':[],'pending':{},'current':None}
            if resume:self.log('没有本账号今日断点，从凡间开始建立进度。')
        self.daily_progress=data
        if 'hunt' in data['completed'] and int(self.ledger.get('hunt_started',0))<2:
            data['completed'].remove('hunt')
        if 'night' in data['completed']:
            counts=self.ledger.get('night_by_destination',{})
            if len(counts)<4 or sum(int(v) for v in counts.values())<60:
                data['completed'].remove('night')
        self.resume_daily=resume
        self.pending.update(data.get('pending',{}))
        if resume:
            current=data.get('current')
            label=TASK_LABELS.get(current,current) if current else '下一项未完成任务'
            self.log(f"继续今日进度：已处理{len(data['completed'])}项；从{label}检查继续")
        self.save_daily_progress()

    def save_daily_progress(self,current=None):
        if not hasattr(self,'daily_progress'):return
        self.daily_progress['current']=current
        self.daily_progress['pending']=dict(self.pending)
        temporary=self.progress_path.with_suffix('.tmp')
        temporary.write_text(json.dumps(self.daily_progress,ensure_ascii=False,indent=2),encoding='utf-8')
        temporary.replace(self.progress_path)

    def recover(self):
        return self.recover_to_main('手动返回')

    def main_screen(self,frame=None):
        if not self.cfg.get('realm_menu'):return None
        frame=self.frame if frame is None else frame
        if getattr(self,'_main_frame',None) is frame:return self._main_result
        self._main_frame=frame;self._main_result=None
        # Portrait stays fixed when realm backgrounds animate. Dark modal overlays
        # dim it and must not be mistaken for the clickable page beneath them.
        if not self.find('oppo_main_guard',frame=frame):return None
        text=self.words((0,940,720,1055),frame).replace(' ','')
        groups={
            'mortal':('福地','门派','洞府','历练'),
            'heaven':('宗门','比斗','太虚','道使','游历'),
            'void':('魂戒','探星','仙居','轮回','征程'),
        }
        matches=[name for name,labels in groups.items() if sum(x in text for x in labels)>=2]
        if '天阙' in text:matches.append('yuanji')
        if len(matches)==1:self._main_result=matches[0]
        return self._main_result

    def fallback_find(self,name,frame,roi=None):
        if name=='sign_entry' and self.cfg.get('realm_menu') and self.main_screen(frame):
            hits=[v for v in self.text((65,170,132,238),frame) if v['confidence']>=.9 and v['text'].replace(' ','')=='签到']
            if len(hits)==1:return hits[0]['pos']
        return None

    def menu_visible(self):
        menu=self.words((100,273,348,312))+' '+self.words((0,245,355,317))
        return sum(s in menu for s in ('凡间','仙界','虚空','元极'))>=2

    def return_arrow_visible(self):
        if any(self.find(n) for n in ('back_palace','back_classic','back_cloud','back_ancestral','back_journey') if n in self.meta):return True
        # The same yellow arrow sits on different coloured realm headers. Match
        # its bright foreground shape, not a rectangle containing the background.
        if 'back_classic' not in self.images:return False
        def yellow(im):
            hsv=cv2.cvtColor(im,cv2.COLOR_BGR2HSV)
            return cv2.inRange(hsv,np.array([12,30,180]),np.array([40,230,255]))
        template=yellow(self.images['back_classic']);crop=yellow(self.frame[8:70,8:65])
        if cv2.countNonZero(template)<30:return False
        _,score,_,pos=cv2.minMaxLoc(cv2.matchTemplate(crop,template,cv2.TM_CCOEFF_NORMED))
        x,y=pos;h,w=template.shape;sample=crop[y:y+h,x:x+w]
        union=cv2.countNonZero(cv2.bitwise_or(sample,template))
        overlap=cv2.countNonZero(cv2.bitwise_and(sample,template))
        return score>=.88 and union>0 and overlap/union>=.8

    def recover_to_main(self,reason='恢复主界面',max_steps=8):
        self.log(reason+'：开始返回四区角色主界面')
        for step in range(max_steps+1):
            self.snap()
            if self.cfg.get('realm_menu'):
                current=self.main_screen()
                if current:
                    self.log('已返回主界面：'+current);return current
            elif any(self.find(n) for n in ('mortal_nav','heaven_nav','void_nav')):
                return 'legacy'
            if step==max_steps:break
            if self.cfg.get('realm_menu') and self.menu_visible():
                self.tap(32,196)
            else:
                if 'master_hint_close' in self.meta and self.find('master_hint_close'):
                    self.click('master_hint_close');time.sleep(.65);continue
                if 'sword_opponents_close' in self.meta and self.find('sword_opponents_close'):
                    self.click('sword_opponents_close');time.sleep(.65);continue
                if 'night_close' in self.meta and self.find('night_close'):
                    self.click('night_close');time.sleep(.65);continue
                generic_x=next((p for n in ('modal_close_white','modal_close_red') if n in self.meta and (p:=self.find(n,roi=(490,120,680,610)))),None)
                if generic_x:
                    self.tap(*generic_x);time.sleep(.65);continue
                modals=[('gift_dialog',(600,280)),('sword_opponents',(626,199)),
                        ('sign_panel',(622,277)),('wander_panel',(610,190)),
                        ('forbidden_progress',(625,178)),('forbidden_detail',(625,178)),
                        ('guard',(615,404)),('questions',(601,460)),('quiz',(610,248)),
                        ('practice',(605,270)),('hunt',(610,184)),('demon',(610,221)),
                        ('treasure',(622,184)),('pond',(629,397)),('family_panel',(622,206)),
                        ('night',(628,166)),('gamble',(619,384)),('market_shop',(618,150))]
                close=next((point for page,point in modals if page in self.meta and self.find(page)),None)
                if close:
                    self.tap(*close);time.sleep(.65);continue
                # Only in-game X/return controls. Android Back invokes OPPO's
                # exit guider instead of closing these dialogs.
                if self.return_arrow_visible():self.tap(35,40)
                else:
                    # Let realm/page transitions settle before sending Back.
                    for _ in range(3):
                        time.sleep(.5);self.snap()
                        current=self.main_screen() if self.cfg.get('realm_menu') else None
                        if current:return current
                    raise TaskStop('没有识别到游戏内X或返回按钮，已停留现场；不发送系统返回')
            time.sleep(.65)
        raise TaskStop('返回主界面失败，已尝试有限次数；停止，避免重复误点')

    def run_task(self,task):
        for attempt in range(2):
            try:
                result=getattr(self,task)();return result is not False
            except TaskStop as exc:
                message=str(exc)
                if any(word in message for word in ('用户已停止','不在前台','前台应用','跨北京时间','分辨率必须','返回主界面失败')):raise
                self.record(task,'界面恢复' if isinstance(exc,ScreenError) else '本项未完成',message)
                self.recover_to_main(task+'异常')
                if isinstance(exc,ScreenError) and attempt==0:
                    self.log('返回成功，重新检查本任务一次：'+task);continue
                self.record(task,'未完成','已返回主界面；本项保留待处理，继续下一项')
                return False

    def run_groups(self,groups,pending_only=False):
        success=True
        for realm,label,tasks in groups:
            if realm=='yuanji' and not self.cfg.get('realm_menu'):continue
            selected=[t for t in tasks if not pending_only or self.pending.get(t)]
            if getattr(self,'resume_daily',False) and not pending_only:
                completed=self.daily_progress['completed']
                selected=[t for t in selected if t not in completed]
            if not selected:continue
            self.recover_to_main('进入'+label+'任务前')
            try:self.realm(realm)
            except ScreenError as exc:
                self.record(label+'任务','未完成',str(exc));self.recover_to_main(label+'切换失败')
                success=False;continue
            self.log('—— '+label+'任务：'+' → '.join(TASK_LABELS.get(t,t) for t in selected)+' ——')
            for index,task in enumerate(selected):
                self.save_daily_progress(task)
                secrets={'demon','hunt','treasure'}
                following=selected[index+1] if index+1<len(selected) else None
                self._secrets_batch=task in secrets|{'tower'} and following in secrets
                palace={'palace_lamp','palace_garden','palace_cultivate','palace_court'}
                self._palace_batch=task in palace and following in palace
                self._home_batch=task=='provisions' and following=='gifts'
                try:result=self.run_task(task)
                finally:self._secrets_batch=False;self._palace_batch=False;self._home_batch=False
                if hasattr(self,'daily_progress'):
                    completed=self.daily_progress['completed']
                    if result and task not in completed:completed.append(task)
                self.save_daily_progress()
                success=result and success
        return success
