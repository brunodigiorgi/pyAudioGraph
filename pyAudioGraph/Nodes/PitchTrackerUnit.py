# -*- coding: utf-8 -*-
"""
Pitch tracking using YIN algorithm [1].

[1] De Cheveigné, Alain, and Hideki Kawahara.
"YIN, a fundamental frequency estimator for speech and music."
The Journal of the Acoustical Society of America 111.4 (2002): 1917-1930.
"""

from ..Wire import Wire
from ..AudioGraph import Node


class PitchTrackerBase:
    """Abstract pitch tracker interface"""

    def __init__(self):
        pass

    def process(self, x):
        """
        Extract pitch from audio buffer x.

        Parameters
        ----------
        x : numpy array float32 dim=2 shape=1,n
            array of samples

        Returns
        -------
        f0 : float
            fundamental frequency
        voiced : float {0, 1}
            a flag, 1 for pitched signal
        """
        f0 = 0
        voiced = False
        return f0, voiced

    def clear(self):
        """Reset any internal state."""
        pass

    def latency(self):
        """Return latency in number of samples."""
        return 0


class PitchTrackerUnit(Node):
    """
    Abstract base class. Use one of its subclass.

    To subclass override methods:
    - pitch_track()
    - latency()
    """

    def __init__(self, world, pitch_tracker):
        """

        Parameters
        ----------
        pitch_tracker : PitchTrackerBase object
            the actual pitch tracker algorithm, encapsulated in the PitchTrackerBase interface
        """
        super().__init__(world)

        self.pitch_tracker = pitch_tracker
        self.w_in = Wire(self, Wire.audioRate, Wire.wiretype_input, world.buf_len)
        self.w_f0 = Wire(self, Wire.controlRate, Wire.wiretype_output, world.buf_len)
        self.w_voiced = Wire(world, Wire.controlRate, Wire.wiretype_output, world.buf_len)

        self.in_wires.append(self.w_in)
        self.out_wires.extend([self.w_f0, self.w_voiced])

    def clear(self):
        self.pitch_tracker.clear()

    def calc_func(self):
        f0, voiced = self.pitch_tracker.process(self.w_in._buf)
        self.w_f0.set_value(f0)
        self.w_voiced.set_value(voiced)

    def latency(self):
        return self.pitch_tracker.latency()



