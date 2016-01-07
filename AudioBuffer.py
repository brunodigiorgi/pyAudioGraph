import numpy as np


class AudioBuffer:
    """
    multichannel buffer, based on numpy ndarray
    """
    def __init__(self, nChannels, length):
        self.nChannels = nChannels
        self.length = length
        self.buf = np.zeros((self.nChannels, self.length), dtype=np.float32)

    def clear(self, length=None, start=0):
        if(length is None):
            length = self.length
        self.buf[:, start:start+length] = 0

    def write(self, length, start, inBuffer, inOffset=0):
        assert(self.length >= start and inBuffer.ndim == 2 and inBuffer.shape[0] == self.nChannels)
        toWrite = np.minimum(length, self.length - start)  # how much space to fill
        self.buf[:, start:start + toWrite] = inBuffer[:, inOffset:inOffset + toWrite]
        return toWrite

    def accumulate(self, length, start, inBuffer, inOffset=0, inScale=1):
        assert(self.length >= start and inBuffer.ndim == 2 and inBuffer.shape[0] == self.nChannels)
        toWrite = np.minimum(length, self.length - start)  # how much space to fill
        self.buf[:, start:start + toWrite] += inScale * inBuffer[:, inOffset:inOffset + toWrite]
        return toWrite

    def read(self, length, start, outBuffer, outOffset=0):
        assert(self.length >= start and outBuffer.ndim == 2 and outBuffer.shape[0] == self.nChannels)
        toRead = np.minimum(length, self.length - start)  # how much space to fill
        outBuffer[:, outOffset:outOffset + toRead] = self.buf[:, start:start + toRead]
        return toRead


class RingBuffer:
    """
    multi_channel ring buffer, based on AudioBuffer

    write does advance the head
    accumulate does not advance the head, in this way the RingBuffer can be used as Overlapper
    read does not avance the tail, in this way the RingBuffer can be used as Framer

    usage as Framer:
    1) write the a frame (incoming frames are non overlapping)
       advanceWriteIndex(frame length)

    2) while(available() > needed)
        2a) read a frame from the tail
        2b) advanceReadIndex(hopsize)

    usage as Overlapper:
    1) accumulate a buffer of N samples
       advanceWriteIndex(M) with M<N

    2) read M samples
       advanceReadIndex(M)
    """
    def __init__(self, nChannels, length):
        self._nChannels = nChannels
        self._length = length
        self._buf = AudioBuffer(self._nChannels, self._length)
        self._head = 0
        self._tail = 0
        self._available = 0

    def resize(self, length):
        self._length = length
        self._buf = AudioBuffer(self._nChannels, self._length)
        self.clear()

    def clear(self):
        self._buf.clear()
        self._head = 0
        self._tail = 0
        self._available = 0

    def write(self, inBuffer):
        assert(inBuffer.ndim == 2 and inBuffer.shape[0] == self._nChannels)

        remaining = np.minimum(inBuffer.shape[1], self._length - self._available)
        count = 0

        while(remaining > 0):
            written = self._buf.write(remaining, self._head, inBuffer, inOffset=count)

            self._head += written
            if(self._head == self._length):
                self._head = 0
            self._available += written
            remaining -= written
            count += written

        return count

    def accumulate(self, inBuffer, offset=0, inScale=1):
        assert(inBuffer.ndim == 2 and inBuffer.shape[0] == self._nChannels)

        remaining = np.minimum(inBuffer.shape[1], self._length - self._available)
        count = 0
        head_tmp = self._head + offset

        while(remaining > 0):
            written = self._buf.accumulate(remaining, head_tmp, inBuffer, inOffset=count, inScale=inScale)

            head_tmp += written
            if(head_tmp == self._length):
                head_tmp = 0
            remaining -= written
            count += written

        return count

    def advanceWriteIndex(self, n):
        """
        advance head
        """
        remaining = np.minimum(n, self._length - self._available)
        count = 0

        while(remaining):
            consumed = np.minimum(self._length - self._head, remaining)
            self._head += consumed
            if(self._head == self._length):
                self._head = 0
            self._available += consumed
            remaining -= consumed
            count += consumed

        return count

    def read(self, outBuffer):
        assert(outBuffer.ndim == 2 and outBuffer.shape[0] == self._nChannels)

        remaining = np.minimum(outBuffer.shape[1], self._available)
        count = 0
        tail_tmp = self._tail

        while(remaining):
            read = self._buf.read(remaining, tail_tmp, outBuffer, outOffset=count)

            tail_tmp += read
            if(tail_tmp == self._length):
                tail_tmp = 0
            remaining -= read
            count += read

        return count

    def advanceReadIndex(self, n):
        """
        advance tail
        """
        remaining = np.minimum(n, self._available)
        count = 0

        while(remaining):
            consumed = np.minimum(self._length - self._tail, remaining)
            self._buf.clear(consumed, self._tail)  # put used samples to zeros, needed for overlapper mode

            self._tail += consumed
            if(self._tail == self._length):
                self._tail = 0
            self._available -= consumed
            remaining -= consumed
            count += consumed

        return count

    def available(self):
        return self._available

    def length(self):
        return self._length
