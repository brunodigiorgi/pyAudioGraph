import numpy as np
from .BufferedAudioStream import BufferedAudioStream
from .AudioGraph import Node
from .Wire import Wire
from .Range import RangeQueue
from .CmdQueue import AsyncCmdQueue


class DiskInUnit(Node):
    def __init__(self, world, audioStream, cmdQueue=None):
        super().__init__(world)
        self.nChannels = audioStream.nChannels
        self.length = audioStream.length
        self.sampleRate = audioStream.sampleRate

        if(cmdQueue is None):
            cmdQueue = AsyncCmdQueue()

        self.baf = BufferedAudioStream(audioStream, cmdQueue, frameLength=world.bufLen)
        self.rangeQueue = RangeQueue()  # rangeQueue of the last read segment

        self.outBuffer = np.zeros((self.baf.nChannels, world.bufLen))
        self.w_out = []
        for i in range(self.nChannels):
            self.w_out.append(Wire(world, Wire.audioRate, Wire.wiretype_output))

    def calcFunc(self):
        self.rangeQueue.clear()
        self.baf.read(self.outBuffer, outRangeQueue=self.rangeQueue)
        for i in range(self.nChannels):
            self.w_out[i].setBuffer(self.outBuffer[i])

    def enableLoop(self, flag):
        self.baf.enableLoop(flag)

    def setLoop(self, loop_start, loop_end):
        self.baf.setLoop(loop_start, loop_end)

    def seek(self, pos):
        self.baf.seek(pos)

    def prime(self):
        # synchronously fill buffer. Do not call when audio thread is running
        self.baf.prime()
