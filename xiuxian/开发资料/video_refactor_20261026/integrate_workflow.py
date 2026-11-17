# -*- coding: utf-8 -*-
import pathlib,re
root=pathlib.Path('E:/xiuxian')
p=root/'navigation.py';s=p.read_text(encoding='utf-8')
start=s.index('DAILY_GROUPS=[');end=s.index('TASK_LABELS=',start)
s=s[:start]+'from workflow import DAILY_GROUPS, FINISH_GROUPS, WORKFLOW_VERSION, shared_parent\n\n'+s[end:]
s=s.replace("'night':'丽晶异域夜猎'","'night':'已驻扎洞天夜猎（四处各15次）'")
s=s.replace("TASK_LABELS={","TASK_LABELS={\n    'sect_deadland':'门派死地闯荡','sect_herbs':'药谷种植收获',\n    'sect_exchange':'门派丹书兑换','freegift':'修真免费礼包',\n    'smallworld':'小世界探秘','battle_exchange':'战境材料兑换',\n    'observatory':'观星台膜拜','star_orbit':'星界每日运转',")
s=s.replace("self.daily_progress=data","self.daily_progress=data\n        data['workflow_version']=WORKFLOW_VERSION",1)
begin=s.index("                secrets={'demon','hunt','treasure'}")
finish=s.index("                if hasattr(self,'daily_progress'):",begin)
s=s[:begin]+'''                following=selected[index+1] if index+1<len(selected) else None
                self._route_hold=shared_parent(task,following)
                self._secrets_batch=self._route_hold=='secrets' or (task=='tower' and self._route_hold=='heaven_travel')
                self._palace_batch=self._route_hold=='palace_map'
                self._home_batch=self._route_hold=='immortal_home'
                try:result=self.run_task(task)
                finally:
                    self._route_hold=None
                    self._secrets_batch=False;self._palace_batch=False;self._home_batch=False
'''+s[finish:]
p.write_text(s,encoding='utf-8')
p=root/'assistant.py';s=p.read_text(encoding='utf-8')
s=s.replace('from gift_tasks import GiftTasks','from gift_tasks import GiftTasks\nfrom hierarchy import Hierarchy\nfrom video_tasks import VideoTasks')
s=s.replace('class Bot(Navigation, NightTasks, GiftTasks, ApprovedTasks, PalaceTasks):',
            'class Bot(Navigation, Hierarchy, NightTasks, GiftTasks, VideoTasks, ApprovedTasks, PalaceTasks):')
s=s.replace("'night_tasks','gift_tasks')","'night_tasks','gift_tasks','video_tasks')")
s=s.replace("        spec = self.meta[name]","        if name not in self.meta:return self.video_page(name,frame)\n        spec = self.meta[name]")
s=s.replace("        self.snap();self.require(page);self.tap(35,40);self.wait(target)",
            "        self.snap()\n        if self.retain_parent():return\n        self.require(page);self.tap(35,40);self.wait(target)")
s=s.replace("        self.realm('heaven');self.tap(70,995);self.wait('island')",
            "        self.snap()\n        if self.find('island'):return\n        self.realm('heaven');self.tap(70,995);self.wait('island')")
s=s.replace("self.realm('mortal');self.tap(270,995);self.wait('mortal_sect')","self.mortal_sect_open()")
s=s.replace("self.island();self.island_label('island_teaching');self.wait('teaching')","self.teaching_open()")
s=s.replace("self.island();self.island_label('island_market');self.wait('market')","self.market_open()")
s=s.replace("self.realm('void');self.tap(360,995);self.wait('immortal_home')","self.home_open()")
start=s.index('    def stars(self):');end=s.index('    def family(self):',start)
s=s[:start]+s[end:]
s=s.replace("            success=bot.continue_open_daily_task()\n            success=bot.run_groups(DAILY_GROUPS) and success", "            success=bot.run_groups(DAILY_GROUPS)")
extra=['sect_deadland','sect_herbs','sect_exchange','freegift','smallworld','battle_exchange','observatory','star_orbit']
s=s.replace("choices=['all','resume'",'choices='+repr(extra)[:-1]+",'all','resume'")
p.write_text(s,encoding='utf-8')
p=root/'daily_tasks.py';s=p.read_text(encoding='utf-8')
s=s.replace("self.island();self.island_label('island_teaching');self.wait('teaching')","self.teaching_open()")
s=s.replace("self.island();self.island_label('island_market');self.wait('market')","self.market_open()")
s=s.replace("self.realm('mortal');self.tap(270,995);self.wait('mortal_sect')","self.mortal_sect_open()")
s=s.replace("self.recover_to_main('练功结束：先关闭X，再点返回')","self.practice_finish()")
s=s.replace("    def home_open(self):\n        self.realm('void');self.tap(360,995);self.wait('immortal_home')",
            "    def home_open(self):\n        self.snap()\n        if self.find('immortal_home'):return\n        self.realm('void');self.tap(360,995);self.wait('immortal_home')")
s=s.replace("self.realm('heaven');self.tap(650,995);self.wait('heaven_travel');self.tap(500,995);self.wait('secrets')",
            "self.heaven_travel_open();self.tap(500,995);self.wait('secrets')")
s=s.replace("self.realm('heaven');self.tap(650,995);self.wait('heaven_travel');self.tap(210,995);self.wait('tower')",
            "self.heaven_travel_open();self.tap(210,995);self.wait('tower')")
p.write_text(s,encoding='utf-8')
p=root/'palace_tasks.py';s=p.read_text(encoding='utf-8')
s=s.replace("tasks=('palace_lamp','palace_garden','palace_cultivate','palace_court')",
            "tasks=('palace_cultivate','palace_court','palace_lamp','palace_garden')")
p.write_text(s,encoding='utf-8')
print('Video workflow, shared-parent routing, helpers and new task dispatch installed.')
