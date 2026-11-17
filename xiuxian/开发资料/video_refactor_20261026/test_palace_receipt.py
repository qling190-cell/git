import sys,pathlib,cv2,numpy as np
sys.path.insert(0,'E:/xiuxian')
from assistant import Bot,RapidOCR
b=Bot.__new__(Bot);b.ocr=RapidOCR(intra_op_num_threads=2,inter_op_num_threads=2);b.snap=lambda:b.frame
root=pathlib.Path('E:/xiuxian/logs/20261027-160156-529181')
for n,wanted in [(42,False),(43,True),(44,False)]:
 b.frame=cv2.imdecode(np.frombuffer((root/f'{n:04}.jpg').read_bytes(),np.uint8),1)
 assert bool(b.palace_reward_notice('palace_cultivate'))==wanted,n
print('PASS: central real same-cultivation receipt accepted; pre-claim and historical chat rejected')
