import numpy as np
from .AudioGraph import Node
from .Wire import Wire


def ramp(start, length, slope):
        return np.linspace(start, start + length * slope, length)


class SinOsc(Node):
    def __init__(self, world):
        super().__init__(world)
        self.w_freq = Wire(self.world, Wire.controlRate, Wire.wiretype_input)
        self.w_out = Wire(self.world, Wire.audioRate, Wire.wiretype_output)
        self.phase = 0
        self.w_freq.set_value(400)

    def calc_func(self):
        buf_len = self.world.buf_len
        sr = self.world.sample_rate
        f = self.w_freq._value
        p = ramp(self.phase, buf_len, f / sr * 2 * np.pi)
        self.w_out.set_buffer(np.sin(p))
        self.phase = p[-1] + f / sr * 2 * np.pi
        self.phase = np.mod(self.phase, 2 * np.pi)
