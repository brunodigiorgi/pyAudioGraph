from ..AudioGraph import Node
from ..Wire import Wire


class OutUnit(Node):
    """
    in_wires:
        - w_in : list, audioRate
        - w_level : audioRate
    """

    def __init__(self, world):
        super().__init__(world)
        self.nchannels = world.nchannels

        self.w_in = []
        for i in range(self.nchannels):
            self.w_in.append(Wire(self, Wire.audioRate, Wire.wiretype_input, world.buf_len))

        self.w_level = Wire(self, Wire.controlRate, Wire.wiretype_input, world.buf_len)
        self.w_level.set_value(1)

        self.in_wires.append(self.w_level)
        self.in_wires.extend(self.w_in)

    def calc_func(self):
        level = self.w_level._value
        for i in range(self.nchannels):
            self.world.outBuffer[i, :] = self.w_in[i]._buf * level


class InUnit(Node):
    """
    in_wires:
        - w_level : audioRate
    out_wires:
        - w_out : list, audioRate
    """

    def __init__(self, world):
        super().__init__(world)
        self.nchannels = world.nchannels

        self.w_out = []
        for i in range(self.nchannels):
            self.w_out.append(Wire(self, Wire.audioRate, Wire.wiretype_output, world.buf_len))

        self.w_level = Wire(self, Wire.controlRate, Wire.wiretype_input, world.buf_len)
        self.w_level.set_value(1)

        self.in_wires.append(self.w_level)
        self.out_wires.extend(self.w_out)

    def calc_func(self):
        level = self.w_level._value
        for i in range(self.nchannels):
            self.w_out[i].set_buffer(self.world.inBuffer[i, :] * level)
