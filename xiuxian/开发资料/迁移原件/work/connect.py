import subprocess,pathlib
adb=r'D:\雷电\leidian\LDPlayer9\adb.exe'
p=pathlib.Path('work/current.png');p.write_bytes(subprocess.check_output([adb,'-s','emulator-5554','exec-out','screencap','-p']))
for args in [['shell','wm','size'],['shell','dumpsys','activity','activities']]:
 r=subprocess.run([adb,'-s','emulator-5554']+args,capture_output=True)
 s=r.stdout.decode('utf-8','replace')
 print(s if args[1]=='wm' else '\n'.join(x for x in s.splitlines() if 'mResumedActivity' in x))
