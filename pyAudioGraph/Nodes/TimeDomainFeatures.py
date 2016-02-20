import numpy as np
from ..AudioGraph import Node
from ..Wire import Wire


class RmsUnit(Node):
    """Compute the Root Mean Square value of the current buffer"""
    def __init__(self, world):
        super().__init__(world)
        self.w_in = Wire(self, Wire.audioRate, Wire.wiretype_input, world.buf_len)
        self.w_out = Wire(self, Wire.controlRate, Wire.wiretype_output, world.buf_len)

        self.in_wires.append(self.w_in)
        self.out_wires.append(self.w_out)

    def calc_func(self):
        buf_len = self.world.buf_len
        s = np.sum(np.power(self.w_in._buf, 2))
        self.w_out.set_value(np.sqrt(s / buf_len))
