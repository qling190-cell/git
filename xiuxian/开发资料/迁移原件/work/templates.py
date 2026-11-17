from PIL import Image
from pathlib import Path
p=Path('outputs/太古仙尊实验版/templates')
items=[('main','work/main.png',(10,105,310,285)),('entry','work/main.png',(140,170,184,225)),('panel','work/sign_before.png',(93,282,363,354)),('ready','work/sign_before.png',(155,510,281,595)),('done','work/sign_after.png',(155,510,281,595)),('close','work/sign_before.png',(603,257,642,296))]
for name,src,box in items: Image.open(src).crop(box).save(p/(name+'.png'))
