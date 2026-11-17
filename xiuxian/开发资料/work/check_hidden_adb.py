import ctypes,json,pathlib,subprocess,sys
root=pathlib.Path(__file__).resolve().parents[1]/'outputs'/'太古仙尊实验版'
sys.path.insert(0,str(root))
from assistant import Bot
b=Bot.__new__(Bot)
b.cfg=json.loads((root/'config.json').read_text(encoding='utf-8-sig'))
original=subprocess.check_output
def child_probe(command,**kwargs):
    assert command[0]==b.cfg['adb']
    assert kwargs['creationflags'] & subprocess.CREATE_NO_WINDOW
    assert kwargs['stdin']==subprocess.DEVNULL and kwargs['stderr']==subprocess.PIPE
    python=str(pathlib.Path(sys.executable).with_name('python.exe'))
    return original([python,'-c','import ctypes; print(ctypes.windll.kernel32.GetConsoleWindow())'],**kwargs)
try:
    subprocess.check_output=child_probe
    assert b.adb('shell','echo','probe').strip()==b'0'
finally:subprocess.check_output=original
assert b.adb('shell','echo','hidden-adb-ok').strip()==b'hidden-adb-ok'
(root.parent.parent/'work'/'hidden-adb-result.json').write_text(json.dumps({'passed':True,'launcher_console':int(ctypes.windll.kernel32.GetConsoleWindow()),'child_console':0,'real_adb_echo':'ok'}),encoding='utf-8')
