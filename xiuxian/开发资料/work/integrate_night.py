import pathlib
root=pathlib.Path('outputs/太古仙尊实验版')
p=root/'assistant.py';s=p.read_text(encoding='utf-8')
start=s.index('    def night(self):')
end=s.index('    def stars(self):',start)
s=s[:start]+s[end:]
s=s.replace('from palace_tasks import PalaceTasks','from palace_tasks import PalaceTasks\nfrom night_tasks import NightTasks')
s=s.replace('class Bot(Navigation, ApprovedTasks, PalaceTasks):','class Bot(Navigation, NightTasks, ApprovedTasks, PalaceTasks):')
s=s.replace("('navigation','daily_tasks','palace_tasks')","('navigation','daily_tasks','palace_tasks','night_tasks')")
p.write_text(s,encoding='utf-8')
