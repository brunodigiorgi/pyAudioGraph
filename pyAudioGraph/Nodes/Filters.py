import numpy as np
import scipy as sp
from scipy import signal
from ..AudioGraph import Node
from ..Wire import InWire, AudioOutWire


def lowpass_coeff(Fs, f0, Q):
    """
    computes filter coefficients for lowpass with 2 poles
    see http://www.musicdsp.org/files/Audio-EQ-Cookbook.txt
    Q is the resonance parameter
    """
    w0 = 2 * np.pi * f0 / Fs

    c_w0 = np.cos(w0)
    s_w0 = np.sin(w0)

    alpha = s_w0 / (2 * Q)

    b0 = (1 - c_w0) / 2
    b1 = 1 - c_w0
    b2 = (1 - c_w0) / 2
    a0 = 1 + alpha
    a1 = -2 * c_w0
    a2 = 1 - alpha

    b = [b0, b1, b2]
    a = [a0, a1, a2]
    return b, a


class Lowpass(Node):

    def __init__(self, world, f0=400, Q=1):
        super().__init__(world)

        self.w_in = InWire(self)
        self.w_f0 = InWire(self, f0)
        self.w_Q = InWire(self, Q)
        self.w_out = AudioOutWire(self, world.buf_len)
        self.in_wires.extend([self.w_in, self.w_f0, self.w_Q])
        self.out_wires.append(self.w_out)
        self.reset()

    def reset(self):
        self.zi = np.zeros((2,))  # initial condition for the filter

    def calc_func(self):
        # buf_len = self.world.buf_len
        Fs = self.world.sample_rate
        f0 = self.w_f0.get_data()
        Q = self.w_Q.get_data()
        b, a = lowpass_coeff(Fs, f0, Q)

        in_array = self.w_in.get_data()
        self.w_out.buf[0, :], self.zi = sp.signal.lfilter(b, a, in_array[0, :], zi=self.zi)
