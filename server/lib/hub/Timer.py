
from threading import Thread, Event


class Timer(Thread):

    def __init__(self, interval, function, repeat = False, args = [], kwargs = {}):
        super().__init__()
        self.daemon = True
        self.interval = interval
        self.repeat = repeat
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.finished = Event()
        self.resetted = True

    def cancel(self):
        self.repeat = False
        self.finished.set()

    def run(self):
        while self.repeat:
            while self.resetted:
                self.resetted = False
                self.finished.wait(self.interval)

            self.resetted = True
            if not self.finished.isSet():
                self.function(*self.args, **self.kwargs)
        self.finished.set()
        
    def reset(self, interval = None, function = None):
        if interval:
            self.interval = interval
        if function:
            self.function = function
            
        self.resetted = True
        self.finished.set()
        self.finished.clear()
