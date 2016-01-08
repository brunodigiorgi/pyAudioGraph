from .AudioBuffer import RingBuffer
from .AudioGraph import Node
from .Wire import Wire
import numpy as np


class SamplerUnit(Node):
    def __init__(self, world, nChannels):
        super().__init__(world)

        self.nChannels = no = nChannels
        self.buffers = []
        self.ringBuffer = RingBuffer(self.nChannels, world.bufLen)
        self.w_out = [Wire(world, Wire.audioRate, Wire.wiretype_output) for o in range(no)]
        self.temp_out = np.zeros((no, world.bufLen), dtype=np.float32)

        self.triggerList = []

    def addBuffer(self, buf):
        assert(buf.shape[0] == self.nChannels)
        self.buffers.append(buf)
        newLen = buf.shape[1] + self.world.bufLen
        if(self.ringBuffer.length() < newLen):
            self.ringBuffer.resize(newLen)
        return len(self.buffers)

    def reset(self):
        self.ringBuffer.clear()

    def setTrigger(self, triggerList):
        """
        triggerList = [(t_id, t_pos, t_scale), ...]
          t_id is the buffer id (int)
          t_pos is the sample offset (int)
          t_scale is a level coeff for accumulation (float)
        """
        self.triggerList = triggerList

    def calcFunc(self):

        nb = len(self.buffers)
        no = self.nChannels

        # pre-conditions
        if(nb == 0):
            for o in range(no):
                self.w_out[o]._buf[:] = 0
            return

        for t_id, t_pos, t_sc in self.triggerList:
            if(t_id < nb):
                self.ringBuffer.accumulate(self.buffers[t_id], offset=t_pos, inScale=t_sc)

        self.triggerList = []
        self.ringBuffer.advanceWriteIndex(self.world.bufLen)
        self.ringBuffer.read(self.temp_out)
        self.ringBuffer.advanceReadIndex(self.world.bufLen)

        for o in range(no):
            self.w_out[o].setBuffer(self.temp_out[o, :])
