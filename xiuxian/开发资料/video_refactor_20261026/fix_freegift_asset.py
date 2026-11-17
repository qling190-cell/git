import pathlib,json,sys
sys.path.insert(0,'E:/xiuxian')
import cv2,numpy as np
root=pathlib.Path('E:/xiuxian')
frame=cv2.imdecode(np.frombuffer((pathlib.Path(__file__).parent/'freegift_native.png').read_bytes(),np.uint8),1)
box=[610,181,648,217]
(root/'assets'/'freegift_close.png').write_bytes(cv2.imencode('.png',frame[box[1]:box[3],box[0]:box[2]])[1].tobytes())
p=root/'assets.json';meta=json.loads(p.read_text(encoding='utf-8'));meta['freegift_close']={'box':box,'moving':True}
p.write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
import py_compile
py_compile.compile(str(root/'video_tasks.py'),doraise=True)
