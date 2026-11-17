import sys,pathlib,py_compile
sys.path.insert(0,'E:/xiuxian')
from assistant import Bot,RapidOCR
class Fake:
    duel_reward_open=Bot.duel_reward_open
    duel_confirm_result=Bot.duel_confirm_result
    duel_finish_battle=Bot.duel_finish_battle
    def __init__(self,state):self.state=state;self.actions=[]
    def snap(self):pass
    def words(self,*a):return '结果 对方信息 结果奖励' if self.state=='reward' else ''
    def button_positions(self,*a):return [(360,910)] if self.state=='reward' else []
    def tap(self,*a):
        self.actions.append(self.state);self.state={'exit':'reward','reward':'root'}[self.state]
    def find(self,name):return (360,860) if name=='battle_exit' and self.state=='exit' else name=='duel' and self.state=='root'
    def duel_remaining(self):return 3
    def log(self,*a):pass
for state,actions in [('reward',['reward']),('exit',['exit','reward'])]:
    b=Fake(state);b.duel_finish_battle(4);assert b.state=='root' and b.actions==actions
class FastExit(Fake):
    def tap(self,*a):self.actions.append(self.state);self.state='root'
b=FastExit('exit');b.duel_finish_battle(4);assert b.actions==['exit']
b=Fake('root');assert not b.duel_confirm_result() and not b.actions
class Ambiguous(Fake):
    def button_positions(self,*a):return [(360,910),(200,900)]
b=Ambiguous('reward')
try:b.duel_confirm_result();raise AssertionError('ambiguous result should stop')
except RuntimeError:pass
assert not b.actions
import cv2,numpy as np
b=Bot.__new__(Bot);b.ocr=RapidOCR(intra_op_num_threads=2,inter_op_num_threads=2)
p=pathlib.Path(__file__).parent/'duel_result_native.png'
b.frame=cv2.imdecode(np.frombuffer(p.read_bytes(),np.uint8),1)
assert b.duel_reward_open()
points=b.button_positions(('确定','确认'),(150,780,600,1020));assert len(points)==1,points
for name in ('assistant.py','video_tasks.py'):py_compile.compile('E:/xiuxian/'+name,doraise=True)
print('PASS: direct result, exit->result, already returned root, ambiguous confirm blocked; native result confirmed:',points)
