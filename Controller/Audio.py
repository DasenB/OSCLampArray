import sounddevice as sd
from collections import deque
import numpy as np
import copy
import random

class Audio:

    queue: deque
    stream: sd.Stream
    samples: int

    def __init__(self, sample_size: int = 10000) -> None:
        self.samples = sample_size
        self.queue = deque([], maxlen = sample_size)

    def start(self):
        def callback(indata: np.ndarray, outdata: np.ndarray, frames: int, time: any, status: any) -> None:
            if status:
                return
            self.queue.extend(indata[:, 0])
            outdata[:] = indata
        self.stream = sd.Stream(blocksize=1024, callback=callback, dtype='float32', channels=1)
        self.stream.start()

    def get_data(self) -> list[int]|None:
        if len(self.queue) < self.samples:
            return None
        return np.array(self.queue)[-self.samples:]

    def stop(self):
        self.stream.stop()
        self.stream.close()
        self.stream = None
        sd.stop()