import random
import time


def simulator(rcvpkt):
    p = random.random()
    if p < 0.1:
        rcvpkt['checksum'] = False
    elif p > 0.9:
        rcvpkt = None
    return rcvpkt


class Timer:
    def __init__(self, target):
        self.start_time = 0
        self.target = target
        self.active = False

    def start_timer(self):
        self.start_time = time.time()
        self.active = True

    def stop_timer(self):
        self.start_time = 0
        self.active = False

    def if_timeout(self):
        if self.active:
            return (time.time() - self.start_time) > self.target
        else:
            print("Please start the timer at first")
            return False
