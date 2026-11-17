import sys
sys.path.insert(0,'work/vendor')
from rapidocr_onnxruntime import RapidOCR
import cv2
ocr=RapidOCR(intra_op_num_threads=2,inter_op_num_threads=2)
r,_=ocr(cv2.imread('work/current.png'))
for line in r or []: print(line[1],round(line[2],2))
