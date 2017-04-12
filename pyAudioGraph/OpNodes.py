from .AudioGraph import Node
from .Wire import InWire, OutWire
import numpy as np


class Op:
    """
    encapsulate a generic operation as a node of the graph.
    each time it is called generate a new node (OpNode) and returns its w_out
    example:
        op = Op(np.add)
        op(w_out1, w_out2)
    """

    def __init__(self, fn):
        self.fn = fn

    def __call__(self, *w_out_tuple):
        n_w_out = len(w_out_tuple)
        assert(n_w_out > 0)
        max_len = 0
        w = w_out_tuple[0].parent.world
        for w_out in w_out_tuple:
            assert(w_out.__class__.__name__ == "OutWire")
            assert(w == w_out.parent.world)
            max_len = max(max_len, w_out._data.shape[1])

        op_node = OpNode(w, self.fn, n_in=n_w_out, out_len=max_len)
        return op_node(*w_out_tuple)


class OpNode(Node):

    def __init__(self, world, fn, n_in, out_len):
        super().__init__(world)
        self.fn = fn
        self.n_in = n_in
        self.w_in = [InWire(self) for i in range(n_in)]
        self.w_out = OutWire(self, out_len)

        self.in_wires.extend(self.w_in)
        self.out_wires.append(self.w_out)

    def calc_func(self):
        in_arrays = [w_in_.get_data() for w_in_ in self.w_in]
        self.w_out.set_data(self.fn(*in_arrays))

    def __call__(self, *out_wires_tuple):
        nout_wires = len(out_wires_tuple)
        assert(nout_wires == self.n_in)
        for ow, iw in zip(out_wires_tuple, self.w_in):
            ow.plug_into(iw)
        return self.w_out


# OutWire Extension
class OutWire(OutWire):

    def __add__(self, other):
        if other.__class__.__name__ == "OutWire":
            op = Op(np.add)
            return op(self, other)
        else:
            op = Op(lambda x: x + other)
            return op(self)

    __radd__ = __add__

    def __mul__(self, other):
        if other.__class__.__name__ == "OutWire":
            op = Op(np.multiply)
            return op(self, other)
        else:
            op = Op(lambda x: x * other)
            return op(self)

    __rmul__ = __mul__

    def __sub__(self, other):
        if other.__class__.__name__ == "OutWire":
            op = Op(np.subtract)
            return op(self, other)
        else:
            op = Op(lambda x: x - other)
            return op(self)

    def __rsub__(self, other):
        if other.__class__.__name__ == "OutWire":
            op = Op(np.subtract)
            return op(other, self)
        else:
            op = Op(lambda x: other - x)
            return op(self)

    def __truediv__(self, other):
        if other.__class__.__name__ == "OutWire":
            op = Op(np.divide)
            return op(self, other)
        else:
            op = Op(lambda x: x / other)
            return op(self)

    def __rtruediv__(self, other):
        if other.__class__.__name__ == "OutWire":
            op = Op(np.divide)
            return op(other, self)
        else:
            op = Op(lambda x: other / x)
            return op(self)

    def clip(self, a_min, a_max):
        op = Op(lambda x: np.clip(x, a_min, a_max))
        return op(self)

    def range_to_unit(self, a_min, a_max, invert=False):
        a = 1 if invert else 0
        b = -1 if invert else 1
        op = Op(lambda x: a + b * (1 / (a_max - a_min)) * (np.clip(x, a_min, a_max) - a_min))
        return op(self)