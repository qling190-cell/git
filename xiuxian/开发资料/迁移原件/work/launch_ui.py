import pathlib,subprocess,json
root=pathlib.Path('outputs/太古仙尊实验版').resolve()
pythonw=r'C:\Users\21413\AppData\Local\Programs\Python\Python39\pythonw.exe'
err=(root/'ui-error.log').open('ab')
p=subprocess.Popen([pythonw,str(root/'ui.py'),'--start'],cwd=str(root),stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=err,creationflags=subprocess.CREATE_NEW_PROCESS_GROUP|subprocess.DETACHED_PROCESS)
print(json.dumps({'ui_pid':p.pid},ensure_ascii=False))
