"""Contains the class World which setup the audio driver and traverse the audio graph evaluating each node."""

from .AudioDriver import AudioDriver
from .AudioGraph import Group
import numpy as np


class World:
    """
    Setup the audio driver and traverse the audio graph evaluating each node.

    Traversal is done by manually setup a call sequence using methods:

    * World.add_head(Node)
    * World.add_tail(Node)
    * Node.add_after(Node)
    * Node.add_before(Node)
    """

    def __init__(self, buf_len=64, sample_rate=44100, nchannels=2):
        self.buf_len = buf_len
        self.sample_rate = sample_rate
        self.nchannels = nchannels

        self._audioDriver = AudioDriver(self)
        self._topGroup = Group(self)
        self._isRunning = False

        self._allocate_buffers()

        self.nrt = False

    def _allocate_buffers(self):
        self.inBuffer = np.zeros((self.nchannels, self.buf_len), dtype=np.float32)
        self.outBuffer = np.zeros((self.nchannels, self.buf_len), dtype=np.float32)

    def append(self, node):
        """
        Append the node to the node list of the top group.
        node may be a Node or a list of Nodes

        Call sort(), after all the nodes have been added in the list
        """
        try:
            for n in node:
                self._topGroup.append(n)
        except TypeError:
            self._topGroup.append(node)

    def sort(self):
        self._topGroup.sort()

    def start(self):
        """Start the audio thread if not already running."""
        if not self._isRunning:
            self._audioDriver.start()
            self._isRunning = True

    def run(self, in_data):
        # deinterlave
        self.inBuffer[:] = np.fromstring(in_data, dtype=np.float32).reshape((self.nchannels, -1), order='F')

        # give self.buffers[0] to in unit
        self._topGroup.calc_func()

        # interlave
        out_data = self.outBuffer.tostring(order='F')
        return out_data

    def stop(self):
        """Stop the audio thread if running."""
        if self._isRunning:
            self._audioDriver.stop()
            self._isRunning = False

    def run_nrt(self, stop_condition):
        """
        Run in non-real-time mode.

        Parameters
        ----------
        stop_condition : callable
            called at every cycle. Return if True
        """
        self.nrt = True
        self._isRunning = True
        while not stop_condition():
            self._topGroup.calc_func()
        self._isRunning = False
        self.nrt = False

    def is_running(self):
        return self._isRunning

    def dispose(self):
        """Clean up."""
        self._audioDriver.dispose()
