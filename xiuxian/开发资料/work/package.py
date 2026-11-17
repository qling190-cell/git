import pathlib,zipfile
root=pathlib.Path('outputs/太古仙尊实验版')
out=pathlib.Path('outputs/太古仙尊每日助手.zip')
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in root.rglob('*'):
  if not p.is_file():continue
  parts=p.relative_to(root).parts
  if any(x in ['logs','__pycache__'] for x in parts) or p.name in ['.running.lock','STOP','ui-state.json']:continue
  z.write(p,pathlib.Path('太古仙尊每日助手')/p.relative_to(root))
print('Package:',out.resolve(),'bytes:',out.stat().st_size)
