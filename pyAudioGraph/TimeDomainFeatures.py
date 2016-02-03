import numpy as np
from .AudioGraph import Node
from .Wire import Wire


class RmsUnit(Node):
    """Compute the Root Mean Square value of the current buffer"""
    def __init__(self, world):
        super().__init__(world)
        self.w_in = Wire(world, Wire.audioRate, Wire.wiretype_input)
        self.w_out = Wire(world, Wire.controlRate, Wire.wiretype_output)

    def calc_func(self):
        buf_len = self.world.buf_len
        s = np.sum(np.power(self.w_in._buf, 2))
        self.w_out.set_value(np.sqrt(s / buf_len))
