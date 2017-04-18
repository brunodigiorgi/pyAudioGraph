import itertools
from ..AudioGraph import Node
from .. import InWire, OutWire
import numpy as np


class MixerNode(Node):
    """
    in_wires:
    out_wires
    """

    def __init__(self, world, matrix):
        """
        matrix is a matrix of shape nOutChannels x nInChannels
        -1 < matrix_ij < 1
        """
        super().__init__(world)

        self.nInChannels = ni = matrix.shape[1]
        self.nOutChannels = no = matrix.shape[0]

        self.w_in = [InWire(self) for i in range(ni)]
        self.w_out = [OutWire(self, world.buf_len) for o in range(no)]
        self.temp_out = np.zeros((1, world.buf_len), dtype=np.float32)
        self.w_level = [[InWire(self, matrix[o, i])
                         for i in range(ni)] for o in range(no)]

    def calc_func(self):
        ni, no = self.nInChannels, self.nOutChannels

        for o in range(no):
            self.temp_out[:] = 0
            for i in range(ni):
                in_array = self.w_in[i].get_data()
                self.temp_out[0, :] += self.w_level[o][i].get_data() * in_array[0, :]
            self.w_out[o].set_data(self.temp_out)


class MonizerNode(MixerNode):
    """Mixer nchannels to mono."""

    def __init__(self, world, in_node):
        nchannels = in_node.nchannels
        matrix = np.ones((1, nchannels)) / nchannels
        super().__init__(world, matrix)
        for i in range(nchannels):
            in_node.w_out[i].plug_into(self.w_in[i])
