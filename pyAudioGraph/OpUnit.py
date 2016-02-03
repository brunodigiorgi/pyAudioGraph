import numpy as np
from .AudioGraph import Node
from .Wire import Wire


class OpMult(Node):
    def __init__(self, world):
        super().__init__(world)
        self.w_in1 = Wire(self.world, Wire.audioRate, Wire.wiretype_input)
        self.w_in2 = Wire(self.world, Wire.audioRate, Wire.wiretype_input)
        self.w_out = Wire(self.world, Wire.audioRate, Wire.wiretype_output)

    def calc_func(self):
        self.w_out.set_buffer(self.w_in1._buf * self.w_in2._buf)
