"""探星禁区：游戏剩余次数优先，拒绝未授权的随机事件消耗。"""
import re,time
import cv2
import numpy as np
from daily_tasks import TaskStop

def material_shortage(body):
    return '不足' in body.replace('实力不足','').replace('修为不足','')

def event_positions(bot,labels):
    hits=bot.button_positions(labels,(100,600,620,1120))
    if len(hits)==1 or not hasattr(bot,'text'):return hits
    # Use the already-read full modal as a second observation. Local crops can
    # change OCR segmentation even when the full frame reads the button well.
    values=bot.text((50,100,670,1200));found=[]
    for item in values:
        x,y=item['pos']
        if (item['confidence']>=.8 and item['text'].replace(' ','') in labels
                and 150<x<600 and 700<y<1050):
            if not any(abs(x-p[0])<20 and abs(y-p[1])<20 for p in found):found.append((x,y))
    return found

def front_x_points(bot):
    frame=bot.frame
    hsv=cv2.cvtColor(frame[:1000,500:715],cv2.COLOR_BGR2HSV)
    mask=cv2.bitwise_or(cv2.inRange(hsv,np.array([0,120,190]),np.array([13,255,255])),
                       cv2.inRange(hsv,np.array([170,120,190]),np.array([180,255,255])))
    contours,_=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    hits=[]
    for c in contours:
        x,y,w,h=cv2.boundingRect(c)
        if not (18<=w<=55 and 18<=h<=55 and .65<w/h<1.5):continue
        shape=cv2.resize(mask[y:y+h,x:x+w],(32,32))>0
        yy,xx=np.indices((32,32));diagonal=(abs(xx-yy)<6)|(abs(xx+yy-31)<6)
        if shape.sum()>80 and (shape&diagonal).sum()/shape.sum()>.75:hits.append((x+500+w//2,y+h//2))
    return hits

def close_front(bot):
    bot.snap();hits=front_x_points(bot)
    if len(hits)!=1:raise TaskStop('禁区当前最上层关闭X未唯一确认')
    bot.tap(*hits[0])

def accept_free_event(bot,body):
    if '收下礼物' not in body:return False
    if getattr(bot,'frame',None) is not None and not front_x_points(bot):return False
    event=bot.words((95,450,625,800)).replace(' ','')
    if any(s in event for s in ('消耗','花费','支付','购买','仙玉','神石')):
        raise TaskStop('禁区礼物事件出现费用，未自动接受')
    choices=bot.button_positions(('收下礼物',),(100,650,620,1120))
    if len(choices)!=1:raise TaskStop('禁区礼物领取按钮不能唯一确认')
    bot.tap(*choices[0]);end=time.monotonic()+8
    while time.monotonic()<end:
        bot.pause_animation(.3);bot.snap()
        if not bot.button_positions(('收下礼物',),(100,650,620,1120)):
            bot.record('禁区随机事件','已收下礼物','确认收下礼物按钮已消失，继续后续探索');return True
    raise TaskStop('禁区收下礼物后状态未变化，不重复领取')

def forbidden_map(bot):
    header=bot.words((65,0,390,100)).replace(' ','')
    return '大苦灭境' in header or '大苦灭境' in bot.words((70,120,650,370)).replace(' ','')

def run_forbidden(bot):
    if getattr(bot,'ledger',{}).get('star_forbidden_rules')==1:
        bot.record('探星禁区','今日已完成','今日已确认探索剩余0，不重复进入禁区');return
    bot.snap()
    current=bot.words((50,100,670,1255)).replace(' ','')
    continuing=(('硬闯' in current and '离开' in current) or '禁区通道' in current or
                '点击屏幕继续' in current or ('神秘僧人' in current and '伤害' in current))
    if not forbidden_map(bot) and not continuing:
        bot.star_open('禁区');bot.snap()
        if '未知禁区' not in bot.words((70,180,660,1190)):
            raise TaskStop('禁区入口未确认')
        bot.tap(200,390)
    started=0;initial=None;last_quota=None
    for _ in range(80):
        bot.pause_animation(.5);bot.snap();body=bot.words((50,100,670,1200)).replace(' ','')
        if '点击屏幕继续' in body:
            bot.video_button(('点击屏幕继续',),(120,1050,600,1255));continue
        if '禁区通道' in body and not forbidden_map(bot):continue
        if '硬闯' in body and '离开' in body:
            bot.video_button(('硬闯',),(100,650,620,850));continue
        if accept_free_event(bot,body):continue
        if '退出' in body and any(s in body for s in ('伤害','生命','战斗')):
            point=bot.find('battle_exit')
            if point:bot.tap(*point)
            else:bot.pause_animation(1)
            continue
        battles=event_positions(bot,('战斗','迎战','挑战'))
        if len(battles)==1 and forbidden_map(bot):
            bot.tap(*battles[0]);bot.record('禁区随机事件','开始战斗','按授权挑战事件敌人');continue
        if material_shortage(body) and forbidden_map(bot):
            choices=bot.button_positions(('确定','确认','取消'),(100,500,620,1150))
            if len(choices)==1:bot.tap(*choices[0])
            else:close_front(bot)
            bot.record('禁区随机事件','已跳过','材料不足，保留材料并继续后续事件');continue
        if any(s in body for s in ('给予灵草','给予材料','给予矿石','给予灵石','委婉回绝','拒绝','离开')) and forbidden_map(bot):
            gifts=event_positions(bot,('给予灵草','给予材料','给予矿石','给予灵石','帮助','相助'))
            event=bot.words((95,450,625,800)).replace(' ','')
            if len(gifts)==1 and not any(s in event for s in ('仙玉','神石')):
                bot.tap(*gifts[0]);bot.pause_animation(.5);bot.snap()
                after=bot.words((60,300,660,1150)).replace(' ','')
                if material_shortage(after):
                    choices=bot.button_positions(('确定','确认','取消'),(100,500,620,1150))
                    if len(choices)==1:bot.tap(*choices[0])
                    # The event remains on screen after a shortage notice.
                    bot.snap();reject=bot.button_positions(('委婉回绝','拒绝','离开'),(100,600,620,1120))
                    if len(reject)==1:bot.tap(*reject[0])
                    else:close_front(bot)
                    bot.record('禁区随机事件','已跳过','材料不足，继续下一个事件')
                else:
                    remaining=bot.button_positions(('给予灵草','给予材料','给予矿石','给予灵石','帮助','相助'),(100,600,620,1120))
                    if remaining:raise TaskStop('禁区给予材料后结果尚未变化，不重复给予')
                    bot.record('禁区随机事件','已选择','按授权给予材料；继续确认游戏结果')
                continue
            choices=bot.button_positions(('委婉回绝','拒绝','离开'),(100,600,620,1120))
            if len(choices)==1:
                bot.tap(*choices[0]);bot.record('禁区随机事件','已跳过','未确认材料操作或涉及仙玉、神石，继续后续');continue
        if any(s in body for s in ('获得物品','获得奖励')):
            bot.reward_popup('star_forbidden_map');continue
        if not forbidden_map(bot):continue
        quota=re.search(r'今日剩余探索次数[：:]?(\d+)/(\d+)',body)
        if quota:
            left=int(quota[1])
            if initial is None:initial=left
            previous=bot.ledger.get('star_forbidden_transaction')
            if previous is not None and left<int(previous):
                bot.ledger['star_forbidden_transaction']=None;bot.ledger_save()
            if last_quota is not None and left<last_quota:
                bot.ledger['star_forbidden_transaction']=None;bot.ledger_save();last_quota=None
            if left==0:
                # Close each modal individually, then return once to the star tabs.
                close_front(bot);bot.wait('star_forbidden_map')
                bot.tap(35,40);bot.wait('stars');bot.back('stars','void_nav')
                bot.ledger['star_forbidden_rules']=1;bot.ledger_save()
                bot.record('探星禁区','今日探索完成',f'游戏剩余次数0；本轮提交{started}次；允许材料与战斗，材料不足跳过，不购买次数');return
            if '探索进度' in body:
                if bot.ledger.get('star_forbidden_transaction')==left:
                    raise TaskStop('禁区上次探索提交尚未确认，不重复消耗次数')
                bot.ledger['star_forbidden_transaction']=left;bot.ledger_save();last_quota=left
                bot.video_button(('探索',),(220,690,510,820));started+=1;continue
            if all(s in body for s in ('孤独园','远古遗迹','仙门遗址')):
                idx=min(3,max(0,int(quota[2])-left))
                bot.tap(*((210,520),(510,520),(210,740),(510,740))[idx]);continue
            # A random result may stay open after the quota has already changed.
            close_front(bot);continue
        if any(s in body for s in ('探索者','禁区修士')):
            raise TaskStop('禁区事件选项尚未确认，不点击背景探索按钮：'+body[:200])
        if getattr(bot,'frame',None) is not None and front_x_points(bot):
            raise TaskStop('禁区仍有未处理的前景弹窗，不点击背景探索：'+body[:200])
        footer=bot.words((60,930,660,1060)).replace(' ','')
        if all(s in footer for s in ('探索','御敌','感悟')):
            bot.video_button(('探索',),(60,930,235,1060));continue
        # Known reward/result dialogs can be dismissed using only their foreground X.
        if any(s in body for s in ('禁区修士','探索结束','获得','没有收获')):
            close_front(bot);continue
        raise TaskStop('禁区出现尚未支持的事件，保留现场：'+body[:220])
    raise TaskStop('禁区处理等待超时，未标记完成')
