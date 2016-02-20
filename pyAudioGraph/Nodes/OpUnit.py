import numpy as np
from ..AudioGraph import Node
from ..Wire import Wire


class OpMult(Node):
    def __init__(self, world):
        super().__init__(world)
        self.w_in1 = Wire(self, Wire.audioRate, Wire.wiretype_input, world.buf_len)
        self.w_in2 = Wire(self, Wire.audioRate, Wire.wiretype_input, world.buf_len)
        self.w_out = Wire(self, Wire.audioRate, Wire.wiretype_output, world.buf_len)

        self.in_wires.extend([self.w_in1, self.w_in2])
        self.out_wires.append(self.w_out)

    def calc_func(self):
        self.w_out.set_buffer(self.w_in1._buf * self.w_in2._buf)
