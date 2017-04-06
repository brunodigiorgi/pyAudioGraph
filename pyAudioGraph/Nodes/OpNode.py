from ..AudioGraph import Node
from ..Wire import InWire, OutWire
import numpy as np


class OpBinary(Node):

    def __init__(self, world, binary_fn, out_len=1):
        super().__init__(world)
        self.binary_fn = binary_fn
        self.w_in1 = InWire(self)
        self.w_in2 = InWire(self)
        self.w_out = OutWire(self, world.buf_len)

        self.in_wires.extend([self.w_in1, self.w_in2])
        self.out_wires.append(self.w_out)

    def calc_func(self):
        in_array1 = self.w_in1.get_data()
        in_array2 = self.w_in2.get_data()
        self.w_out.set_data(self.binary_fn(in_array1, in_array2))


ControlOpBinary = OpBinary


class AudioOpBinary(OpBinary):

    def __init__(self, world, binary_fn):
        super().__init__(world, binary_fn, out_len=world.buf_len)


class AudioOpMult(AudioOpBinary):

    def __init__(self, world):
        super().__init__(world, np.multiply)


class ControlOpMult(ControlOpBinary):

    def __init__(self, world):
        super().__init__(world, np.multiply)
