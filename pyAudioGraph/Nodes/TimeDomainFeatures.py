import numpy as np
from ..AudioGraph import Node
from .. import InWire, OutWire


class RmsNode(Node):
    """Compute the Root Mean Square value of the current buffer"""

    def __init__(self, world):
        super().__init__(world)
        self.w_in = InWire(self)
        self.w_out = OutWire(self)

    def calc_func(self):
        buf_len = self.world.buf_len
        in_array = self.w_in.get_data()
        s = np.sum(np.power(in_array, 2))
        self.w_out.set_data(np.sqrt(s / buf_len))
