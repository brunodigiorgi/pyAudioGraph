from .AudioGraph import Node
from .Wire import InWire, OutWire
import numpy as np


class OpUnary(Node):

    def __init__(self, world, unary_fn, out_len=1):
        super().__init__(world)
        self.unary_fn = unary_fn
        self.w_in = InWire(self)
        self.w_out = OutWire(self, out_len)

        self.in_wires.extend([self.w_in])
        self.out_wires.append(self.w_out)

    def calc_func(self):
        in_array = self.w_in.get_data()
        self.w_out.set_data(self.unary_fn(in_array))

    def __call__(self, out_wire):
        out_wire.plug_into(self.w_in)
        return self.w_out


class OpBinary(Node):

    def __init__(self, world, binary_fn, out_len=1):
        super().__init__(world)
        self.binary_fn = binary_fn
        self.w_in1 = InWire(self)
        self.w_in2 = InWire(self)
        self.w_out = OutWire(self, out_len)

        self.in_wires.extend([self.w_in1, self.w_in2])
        self.out_wires.append(self.w_out)

    def calc_func(self):
        in_array1 = self.w_in1.get_data()
        in_array2 = self.w_in2.get_data()
        self.w_out.set_data(self.binary_fn(in_array1, in_array2))


ControlOpUnary = OpUnary
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


# OutWire Extension
class OutWire(OutWire):

    def __add__(self, other):
        if(other.__class__.__name__ == "OutWire"):
            l_ = max(self._data.shape[1], other._data.shape[1])
            op = OpBinary(self.parent.world, np.add, out_len=l_)
            self.plug_into(op.w_in1)
            other.plug_into(op.w_in2)
            return op.w_out
        else:
            l_ = self._data.shape[1]
            op = OpUnary(self.parent.world, lambda x: x + other, out_len=l_)
            self.plug_into(op.w_in)
            return op.w_out

    def __mul__(self, other):
        if(other.__class__.__name__ == "OutWire"):
            l_ = max(self._data.shape[1], other._data.shape[1])
            op = OpBinary(self.parent.world, np.multiply, out_len=l_)
            self.plug_into(op.w_in1)
            other.plug_into(op.w_in2)
            return op.w_out
        else:
            l_ = self._data.shape[1]
            op = OpUnary(self.parent.world, lambda x: x * other, out_len=l_)
            self.plug_into(op.w_in)
            return op.w_out
