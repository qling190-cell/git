import ast,hashlib,json,pathlib,shutil,subprocess,time,datetime
ROOT=pathlib.Path('E:/xiuxian');OUT=ROOT/'论文报告';OUT.mkdir(exist_ok=True)
SNAP=OUT/'审计资料'/'源码快照';SNAP.mkdir(parents=True,exist_ok=True)
records=[]
for p in sorted(ROOT.glob('*.py')):
    text=p.read_text(encoding='utf-8-sig');tree=ast.parse(text);shutil.copy2(p,SNAP/p.name)
    symbols=[]
    for n in tree.body:
        if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
            symbols.append({'name':n.name,'kind':type(n).__name__,'start':n.lineno,'end':n.end_lineno,
                'methods':[{'name':f.name,'start':f.lineno,'end':f.end_lineno,'doc':ast.get_docstring(f),
                'calls':sorted({ast.unparse(c.func) for c in ast.walk(f) if isinstance(c,ast.Call)})} for f in n.body if isinstance(f,ast.FunctionDef)] if isinstance(n,ast.ClassDef) else [],
                'calls':sorted({ast.unparse(c.func) for c in ast.walk(n) if isinstance(c,ast.Call)}) if not isinstance(n,ast.ClassDef) else []})
    imports=[ast.unparse(n) for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom))]
    records.append({'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'lines':len(text.splitlines()),'symbols':symbols,'imports':imports})
data={'snapshot_time':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'files':records,'human_review':'pending','submission_ready':False}
(OUT/'审计资料'/'source_manifest.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
tests=['test_contracts.py','test_waiting_states.py','test_star_rewards.py','test_freegift.py','test_smallworld.py','test_sword_schedule.py','test_palace_order.py','test_palace_claim_v5.py','test_palace_real_screens.py','test_star_forbidden.py','test_celestial_close.py','test_v5.py']
results=[];python=pathlib.Path('C:/Users/21413/AppData/Local/Programs/Python/Python39/python.exe')
for name in tests:
    p=ROOT/'开发资料/video_refactor_20261026'/name;shutil.copy2(p,OUT/'审计资料'/name)
    start=time.monotonic()
    try:
        r=subprocess.run([str(python),str(p)],cwd=str(ROOT),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=100,creationflags=subprocess.CREATE_NO_WINDOW)
        results.append({'test':name,'exit_code':r.returncode,'elapsed_seconds':round(time.monotonic()-start,3),'output':r.stdout.decode('utf-8','replace')})
    except Exception as ex:results.append({'test':name,'exit_code':None,'error':str(ex)})
    print(name,results[-1]['exit_code'],flush=True)
(OUT/'审计资料'/'test_results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print('SUMMARY',len(records),'files',sum(x['lines'] for x in records),'lines',len(results),'test scripts',flush=True)
