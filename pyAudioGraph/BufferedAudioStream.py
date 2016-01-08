import numpy as np
from .Range import RangeQueue
from .AudioStream import AudioStream
from .CmdQueue import LambdaCommand


class LoopableAudioStream(AudioStream):
    def __init__(self, stream):
        super().__init__()
        self.stream = stream
        self.nChannels = self.stream.nChannels
        self.length = self.stream.length
        self.sampleRate = self.stream.sampleRate
        
        self.loop_enabled = False
        self.loop_start = 0
        self.loop_end = self.length

    def enableLoop(self, flag):
        self.loop_enabled = flag
        if(self.loop_enabled and
           (self.stream.pos() > self.loop_end) or
           (self.stream.pos() < self.loop_start)):
            self.stream.seek(self.loop_start)

    def setLoop(self, loop_start, loop_end):
        assert(loop_end > loop_start)
        self.loop_start = loop_start
        self.loop_end = loop_end
        if(self.loop_enabled and
           (self.stream.pos() > self.loop_end) or
           (self.stream.pos() < self.loop_start)):
            self.stream.seek(self.loop_start)

    def read(self, outBuffer, start=0, length=None, outRangeQueue=None):
        if(length is None):
            length = outBuffer.shape[1]
        assert(start + length <= outBuffer.shape[1])

        l_enabled = self.loop_enabled
        l_start = self.loop_start
        l_end = self.loop_end

        if(not l_enabled):
            return self.stream.read(outBuffer, 
                                    start=start, 
                                    length=length, 
                                    outRangeQueue=outRangeQueue)
        else:
            remaining = length
            count = 0
            while(remaining):
                if(self.stream.pos() < l_end):
                    toRead = np.minimum(remaining, l_end - self.stream.pos())
                else:
                    toRead = remaining
                advance = self.stream.read(outBuffer, 
                                           start=count, 
                                           length=toRead,
                                           outRangeQueue=outRangeQueue)
                remaining -= advance
                count += advance
                if(self.stream.pos() == l_end):
                    self.stream.seek(l_start)
            return count

    def seek(self, pos):
        self.stream.seek(pos)

    def pos(self):
        return self.stream.pos()


class AudioFrame:
    def __init__(self, nChannels, length):
        self.data = np.zeros((nChannels, length), dtype=np.float32)
        self.rangeQueue = RangeQueue()


class AudioFrameRingBuffer:
    def __init__(self, nFrames, nChannels, frameLength):
        self.numFrames = nFrames
        self.nChannels = nChannels
        self.frameLength = frameLength
        self.frameList = [AudioFrame(self.nChannels, self.frameLength) for i in range(self.numFrames)]
        self.buf_head = 0
        self.buf_tail = 0
        self.buf_available = 0
        self._needRefill = True

    def clear(self):
        self.buf_head = 0
        self.buf_tail = 0
        self.buf_available = 0

    def fill(self, stream):
        toRead = self.numFrames - self.buf_available

        for i in range(toRead):
            self.frameList[self.buf_head].rangeQueue.clear()
            stream.read(self.frameList[self.buf_head].data, 0, None, self.frameList[self.buf_head].rangeQueue)

            self.buf_available += 1
            self.buf_head += 1
            if(self.buf_head == self.numFrames):
                self.buf_head = 0

        self._needRefill = False

    def read(self, outBuffer, start=0, length=None, outRangeQueue=None):
        assert(outBuffer.shape[0] == self.nChannels)
        assert(length == self.frameLength)

        if(self.buf_available > 0):
            outBuffer[:, start:start + length] = self.frameList[self.buf_tail].data
            if(outRangeQueue is not None):
                outRangeQueue.pushRangeQueue(self.frameList[self.buf_tail].rangeQueue)

            self.buf_available -= 1
            self.buf_tail += 1
            if(self.buf_tail == self.numFrames):
                self.buf_tail = 0

        if(self.buf_available <= self.numFrames / 2):
            self._needRefill = True

    def needRefill(self):
        return self._needRefill


class BufferedAudioStream(LoopableAudioStream):
    """
    reads from the hard drive in a worker thread
    """
    def __init__(self, stream, cmdQueue, frameLength, numFrames=16):
        # type check
        assert(isinstance(stream, AudioStream))
        assert(not isinstance(stream, LoopableAudioStream))

        self.stream = LoopableAudioStream(stream)
        self.nChannels = self.stream.nChannels
        self.length = self.stream.length
        self.sampleRate = self.stream.sampleRate

        self.loop_enabled = self.stream.loop_enabled
        self.loop_start = self.stream.loop_start
        self.loop_end = self.stream.loop_end

        self.cmdQueue = cmdQueue
        self.ringBuffer = AudioFrameRingBuffer(numFrames, self.nChannels, frameLength)

        self.needSeek = False
        self.needSeekPos = 0

    # LoopableAudioStream
    def enableLoop(self, flag):
        self.stream.enableLoop(flag)
        self.loop_enabled = self.stream.loop_enabled

    def setLoop(self, loop_start, loop_end):
        self.stream.setLoop(loop_start, loop_end)
        self.loop_start = self.stream.loop_start
        self.loop_end = self.stream.loop_end

    # AudioStream
    def read(self, outBuffer, start=0, length=None, outRangeQueue=None):
        assert(outBuffer.shape[0] == self.nChannels)
        if(length is None):
            length = outBuffer.shape[1]
        assert(start + length <= outBuffer.shape[1])

        # ring buffer read
        self.ringBuffer.read(outBuffer, start=start, length=length, outRangeQueue=outRangeQueue)

        # async seek, if needed, and fill buffer
        if(self.ringBuffer.needRefill()):
            self._seekFillBuffer(True)

        return length

    def seek(self, pos):
        self.needSeek = True
        self.needSeekPos = pos

    def pos(self):
        return self.stream.pos()

    # BufferedAudioStream
    def prime(self):
        # synchronously fill buffer. Do not call when audio thread is running
        self.cmdQueue.flush()
        self.ringBuffer.clear()
        self._seekFillBuffer(False)  # seek and fill synchronously

    def _seekFillBuffer(self, async):
        if(self.needSeek):
            self._seekCmd(async)
            self.needSeek = False

        self._readCmd(async)

    def _seekCmd(self, async):
        cmd = LambdaCommand(self.stream.seek, args=(self.needSeekPos,))
        if(async):
            self.cmdQueue.push(cmd)
        else:
            cmd()

    def _readCmd(self, async):
        cmd = LambdaCommand(self.ringBuffer.fill, args=(self.stream,))
        if(async):
            self.cmdQueue.push(cmd)
        else:
            cmd()
