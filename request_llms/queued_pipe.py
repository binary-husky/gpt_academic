from multiprocessing import Pipe, Queue
import time
import threading

class PipeSide(object):
    def __init__(self, q_2remote, q_2local) -> None:
        self.q_2remote = q_2remote
        self.q_2local = q_2local

    def recv(self):
        return self.q_2local.get()

    def send(self, buf):
        self.q_2remote.put(buf)

    def poll(self):
        return not self.q_2local.empty()

def create_queue_pipe():
    q_p2c = Queue()
    q_c2p = Queue()
    pipe_c = PipeSide(q_2local=q_p2c, q_2remote=q_c2p)
    pipe_p = PipeSide(q_2local=q_c2p, q_2remote=q_p2c)
    return pipe_c, pipe_p
