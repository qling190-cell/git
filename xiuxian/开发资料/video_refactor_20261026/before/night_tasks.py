"""The four stationed night-hunt destinations, fifteen rounds each."""
import re
import time
import cv2
import numpy as np
from daily_tasks import TaskStop


class NightTasks:
    def night_buttons(self,frame=None):
        frame=self.frame if frame is None else frame
        hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
        mask=cv2.inRange(hsv[325:690,120:600],np.array([12,70,170]),np.array([40,255,255]))
        # Orange vertical stationing ribbons can connect neighbouring rows.
        # Separate their strip before locating the gold button rectangles.
        mask[:,195:235]=0;mask[:,433:480]=0
        # Selected borders extend into the row gap; do not join adjacent rows.
        mask=cv2.morphologyEx(mask,cv2.MORPH_CLOSE,np.ones((3,11),np.uint8))
        contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        buttons=[]
        for contour in contours:
            x,y,w,h=cv2.boundingRect(contour);x+=120;y+=325
            if not (160<=w<=220 and 40<=h<=76):continue
            w=205
            crop=hsv[y+8:y+h-8,x+10:x+w-10]
            gold=cv2.inRange(crop,np.array([12,65,190]),np.array([40,255,255]))
            if cv2.countNonZero(gold)/gold.size<.45:continue
            name=self.words((x+10,y+5,x+w-40,y+h-5),frame).replace(' ','')
            if not name:raise TaskStop('夜猎亮色洞天名称未识别')
            green=cv2.inRange(hsv[y:y+h,x+w-50:x+w],np.array([35,70,80]),np.array([90,255,255]))
            badge_roi=(max(0,x+w-40),max(0,y-15),min(720,x+w+15),min(1280,y+h+15))
            stationed=bool(self.find('night_stationed',frame=frame,roi=badge_roi))
            buttons.append({'name':name,'pos':(x+w//2,y+h//2),
                            'stationed':stationed,'complete':cv2.countNonZero(green)>30})
        # Recognize the stationing ribbon independently: a highlighted border
        # can connect two gold rectangles, but must not hide either ribbon.
        template=self.images['night_stationed'];th,tw=template.shape[:2]
        crop=frame[325:690,300:590]
        scores=cv2.matchTemplate(crop,template,cv2.TM_CCOEFF_NORMED)
        for _ in range(12):
            _,score,_,(bx,by)=cv2.minMaxLoc(scores)
            if score<.94:break
            sample=crop[by:by+th,bx:bx+tw]
            scores[max(0,by-20):by+21,max(0,bx-20):bx+21]=-1
            if float(np.mean(np.abs(sample.astype(float)-template.astype(float))))>15:continue
            cx=238 if bx+300<400 else 476
            cy=325+by+th//2+3
            existing=next((b for b in buttons if abs(b['pos'][0]-cx)<25 and abs(b['pos'][1]-cy)<25),None)
            if existing:existing['stationed']=True;continue
            name=self.words((cx-90,cy-25,cx+65,cy+25),frame).replace(' ','')
            if not name:raise TaskStop('已驻扎洞天名称无法读取')
            buttons.append({'name':name,'pos':(cx,cy),'stationed':True,'complete':False})
        return sorted(buttons,key=lambda b:(b['pos'][1]//20,b['pos'][0]))

    def night(self):
        self.realm('void');self.tap(650,995);self.wait('journey')
        self.tap(360,995);self.wait('night')
        # The list scrolls independently of the quota/round controls below it.
        for _ in range(4):
            self.adb('shell','input','swipe',350,620,350,360,450)
            time.sleep(.4);self.snap();self.require('night')
        # A completed hunt also proves previous stationing and must be collected.
        destinations=[b for b in self.night_buttons() if b['stationed'] or b['complete']]
        if len(destinations)!=4:raise TaskStop(f'夜猎识别到{len(destinations)}个已驻扎/已完成洞天，需确认四处，不按新旧猜测')
        self.ledger['night_stationed']=[b['name'] for b in destinations]
        self.ledger_save()
        self.log('夜猎已驻扎四处：'+'、'.join(b['name'] for b in destinations))
        counts=self.ledger.setdefault('night_by_destination',{})
        claimed=0;started=0;self.pending['night']=False
        for destination in destinations:
            name=destination['name']
            self.snap();self.require('night');self.tap(*destination['pos']);self.snap()
            if self.find('night_claim'):
                self.click('night_claim')
                self.wait_gone('night','night_claim');claimed+=1
                self.record('夜猎'+name,'已领取','已领取完成洞天的奖励')
            self.snap();self.require('night')
            state=self.words((95,970,610,1135))
            if re.search(r'\d{1,2}[:：]\d{2}',state) or '剩余夜猎' in state or '本轮夜猎' in state:
                self.pending['night']=True
                self.record('夜猎'+name,'进行中','识别到倒计时，保留并处理下一个洞天');continue
            if int(counts.get(name,0))>=15:
                self.record('夜猎'+name,'今日已处理','今日已启动15次，不重复开启');continue
            if not self.find('night_start'):raise TaskStop('夜猎洞天状态未知：'+name+' '+state)
            hsv=cv2.cvtColor(self.frame[856:962,160:570],cv2.COLOR_BGR2HSV)
            red=cv2.countNonZero(cv2.inRange(hsv,np.array([0,130,130]),np.array([10,255,255])))
            green=cv2.countNonZero(cv2.inRange(hsv,np.array([35,100,80]),np.array([90,255,255])))
            if red>20 or green<50:
                self.record('夜猎'+name,'条件不足','当前驻扎条件不足，继续检查下一处');continue
            quota=self.words((90,238,635,315)).replace(' ','')
            match=re.search(r'夜猎(\d+)次',quota)
            if not match:raise TaskStop('无法确认夜猎剩余总次数：'+quota)
            if int(match[1])<15:
                self.record('夜猎'+name,'次数不足','游戏剩余额度不足15次，不购买次数');continue
            self.tap(541,1009);self.snap();self.require('night')
            value=self.line((270,985,365,1033))
            if not value.isdigit() or not 1<=int(value)<=60:raise TaskStop('夜猎最大轮数未确认：'+value)
            maximum=int(value)
            if maximum<15:
                self.record('夜猎'+name,'轮数不足','当前最大轮数不足15次');continue
            for _ in range(maximum-15):self.tap(179,1009)
            self.snap();self.require('night')
            if self.line((270,985,365,1033))!='15':raise TaskStop('夜猎轮数未确认为15')
            self.click('night_start')
            self.wait_words('night',(95,975,610,1135),lambda s:bool(re.search(r'\d{1,2}[:：]\d{2}',s)) or '剩余夜猎' in s or '本轮夜猎' in s)
            counts[name]=15
            self.ledger['night_started']=sum(int(v) for v in counts.values())
            self.ledger_save();started+=15;self.pending['night']=True
            self.record('夜猎'+name,'已启动','已确认15次及倒计时，继续处理下一处')
        self.record('虚空夜猎','本轮处理结束',f'已检查4处，领取{claimed}处，新启动{started}次；倒计时交给自动收尾')
        self.close('night',628,166,'journey');self.back('journey','void_nav')
