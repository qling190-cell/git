import pathlib,sys,subprocess,msvcrt
root=pathlib.Path('outputs/太古仙尊实验版').resolve();sys.path.insert(0,str(root))
from assistant import Bot,Stop
lock=(root/'.running.lock').open('a+b');lock.write(b'0');lock.flush();lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
p=subprocess.run([sys.executable,str(root/'assistant.py'),'inspect'],capture_output=True,encoding='utf-8')
assert '已有助手正在运行' in p.stdout,p.stdout
lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1);lock.close()
b=Bot();(root/'STOP').write_text('stop',encoding='utf-8')
def no_adb(*args):raise AssertionError('STOP should prevent ADB access')
b.adb=no_adb
try:
 b.snap();raise AssertionError('STOP did not stop')
except Stop:pass
finally:(root/'STOP').unlink(missing_ok=True)
print('通过：并行启动被拒绝；停止信号在读取设备前生效。')
