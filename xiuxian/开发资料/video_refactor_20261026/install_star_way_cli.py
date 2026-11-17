# -*- coding: utf-8 -*-
from pathlib import Path
p=Path('E:/xiuxian/assistant.py');s=p.read_text(encoding='utf-8');s=s.replace("choices=['enlightenment',", "choices=['star_way','enlightenment',");p.write_text(s,encoding='utf-8')
