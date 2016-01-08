from .AudioGraph import Node
from .Wire import Wire


class OutUnit(Node):
    def __init__(self, world):
        super().__init__(world)
        self.nChannels = world.nChannels

        self.w_in = []
        for i in range(self.nChannels):
            self.w_in.append(Wire(world, Wire.audioRate, Wire.wiretype_input))

        self.w_level = Wire(world, Wire.controlRate, Wire.wiretype_input)
        self.w_level.setValue(1)

    def calcFunc(self):
        level = self.w_level._value
        for i in range(self.nChannels):
            self.world.outBuffer[i, :] = self.w_in[i]._buf * level


class InUnit(Node):
    def __init__(self, world):
        super().__init__(world)
        self.nChannels = world.nChannels

        self.w_out = []
        for i in range(self.nChannels):
            self.w_out.append(Wire(world, Wire.audioRate, Wire.wiretype_output))

        self.w_level = Wire(world, Wire.controlRate, Wire.wiretype_input)
        self.w_level.setValue(1)

    def calcFunc(self):
        level = self.w_level._value
        for i in range(self.nChannels):
            self.w_out[i].setBuffer(self.world.inBuffer[i, :] * level)
