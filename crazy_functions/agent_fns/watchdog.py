import threading, time
from loguru import logger

class WatchDog():
    def __init__(self, timeout, bark_fn, interval=3, msg="") -> None:
        self.last_feed = None
        self.timeout = timeout
        self.bark_fn = bark_fn
        self.interval = interval
        self.msg = msg
        self.kill_dog = False

    def watch(self):
        while True:
            if self.kill_dog: break
            if time.time() - self.last_feed > self.timeout:
                if len(self.msg) > 0: logger.info(self.msg)
                self.bark_fn()
                break
            time.sleep(self.interval)

    def begin_watch(self):
        self.last_feed = time.time()
        th = threading.Thread(target=self.watch)
        th.daemon = True
        th.start()

    def feed(self):
        self.last_feed = time.time()
