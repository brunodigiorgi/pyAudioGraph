from ..AudioGraph import Node
from .. import InWire, OutWire


class OutNode(Node):
    """
    in_wires:
        - w_in : list, numpy.array shape = [1, buf_len]
        - w_level : scalar
    """

    def __init__(self, world):
        super().__init__(world)
        self.nchannels = world.nchannels

        self.w_in = []
        for i in range(self.nchannels):
            self.w_in.append(InWire(self))
        self.w_level = InWire(self, 1)

    def calc_func(self):
        level = self.w_level.get_data()
        for i in range(self.nchannels):
            self.world.outBuffer[i, :] = self.w_in[i].get_data() * level


class InNode(Node):
    """
    in_wires:
        - w_level : controlRate
    out_wires:
        - w_out : list, audioRate
    """

    def __init__(self, world):
        super().__init__(world)
        self.nchannels = world.nchannels

        self.w_out = []
        for i in range(self.nchannels):
            self.w_out.append(OutWire(self, world.buf_len))
        self.w_level = InWire(self, 1)

    def calc_func(self):
        level = self.w_level.get_data()
        for i in range(self.nchannels):
            self.w_out[i].set_data(self.world.inBuffer[i, :] * level)
