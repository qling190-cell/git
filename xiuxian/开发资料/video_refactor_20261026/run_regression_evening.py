# -*- coding: utf-8 -*-
import pathlib,subprocess,sys,json,time
folder=pathlib.Path(__file__).parent
results=[]
for p in sorted(folder.glob('test*.py')):
 start=time.time()
 try:
  r=subprocess.run([sys.executable,str(p)],cwd='E:/xiuxian',capture_output=True,encoding='utf-8',errors='replace',timeout=100)
  row={'name':p.name,'code':r.returncode,'seconds':round(time.time()-start,1),'output':r.stdout+r.stderr}
 except subprocess.TimeoutExpired:row={'name':p.name,'code':-1,'seconds':100,'output':'Timed out'}
 results.append(row);print(('PASS' if row['code']==0 else 'FAIL')+' '+p.name,flush=True)
(folder/'regression_20261027_evening.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'{sum(x["code"]==0 for x in results)}/{len(results)} passed',flush=True)
