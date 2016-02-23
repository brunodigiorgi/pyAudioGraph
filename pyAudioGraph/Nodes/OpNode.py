from ..AudioGraph import Node
from ..Wire import InWire, AudioOutWire


class OpMult(Node):
    def __init__(self, world):
        super().__init__(world)
        self.w_in1 = InWire(self)
        self.w_in2 = InWire(self)
        self.w_out = AudioOutWire(self, world.buf_len)

        self.in_wires.extend([self.w_in1, self.w_in2])
        self.out_wires.append(self.w_out)

    def calc_func(self):
        in_array1 = self.w_in1.get_data()
        in_array2 = self.w_in2.get_data()
        self.w_out.set_buffer(in_array1 * in_array2)
