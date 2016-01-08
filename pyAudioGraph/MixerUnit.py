import itertools
from .AudioGraph import Node
from .Wire import Wire
import numpy as np


class MixerUnit(Node):
    def __init__(self, world, matrix):
        """
        matrix is a matrix of shape nOutChannels x nInChannels
        -1 < matrix_ij < 1
        """
        super().__init__(world)

        self.nInChannels = ni = matrix.shape[1]
        self.nOutChannels = no = matrix.shape[0]

        self.w_in = [Wire(world, Wire.audioRate, Wire.wiretype_input) for i in range(ni)]
        self.w_out = [Wire(world, Wire.audioRate, Wire.wiretype_output) for o in range(no)]
        self.temp_out = np.zeros((no, world.buf_len), dtype=np.float32)
        self.w_level = [[Wire(world, Wire.controlRate, Wire.wiretype_input)
                        for i in range(ni)] for o in range(no)]

        for i, o in itertools.product(range(ni), range(no)):
            self.w_level[o][i].set_value(matrix[o, i])

    def calc_func(self):
        ni, no = self.nInChannels, self.nOutChannels
        for o in range(no):
            self.w_out[o]._buf[0, :] = 0
        for i, o in itertools.product(range(ni), range(no)):
            self.w_out[o]._buf[0, :] += self.w_level[o][i]._value * self.w_in[i]._buf[0, :]
