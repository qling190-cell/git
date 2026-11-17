import pathlib,zipfile
root=pathlib.Path('outputs/太古仙尊实验版');out=pathlib.Path('outputs/太古仙尊每日助手.zip')
proofs={'20261024-152241-392802','20261024-170215-949802','20261024-185327-784181','20261024-185833-016076','20261024-190412-499862','20261025-012656-887447','20261025-013057-277016'}
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in root.rglob('*'):
  if not p.is_file():continue
  parts=p.relative_to(root).parts
  if '__pycache__' in parts or p.name in ['.running.lock','STOP','PAUSE','PAUSED','ui-state.json','ui-error.log']:continue
  if parts[0]=='logs' and (len(parts)<3 or parts[1] not in proofs):continue
  if parts[0]=='logs' and parts[1]=='20261024-170215-949802' and p.suffix.lower() in ('.jpg','.png'):continue
  z.write(p,pathlib.Path('太古仙尊每日助手')/p.relative_to(root))
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 assert any(n.endswith('/assistant.py') for n in z.namelist())
 assert any(n.endswith('/ui.py') for n in z.namelist())
 assert any(n.endswith('/daily_tasks.py') for n in z.namelist())
 assert any(n.endswith('/palace_tasks.py') for n in z.namelist())
 assert any(n.endswith('/navigation.py') for n in z.namelist())
 assert any(n.endswith('/runtime_control.py') for n in z.namelist())
 assert any(n.endswith('/night_tasks.py') for n in z.namelist())
 assert any(n.endswith('/gift_tasks.py') for n in z.namelist())
 assert any(n.endswith('/report.json') for n in z.namelist())
print('Verified archive:',out.stat().st_size,'bytes')
