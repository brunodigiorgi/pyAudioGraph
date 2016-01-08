from .AudioDriver import AudioDriver
from .AudioGraph import Group
import numpy as np


class World:
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
        self._topGroup.add_head(node)

    def add_tail(self, node):
        self._topGroup.add_tail(node)

    def start(self):
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
        if(self._isRunning):
            self._audioDriver.stop()
            self._isRunning = False

    def dispose(self):
        self._audioDriver.dispose()
