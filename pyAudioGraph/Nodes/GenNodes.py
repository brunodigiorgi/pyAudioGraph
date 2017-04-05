import numpy as np
import scipy as sp
from scipy import signal
from ..AudioGraph import Node
from ..Wire import InWire, AudioOutWire


def ramp(start, length, slope):
        return np.linspace(start, start + length * slope, length)


# TODO: split into AudioSlopeGen and ControlSlopeGen
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
        self.w_in = InWire(self, initial_value)
        self.in_wires.append(self.w_in)

        # TODO: Control version with OutWire
        self.w_out = AudioOutWire(self, world.buf_len)
        self.out_wires.append(self.w_out)

    def _set_value(self, value):
        if(self.world.is_running()):
            self.value = value
        else:
            self.value = value
            self.v_temp = value

    def calc_func(self):
        self._set_value(self.w_in.get_data())
        dest = self.v_temp + self.speed * (self.value - self.v_temp)

        # TODO: Control version simply puts dest in w_out
        buf_len = self.world.buf_len
        slope = (dest - self.v_temp) / buf_len
        self.w_out.set_buffer(ramp(self.v_temp, buf_len, slope))

        self.v_temp = dest


class SignalOsc(Node):

    def __init__(self, world, signal_fn):
        super().__init__(world)
        self.signal_fn = signal_fn

        self.w_freq = InWire(self, 400)
        self.w_out = AudioOutWire(self, world.buf_len)
        self.phase = 0

        self.in_wires.extend([self.w_freq])
        self.out_wires.append(self.w_out)

    def calc_func(self):
        buf_len = self.world.buf_len
        sr = self.world.sample_rate
        f = self.w_freq.get_data()

        p = ramp(self.phase, buf_len, f / sr * 2 * np.pi)
        self.w_out.set_buffer(self.signal_fn(p))
        self.phase = p[-1] + f / sr * 2 * np.pi
        self.phase = np.mod(self.phase, 2 * np.pi)


class SinOsc(SignalOsc):

    def __init__(self, world):
        super().__init__(world, np.sin)


class SawOsc(SignalOsc):

    def __init__(self, world):
        super().__init__(world, sp.signal.sawtooth)
