from .AudioGraph import Node
from .Wire import Wire


class OutUnit(Node):
    def __init__(self, world):
        super().__init__(world)
        self.nchannels = world.nchannels

        self.w_in = []
        for i in range(self.nchannels):
            self.w_in.append(Wire(world, Wire.audioRate, Wire.wiretype_input))

        self.w_level = Wire(world, Wire.controlRate, Wire.wiretype_input)
        self.w_level.set_value(1)

    def calc_func(self):
        level = self.w_level._value
        for i in range(self.nchannels):
            self.world.outBuffer[i, :] = self.w_in[i]._buf * level


class InUnit(Node):
    def __init__(self, world):
        super().__init__(world)
        self.nchannels = world.nchannels

        self.w_out = []
        for i in range(self.nchannels):
            self.w_out.append(Wire(world, Wire.audioRate, Wire.wiretype_output))

        self.w_level = Wire(world, Wire.controlRate, Wire.wiretype_input)
        self.w_level.set_value(1)

    def calc_func(self):
        level = self.w_level._value
        for i in range(self.nchannels):
            self.w_out[i].set_buffer(self.world.inBuffer[i, :] * level)
