"""本机运行面板；仅启动同目录脚本。"""
import json
import pathlib
import queue
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox

ROOT=pathlib.Path(__file__).resolve().parent
TASKS={'全部日常':'all','倒计时收尾':'finish','签到':'signin','凡间神游':'travel','门派练功':'practice','宗门禁地':'forbidden','宗门护法':'guard','宗门答疑':'quiz','仙界斗法':'duel','论剑':'sword','市肆博戏':'gamble','虚空夜猎':'night','家族征收':'family','检查探星禁区':'stars','检查传功消耗':'transfer','检查仙猎消耗':'hunt','检查当前画面':'inspect'}

class App:
    def __init__(self):
        self.root=tk.Tk();self.root.title('太古仙尊 · 每日助手');self.root.geometry('820x630')
        self.proc=None;self.messages=queue.Queue()
        cfg=json.loads((ROOT/'config.json').read_text(encoding='utf-8-sig'))
        body=ttk.Frame(self.root,padding=18);body.pack(fill='both',expand=True)
        ttk.Label(body,text='太古仙尊 · 每日助手',font=('Microsoft YaHei UI',19,'bold')).pack(anchor='w')
        ttk.Label(body,text='vivo 版 · 雷电 720×1280 · 登录后停在角色主界面',font=('Microsoft YaHei UI',10)).pack(anchor='w',pady=(6,14))
        row=ttk.Frame(body);row.pack(fill='x')
        self.task=tk.StringVar(value='全部日常')
        ttk.Combobox(row,textvariable=self.task,values=list(TASKS),state='readonly',width=20).pack(side='left')
        self.start_btn=ttk.Button(row,text='开始',command=self.start);self.start_btn.pack(side='left',padx=10)
        self.stop_btn=ttk.Button(row,text='停止',command=self.stop,state='disabled');self.stop_btn.pack(side='left')
        ttk.Button(row,text='打开运行记录',command=self.open_logs).pack(side='right')
        opts=ttk.LabelFrame(body,text='普通资源',padding=10);opts.pack(fill='x',pady=14)
        self.food=tk.BooleanVar(value=cfg['allow_food']);self.gamble=tk.BooleanVar(value=cfg['allow_gamble_lingshi'])
        ttk.Checkbutton(opts,text='允许神游消耗食物（每轮400）',variable=self.food).grid(row=0,column=0,sticky='w')
        ttk.Label(opts,text='最多轮数').grid(row=0,column=1,padx=(18,4))
        self.rounds=tk.StringVar(value=str(cfg['wander_rounds']))
        ttk.Spinbox(opts,from_=1,to=100,textvariable=self.rounds,width=6).grid(row=0,column=2)
        ttk.Checkbutton(opts,text='允许博戏消耗灵石（每次2000，每日最多10次）',variable=self.gamble).grid(row=1,column=0,columnspan=3,sticky='w',pady=(8,0))
        self.practice=tk.BooleanVar(value=cfg.get('allow_practice_lingshi',True))
        ttk.Checkbutton(opts,text='允许门派练功消耗1000灵石',variable=self.practice).grid(row=2,column=0,columnspan=3,sticky='w',pady=(8,0))
        self.watch=tk.BooleanVar(value=True)
        ttk.Checkbutton(body,text='自动收尾：每5分钟检查倒计时，最长8小时；请保持游戏在主界面',variable=self.watch).pack(anchor='w',pady=(0,10))
        ttk.Label(body,text='仙玉、神石、丹药、兑换和背包清理均保持关闭。运行时请暂停手动操作。').pack(anchor='w')
        self.status=tk.StringVar(value='就绪')
        ttk.Label(body,textvariable=self.status).pack(anchor='w',pady=8)
        self.output=tk.Text(body,wrap='word',font=('Microsoft YaHei UI',10),background='#f5f6fa',relief='flat')
        self.output.pack(fill='both',expand=True)
        self.output.insert('end','当前支持的任务见上方下拉菜单。\n探索和神游有倒计时，启动后会保留任务；完成后可再次运行领取。\n未知题目会记录并跳过，异常画面会停止并保存截图。\n')
        self.root.protocol('WM_DELETE_WINDOW',self.close)
        self.root.after(150,self.poll)

    def start(self):
        if self.proc and self.proc.poll() is None:return
        try:
            n=int(self.rounds.get())
            if not 1<=n<=100:raise ValueError()
        except ValueError:
            messagebox.showerror('轮数无效','请填写1至100之间的整数。');return
        cfg=json.loads((ROOT/'config.json').read_text(encoding='utf-8-sig'))
        cfg.update(allow_food=self.food.get(),wander_rounds=n,allow_gamble_lingshi=self.gamble.get(),allow_practice_lingshi=self.practice.get())
        (ROOT/'config.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2),encoding='utf-8')
        cmd=[sys.executable,'-u',str(ROOT/'assistant.py'),TASKS[self.task.get()]]
        if self.watch.get() and TASKS[self.task.get()] in ['all','finish','forbidden','family','night','travel']:
            cmd.append('--watch')
        self.proc=subprocess.Popen(cmd,cwd=str(ROOT),stdout=subprocess.PIPE,stderr=subprocess.STDOUT,encoding='utf-8',errors='replace',creationflags=subprocess.CREATE_NO_WINDOW)
        self.save_status('running')
        self.start_btn.configure(state='disabled');self.stop_btn.configure(state='normal')
        self.status.set('运行中：'+self.task.get())
        def read():
            for line in self.proc.stdout:self.messages.put(line)
            self.proc.wait();self.messages.put(('done',self.proc.returncode))
        threading.Thread(target=read,daemon=True).start()

    def stop(self):
        if self.proc and self.proc.poll() is None:
            (ROOT/'STOP').write_text('stop',encoding='utf-8')
            self.proc.terminate()
            self.status.set('已停止；已启动的游戏内倒计时会继续')
            self.save_status('stopped')

    def save_status(self,state):
        import os
        data={'ui_pid':os.getpid(),'worker_pid':self.proc.pid if self.proc else None,'state':state,'task':self.task.get(),'watch':self.watch.get()}
        (ROOT/'ui-state.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')

    def poll(self):
        while not self.messages.empty():
            item=self.messages.get()
            if isinstance(item,tuple):
                self.start_btn.configure(state='normal');self.stop_btn.configure(state='disabled')
                self.status.set('已结束' if item[1]==0 else '已停止，请查看记录')
                self.save_status('finished' if item[1]==0 else 'stopped')
            else:
                self.output.insert('end',item);self.output.see('end')
        self.root.after(150,self.poll)

    def open_logs(self):
        import os
        (ROOT/'logs').mkdir(exist_ok=True);os.startfile(str(ROOT/'logs'))

    def close(self):
        self.stop();self.root.destroy()

if __name__=='__main__':
    app=App()
    if '--finish' in sys.argv:app.task.set('倒计时收尾')
    if '--start' in sys.argv:app.root.after(300,app.start)
    app.root.mainloop()

