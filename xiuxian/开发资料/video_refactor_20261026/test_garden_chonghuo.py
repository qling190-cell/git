import sys,pathlib,cv2,numpy as np
sys.path.insert(0,'E:/xiuxian')
from assistant import Bot,RapidOCR
from palace_tasks import PalaceTasks
assert PalaceTasks.garden_action('状态:虫祸')=='除虫'
assert PalaceTasks.garden_action('健康') is None
for state,action in [('虫害','除虫'),('干旱','浇水'),('缺肥','施肥')]:assert PalaceTasks.garden_action(state)==action
b=Bot.__new__(Bot);b.ocr=RapidOCR(intra_op_num_threads=2,inter_op_num_threads=2)
p=pathlib.Path('E:/xiuxian/logs/20261027-160643-250639/0050.jpg');b.frame=cv2.imdecode(np.frombuffer(p.read_bytes(),np.uint8),1)
s=b.words((485,846,652,890));assert PalaceTasks.garden_action(s)=='除虫',s
print('PASS native red 虫祸 state selects 除虫; healthy, water and fertilizer mappings preserved')
