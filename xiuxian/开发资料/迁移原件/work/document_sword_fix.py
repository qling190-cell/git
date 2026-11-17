import pathlib,shutil
root=pathlib.Path('outputs/太古仙尊实验版')
live=pathlib.Path('outputs/太古仙尊每日助手/太古仙尊每日助手')
note='\n\n论剑修复（2026-10-25）：每次匹配后直接挑战第一位，不读取对手或自身战力。只处理现有免费次数，保留战后次数减少的验证，不购买次数。补充论剑选择对手弹窗专用红叉模板与页面关闭规则；恢复时先关闭弹窗，再点击游戏内返回箭头。\n'
for name in ('任务顺序.md','验收记录.md'):
    p=root/name
    text=p.read_text(encoding='utf-8')
    if note not in text:p.write_text(text+note,encoding='utf-8')
    shutil.copy2(p,live/name)
