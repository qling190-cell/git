"""Additional operations shown in the supplied video, with verified dialogs."""
import re
import time
import cv2
import numpy as np
from daily_tasks import TaskStop
from forbidden_tasks import run_forbidden,forbidden_map,close_front


class VideoTasks:
    def recover_video_dialog(self):
        celestial=self.words((60,0,660,1200)).replace(' ','')
        if '运转全部' in celestial and any(s in celestial for s in ('天道','人口上限','修士上限')):
            self.video_close(None);return True
        if forbidden_map(self) and any(s in celestial for s in ('今日剩余探索次数','禁区修士','探索进度')):
            close_front(self);return True
        title=self.words((180,60,540,260)).replace(' ','')
        if ('探索' in title or '事件' in title) and self.video_page('smallworld_map',self.frame):
            self.video_close('smallworld_map');return True
        if self.freegift_panel():
            self.video_close('mortal_nav');return True
        body=self.words((80,100,650,1020)).replace(' ','')
        if '获得物品' in body or '获得奖励' in body:
            self.reward_popup('mortal_sect');return True
        if '夺道奖励' in body and '修炼加速' in body:
            self.video_close('stars');return True
        if hasattr(self,'tribute_panel_name') and self.tribute_panel_name():
            self.video_close('stars');return True
        if '运转全部' in body and '天道' in body:
            self.video_close(None);return True
        if '在这里可以兑换各种材料和物品' in body:
            self.video_close('sect_npc');return True
        if '门派首徒' in body and ('俸禄' in body or '切磋' in body):
            self.video_close('mortal_sect');return True
        if '已学习' in body and '兑换' in body and self.video_page('battle_map',self.frame):
            self.video_close('battle_map');return True
        if any(s in body for s in ('闯荡涅元结界','收获已经成熟的药材','种植耗费500灵石',
                                   '种植消耗500灵石','选择药谷种植的药材','每百年只能种植一次','细心等待药材')):
            self.video_close('mortal_sect');return True
        return False

    def video_page(self,name,frame):
        if name=='star_forbidden_map':return (360,500) if forbidden_map(self) else None
        if name=='battle_map':
            header=self.words((65,5,325,95),frame).replace(' ','')
            return (360,500) if any(s in header for s in ('胜境','战境')) else None
        if name=='star_world':
            header=self.words((0,0,720,165),frame).replace(' ','')
            return (360,500) if '星界' in header and '仙缘' in header else None
        if name=='smallworld_map':
            header=self.words((0,0,720,120),frame).replace(' ','')
            if '小世界' in header:return (360,500)
        labels={'sect_npc':('门派首徒','切磋','俸禄'),
                'battle_map':('胜境','战境'),'smallworld_map':('诸星','玄灵','小世界'),
                'star_world':('星界','仙缘')}
        if name not in labels:return None
        body=self.words((0,0,720,1000),frame).replace(' ','')
        count=sum(label in body for label in labels[name])
        minimum=1 if name=='battle_map' else min(2,len(labels[name]))
        return (360,500) if count>=minimum else None

    def video_wait(self,labels,roi=(70,100,650,1120),seconds=12):
        end=time.monotonic()+seconds
        while time.monotonic()<end:
            self.snap();body=self.words(roi).replace(' ','')
            if any(s in body for s in labels):return body
            time.sleep(.3)
        raise TaskStop('视频任务页面未确认：'+' / '.join(labels))

    def video_button(self,labels,roi=(70,150,650,1120)):
        self.snap();hits=self.button_positions(tuple(labels),roi)
        if len(hits)!=1:raise TaskStop('视频任务按钮不能唯一确认：'+' / '.join(labels))
        self.log('点击：'+'/'.join(labels));self.tap(*hits[0])

    def video_close(self,target):
        self.snap()
        for name in ('freegift_close','seize_close','sect_npc_close','modal_close_white','modal_close_red','night_close','sword_opponents_close'):
            if name not in self.meta:continue
            p=self.find(name,roi=(500,0,715,650))
            if p:
                self.tap(*p)
                if target:self.wait(target)
                return
        hsv=cv2.cvtColor(self.frame[0:650,500:715],cv2.COLOR_BGR2HSV)
        red=cv2.bitwise_or(cv2.inRange(hsv,np.array([0,100,130]),np.array([12,255,255])),
                          cv2.inRange(hsv,np.array([170,100,130]),np.array([180,255,255])))
        contours,_=cv2.findContours(red,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        candidates=[]
        for c in contours:
            x,y,w,h=cv2.boundingRect(c)
            if not (18<=w<=48 and 18<=h<=48 and .65<w/h<1.5):continue
            shape=cv2.resize(red[y:y+h,x:x+w],(32,32))>0
            yy,xx=np.indices((32,32));diagonals=(abs(xx-yy)<5)|(abs(xx+yy-31)<5)
            pixels=np.count_nonzero(shape)
            if pixels>80 and np.count_nonzero(shape&diagonals)/pixels>.75:
                candidates.append((x+500+w//2,y+h//2))
        if len(candidates)!=1:raise TaskStop('已确认视频任务弹窗，但关闭X不能唯一识别')
        self.tap(*candidates[0])
        if target:self.wait(target)

    def sect_deadland(self):
        self.mortal_sect_open();self.tap(360,995);self.tap(150,285)
        body=self.video_wait(('闯荡','剩余闯荡','涅元'),(80,350,650,920))
        self.pending['sect_deadland']=False
        if '闯荡收获' in body or '领取' in body:
            self.video_button(('闯荡收获','领取','领取奖励'),(90,790,640,910))
            self.reward_popup('mortal_sect')
            self.ledger['sect_deadland_claimed']=True;self.ledger_save()
            body=self.video_wait(('闯荡三年','闯荡一年','剩余'),(80,350,650,920))
        if re.search(r'\d{1,2}[:：]\d{2}',body):self.pending['sect_deadland']=True
        elif not self.ledger.get('sect_deadland_started'):
            self.video_button(('闯荡三年','闯荡3年'),(90,790,640,910))
            self.video_wait(('剩余闯荡','剩余时间'),(90,740,640,920))
            self.ledger['sect_deadland_started']=True;self.ledger_save();self.pending['sect_deadland']=True
        self.record('门派死地','已处理','领取旧奖励或启动三年闯荡；倒计时期间继续后续任务')
        self.video_close('mortal_sect');self.back('mortal_sect','mortal_nav')

    def sect_herbs(self):
        self.mortal_sect_open();self.tap(360,995);self.tap(150,285)
        self.video_wait(('闯荡','涅元','药谷'),(70,150,650,920))
        self.tap(266,285)
        body=self.video_wait(('选择药谷','成熟','种植','收获'),(80,350,650,1110))
        self.pending['sect_herbs']=False
        if '收获' in body or '采摘' in body:
            self.video_button(('收获药材','收获','采摘'),(180,780,550,890))
            self.reward_popup('mortal_sect')
            self.ledger['sect_herbs_claimed']=True;self.ledger_save()
            body=self.video_wait(('种植耗费','种植消耗','开始种植','每百年只能种植一次'),(80,350,650,920))
        if '每百年只能种植一次' in body:
            self.ledger['sect_herbs_started']=True;self.ledger_save()
        if re.search(r'\d{1,2}[:：]\d{2}',body):self.pending['sect_herbs']=True
        elif not self.ledger.get('sect_herbs_started'):
            if '500灵石' not in body:raise TaskStop('药谷种植费用未确认为500灵石：'+body)
            for point in ((230,580),(360,540),(490,580)):
                self.tap(*point);self.video_wait(('选择种植','涅真花'))
                self.video_button(('涅真花',),(110,400,615,750))
                self.video_wait(('开始种植',))
            self.video_button(('开始种植',),(180,780,550,890))
            self.video_wait(('药材培育中','培育中','成熟'),(80,600,650,1120))
            self.ledger['sect_herbs_started']=True;self.ledger_save();self.pending['sect_herbs']=True
        self.record('门派药谷','已处理','选择三份涅真花，种植费用500灵石；等待成熟时继续后续任务')
        self.video_close('mortal_sect');self.back('mortal_sect','mortal_nav')

    def sect_exchange(self):
        self.mortal_sect_open()
        if self.ledger.get('sect_exchange_done'):
            self.record('门派每日丹药','今日已完成','按本角色记录跳过');self.back('mortal_sect','mortal_nav');return
        self.tap(230,675);self.video_wait(('门派首徒','俸禄','切磋'))
        self.video_button(('兑换',),(300,400,580,850))
        self.video_wait(('丹书','丹道','兑换'),(80,200,650,1000))
        body=self.words((90,300,630,540)).replace(' ','')
        if '1/1' not in body:
            if '100' not in body or '0/1' not in body:raise TaskStop('视频门派每日丹药兑换额度/费用未确认：'+body)
            hits=self.button_positions(('兑换',),(485,330,635,570))
            if not hits:raise TaskStop('门派每日丹药兑换按钮未识别')
            self.tap(*min(hits,key=lambda p:p[1]))
            self.video_wait(('1/1',),(90,300,650,560))
        self.ledger['sect_exchange_done']=True;self.ledger_save()
        self.record('门派每日丹药兑换','今日完成','已确认每日1/1额度，消耗100门派贡献；不兑换其余材料')
        # Two nested close controls, then leave the sect only once.
        self.video_close('sect_npc');self.video_close('mortal_sect')
        self.back('mortal_sect','mortal_nav')

    def freegift_panel(self):
        return '修真礼包' in self.words((140,130,590,325)).replace(' ','')

    def freegift(self):
        self.snap()
        opened=self.freegift_panel()
        if not opened:self.realm('mortal')
        if self.ledger.get('freegift_done'):
            if opened:self.video_close('mortal_nav')
            self.record('修真免费礼包','今日已完成','按本角色记录跳过');return
        if not opened:
            self.snap();entries=self.button_positions(('修真',),(0,130,230,400))
            if len(entries)!=1:
                self.record('修真免费礼包','跳过','未识别到唯一修真入口，继续后续任务');return
            self.log('点击：修真');self.tap(*entries[0])
            self.video_wait(('修真礼包',),(140,130,590,325))
        # Claiming removes the free tier; the paid tiers then move upward.
        self.snap();hits=self.button_positions(('领取',),(90,330,630,1140))
        if len(hits)>1:raise TaskStop('修真免费领取按钮不能唯一确认')
        claimed=False
        if hits:
            self.log('点击：领取');self.tap(*hits[0]);self.pause_animation(.5)
            popup=self.reward_popup('mortal_nav')
            end=time.monotonic()+8
            while time.monotonic()<end:
                self.snap()
                body=self.words((90,330,630,1140)).replace(' ','')
                if self.freegift_panel() and (popup or any(s in body for s in ('已领取','今日已','领取成功'))
                        or not self.button_positions(('领取',),(90,330,630,1140))):
                    claimed=True;break
                time.sleep(.3)
        self.video_close('mortal_nav')
        if claimed:
            self.ledger['freegift_done']=True;self.ledger_save()
            self.record('修真免费礼包','今日完成','免费领取后奖励弹窗或领取入口变化已确认，点击礼包X退出')
        elif hits:raise TaskStop('修真免费礼包领取结果未确认，已关闭礼包；不重复领取')
        else:self.record('修真免费礼包','跳过','当前无免费领取按钮，点击礼包X退出，不操作付费礼包')

    def smallworld(self):
        self.snap()
        headers=[v['text'].replace(' ','') for v in self.text((180,120,540,280)) if v['confidence']>=.8]
        if any(s in ('探索','事件') for s in headers) and self.video_page('smallworld_map',self.frame):
            self.video_close('smallworld_map')
        if not self.video_page('smallworld_map',self.frame):
            self.heaven_travel_open();self.tap(430,40);self.wait('smallworld_map')
        self.smallworld_explore()
        self.smallworld_events()
        self.ledger['smallworld_rules']=2;self.ledger_save()
        self.back('smallworld_map','heaven_nav')

    def smallworld_explore(self):
        self.video_button(('探索',),(30,940,230,1140))
        self.video_wait(('每百年','探索结束','探索中'),(80,100,650,1120))
        self.pending['smallworld']=False
        for _ in range(8):
            self.snap();body=self.words((80,160,650,1130)).replace(' ','')
            claims=self.button_positions(('领取','领取奖励'),(140,700,590,1130))
            running=bool(re.search(r'\d{1,2}[:：]\d{2}',body)) or any(s in body for s in ('探索中','结束还需'))
            if self.ledger.get('smallworld_unconfirmed') and (claims or running):
                self.ledger['smallworld_started']=int(self.ledger.get('smallworld_started',0))+1
                self.ledger['smallworld_unconfirmed']=False;self.ledger_save()
            if len(claims)==1:
                self.tap(*claims[0]);self.pause_animation(.6);self.reward_popup('smallworld_map')
                self.record('小世界探索','已领取','领取旧奖励后继续检查探索次数');continue
            if running:
                self.pending['smallworld']=True;break
            quota=re.search(r'(?:剩余|还可|可探索次数)[：:]?(\d+)次?',body)
            if quota and int(quota[1])==0:break
            if int(self.ledger.get('smallworld_started',0))>=3:break
            if self.ledger.get('smallworld_unconfirmed'):
                raise TaskStop('小世界上次探索提交未确认，保留现场，不重复消耗')
            starts=self.button_positions(('探索','开始探索'),(140,700,590,1130))
            if len(starts)!=1:break
            # A price in premium currency must never be accepted.
            if '仙玉' in self.words((120,700,610,1140)):break
            self.ledger['smallworld_unconfirmed']=True;self.ledger_save()
            self.tap(*starts[0]);self.pause_animation(.6);self.snap()
            confirm=self.words((100,400,620,930)).replace(' ','')
            buttons=self.button_positions(('确定','确认'),(150,550,610,1000))
            if len(buttons)==1 and ('消耗' in confirm or '是否' in confirm):
                if '仙玉' in confirm:
                    self.video_button(('取消',),(100,550,600,1000))
                    self.ledger['smallworld_unconfirmed']=False;self.ledger_save();break
                self.tap(*buttons[0])
            after=self.video_wait(('探索中','结束还需','探索结束','领取'),(90,500,640,1140))
            self.ledger['smallworld_started']=int(self.ledger.get('smallworld_started',0))+1
            self.ledger['smallworld_unconfirmed']=False;self.ledger_save()
            if re.search(r'\d{1,2}[:：]\d{2}',after) or '探索中' in after:
                self.pending['smallworld']=True;break
        self.video_close('smallworld_map')
        self.record('小世界探索','本轮处理结束','每天最多启动3次；计时中保留收尾，有奖励先领取')

    def smallworld_event_options(self):
        # Read only the four gold option bars, not the reward captions below.
        hsv=cv2.cvtColor(self.frame,cv2.COLOR_BGR2HSV)
        mask=cv2.inRange(hsv,np.array([15,80,155]),np.array([40,255,255]))
        contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        boxes=[]
        for c in contours:
            x,y,w,h=cv2.boundingRect(c)
            if 65<x<180 and 350<y<1040 and 420<w<610 and 35<h<100:
                boxes.append((x,y,x+w,y+h))
        return sorted(boxes,key=lambda b:b[1])

    def smallworld_events(self):
        self.video_button(('事件',),(250,940,460,1140))
        self.video_wait(('事件',),(200,0,530,220))
        processed=0
        for _ in range(16):
            if processed>=8:break
            self.snap();options=self.smallworld_event_options()
            if not options:
                body=self.words((60,200,660,1100))
                if any(s in body for s in ('暂无','没有事件','无事件','当前无','暂无事件')):break
                if '获得' in body:
                    # A resolved event remains as a reward page until reopened.
                    self.video_close('smallworld_map')
                    self.video_button(('事件',),(250,940,460,1140))
                    self.video_wait(('事件',),(200,0,530,220));continue
                self.video_close('smallworld_map')
                raise TaskStop('小世界事件四个选项未识别，已退出事件，不盲点')
            if len(options)!=4:
                self.video_close('smallworld_map');raise TaskStop('小世界事件未唯一确认四个选项')
            box=options[1];choice=self.words(box).replace(' ','')
            if not choice:
                self.video_close('smallworld_map');raise TaskStop('小世界第二选项文字未确认')
            if '仙玉' in choice:
                self.record('小世界事件','跳过','第二选项消耗仙玉，不点击：'+choice);break
            before=self.words((50,200,670,1160))
            self.log('小世界事件：选择第二项 '+choice)
            self.tap((box[0]+box[2])//2,(box[1]+box[3])//2)
            self.pause_animation(.5);self.snap()
            confirmation=self.words((100,400,620,930)).replace(' ','')
            buttons=self.button_positions(('确定','确认'),(150,550,610,1000))
            if len(buttons)==1 and any(s in confirmation for s in ('消耗','是否','不足')):
                if '仙玉' in confirmation or '不足' in confirmation:
                    cancel=self.button_positions(('取消',),(100,550,610,1000))
                    if len(cancel)==1:self.tap(*cancel[0])
                    else:raise TaskStop('事件出现仙玉或资源不足提示，未确认')
                    break
                self.tap(*buttons[0]);self.pause_animation(.5)
            popup=self.reward_popup('smallworld_map');self.snap()
            after=self.words((50,200,670,1160))
            if not popup and after==before:
                self.video_close('smallworld_map');raise TaskStop('事件选择后结果未变化，不重复提交')
            processed+=1
        self.video_close('smallworld_map')
        self.record('小世界事件','本轮处理结束',f'处理{processed}个事件；仅选第二项，禁止仙玉消耗')

    def battle_exchange(self):
        self.journey_open();self.tap(220,995)
        self.video_wait(('胜境','战境'),(0,0,720,150))
        self.tap(665,55);self.video_wait(('兑换','已购买','已购'))
        # Basic material rows only; skip token trades and learned books.
        rows=self.ledger.setdefault('battle_exchange_rows',{})
        for key,top,bottom,price in (('basic',230,335,50),('alchemy',495,595,20),('craft',625,725,20)):
            if rows.get(key):continue
            self.snap();row=self.words((90,top,640,bottom)).replace(' ','')
            if '已购' in row or '已学习' in row:continue
            hits=self.button_positions(('兑换',),(470,top,640,bottom))
            if len(hits)!=1:raise TaskStop('战境兑换材料行不能唯一确认：'+row)
            quote=re.search(r'(\d+)/(\d+)',row)
            if not quote or int(quote[2])!=price:raise TaskStop('战境兑换材料报价未确认：'+row)
            if int(quote[1])<price:raise TaskStop('战境材料兑换资源不足：'+row)
            self.tap(*hits[0]);self.snap()
            confirmation=self.words((100,450,620,850))
            if any(k in confirmation for k in ('仙玉','神石','充值','购买次数')):
                raise TaskStop('战境材料兑换出现额外消耗：'+confirmation)
            self.reward_popup('battle_map');self.snap()
            if self.words((90,top,640,bottom)).replace(' ','')==row:
                raise TaskStop('战境材料兑换后计数未变化：'+key)
            rows[key]=True;self.ledger_save()
        self.record('战境材料兑换','已处理','检查视频中三行每日材料兑换，不购买额外次数')
        self.video_close('battle_map');self.tap(35,40);self.wait('journey')
        self.back('journey','void_nav')

    def star_open(self,tab='探索'):
        self.snap()
        if not self.find('stars'):
            self.realm('void');self.tap(213,995);self.wait('stars')
        self.video_button((tab,),(20,70,700,170))

    def observatory(self):
        self.star_open('化身')
        if self.ledger.get('observatory_done'):
            self.record('观星台','今日已完成','按本角色记录跳过');self.back('stars','void_nav');return
        self.video_button(('观星','观星台'),(35,100,250,350))
        self.video_wait(('观星台','膜拜'))
        self.snap();hits=self.button_positions(('膜拜',),(80,450,650,1250))
        if len(hits)!=3:raise TaskStop('观星台未唯一识别到三个膜拜入口')
        for point in sorted(hits,key=lambda p:(p[1],p[0])):
            before=self.words((60,300,660,1250))
            self.tap(*point);time.sleep(.7);self.snap()
            after=self.words((60,300,660,1250))
            self.record('观星台膜拜','已点击','出现新回礼记录' if before!=after else '游戏未出现新回礼，保留该入口当前状态')
        self.ledger['observatory_done']=True;self.ledger_save()
        self.record('观星台','今日完成','已按视频逐个检查三个膜拜入口')
        self.tap(35,40);self.wait('stars');self.back('stars','void_nav')

    def stars(self):
        self.snap()
        if self.ledger.get('seize_reward_done') and self.ledger.get('seize_boost_done'):
            current=self.tribute_panel_name()
            if current:self.collect_tribute(current)
        self.seize_rewards()
        self.star_tributes()
        self.back('stars','void_nav')

    def star_orbit(self):
        self.record('星界天道','已取消','按用户要求暂停星界任务，兼容旧入口但不发送任何点击')

    def star_forbidden(self):
        run_forbidden(self)
