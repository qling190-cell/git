import pathlib,sys,cv2,numpy as np
sys.path.insert(0,str(pathlib.Path('outputs/太古仙尊实验版').resolve()))
from assistant import Bot
from gift_tasks import GiftTasks
import gift_tasks
b=Bot()
for image,expected in [('gift_before',False),('gift_selected',True)]:
    b.frame=cv2.imdecode(np.frombuffer(pathlib.Path(f'work/{image}.png').read_bytes(),np.uint8),1)
    assert b.find('gift_dialog')
    cards=b.gift_cards();special=next(c for c in cards if c['name']=='三角梅')
    assert special['quality']=='甲下'
    assert b.gift_selected(special['pos'])==expected,(image,special)
    assert next(c for c in cards if c['name']=='朱槿')['quality']=='甲中'
print('PASS: real screenshot name/quality pairing and selection glow.')

class Fake(GiftTasks):
    def __init__(self):
        self.ledger={};self.page=0;self.selected={'桃花'};self.submissions=0
        self.pending={};self.phase='before';self.finished=False
    def snap(self):pass
    def find(self,name):return name=='gift_dialog'
    def require(self,*a):pass
    def log(self,*a):pass
    def record(self,*a):pass
    def ledger_save(self):pass
    def gift_cards(self):
        rows=[('三角梅','甲下'),('桃花','甲下')] if not self.page else [('朱槿','甲中'),('扶桑','甲中')]
        return [{'name':name,'quality':q,'pos':(200+i*150,500)} for i,(name,q) in enumerate(rows)]
    def gift_selected(self,point):
        card=next(c for c in self.gift_cards() if c['pos']==point)
        return card['name'] in self.selected
    def tap(self,*point):
        name=next(c['name'] for c in self.gift_cards() if c['pos']==point)
        if name in self.selected:self.selected.remove(name)
        else:self.selected.add(name)
    def adb(self,*args):self.page=0 if args[4]==450 else 1
    def words(self,roi):
        if roi==(500,65,715,110):return '子嗣上限：4/4'
        return '三角梅使用丹药' if self.phase=='after' else '旧记录'
    def text_button(self,*a):
        assert self.ledger.get('ancestral_gift_submitted')
        assert self.selected=={'三角梅','朱槿','扶桑'}
        self.submissions+=1;self.phase='after'
    def close(self,*a):self.finished=True
    def wait(self,name):assert name=='ancestral';self.finished=True
    def back(self,*a):pass

original=gift_tasks.time.sleep;gift_tasks.time.sleep=lambda _:None
try:
    b=Fake();b.gifts()
    assert b.ledger['ancestral_gift_done'] and b.submissions==1 and b.finished
    b.gifts();assert b.submissions==1
    class AutoClose(Fake):
        def find(self,name):return name=='gift_dialog' and self.phase!='after'
    b=AutoClose();b.gifts();assert b.finished and b.submissions==1
    b=Fake();b.ledger['ancestral_gift_submitted']=True
    try:b.gifts()
    except RuntimeError:pass
    else:raise AssertionError('uncertain submission repeated')
finally:gift_tasks.time.sleep=original
print('PASS: special name plus 甲中, unwanted deselection, full-list validation, once daily, uncertain submission not repeated.')
