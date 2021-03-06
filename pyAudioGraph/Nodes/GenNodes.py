import numpy as np
import scipy as sp
from scipy import signal
from ..AudioGraph import Node
from .. import InWire, OutWire


def ramp(start, length, slope):
    return np.linspace(start, start + length * slope, length)


def phases_ramp(start_phase, length, start_freq, end_freq, sample_rate):
    eps = 0.01
    fr = np.logspace(np.log10(start_freq + eps), np.log10(end_freq + eps), num=length)
    phase = start_phase + np.cumsum(fr / sample_rate * 2 * np.pi)
    return phase


class SlopeGen(Node):
    """
    in_wires:
        - w_in : controlRate
            the target level of the slope
    out_wires:
        - w_out : audioRate
    """

    def __init__(self, world, initial_value=1, speed=.5, out_len=1):
        super().__init__(world)
        self.value = initial_value
        self.v_temp = initial_value
        self.speed = speed
        self.w_in = InWire(self, initial_value)
        self.w_out = OutWire(self, buf_len=out_len)

    def _set_value(self, value):
        if(self.world.is_running()):
            self.value = value
        else:
            self.value = value
            self.v_temp = value

    def calc_func(self):
        self._set_value(self.w_in.get_data())
        dest = self.v_temp + self.speed * (self.value - self.v_temp)
        self.w_out.set_data(dest)
        self.v_temp = dest


ControlSlopeGen = SlopeGen


class AudioSlopeGen(SlopeGen):

    def __init__(self, world, initial_value=1, speed=.5):
        super().__init__(world, initial_value=initial_value, speed=speed, out_len=world.buf_len)

    def calc_func(self):
        self._set_value(self.w_in.get_data())
        dest = self.v_temp + self.speed * (self.value - self.v_temp)

        buf_len = self.world.buf_len
        slope = (dest - self.v_temp) / buf_len
        self.w_out.set_data(ramp(self.v_temp, buf_len, slope))

        self.v_temp = dest


class ControlSeqGen(Node):
    """
    Mostly used for testing

    w_out : outputs 1 elements of the given seq each cycle
    """

    def __init__(self, world, seq):
        super().__init__(world)
        self.seq = np.array(seq, dtype=np.float32)
        self.w_out = OutWire(self)
        self.out_wires.append(self.w_out)
        self.reset()

    def reset(self):
        self.i = 0

    def calc_func(self):
        out_ = self.seq[self.i]
        self.w_out.set_data(out_)
        self.i += 1
        if(self.i == len(self.seq)):
            self.i = 0



class SignalOsc(Node):

    def __init__(self, world, signal_fn):
        super().__init__(world)
        self.signal_fn = signal_fn

        self.w_freq = InWire(self, 400)
        self.w_out = OutWire(self, world.buf_len)
        self.phase = 0
        self.prev_f = self.w_freq.get_data()

    def calc_func(self):
        buf_len = self.world.buf_len
        sr = self.world.sample_rate
        f = self.w_freq.get_data()

        # p = ramp(self.phase, buf_len, f / sr * 2 * np.pi)
        p = phases_ramp(self.phase, buf_len, self.prev_f, f, sr)
        self.w_out.set_data(self.signal_fn(p))
        self.phase = p[-1] + f / sr * 2 * np.pi
        self.phase = np.mod(self.phase, 2 * np.pi)

        self.prev_f = f


class ControlOsc(Node):

    def __init__(self, world, signal_fn):
        super().__init__(world)
        self.signal_fn = signal_fn

        self.w_freq = InWire(self, 6)
        self.w_out = OutWire(self)
        self.phase = 0
        self.prev_f = self.w_freq.get_data()

    def calc_func(self):
        buf_len = self.world.buf_len
        sr = self.world.sample_rate
        f = self.w_freq.get_data()

        self.w_out.set_data(self.signal_fn(self.phase))
        self.phase = self.phase + buf_len * f / sr * 2 * np.pi
        self.phase = np.mod(self.phase, 2 * np.pi)


class ControlSinOsc(ControlOsc):

    def __init__(self, world):
        super().__init__(world, np.sin)


class SinOsc(SignalOsc):

    def __init__(self, world):
        super().__init__(world, np.sin)


class SawOsc(SignalOsc):

    def __init__(self, world):
        super().__init__(world, sp.signal.sawtooth)
