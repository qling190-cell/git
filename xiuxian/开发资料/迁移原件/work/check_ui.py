import pathlib,sys
sys.path.insert(0,str(pathlib.Path('outputs/太古仙尊实验版').resolve()))
from ui import App
app=App();app.root.withdraw();app.root.update_idletasks()
print('UI built; requested width:',app.root.winfo_reqwidth(),'tasks:',len(__import__('ui').TASKS),'watch default:',app.watch.get())
app.root.destroy()
