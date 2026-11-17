import subprocess,pathlib
p=pathlib.Path('E:/xiuxian/开发资料/video_refactor_20261026/battle_exchange_current.png')
p.write_bytes(subprocess.check_output(['D:/雷电/leidian/LDPlayer9/adb.exe','-s','emulator-5554','exec-out','screencap','-p'],creationflags=subprocess.CREATE_NO_WINDOW))
