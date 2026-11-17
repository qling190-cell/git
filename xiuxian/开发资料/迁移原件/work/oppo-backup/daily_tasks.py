"""用户补充的日常规则；每次消耗前检查页面、物品和计数。"""
import datetime as dt
import json
import pathlib
import re
import time
import cv2
import numpy as np

ROOT=pathlib.Path(__file__).resolve().parent
class TaskStop(RuntimeError):pass

class ApprovedTasks:
    def lecture(self):
        if self.ledger.get('lecture'):
            self.record('掌门大殿训话','今日已处理','按今日记录跳过');return
        self.island();self.island_label('island_hall');self.wait('hall');self.click('hall_lecture')
        message=self.wait_words('hall',(0,1045,720,1250),lambda s:'训' in s and ('今天' in s or '功德' in s))
        if '今天已经' in message:
            self.record('掌门大殿训话','本日已完成','游戏提示今天已经训过话')
        elif '功德' in message:
            self.record('掌门大殿训话','完成',message)
        else:raise TaskStop('掌门训话结果需核查：'+message)
        self.ledger['lecture']=True;self.ledger_save()
        self.back('hall','island');self.back('island','heaven_nav')

    def guard(self):
        self.island();self.island_label('island_teaching');self.wait('teaching');self.tap(527,735)
        if self.wait('guard','guard_none')=='guard_none':
            self.record('宗门护法','已完成','没有弟子需要护法')
        else:
            self.text_button('全部护法',(410,820,600,878));self.snap()
            body=self.words((105,580,610,670))
            if '全部护法' not in body or '100灵石' not in body.replace(' ',''):
                raise TaskStop('全部护法消耗未确认：'+body)
            self.text_button('确定',(410,740,575,810));self.wait('guard')
            names=self.text((100,550,600,610))
            if any(v['confidence']>.85 and len(v['text'])>=2 for v in names):
                raise TaskStop('全部护法后弟子列表仍未清空')
            self.record('宗门护法','完成','全部护法，消耗100灵石')
            self.close('guard',615,404,'teaching')
        self.back('teaching','island');self.back('island','heaven_nav')

    def quiz(self):
        self.island();self.island_label('island_teaching');self.wait('teaching');self.tap(359,738)
        if self.wait('questions','quiz_none')=='quiz_none':
            self.record('宗门答疑','本日完成','游戏提示没有疑惑了')
        else:
            self.text_button('课训',(160,835,310,900));self.snap()
            # 接受用户明确指定的一键解答可能答错的提示，仅匹配答疑语境。
            if not self.find('questions') and not self.find('teaching'):
                body=self.words((105,510,615,745))
                if not any(k in body for k in ('课训','解答','答疑')):raise TaskStop('课训出现未知提示：'+body)
                if not any(k in body for k in ('错误','出错','错误的')):raise TaskStop('课训确认内容不符：'+body)
                self.text_button('确定',(405,735,580,815));self.snap()
            if self.find('questions'):self.close('questions',601,460,'teaching')
            self.wait('teaching');self.tap(359,738)
            if self.wait('quiz_none','questions')!='quiz_none':raise TaskStop('课训后仍有疑惑，保留截图待核查')
            self.record('宗门答疑','完成','已一键课训，接受少量答案可能错误的规则')
        self.back('teaching','island');self.back('island','heaven_nav')

    def practice(self):
        self._v1_practice()
        if self.ledger.get('master_transfer'):return
        self.realm('mortal');self.tap(270,995);self.wait('mortal_sect');self.tap(70,995);self.wait('practice')
        self.text_button('掌门练功',(400,870,590,945));self.snap()
        buttons=[v for v in self.text((120,765,595,825)) if v['confidence']>=.85 and v['text'].replace(' ','')=='传功']
        body=self.words((115,625,610,765))
        if len(buttons)==1 and '掌门' in body:
            self.tap(*buttons[0]['pos']);self.snap()
            # 仅一次，不购买、不自动补充次数；结果必须有明确提示。
            result=self.words((100,420,620,980))
            if not any(k in result for k in ('修炼中','修炼速度','练功速度','传功成功')):
                raise TaskStop('掌门传功结果需核查：'+result)
            self.ledger['master_transfer']=True;self.ledger_save()
            self.record('掌门传功','已执行','使用已有传功机会一次')
        elif '购买' in self.words((120,765,595,825)):
            self.record('掌门传功','等待已有次数','页面仅有购买按钮，未充值、未购买')
        else:raise TaskStop('掌门传功按钮未识别，保留当前界面')
        self.snap()
        if not self.find('practice'):self.tap(582,443);self.wait('practice')
        self.close('practice',605,270,'mortal_sect');self.back('mortal_sect','mortal_nav')

    def ledger_save(self):
        (ROOT/'ledger.json').write_text(json.dumps(self.ledger,ensure_ascii=False,indent=2),encoding='utf-8')

    def home_open(self):
        self.realm('void');self.tap(360,995);self.wait('immortal_home')

    def familycare(self):
        self.home_open();self.tap(360,240);self.wait('ancestral')
        if self.find('ancestral_disabled'):
            self.record('仙祠指点','已完成','一键指点按钮已灰')
        elif not self.ledger.get('ancestral'):
            self.snap();self.require('ancestral')
            hsv=cv2.cvtColor(self.frame[630:785,550:585],cv2.COLOR_BGR2HSV)
            enabled=cv2.countNonZero(cv2.inRange(hsv,np.array([12,80,140]),np.array([40,255,255])))
            if enabled<400:raise TaskStop('仙祠一键指点按钮状态未确认')
            self.tap(567,705);self.wait('ancestral_disabled')
            self.ledger['ancestral']=True;self.ledger_save();self.record('仙祠指点','完成','已一键指点')
        self.back('ancestral','immortal_home');self.tap(530,585);self.wait('tree')
        if not self.ledger.get('tree_claimed'):
            self.text_button('采摘',(275,980,445,1048));self.snap();self.require('tree')
            body=self.words((0,1060,715,1245))
            if '采摘' not in body and '获得' not in self.words((80,420,630,800)):
                raise TaskStop('玄灵树领取结果未确认')
            self.ledger['tree_claimed']=True;self.ledger_save();self.record('玄灵树','已领取','已确认采摘记录')
        else:self.record('玄灵树','今日已处理','按今日记录跳过重复采摘')
        self.back('tree','immortal_home');self.back('immortal_home','void_nav')

    def raid_remaining(self):
        s=self.words((255,861,465,907));m=re.search(r'今日可讨伐次数[:：]?(\d+)',s.replace(' ',''))
        if not m:raise TaskStop('讨伐剩余次数无法读取：'+s)
        return int(m[1])

    def raid(self):
        self.home_open();self.tap(188,945);self.wait('diplomacy');self.tap(360,705);self.wait('raid')
        done=0
        for _ in range(10):
            self.snap();self.require('raid');before=self.raid_remaining()
            if before==0:break
            self.tap(360,995)
            end=time.monotonic()+120;changed=False
            while time.monotonic()<end:
                time.sleep(.7);self.snap()
                if self.find('raid') and self.raid_remaining()==before-1:
                    changed=True;break
            if not changed:raise TaskStop('自动讨伐超时或剩余次数未变化')
            done+=1
        self.record('鸿胪台讨伐','完成本次处理',f'本次自动战斗{done}次，今日剩余{self.raid_remaining()}次')
        self.back('raid','diplomacy');self.back('diplomacy','immortal_home');self.back('immortal_home','void_nav')

    def provisions(self):
        self.home_open();self.tap(188,765);self.wait('food_shop')
        for item in ('人参果','灵机丹','狂击丹'):
            count=int(self.ledger.get('buy_'+item,0))
            for _ in range(1 if count<2 else 0):
                found=False
                for step in range(8):
                    self.snap();self.require('food_shop')
                    hits=[v for v in self.text((75,115,645,1110)) if v['confidence']>=.85 and v['text']==item]
                    if len(hits)==1:
                        ix,iy=hits[0]['pos']
                        if iy<300:
                            self.adb('shell','input','swipe',600,400,600,720,650);time.sleep(1.4);continue
                        card=(max(60,ix-100),max(110,iy-165),min(650,ix+100),iy+35)
                        if self.find('food_soldout',roi=card) or any(k in self.words(card) for k in ('售罄','售馨')):
                            count=2;self.ledger['buy_'+item]=2;self.ledger_save();found='sold';break
                        self.tap(ix,iy);found=True;break
                    # 首先回到顶部，然后逐屏向下寻找精确名称。
                    if step==0:self.adb('shell','input','swipe',600,350,600,1070,600)
                    else:self.adb('shell','input','swipe',600,1040,600,380,600)
                    time.sleep(1.4)
                if not found:raise TaskStop('珍馐坊没有找到：'+item)
                if found=='sold':break
                self.wait('food_buy')
                title=self.words((270,355,465,410));price=self.line((332,817,412,851));quantity=self.line((340,750,378,795))
                quota=self.words((120,875,255,919));m=re.search(r'今日剩余[:：]?(\d+)',quota.replace(' ',''))
                if item not in title or price!='6500' or quantity!='1' or not m:
                    raise TaskStop('珍馐坊物品、单价或数量未确认：'+title+' '+price+' '+quantity+' '+quota)
                remaining=int(m[1])
                if remaining==0:
                    self.tap(599,353);self.wait('food_shop');break
                buy_count=min(2-count,remaining)
                if buy_count==2:
                    self.tap(501,773);self.snap();self.require('food_buy')
                    quantity=self.line((340,750,378,795));total=self.line((332,817,430,851))
                    if quantity!='2' or total!='13000':raise TaskStop('数量加一后未确认2颗/13000仙居币：'+quantity+' '+total)
                balance=self.line((634,13,714,42))
                if not balance.isdigit() or int(balance)<6500*buy_count:raise TaskStop('仙居币余额不足或无法确认')
                self.click('food_buy');self.wait('food_shop')
                self.snap();after=self.line((634,13,714,42))
                if not after.isdigit() or int(after)!=int(balance)-6500*buy_count:
                    raise TaskStop('购买后仙居币扣费未确认：'+item)
                count+=buy_count;self.ledger['buy_'+item]=count;self.ledger_save()
            self.record('珍馐坊'+item,'完成本次处理',f'今日脚本记录购买{count}颗，最多2颗，单价6500仙居币；游戏限购优先')
        self.back('food_shop','immortal_home');self.back('immortal_home','void_nav')

    def pond_remaining(self):
        s=self.words((155,843,565,887));m=re.search(r'剩余(\d+)次',s.replace(' ',''))
        if not m:raise TaskStop('游心塘次数无法读取：'+s)
        return int(m[1])

    def pond(self):
        self.home_open();self.tap(530,765);self.wait('pond');done=0
        for _ in range(3):
            self.snap();self.require('pond');before=self.pond_remaining()
            if before==0:break
            if int(self.ledger.get('pond_started',0))>=3:break
            self.tap(360,700);self.wait('fish_cast');self.click('fish_cast')
            self.ledger['pond_started']=int(self.ledger.get('pond_started',0))+1;self.ledger_save()
            self.wait('pond_fish_done',seconds=85);self.click('pond_fish_leave');self.wait('pond')
            if self.pond_remaining()!=before-1:raise TaskStop('游心塘结束后剩余次数未减少')
            done+=1
        self.record('游心塘','完成本次处理',f'本次钓鱼{done}次，每次等待一分钟；当前剩余{self.pond_remaining()}次')
        self.close('pond',629,397,'immortal_home');self.back('immortal_home','void_nav')

    def text_button(self,label,roi=(70,100,650,1150)):
        self.snap()
        hits=[v for v in self.text(roi) if v['confidence']>=.85 and v['text'].replace(' ','')==label]
        if len(hits)!=1:raise TaskStop('按钮文字不能唯一确认：'+label)
        self.log('点击：'+label);self.tap(*hits[0]['pos'])

    def secrets_open(self):
        self.realm('heaven');self.tap(650,995);self.wait('heaven_travel');self.tap(500,995);self.wait('secrets')

    def secrets_back(self):
        self.back('secrets','heaven_travel');self.back('heaven_travel','heaven_nav')

    def tower(self):
        self.realm('heaven');self.tap(650,995);self.wait('heaven_travel');self.tap(210,995);self.wait('tower')
        s=self.words((190,1165,530,1220))
        if '今日已领取' in s:self.record('通天塔每日奖励','已领取','游戏显示今日已领取')
        else:
            hits=[v for v in self.text((190,1165,530,1220)) if v['confidence']>=.85 and v['text'] in ('领取','领取奖励','点击领取')]
            if len(hits)!=1:raise TaskStop('通天塔每日奖励按钮需核查：'+s)
            self.tap(*hits[0]['pos']);self.wait_words('tower',(190,1165,530,1220),lambda s:'今日已领取' in s)
            self.record('通天塔每日奖励','已领取','已确认今日已领取')
        self.back('tower','heaven_travel');self.back('heaven_travel','heaven_nav')

    def demon(self):
        self.secrets_open();self.tap(360,390);self.wait('demon');self.text_button('埋骨地',(440,880,605,945));self.wait('demon_selected')
        s=self.words((285,1025,439,1067));m=re.search(r'今日剩余[:：]?(\d+)次',s.replace(' ',''))
        if not m:raise TaskStop('魔域剩余次数未知：'+s)
        count=int(m[1])
        if count:
            self.text_button('扫荡',(420,975,570,1026));self.snap()
            body=self.words((120,590,615,670)).replace(' ','')
            if f'{count}次埋骨地' not in body or f'{count*100}功德' not in body:
                raise TaskStop('魔域扫荡消耗不符合每次100功德规则：'+body)
            self.text_button('确定',(420,744,570,808));self.wait('demon')
            self.wait_words('demon',(285,1025,439,1067),lambda s:bool(re.search(r'剩余[:：]?\s*0次',s)))
        self.record('魔域埋骨地','完成',f'本次扫荡{count}次；不购买次数')
        self.close('demon',610,221,'secrets');self.secrets_back()

    def hunt(self):
        self.secrets_open();self.tap(360,600);self.wait('hunt');self.snap()
        if self.find('hunt_start') and not self.ledger.get('hunt_started'):
            self.click('hunt_start');self.wait('hunt_cost')
            body=self.words((115,575,607,685)).replace(' ','')
            if '75000陨铁' not in body or '125000木材' not in body:raise TaskStop('仙猎资源报价不符：'+body)
            self.text_button('确定',(410,740,575,810));self.wait('hunt')
            state=self.words((100,1015,620,1120))
            if not re.search(r'\d{2}[:：]\d{2}',state):raise TaskStop('仙猎启动后未出现倒计时：'+state)
            self.ledger['hunt_started']=True;self.ledger_save()
            self.record('仙猎','已启动','使用75000陨铁、125000木材；一天最多新开一次')
        else:self.record('仙猎','保留现有状态','已有仙猎或今日已启动；不重复消耗材料')
        self.close('hunt',610,184,'secrets');self.secrets_back()

    def treasure(self):
        self.secrets_open();self.tap(360,860);self.wait('treasure')
        self.snap();state=self.words((100,985,620,1110))
        if re.search(r'\d{2}[:：]\d{2}',state):
            self.pending['treasure']=True;self.record('降妖寻宝','进行中','保留当前寻宝，完成后先领取')
        else:
            claim=[v for v in self.text((100,970,620,1120)) if v['confidence']>=.85 and v['text'] in ('领取','领取奖励')]
            if len(claim)==1:
                self.tap(*claim[0]['pos']);self.wait('treasure_reward');self.click('treasure_reward_confirm');self.wait('treasure')
                self.record('降妖寻宝','已领取','先领取上一轮奖励，并确认获得物品')
            self.snap();state=self.words((100,985,620,1110))
            if self.ledger.get('treasure_started') or '寻宝已结束' in state:
                self.pending['treasure']=False
                if '寻宝已结束' in state:self.record('降妖寻宝','本期已结束','游戏显示每百年只能寻宝一次，当前没有开始按钮')
            else:
                self.text_button('开始寻宝',(100,970,620,1120));self.snap()
                body=self.words((105,520,615,735))
                if '寻宝' not in body:raise TaskStop('寻宝确认内容不符：'+body)
                # 只确认无额外仙玉/神石/付费购买的寻宝提示。
                if any(k in body for k in ('仙玉','神石','充值','购买')):raise TaskStop('寻宝提示额外费用，停止：'+body)
                self.text_button('确定',(405,735,580,815));self.wait('treasure')
                self.wait_words('treasure',(100,985,620,1110),lambda s:bool(re.search(r'\d{2}[:：]\d{2}',s)))
                self.ledger['treasure_started']=True;self.ledger_save();self.pending['treasure']=True
                self.record('降妖寻宝','已启动','已确认寻宝；下一次处理先领取奖励')
        self.close('treasure',622,184,'secrets');self.secrets_back()

    def signin(self):
        self.wait('main_anchor');self.click('sign_entry');self.wait('sign_panel')
        if self.find('sign_ready'):self.click('sign_ready');self.wait('sign_done')
        else:self.require('sign_done')
        draws=0
        for _ in range(10):
            self.snap();self.require('sign_panel')
            value=self.words((415,560,610,602));m=re.search(r'可抽奖次数[:：]?(\d+)',value.replace(' ',''))
            if not m:raise TaskStop('无法确认签到抽奖次数：'+value)
            before=int(m[1])
            if before==0:break
            self.click('sign_draw');time.sleep(.8);self.snap();self.require('sign_panel')
            after=self.words((415,560,610,602));n=re.search(r'可抽奖次数[:：]?(\d+)',after.replace(' ',''))
            if not n or int(n[1])!=before-1:raise TaskStop('签到抽奖次数未减少')
            draws+=1
        self.record('签到及抽奖','完成',f'今日已签到；本次使用已有抽奖次数{draws}次')
        self.click('sign_close');self.wait('main_anchor')

    def duel(self):
        now=dt.datetime.now(dt.timezone(dt.timedelta(hours=8)))
        if now.weekday()==0 or (now.weekday()==1 and now.hour<10):
            self.record('仙界斗法','未开放','周一休赛，周二北京时间10:00开放');return
        self._v1_duel()

    def travel(self):
        if not self.cfg.get('allow_food'):
            self.pending['travel']=False;self.record('凡间历练','跳过','食物消耗关闭');return
        self.realm('mortal');self.tap(630,995);self.wait('travel');self.click('wander_button');self.wait('wander_panel')
        started=int(self.ledger.get('wander_started',0));limit=min(300,int(self.cfg.get('wander_rounds',300)))
        if self.find('wander_running'):
            self.pending['travel']=True;self.record('凡间神游','进行中',f'今日脚本已登记{started}/{limit}次；等待现有批次完成')
        elif self.ledger.get('wander_reservation'):
            raise TaskStop('上次神游提交结果未确认，需核对日志后处理预留次数，避免重复计数')
        elif started>=limit:
            self.pending['travel']=False;self.record('凡间神游','每日目标已安排',f'今日已登记{started}/{limit}次')
        else:
            self.require('wander_map');self.require('wander_food');self.require('wander_start')
            # 神魂虚弱剩余100次是收益门槛，不是用户指定的每日300次目标。
            self.tap(541,978);self.snap();self.require('wander_panel')
            value=self.line((215,950,425,1005))
            if not value.isdigit():raise TaskStop('神游单批可用上限未识别：'+value)
            cap=int(value);count=min(cap,limit-started)
            if count<=0:
                self.pending['travel']=False;self.record('凡间神游','无法继续','当前可用上限为0；未购买次数')
            else:
                for _ in range(cap-count):
                    self.snap();self.require('wander_panel');self.tap(179,978)
                self.snap();self.require('wander_panel')
                if self.line((215,950,425,1005))!=str(count):raise TaskStop('神游批次未确认')
                self.ledger['wander_reservation']=count;self.ledger_save()
                self.click('wander_start');self.wait('wander_running')
                self.ledger['wander_started']=started+count;self.ledger.pop('wander_reservation',None);self.ledger_save()
                self.pending['travel']=True
                self.record('凡间神游','已启动',f'常羊山本批{count}次、消耗{count*400}食物；今日已安排{started+count}/{limit}次，完成后继续补齐')
        self.close('wander_panel',610,190,'travel');self.back('travel','mortal_nav')

    def jade(self):
        self.island();self.island_label('island_market');self.wait('market')
        self.tap(200,738);self.wait('market_shop')
        bought=0
        for _ in range(20):
            self.snap();self.require('market_shop');self.require('jade_item')
            price=self.line((197,359,325,385));quota=self.line((532,344,593,376))
            m=re.fullmatch(r'(\d+)/20',quota.replace(' ',''));p=re.fullmatch(r'(\d+)/500',price.replace(' ',''))
            if not m or not p:raise TaskStop('玉盒价格或每日限购识别失败：'+price+' '+quota)
            used=int(m[1])
            if used>=20:break
            if int(p[1])<500:raise TaskStop('玉盒所需灵石不足')
            self.click('jade_exchange');self.snap();self.require('market_shop')
            after=self.line((532,344,593,376));n=re.fullmatch(r'(\d+)/20',after.replace(' ',''))
            if not n or int(n[1])!=used+1:raise TaskStop('购买玉盒后限购计数未增加，检查背包')
            bought+=1
        self.record('市场玉盒','完成',f'今日限购已到20；本次购买{bought}个，消耗{bought*500}灵石')
        self.close('market_shop',618,150,'market');self.back('market','island');self.back('island','heaven_nav')

    def fishing_mortal(self):
        self.realm('mortal');self.tap(630,995);self.wait('travel')
        self.click('fish_entry');self.wait('fish_list')
        self.fishing_rounds('凡间幻海之心')
        self.back('fish_list','travel');self.back('travel','mortal_nav')

    def fishing_rounds(self,title):
        done=0
        for _ in range(3):
            self.snap();self.require('fish_list')
            s=self.words((255,1120,480,1165));m=re.search(r'剩余次数[:：]?(\d+)',s.replace(' ',''))
            if not m:raise TaskStop('无法确认钓鱼剩余次数：'+s)
            before=int(m[1])
            if before==0:break
            self.require('fish_heart');self.tap(355,851);self.snap()
            body=self.words((105,510,620,745))
            if '幻海之心' not in body or '4000' not in body or '灵石' not in body:
                raise TaskStop('幻海之心钓鱼费用未确认：'+body)
            self.text_button('确定',(365,730,580,815))
            self.snap()
            if '剩余时间' not in self.words((200,65,520,170)):raise TaskStop('未进入钓鱼场景')
            # 愿者上钩会自动抛竿；未勾选时只点击明确的抛竿按钮。
            hits=[v for v in self.text((40,650,680,1180)) if v['text']=='抛竿' and v['confidence']>=.85]
            if hits:self.tap(*hits[0]['pos'])
            self.wait('fish_done',seconds=85)
            self.click('fish_leave');self.wait('fish_list')
            after=self.words((255,1120,480,1165));n=re.search(r'剩余次数[:：]?(\d+)',after.replace(' ',''))
            if not n or int(n[1])!=before-1:raise TaskStop('钓鱼结束后次数未减少')
            done+=1
        self.record(title,'完成本次处理',f'完成{done}次，每次抛竿后等待一分钟；以游戏剩余次数为准')
