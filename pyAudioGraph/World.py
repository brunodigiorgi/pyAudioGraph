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

        self.t = 0
        self.fr = 400

    def _allocate_buffers(self):
        self.inBuffer = np.zeros((self.nchannels, self.buf_len), dtype=np.float32)
        self.outBuffer = np.zeros((self.nchannels, self.buf_len), dtype=np.float32)

    def add_head(self, node):
        """
        Set the first node in the graph traversal sequence.

        Parameters
        ----------
        node : Node
            first node to be called in the audio graph traversal sequence
        """
        self._topGroup.add_head(node)

    def add_tail(self, node):
        """
        Set the last node in the graph traversal sequence.

        Parameters
        ----------
        node : Node
            last node to be called in the audio graph traversal sequence
        """
        self._topGroup.add_tail(node)

    def start(self):
        """Start the audio thread if not already running."""
        if(not self._isRunning):
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
        if(self._isRunning):
            self._audioDriver.stop()
            self._isRunning = False

    def dispose(self):
        """Clean up."""
        self._audioDriver.dispose()
