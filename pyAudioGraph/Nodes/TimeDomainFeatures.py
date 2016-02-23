import numpy as np
from ..AudioGraph import Node
from ..Wire import InWire, AudioOutWire


class RmsNode(Node):
    """Compute the Root Mean Square value of the current buffer"""
    def __init__(self, world):
        super().__init__(world)
        self.w_in = InWire(self)
        self.w_out = AudioOutWire(self, world.buf_len)

        self.in_wires.append(self.w_in)
        self.out_wires.append(self.w_out)

    def calc_func(self):
        buf_len = self.world.buf_len
        in_array = self.w_in.buf
        s = np.sum(np.power(in_array, 2))
        self.w_out.set_value(np.sqrt(s / buf_len))
