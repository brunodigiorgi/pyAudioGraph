import numpy as np
from ..AudioGraph import Node
from ..Wire import Wire


def ramp(start, length, slope):
        return np.linspace(start, start + length * slope, length)


class LevelSlopeGen(Node):
    """
    in_wires:
        - w_in : controlRate
            the target level of the slope
    out_wires:
        - w_out : audioRate
    """

    def __init__(self, world, initial_value=1, speed=.5):
        super().__init__(world)
        self.value = initial_value
        self.v_temp = initial_value
        self.speed = speed
        self.w_in = Wire(self, Wire.controlRate, Wire.wiretype_input, world.buf_len)
        self.w_in.set_value(initial_value)
        self.w_out = Wire(self, Wire.audioRate, Wire.wiretype_output, world.buf_len)

        self.in_wires.append(self.w_in)
        self.out_wires.append(self.w_out)

    def _set_value(self, value):
        if(self.world.is_running()):
            self.value = value
            self.v_temp = value
        else:
            self.value = value

    def calc_func(self):
        self._set_value(self.w_in._value)
        buf_len = self.world.buf_len
        dest = self.v_temp + self.speed * (self.value - self.v_temp)
        slope = (dest - self.v_temp) / buf_len
        self.w_out.set_buffer(ramp(self.v_temp, buf_len, slope))
        self.v_temp = dest


class SinOsc(Node):
    def __init__(self, world):
        super().__init__(world)
        self.level_node = LevelSlopeGen(world, initial_value=1)

        self.w_level = Wire(self, Wire.controlRate, Wire.wiretype_input, world.buf_len)
        self.w_freq = Wire(self, Wire.controlRate, Wire.wiretype_input, world.buf_len)
        self.w_out = Wire(self, Wire.audioRate, Wire.wiretype_output, world.buf_len)
        self.phase = 0
        self.w_freq.set_value(400)

        self.in_wires.extend([self.w_freq, self.w_level])
        self.out_wires.append(self.w_out)

    def calc_func(self):
        buf_len = self.world.buf_len
        sr = self.world.sample_rate
        f = self.w_freq._value

        self.level_node.w_in.set_value(self.w_level._value)
        self.level_node.calc_func()

        p = ramp(self.phase, buf_len, f / sr * 2 * np.pi)
        self.w_out.set_buffer(np.sin(p) * self.level_node.w_out._buf)
        self.phase = p[-1] + f / sr * 2 * np.pi
        self.phase = np.mod(self.phase, 2 * np.pi)
