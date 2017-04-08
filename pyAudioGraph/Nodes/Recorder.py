import numpy as np
from .. import InWire
from ..AudioGraph import Node


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
            self.w_in.append(InWire(self))
            self.data.append(np.zeros(self.size, dtype=np.float32))

        self.in_wires.extend(self.w_in)

    def calc_func(self):
        for i in range(self.nchannels):
            in_scalar = self.w_in[i].get_data()
            self.data[i][self.count] = in_scalar
        self.count += 1

        if(self.count == self.size):
            self.extend()

    def extend(self):
        new_size = self.size * 2
        for i in range(self.nchannels):
            self.data[i].resize(new_size)
        self.size = new_size

    def clear(self):
        self.count = 0

    def get_data(self, k):
        if(k > self.nchannels):
            raise IndexError('Index out of bounds')
        return self.data[k][:self.count]


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
            self.w_in.append(InWire(self))
            self.data.append(np.zeros(self.size, dtype=np.float32))

        self.in_wires.extend(self.w_in)

    def calc_func(self):
        b = self.world.buf_len
        c = self.count
        for i in range(self.nchannels):
            in_array = self.w_in[i].get_data()
            self.data[i][c * b:(c + 1) * b] = in_array
        self.count += 1

        if(self.count * b == self.size):
            self.extend()

    def extend(self):
        new_size = self.size * 2
        for i in range(self.nchannels):
            self.data[i].resize(new_size)
        self.size = new_size

    def clear(self):
        self.count = 0

    def get_data(self, k):
        if(k > self.nchannels):
            raise IndexError('Index out of bounds')
        return self.data[k][:self.count * self.world.buf_len]
