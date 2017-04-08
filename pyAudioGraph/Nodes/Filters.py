import numpy as np
import scipy as sp
from scipy import signal
from .. import Node, InWire, OutWire, RingBuffer


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
        self.temp_buffer = np.zeros((1, len(self.taps)))
        self.ringbuffer = RingBuffer(1, len(self.taps))
        self.w_in = InWire(self)
        self.w_out = OutWire(self)
        self.in_wires.append(self.w_in)
        self.out_wires.append(self.w_out)
        self.reset()

    def reset(self):
        self.ringbuffer.clear()
        self.ringbuffer.advance_write_index(len(self.taps) - 1)

    def calc_func(self):
        in_ = self.w_in.get_data()
        to_write = np.array([[in_]], np.float32)
        self.ringbuffer.write(to_write)  # write 1
        self.ringbuffer.read(self.temp_buffer)  # read all
        self.ringbuffer.advance_read_index(1)  # advance read 1
        out_ = np.dot(self.temp_buffer[0][::-1], self.taps)
        self.w_out.set_data(out_)
