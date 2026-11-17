from PIL import Image
from pathlib import Path
p=Path('outputs/太古仙尊实验版/assets/mortal_nav.png')
Image.open('work/current.png').crop((240,958,311,1044)).save(p)
