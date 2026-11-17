import pathlib,sys
sys.path.insert(0,'E:/xiuxian')
from assistant import Bot,RapidOCR
import cv2,numpy as np
class Fake:
    family_select_target=Bot.family_select_target
    def __init__(self,selected,visible=False):self.selected=selected;self.visible=visible;self.actions=[]
    def snap(self):pass
    def require(self,*a):pass
    def words(self,*a):return '征收地点：'+self.selected
    def log(self,*a):pass
    def button_positions(self,*a):return [(230,600)] if self.visible else []
    def tap(self,*a):self.selected='太上凰宗';self.actions.append('select')
    def adb(self,*a):self.visible=True;self.actions.append('scroll')
b=Fake('太上凰宗');b.family_select_target('太上凰宗');assert not b.actions
b=Fake('九尾狐宗');b.family_select_target('太上凰宗');assert b.actions==['scroll','select']
b=Bot.__new__(Bot);b.ocr=RapidOCR(intra_op_num_threads=2,inter_op_num_threads=2)
p=pathlib.Path('E:/xiuxian/logs/20261027-150525-619231/0117.jpg')
b.frame=cv2.imdecode(np.frombuffer(p.read_bytes(),np.uint8),1)
assert '太上凰宗' in b.words((92,899,470,940)).replace(' ',''),b.words((92,899,470,940))
print('PASS: reuse selected target, scroll only if needed, actual failed screenshot already selected target')
