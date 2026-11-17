"""Night hunt v5: recognize stationing, visit all four, verify 15 rounds each."""
import re
import time
import cv2
import numpy as np
from daily_tasks import TaskStop

GRID=(120,325,600,695)


def destination_name(text):
    return text.replace(' ','').replace('埋骨凶间','埋骨凶涧').replace('埋骨凶澗','埋骨凶涧')


class NightTasks:
    def night_buttons(self,frame=None):
        frame=self.frame if frame is None else frame
        left,top,right,bottom=GRID;crop=frame[top:bottom,left:right]
        hsv=cv2.cvtColor(crop,cv2.COLOR_BGR2HSV)
        markers=[]
        template=self.images['night_stationed'];th,tw=template.shape[:2]
        scores=cv2.matchTemplate(cv2.cvtColor(crop,cv2.COLOR_BGR2GRAY),
                                 cv2.cvtColor(template,cv2.COLOR_BGR2GRAY),cv2.TM_CCOEFF_NORMED)
        for _ in range(16):
            _,score,_,(x,y)=cv2.minMaxLoc(scores)
            if score<.88:break
            scores[max(0,y-23):y+24,max(0,x-18):x+19]=-1
            patch=hsv[y:y+th,x:x+tw]
            orange=cv2.inRange(patch,np.array([6,110,120]),np.array([30,255,255]))
            white=cv2.inRange(patch,np.array([0,0,190]),np.array([180,100,255]))
            if cv2.countNonZero(orange)<tw*th*.25 or cv2.countNonZero(white)<20:continue
            markers.append((x+left+tw//2,y+top+th//2+3,'stationed'))
        green=cv2.inRange(hsv,np.array([35,65,80]),np.array([90,255,255]))
        contours,_=cv2.findContours(green,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            x,y,w,h=cv2.boundingRect(contour)
            if 22<=w<=65 and 24<=h<=70 and cv2.contourArea(contour)>140:
                markers.append((x+left+w//2,y+top+h//2,'complete'))
        entries=[]
        for badge_x,cy,state in markers:
            cx=238 if badge_x<400 else 476
            if not 345<=cy<=670:continue
            if any(abs(e['pos'][0]-cx)<30 and abs(e['pos'][1]-cy)<24 for e in entries):continue
            name=destination_name(self.words((cx-92,cy-26,cx+64,cy+26),frame))
            if not re.fullmatch('[\u4e00-\u9fff]{3,8}',name):continue
            entries.append({'name':name,'pos':(cx,cy),'stationed':state=='stationed','complete':state=='complete','source':state})
        # During a running countdown the marker can change. Only reuse identities
        # that have already been positively observed as stationed on this account.
        known={destination_name(n) for n in self.ledger.get('night_stationed',[])}
        grid_words=self.text(GRID,frame)
        for item in grid_words:
            name=destination_name(item['text'])
            if item['confidence']<.85 or name not in known or any(e['name']==name for e in entries):continue
            x,y=item['pos']
            has_clock=any(re.search(r'\d{1,2}[:：]\d{2}',v['text']) and abs(v['pos'][0]-x)<105
                          and abs(v['pos'][1]-y)<40 for v in grid_words)
            if has_clock and 345<=y<=670:
                entries.append({'name':name,'pos':(238 if x<350 else 476,y),'stationed':True,'complete':False,'source':'cached'})
        return sorted(entries,key=lambda e:(round(e['pos'][1]/20),e['pos'][0]))

    def night_scroll(self,towards_bottom=True):
        self.require('night')
        start,end=(610,430) if towards_bottom else (410,590)
        self.adb('shell','input','swipe',350,start,350,end,650)
        time.sleep(.8);self.snap();self.require('night')

    def night_discover(self):
        found={}
        for direction in (None,True,True,True,True,False,False,False,False,False,False):
            if direction is not None:self.night_scroll(direction)
            self.snap();self.require('night')
            for entry in self.night_buttons():found[entry['name']]=entry
            if len(found)==4:return list(found)
            if len(found)>4:raise TaskStop('夜猎驻扎标记超过四处，需核对驻扎名单；未开始夜猎')
        return list(found)

    def night_locate(self,name):
        for direction in (None,True,True,True,True,False,False,False,False,False,False):
            if direction is not None:self.night_scroll(direction)
            self.snap();self.require('night')
            match=next((e for e in self.night_buttons() if e['name']==name),None)
            if match:
                self.tap(*match['pos'])
                self.wait_words('night',(105,710,530,790),lambda s:name in destination_name(s))
                return
        raise TaskStop('已驻扎洞天重新定位失败：'+name)

    def night_quota(self):
        self.snap();self.require('night')
        text=self.words((80,235,640,320)).replace(' ','')
        match=re.search(r'(?:夜猎|尚可)(\d+)次',text)
        if not match:raise TaskStop('夜猎总剩余次数未确认：'+text)
        return int(match[1])

    def night_running(self):
        text=self.words((95,970,620,1140)).replace(' ','')
        return bool(re.search(r'\d{1,2}[:：]\d{2}',text) or '剩余夜猎' in text or '本轮夜猎' in text)

    def night_rounds(self):
        text=self.line((270,985,365,1033)).strip()
        if not text.isdigit() or not 1<=int(text)<=60:raise TaskStop('夜猎轮数无法确认：'+text)
        return int(text)

    def night_process(self,name):
        self.night_locate(name);self.snap();self.require('night')
        counts=self.ledger.setdefault('night_by_destination',{})
        transactions=self.ledger.setdefault('night_transactions',{})
        transaction=transactions.get(name,{})
        if self.find('night_claim'):
            self.click('night_claim');self.wait_gone('night','night_claim')
            self.record('夜猎'+name,'已领取','已完成洞天的奖励领取成功')
            transaction['claimed']=True;transactions[name]=transaction;self.ledger_save()
        self.snap();self.require('night')
        if self.night_running():
            if transaction.get('phase')=='reserved':
                counts[name]=15;transaction['phase']='running';self.ledger_save()
            self.record('夜猎'+name,'进行中','已识别倒计时，继续下一个洞天')
            return 'running'
        if int(counts.get(name,0))>=15:
            self.record('夜猎'+name,'今日完成','今日15次已处理，不重复开始')
            return 'done'
        if transaction.get('phase')=='reserved':
            if not self.find('night_start') or self.night_quota()!=transaction.get('before_quota'):
                raise TaskStop('该洞天上次提交结果不明确，不重复消耗：'+name)
            # A visible ready button and unchanged global quota prove no start.
            transactions.pop(name,None);self.ledger_save()
        if not self.find('night_start'):raise TaskStop('洞天既无倒计时、也无开始按钮：'+name)
        committed=sum(max(min(15,int(counts.get(key,0))),15 if item.get('phase')=='reserved' else 0)
                      for key,item in transactions.items())
        committed+=sum(min(15,int(value)) for key,value in counts.items() if key not in transactions)
        if committed+15>60:raise TaskStop('今日已确认或待核对的夜猎将超过60次，不再新增')
        condition=cv2.cvtColor(self.frame[856:962,160:570],cv2.COLOR_BGR2HSV)
        red=cv2.countNonZero(cv2.inRange(condition,np.array([0,110,120]),np.array([12,255,255])))
        green=cv2.countNonZero(cv2.inRange(condition,np.array([35,80,70]),np.array([90,255,255])))
        if red>20 or green<50:raise TaskStop('该洞天驻扎条件未满足：'+name)
        quota=self.night_quota()
        if quota<15:raise TaskStop(f'夜猎游戏剩余{quota}次，无法为{name}安排15次；不购买额外次数')
        self.tap(541,1009);self.snap();self.require('night')
        maximum=self.night_rounds()
        if maximum<15:raise TaskStop('该洞天最大夜猎轮数不足15：'+name)
        for _ in range(maximum-15):self.tap(179,1009)
        self.snap();self.require('night')
        if self.night_rounds()!=15:raise TaskStop('开始前未确认15次：'+name)
        transactions[name]={'phase':'reserved','before_quota':quota,'rounds':15,'submitted_at':time.time()}
        self.ledger_save()
        self.click('night_start')
        end=time.monotonic()+15
        while time.monotonic()<end:
            self.snap();self.require('night')
            if self.night_running():break
            time.sleep(.4)
        else:raise TaskStop('已点击开始夜猎，但未确认倒计时；保留提交记录：'+name)
        counts[name]=15;transactions[name]['phase']='running'
        self.ledger['night_started']=sum(min(15,int(v)) for v in counts.values())
        self.ledger_save()
        after=self.night_quota()
        if after!=quota-15:raise TaskStop(f'夜猎已运行但总次数变化需核查：{quota}→{after}；已保留15次记录')
        self.record('夜猎'+name,'已启动',f'15次已确认；总剩余{quota}→{after}，继续下一个洞天')
        return 'running'

    def night(self):
        self.snap()
        if not self.find('night'):
            self.journey_open();self.tap(360,995);self.wait('night')
        names=self.night_discover()
        if not names:raise TaskStop('整个洞天列表未识别到已驻扎标记，未开始夜猎')
        self.log('夜猎驻扎名单：'+'、'.join(names))
        self.ledger['night_stationed']=names
        # Migrate OCR spelling differences, retaining the maximum confirmed count.
        old=self.ledger.get('night_by_destination',{});counts={}
        for key,value in old.items():
            name=destination_name(key);counts[name]=max(counts.get(name,0),int(value))
        self.ledger['night_by_destination']=counts;self.ledger_save()
        statuses={};errors=[]
        for name in names:
            try:statuses[name]=self.night_process(name)
            except TaskStop as exc:
                message=str(exc)
                if any(s in message for s in ('用户已停止','不在前台','前台应用','跨北京时间','分辨率必须')):raise
                self.record('夜猎'+name,'本处未完成',message);errors.append(name)
                self.snap()
                if not self.find('night'):raise
                # Stay inside the same panel; a single blocked destination must
                # not prevent the remaining stationed destinations being checked.
        if len(names)!=4:
            errors.append('驻扎名单不足四处')
            self.record('虚空夜猎','名单未完整',f'已处理识别到的{len(names)}处，下次继续查找；不把整项标为完成')
        self.pending['night']=bool(errors or any(s=='running' for s in statuses.values()))
        self.ledger['night_statuses']=statuses;self.ledger_save()
        total=sum(min(15,int(counts.get(name,0))) for name in names)
        self.record('虚空夜猎','本轮处理结束' if not errors else '尚有待处理',
                    f'逐处检查{len(names)}处；今日已确认安排{total}/60次；未完成{len(errors)}处；最后统一返回')
        self.close('night',628,166,'journey');self.back('journey','void_nav')
        return not errors
