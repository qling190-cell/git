"""Cooperative pause at input/capture boundaries, with pause-aware timeouts."""
import pathlib
import time as wall_time


class PauseClock:
    def __init__(self,root,stop_type=RuntimeError):
        self.root=pathlib.Path(root)
        self.stop_type=stop_type
        self.paused_seconds=0.0

    def gate(self):
        def check_stop():
            if (self.root/'STOP').exists():raise self.stop_type('用户已停止运行。')
        check_stop()
        if not (self.root/'PAUSE').exists():return
        started=wall_time.monotonic()
        try:
            (self.root/'PAUSED').write_text('paused',encoding='utf-8')
            while (self.root/'PAUSE').exists():
                check_stop()
                wall_time.sleep(.1)
            check_stop()
        finally:
            self.paused_seconds+=wall_time.monotonic()-started
            (self.root/'PAUSED').unlink(missing_ok=True)

    def monotonic(self):
        self.gate()
        return wall_time.monotonic()-self.paused_seconds

    def sleep(self,seconds):
        end=self.monotonic()+max(0,seconds)
        while True:
            remaining=end-self.monotonic()
            if remaining<=0:return
            wall_time.sleep(min(.1,remaining))

    def __getattr__(self,name):return getattr(wall_time,name)
