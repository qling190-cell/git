"""Daily enlightenment, creation dew and saint-beast reservation."""
import re
import time
from daily_tasks import TaskStop


class SupplementTasks:
    def star_way_running(self):
        state=self.words((100,885,610,1085)).replace(' ','')
        return bool('修炼' in state and re.search(r'\d{1,3}[:：]\d{2}(?:[:：]\d{2})?',state))

    def star_way(self):
        self.snap()
        if self.ledger.get('star_way_done'):
            if self.find('star_way_panel'):self.video_close('stars')
            self.record('游道修炼','今日已处理','今日已确认修炼倒计时，不重复启动');return
        if not self.find('star_way_panel'):
            self.star_open('探索');self.video_button(('游道',),(270,900,440,1060));self.wait('star_way_panel')
        if not self.star_way_running():
            hint=self.words((90,980,380,1100)).replace(' ','')
            already=('今日' in hint or '今天' in hint) and any(s in hint for s in ('已修炼','已经修炼','修炼过'))
            if not already:
                if self.ledger.get('star_way_phase') == 'submitted':
                    raise TaskStop('游道修炼已提交但结果未确认，不重复点击')

                roi = (90, 980, 380, 1100)
                self.snap()
                hits = self.button_positions(('修炼分身',), roi)

                if len(hits) != 1:
                    raise TaskStop(
                        f'修炼分身匹配到{len(hits)}个按钮；'
                        f'OCR结果：{self.text(roi)}'
                    )

                cost = self.words((120, 1090, 350, 1130))
                if '神石' in cost or '仙玉' in cost:
                    raise TaskStop('修炼分身存在付费资源消耗：' + cost)

                self.ledger['star_way_phase'] = 'submitted'
                self.ledger_save()
                self.log('点击：修炼分身')
                self.tap(*hits[0])
                end=time.monotonic()+12
                while time.monotonic()<end:
                    self.snap()
                    if self.star_way_running():break
                    time.sleep(.3)
                else:raise TaskStop('游道修炼启动后未确认倒计时，不重复启动或点击神游天外')
        self.ledger['star_way_done']=True;self.ledger['star_way_phase']='confirmed';self.ledger_save()
        self.record('游道修炼','已处理','已识别修炼倒计时或今日已修炼，直接退出执行下一任务')
        self.video_close('stars');self.back('stars','void_nav')

    def enlightenment(self):
        if self.ledger.get('enlightenment_done'):
            self.record('悟道室','今日已完成','今日已确认悟道成功，不重复启动');return
        self.snap()
        if not self.find('enlightenment_room'):
            self.island()
            for _ in range(4):
                self.snap();self.require('island')
                hits=self.button_positions(('悟道室',),(0,80,720,920))
                if len(hits)==1:self.tap(*hits[0]);break
                self.adb('shell','input','swipe',650,550,130,550,500);self.pause_animation(.7)
            else:raise TaskStop('宗门悟道室入口未唯一识别')
            self.wait('enlightenment_room')
        before=self.ledger.get('enlightenment_before','')
        if self.ledger.get('enlightenment_phase')!='submitted':
            before=self.words((0,1020,720,1280)).replace(' ','')
            self.ledger.update(enlightenment_phase='submitted',enlightenment_before=before);self.ledger_save()
            self.video_button(('悟道',),(200,630,340,850))
        end=time.monotonic()+60
        while time.monotonic()<end:
            self.snap();self.require('enlightenment_room')
            hint=self.words((100,580,630,900)).replace(' ','')
            after=self.words((0,1020,720,1280)).replace(' ','')
            already=('今日' in hint or '今天' in hint) and any(s in hint for s in ('已经悟道','已悟道','悟道过'))
            receipt=after!=before and '悟道成功' in after and '获得' in after and '修为' in after
            if already or receipt:
                self.ledger['enlightenment_done']=True;self.ledger['enlightenment_phase']='confirmed';self.ledger_save()
                self.record('悟道室','今日完成','已确认悟道成功与修为记录，或今日已悟道提示');break
            time.sleep(.4)
        else:raise TaskStop('悟道结果未确认，保留提交记录，不重复悟道')
        self.back('enlightenment_room','island');self.back('island','heaven_nav')

    def creation_dew(self):
        if self.ledger.get('creation_dew_done'):
            self.record('参天造化露','今日已购买','今日只买1个，不重复购买');return
        self.snap()
        if not self.find('market_shop'):
            self.market_open();self.tap(200,738);self.wait('market_shop')
        self.video_button(('丹方',),(80,190,215,250))
        point=None
        for _ in range(9):
            self.snap();self.require('market_shop')
            point=self.find('creation_dew_item',roi=(85,265,180,1140))
            if point and 330<=point[1]<=1040:break
            self.adb('shell','input','swipe',400,990,400,480,650);self.pause_animation(.7)
        else:raise TaskStop('市场向下查找后未确认参天造化露图标，不购买其他物品')
        y=point[1];roi=(190,max(260,y-60),635,min(1145,y+90))
        row=self.words(roi)
        quote=re.search(r'(\d+)/6000',row);quota=re.search(r'(?<!\d)([012])/2(?!\d)',row)
        if not quote or not quota:raise TaskStop('参天造化露报价或限购未确认：'+row)
        used=int(quota[1])
        # Preserve purchases made manually or by an earlier interrupted run.
        if used>=1:
            self.ledger['creation_dew_done']=True;self.ledger_save()
            self.record('参天造化露','今日已购买','游戏限购已使用至少1次，不再购买')
        elif int(quote[1])<6000:
            self.record('参天造化露','资源不足','需要6000功德，不改用其他资源或物品')
        else:
            if self.ledger.get('creation_dew_phase')=='submitted':
                raise TaskStop('造化露已提交但结果未确认，不重复购买')
            self.tap(*point);self.video_wait(('参天造化露',),(90,300,630,900))
            self.video_close('market_shop')
            self.snap();self.require('market_shop')
            hits=self.button_positions(('兑换',),(480,y-35,635,y+35))
            if len(hits)!=1:raise TaskStop('参天造化露所在行兑换按钮不唯一')
            self.ledger['creation_dew_phase']='submitted';self.ledger_save()
            self.tap(*hits[0]);self.reward_popup('market_shop')
            end=time.monotonic()+12
            while time.monotonic()<end:
                self.snap();after=self.words(roi)
                count=re.search(r'(?<!\d)([012])/2(?!\d)',after)
                if count and int(count[1])==used+1:break
                time.sleep(.3)
            else:raise TaskStop('造化露购买后限购次数未确认增加1，不重复提交')
            self.ledger['creation_dew_done']=True;self.ledger['creation_dew_phase']='confirmed';self.ledger_save()
            self.record('参天造化露','已购买','确认商品名称，消耗6000功德购买1个，限购计数增加1')
        self.close('market_shop',618,150,'market');self.back('market','island');self.back('island','heaven_nav')

    def saint_beast(self):
        if self.ledger.get('saint_beast_done'):
            self.record('圣兽预约','今日已完成','今日已确认预约，不重复点击');return
        self.snap()
        if not self.find('saint_beast_panel'):
            if not self.find('travel'):
                self.realm('mortal');self.tap(630,995);self.wait('travel')
            self.require('travel');self.tap(650,995);self.wait('saint_beast_panel')
        self.snap();state=self.words((180,1010,550,1120)).replace(' ','')
        if '已预约' not in state:
            if self.ledger.get('saint_beast_phase')=='submitted':raise TaskStop('圣兽预约已提交但未确认，不重复点击')
            self.ledger['saint_beast_phase']='submitted';self.ledger_save()
            self.video_button(('预约','预约封印'),(180,1010,550,1120))
            end=time.monotonic()+12
            while time.monotonic()<end:
                self.snap();state=self.words((100,450,630,1120)).replace(' ','')
                if '已预约' in state or '预约成功' in state:break
                time.sleep(.3)
            else:raise TaskStop('圣兽预约后未确认已预约或预约成功，保留提交记录')
        self.ledger['saint_beast_done']=True;self.ledger['saint_beast_phase']='confirmed';self.ledger_save()
        self.record('圣兽预约','完成','已确认预约状态；每天只预约一次，不参加战斗或兑换')
        self.video_close('travel');self.back('travel','mortal_nav')
