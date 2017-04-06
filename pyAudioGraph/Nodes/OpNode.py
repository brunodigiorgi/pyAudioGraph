from ..AudioGraph import Node
from ..Wire import InWire, OutWire, AudioOutWire
import numpy as np


class AudioOpBinary(Node):

    def __init__(self, world, binary_fn):
        super().__init__(world)
        self.binary_fn = binary_fn
        self.w_in1 = InWire(self)
        self.w_in2 = InWire(self)
        self.w_out = AudioOutWire(self, world.buf_len)

        self.in_wires.extend([self.w_in1, self.w_in2])
        self.out_wires.append(self.w_out)

    def calc_func(self):
        in_array1 = self.w_in1.get_data()
        in_array2 = self.w_in2.get_data()
        self.w_out.set_buffer(self.binary_fn(in_array1, in_array2))


class ControlOpBinary(Node):

    def __init__(self, world, binary_fn):
        super().__init__(world)
        self.binary_fn = binary_fn
        self.w_in1 = InWire(self)
        self.w_in2 = InWire(self)
        self.w_out = OutWire(self)

        self.in_wires.extend([self.w_in1, self.w_in2])
        self.out_wires.append(self.w_out)

    def calc_func(self):
        in1 = self.w_in1.get_data()
        in2 = self.w_in2.get_data()
        self.w_out.set_data(self.binary_fn(in1, in2))


class AudioOpMult(AudioOpBinary):

    def __init__(self, world):
        super().__init__(world, np.multiply)


class ControlOpMult(ControlOpBinary):

    def __init__(self, world):
        super().__init__(world, np.multiply)
