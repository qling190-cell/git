import pathlib,sys,cv2,numpy as np
sys.path.insert(0,'E:/xiuxian')
from assistant import Bot
b=Bot();b.frame=cv2.imdecode(np.frombuffer(pathlib.Path(__file__).with_name('stars_native.png').read_bytes(),np.uint8),1)
for name in ('star_tribute_badge','star_tribute_badge_right'):
    template=b.images[name]
    for top,bottom in ((420,495),(625,705)):
        scores=cv2.matchTemplate(b.frame[top:bottom,540:610],template,cv2.TM_CCOEFF_NORMED)
        print(name,top,cv2.minMaxLoc(scores)[1::2])
print('name',b.words((415,746,595,806)),b.text((415,746,595,806)))
