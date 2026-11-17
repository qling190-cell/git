from pathlib import Path
import sys
sys.path.insert(0, "E:/xiuxian/vendor")
import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR

p = Path("E:/xiuxian/学习资料/learn.png")
if not p.exists():
    raise SystemExit("先按第6节保存learn.png")
frame = cv2.imdecode(np.frombuffer(p.read_bytes(), np.uint8), 1)
if frame is None:
    raise SystemExit("图片无法解码")
ocr = RapidOCR()
result, _ = ocr(frame)
for box, text, confidence in result or []:
    x = sum(point[0] for point in box) / len(box)
    y = sum(point[1] for point in box) / len(box)
    print(text, round(confidence, 3), (int(x), int(y)))
