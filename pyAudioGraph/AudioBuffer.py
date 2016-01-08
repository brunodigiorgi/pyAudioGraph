import numpy as np


class AudioBuffer:
    """
    multichannel buffer, based on numpy ndarray
    """
    def __init__(self, nchannels, length):
        self.nchannels = nchannels
        self.length = length
        self.buf = np.zeros((self.nchannels, self.length), dtype=np.float32)

    def clear(self, length=None, start=0):
        if(length is None):
            length = self.length
        self.buf[:, start:start + length] = 0

    def write(self, length, start, in_buffer, in_offset=0):
        assert(self.length >= start and in_buffer.ndim == 2 and in_buffer.shape[0] == self.nchannels)
        to_write = np.minimum(length, self.length - start)  # how much space to fill
        self.buf[:, start:start + to_write] = in_buffer[:, in_offset:in_offset + to_write]
        return to_write

    def accumulate(self, length, start, in_buffer, in_offset=0, in_scale=1):
        assert(self.length >= start and in_buffer.ndim == 2 and in_buffer.shape[0] == self.nchannels)
        to_write = np.minimum(length, self.length - start)  # how much space to fill
        self.buf[:, start:start + to_write] += in_scale * in_buffer[:, in_offset:in_offset + to_write]
        return to_write

    def read(self, length, start, out_buffer, out_offset=0):
        assert(self.length >= start and out_buffer.ndim == 2 and out_buffer.shape[0] == self.nchannels)
        to_read = np.minimum(length, self.length - start)  # how much space to fill
        out_buffer[:, out_offset:out_offset + to_read] = self.buf[:, start:start + to_read]
        return to_read


class RingBuffer:
    """
    multi_channel ring buffer, based on AudioBuffer

    write does advance the head
    accumulate does not advance the head, in this way the RingBuffer can be used as Overlapper
    read does not avance the tail, in this way the RingBuffer can be used as Framer

    usage as Framer:
    1) write the a frame (incoming frames are non overlapping)
       advance_write_index(frame length)

    2) while(available() > needed)
        2a) read a frame from the tail
        2b) advance_read_index(hopsize)

    usage as Overlapper:
    1) accumulate a buffer of N samples
       advance_write_index(M) with M<N

    2) read M samples
       advance_read_index(M)
    """
    def __init__(self, nchannels, length):
        self._nchannels = nchannels
        self._length = length
        self._buf = AudioBuffer(self._nchannels, self._length)
        self._head = 0
        self._tail = 0
        self._available = 0

    def resize(self, length):
        self._length = length
        self._buf = AudioBuffer(self._nchannels, self._length)
        self.clear()

    def clear(self):
        self._buf.clear()
        self._head = 0
        self._tail = 0
        self._available = 0

    def write(self, in_buffer):
        assert(in_buffer.ndim == 2 and in_buffer.shape[0] == self._nchannels)

        remaining = np.minimum(in_buffer.shape[1], self._length - self._available)
        count = 0

        while(remaining > 0):
            written = self._buf.write(remaining, self._head, in_buffer, in_offset=count)

            self._head += written
            if(self._head == self._length):
                self._head = 0
            self._available += written
            remaining -= written
            count += written

        return count

    def accumulate(self, in_buffer, offset=0, in_scale=1):
        assert(in_buffer.ndim == 2 and in_buffer.shape[0] == self._nchannels)

        remaining = np.minimum(in_buffer.shape[1], self._length - self._available)
        count = 0
        head_tmp = self._head + offset

        while(remaining > 0):
            written = self._buf.accumulate(remaining, head_tmp, in_buffer, in_offset=count, in_scale=in_scale)

            head_tmp += written
            if(head_tmp == self._length):
                head_tmp = 0
            remaining -= written
            count += written

        return count

    def advance_write_index(self, n):
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

    def read(self, out_buffer):
        assert(out_buffer.ndim == 2 and out_buffer.shape[0] == self._nchannels)

        remaining = np.minimum(out_buffer.shape[1], self._available)
        count = 0
        tail_tmp = self._tail

        while(remaining):
            read = self._buf.read(remaining, tail_tmp, out_buffer, out_offset=count)

            tail_tmp += read
            if(tail_tmp == self._length):
                tail_tmp = 0
            remaining -= read
            count += read

        return count

    def advance_read_index(self, n):
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
