import pathlib,sys,tempfile
sys.path.insert(0,str(pathlib.Path('outputs/太古仙尊实验版').resolve()))
import assistant
calls=[]
class Fake:
    def __init__(self):self.pending={};self.out='test'
    def snap(self):pass
    def run_groups(self,groups):calls.extend(groups);return True
    def log(self,*a):pass
with tempfile.TemporaryDirectory() as folder:
    assistant.ROOT=pathlib.Path(folder);assistant.Bot=Fake
    sys.argv=['assistant.py','provisions'];assistant.main()
assert calls==[('void','虚空',['provisions','gifts'])],calls
print('PASS: standalone provisions CLI dispatch includes gifting.')
