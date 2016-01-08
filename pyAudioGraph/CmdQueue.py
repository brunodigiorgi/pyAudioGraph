import threading
import queue


class LambdaCommand:
    def __init__(self, func, args=(), kwargs={}):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        pass

    def __call__(self):
        return self.func(*self.args, **self.kwargs)


class AsyncCmdQueue:
    """
    Asynchronous command queue
    """
    def __init__(self):
        self.thread = threading.Thread(target=self.threadFunc)
        self.isRunning = False
        self.isFlushing = False
        self.cmdQueue = queue.Queue()
        self.cv = threading.Condition()
        self.launch()

    def push(self, cmd):
        """
        cmd: a callable (function or class with __call__ method)
        """
        with self.cv:
            self.cmdQueue.put(cmd, block=False)
            self.cv.notify()

    def launch(self):
        if(not self.isRunning):
            self.isRunning = True
            self.thread.start()

    def threadFunc(self):
        while(self.isRunning):
            with self.cv:
                if(not self.isFlushing):
                    self.cv.wait(0.1)
            while(not self.cmdQueue.empty()):
                cmd = self.cmdQueue.get_nowait()
                cmd()

    def flush(self):
        fcv = threading.Condition()
        self.isFlushing = True
        with fcv:
            fcv.wait_for(self.cmdQueue.empty, timeout=0.1)
        assert(self.cmdQueue.empty())
        self.isFlushing = False

    def join(self):
        if(self.isRunning):
            self.isRunning = False
            self.thread.join()

    def __del__(self):
        self.join()

    def empty(self):
        return self.cmdQueue.empty()
