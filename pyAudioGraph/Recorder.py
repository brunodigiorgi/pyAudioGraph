import numpy as np
from .Wire import Wire
from .AudioGraph import Node


class ControlRateRecorder(Node):
    def __init__(self, world, nchannels, init_size=8192):
        super().__init__(world)
        self.nchannels = nchannels

        self.init_size = init_size
        self.w_in = []
        self.data = []
        self.size = self.init_size
        self.count = 0
        for i in range(self.nchannels):
            self.w_in.append(Wire(world, Wire.controlRate, Wire.wiretype_input))
            self.data.append(np.zeros(self.size, dtype=np.float32))

    def calc_func(self):
        for i in range(self.nchannels):
            self.data[i][self.count] = self.w_in[i]._value
        self.count += 1

        if(self.count == self.size):
            self.extend()

    def extend(self):
        for i in range(self.nchannels):
            self.data[i] = np.append(self.data[i], np.zeros(self.size, dtype=np.float32))
        self.size *= 2

    def clear(self):
        self.count = 0


class AudioRateRecorder(Node):
    def __init__(self, world, nchannels, init_size=131072):
        super().__init__(world)
        self.nchannels = nchannels

        self.init_size = init_size
        self.w_in = []
        self.data = []
        self.size = self.init_size
        self.count = 0
        for i in range(self.nchannels):
            self.w_in.append(Wire(world, Wire.audioRate, Wire.wiretype_input))
            self.data.append(np.zeros(self.size, dtype=np.float32))

    def calc_func(self):
        b = self.world.buf_len
        c = self.count
        for i in range(self.nchannels):
            self.data[i][c * b:(c + 1) * b] = self.w_in[i]._buf
        self.count += 1

        if(self.count * b == self.size):
            self.extend()

    def extend(self):
        for i in range(self.nchannels):
            self.data[i] = np.append(self.data[i], np.zeros(self.size, dtype=np.float32))
        self.size *= 2

    def clear(self):
        self.count = 0
