import numpy as np
import scipy as sp
from .. import Node, InWire, OutWire


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
        self.w_out = OutWire(self, world.buf_len)
        self.reset()

    def reset(self):
        len_a = len_b = 3
        len_zi = max(len_a, len_b) - 1  # see scipy.signal.lfilter docs
        self.zi = np.zeros((len_zi,))  # initial condition for the filter

    def calc_func(self):
        # buf_len = self.world.buf_len
        Fs = self.world.sample_rate
        f0 = self.w_f0.get_data()
        Q = self.w_Q.get_data()
        b, a = lowpass_coeff(Fs, f0, Q)

        in_array = self.w_in.get_data()
        out_data, self.zi = sp.signal.lfilter(b, a, in_array[0, :], zi=self.zi)
        self.w_out.set_data(out_data)


class ControlFIRFilter(Node):
    """
    A FIR filter for control signals
    """

    def __init__(self, world, taps):
        """
        taps: np.ndarray 1-dim, coefficients of the filter
        """
        super().__init__(world)
        self.taps = np.array(taps, dtype=np.float32)
        self.rev_taps = self.taps[::-1]
        self.temp_buffer = np.zeros(len(self.taps))
        self.i = 0
        self.w_in = InWire(self)
        self.w_out = OutWire(self)
        self.reset()

    def reset(self):
        self.temp_buffer[:] = 0
        self.i = 0

    def calc_func(self):
        L = len(self.taps)
        in_ = self.w_in.get_data()
        self.temp_buffer[self.i] = in_
        out_ = np.dot(self.temp_buffer[:(self.i + 1)], self.rev_taps[L - (self.i + 1):L])
        out_ += np.dot(self.temp_buffer[(self.i + 1):], self.rev_taps[:L - (self.i + 1)])
        self.i += 1
        if(self.i == len(self.taps)):
            self.i = 0
        self.w_out.set_data(out_)
