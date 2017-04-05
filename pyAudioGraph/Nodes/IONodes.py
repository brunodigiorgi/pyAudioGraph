from ..AudioGraph import Node
from ..Wire import InWire, AudioOutWire


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

        self.in_wires.append(self.w_level)
        self.in_wires.extend(self.w_in)

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
            self.w_out.append(AudioOutWire(self, world.buf_len))

        self.w_level = InWire(self, 1)

        self.in_wires.append(self.w_level)
        self.out_wires.extend(self.w_out)

    def calc_func(self):
        level = self.w_level.get_data()
        for i in range(self.nchannels):
            self.w_out[i].set_buffer(self.world.inBuffer[i, :] * level)
