from .AudioDriver import AudioDriver
from .AudioGraph import Group
import numpy as np


class World:
    def __init__(self, bufLen=64, sampleRate=44100, nChannels=2):
        self.bufLen = bufLen
        self.sampleRate = sampleRate
        self.nChannels = nChannels

        self._audioDriver = AudioDriver(self)
        self._topGroup = Group(self)
        self._isRunning = False

        self._allocateBuffers()

        self.t = 0
        self.fr = 400

    def _allocateBuffers(self):
        self.inBuffer = np.zeros((self.nChannels, self.bufLen), dtype=np.float32)
        self.outBuffer = np.zeros((self.nChannels, self.bufLen), dtype=np.float32)

    def addHead(self, node):
        self._topGroup.addHead(node)

    def addTail(self, node):
        self._topGroup.addTail(node)

    def start(self):
        if(self._isRunning == False):
            self._audioDriver.start()
            self._isRunning = True

    def run(self, in_data):
        # deinterlave
        self.inBuffer[:] = np.fromstring(in_data, dtype=np.float32).reshape((self.nChannels, -1), order='F')

        # give self.buffers[0] to in unit
        self._topGroup.calcFunc()

        # interlave
        out_data = self.outBuffer.tostring(order='F')
        return out_data

    def stop(self):
        if(self._isRunning == True):
            self._audioDriver.stop()
            self._isRunning = False

    def dispose(self):
        self._audioDriver.dispose()
