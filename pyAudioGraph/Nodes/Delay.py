from .. import Node, RingBuffer, InWire
from . import OutWire
import numpy as np


class Delay(Node):

    def __init__(self, world, samples, weight=.2):
        super().__init__(world)

        self.samples = int(samples)
        self.ringbuffer = RingBuffer(1, self.samples)
        self.w_in = InWire(self)
        self.w_in_weight = InWire(self, weight)
        self.w_out = OutWire(self, world.buf_len)
        self.out_temp = np.zeros((1, world.buf_len), dtype=np.float32)
        self.in_wires.extend([self.w_in, self.w_in_weight])
        self.out_wires.append(self.w_out)
        self.reset()

    def reset(self):
        self.ringbuffer.clear()
        self.ringbuffer.advance_write_index(self.samples)

    def calc_func(self):
        buf_len = self.world.buf_len
        in_array = self.w_in.get_data()
        in_weight = self.w_in_weight.get_data()
        self.ringbuffer.read(self.out_temp)
        self.out_temp[:] = self.out_temp[:] * in_weight + in_array[:]
        self.ringbuffer.advance_read_index(buf_len)
        self.w_out.set_data(self.out_temp)
        self.ringbuffer.write(in_array)
