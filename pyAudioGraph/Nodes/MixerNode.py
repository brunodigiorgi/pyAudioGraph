import itertools
from ..AudioGraph import Node
from ..Wire import InWire, AudioOutWire
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
        self.w_out = [AudioOutWire(self, world.buf_len) for o in range(no)]
        self.temp_out = np.zeros((no, world.buf_len), dtype=np.float32)
        self.w_level = [[InWire(self, matrix[o, i])
                        for i in range(ni)] for o in range(no)]

        self.in_wires.extend([l for o_list in self.w_level for l in o_list])
        self.in_wires.extend(self.w_in)
        self.out_wires.extend(self.w_out)

    def calc_func(self):
        ni, no = self.nInChannels, self.nOutChannels
        for o in range(no):
            self.w_out[o].buf[0, :] = 0
        for i, o in itertools.product(range(ni), range(no)):
            in_array = self.w_in[i].get_data()
            self.w_out[o].buf[0, :] += self.w_level[o][i].get_value() * in_array[0, :]


class MonizerNode(MixerNode):
    """Mixer nchannels to mono."""

    def __init__(self, world, diskin_node):
        nchannels = diskin_node.nchannels
        matrix = np.ones((1, nchannels)) / nchannels
        super().__init__(world, matrix)
        for i in range(nchannels):
            diskin_node.w_out[i].plug_into(self.w_in[i])