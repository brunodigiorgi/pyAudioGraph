# -*- coding: utf-8 -*-
"""Pitch Tracker Node class (PitchTrackerNode) and Pitch Tracker Algorithm (PitchTrackerBase) interface."""

from ..Wire import InWire, OutWire
from ..AudioGraph import Node


class PitchTrackerBase:
    """Abstract pitch tracker interface."""

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


class PitchTrackerNode(Node):
    """
    Abstract base class. Use one of its subclass.

    To subclass override methods:
    - pitch_track()
    - latency()
    """

    def __init__(self, world, pitch_tracker):
        """
        Initialize the PitchTrackerNode.

        Parameters
        ----------
        pitch_tracker : PitchTrackerBase object
            the actual pitch tracker algorithm, encapsulated in the PitchTrackerBase interface
        """
        super().__init__(world)

        self.pitch_tracker = pitch_tracker
        self.w_in = InWire(self)
        self.w_f0 = OutWire(self)
        self.w_voiced = OutWire(self)

        self.in_wires.append(self.w_in)
        self.out_wires.extend([self.w_f0, self.w_voiced])

    def clear(self):
        self.pitch_tracker.clear()

    def calc_func(self):
        in_array = self.w_in.get_data()
        f0, voiced = self.pitch_tracker.process(in_array)
        self.w_f0.set_data(f0)
        self.w_voiced.set_data(voiced)

    def latency(self):
        return self.pitch_tracker.latency()
