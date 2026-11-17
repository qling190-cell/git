"""Reuse known parent pages; only normal task exits may be retained."""
class Hierarchy:
    def retain_parent(self):
        hold=getattr(self,'_route_hold',None)
        return bool(hold and hold in self.meta and self.find(hold))

    def mortal_sect_open(self):
        for _ in range(3):
            self.snap()
            if self.find('mortal_sect'):return
            if hasattr(self,'recover_video_dialog') and self.recover_video_dialog():continue
            break
        self.realm('mortal');self.tap(270,995);self.wait('mortal_sect')

    def teaching_open(self):
        self.snap()
        if self.find('teaching'):return
        self.island();self.island_label('island_teaching');self.wait('teaching')

    def market_open(self):
        self.snap()
        if self.find('market'):return
        self.island();self.island_label('island_market');self.wait('market')

    def heaven_travel_open(self):
        self.snap()
        if self.find('heaven_travel'):return
        self.realm('heaven');self.tap(650,995);self.wait('heaven_travel')

    def journey_open(self):
        self.snap()
        if self.find('journey'):return
        self.realm('void');self.tap(650,995);self.wait('journey')

    def practice_finish(self):
        self.snap()
        if self.find('master_hint_title'):
            self.click('master_hint_close');self.wait('practice')
        if self.find('practice'):self.close('practice',605,270,'mortal_sect')
        self.back('mortal_sect','mortal_nav')
