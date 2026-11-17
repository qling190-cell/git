"""Daily ancestral gift selection: 三角梅 plus 甲中 offspring."""
import re
import time
import cv2
import numpy as np
from daily_tasks import TaskStop


class GiftTasks:
    def gift_cards(self):
        crop=cv2.resize(self.frame[400:905,110:610],None,fx=2,fy=2)
        result,_=self.ocr(crop)
        words=[{'text':s,'confidence':float(conf),
                'pos':(110+int(np.mean([p[0] for p in box])/2),400+int(np.mean([p[1] for p in box])/2))}
               for box,s,conf in (result or []) if conf>=.65]
        cards=[]
        for quality in words:
            label=quality['text'].replace(' ','')
            if not re.fullmatch('[甲乙丙丁][上中下]',label):continue
            x,y=quality['pos']
            names=[v for v in words if abs(v['pos'][0]-x)<45 and 15<=v['pos'][1]-y<=45]
            if not names:continue  # A clipped row will be read on the next overlapping page.
            if len(names)!=1:raise TaskStop('赠予子嗣姓名与品质未能唯一配对')
            name=names[0]['text'].replace(' ','')
            if name=='思全' and label=='甲中':
                nx,ny=names[0]['pos']
                detail=cv2.resize(self.frame[max(0,ny-18):ny+20,max(0,nx-55):nx+55],None,fx=3,fy=3)
                reread,_=self.ocr(detail)
                verified=[s.replace(' ','') for _,s,c in (reread or []) if c>=.85]
                if '思念' in verified:name='思念'
            if not re.fullmatch('[\u4e00-\u9fff]{2,6}',name):continue  # Clipped names are re-read on the overlapping page; final headcount remains mandatory.
            if names[0]['pos'][1]-90<480:continue
            cards.append({'name':name,'quality':label,'pos':(x,names[0]['pos'][1]-90)})
        return cards

    def gift_selected(self,point):
        x,y=point;hsv=cv2.cvtColor(self.frame,cv2.COLOR_BGR2HSV)
        count=0
        for left,right in ((x-72,x-52),(x+52,x+72)):
            crop=hsv[max(400,y-15):min(905,y+20),max(110,left):min(610,right)]
            if crop.size:
                count+=cv2.countNonZero(cv2.inRange(crop,np.array([18,60,185]),np.array([40,255,255])))
        return count>100

    def gifts(self):
        if self.ledger.get('ancestral_gift_done'):
            self.record('仙祠一键赠予','今日已完成','按本角色今日记录跳过');return
        if self.ledger.get('ancestral_gift_submitted'):
            raise TaskStop('今日赠予已提交但结果未确认，保留现场，不重复赠予')
        self.snap()
        if not self.find('gift_dialog'):
            if not self.find('ancestral'):
                if not self.find('immortal_home'):self.home_open()
                self.tap(360,240);self.wait('ancestral')
            self.tap(430,705);self.wait('gift_dialog')
        # Start at the top; selecting portraits is reversible and costs nothing.
        for _ in range(5):
            self.adb('shell','input','swipe',350,450,350,820,350)
            time.sleep(.25)
        chosen=set();seen={};previous=None;stable=0
        for _ in range(36):
            self.snap();self.require('gift_dialog');cards=self.gift_cards()
            if not cards:raise TaskStop('赠予子嗣列表无法识别')
            signature=tuple((c['name'],c['quality']) for c in cards)
            stable=stable+1 if signature==previous else 0;previous=signature
            for card in cards:
                name=card['name'];quality=card['quality']
                if name in seen and seen[name]!=quality:raise TaskStop('赠予子嗣品质识别冲突：'+name)
                seen[name]=quality
                wanted=name=='三角梅' or quality=='甲中'
                self.snap();selected=self.gift_selected(card['pos'])
                if selected!=wanted:
                    self.tap(*card['pos'])
                    end=time.monotonic()+3
                    while time.monotonic()<end:
                        self.snap()
                        if self.gift_selected(card['pos'])==wanted:break
                        time.sleep(.25)
                    else:raise TaskStop('赠予选中状态未确认：'+name)
                if wanted:chosen.add(name)
            if stable>=2:break
            self.log(f'赠予名单：已核对{len(seen)}人，已选择{len(chosen)}人')
            # Short, slow swipes retain overlapping rows and avoid inertial skips.
            self.adb('shell','input','swipe',350,760,350,680,900);time.sleep(1.5)
        else:raise TaskStop('赠予列表未到达底部，未提交赠予')
        if '三角梅' not in chosen:raise TaskStop('赠予未找到三角梅，未提交')
        self.snap()
        header=self.words((500,65,715,110)).replace(' ','')
        total=re.search(r'上限[:：]?(\d+)(?:/(\d+))?',header)
        if not total or len(seen)!=int(total[1]):
            raise TaskStop(f'赠予子嗣未全部核对：识别{len(seen)}人，页面{header}；名单：'+ '、'.join(seen))
        before=self.words((0,1040,720,1280))
        self.ledger['ancestral_gift_submitted']=True;self.ledger_save()
        self.text_button('一键赠予',(250,920,470,1005))
        end=time.monotonic()+15
        while time.monotonic()<end:
            self.snap();after=self.words((0,1040,720,1280))
            if after!=before and any(s in after for s in ('使用','赠予','赠送')):break
            time.sleep(.4)
        else:raise TaskStop('赠予已提交，未识别到新的用药记录，不重复提交')
        self.ledger['ancestral_gift_done']=True
        self.ledger['ancestral_gift_recipients']=sorted(chosen);self.ledger_save()
        self.record('仙祠一键赠予','今日完成','已赠予：'+'、'.join(sorted(chosen)))
        self.snap()
        if self.find('gift_dialog'):self.close('gift_dialog',600,280,'ancestral')
        else:self.wait('ancestral')
        self.back('ancestral','immortal_home');self.back('immortal_home','void_nav')
