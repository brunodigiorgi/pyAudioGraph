"""
AudioBuffer module provides two class.

* AudioBuffer: a simple wrapper of 2-dim numpy array with methods for writing, accumulating and reading.
* RingBuffer: a circular buffer with independent writeIndex and readIndex
"""

import numpy as np


class AudioBuffer:
    """Multichannel buffer, based on numpy ndarray."""

    def __init__(self, nchannels, length):
        self.nchannels = nchannels
        self.length = length
        self.buf = np.zeros((self.nchannels, self.length), dtype=np.float32)

    def clear(self, length=None, start=0):
        """Write zero to all buffer samples."""
        if(length is None):
            length = self.length
        self.buf[:, start:start + length] = 0

    def write(self, length, start, in_buffer, in_offset=0):
        """Write to the buffer.

        Parameters
        ----------
        length : int
            number of samples to write
        start : int
            start position of the destination buffer
        in_buffer : numpy.ndarray of shape (nchannels, n)
            input buffer
        in_offset : int
            start position of the source buffer

        Returns
        -------
        int
            number of samples written
        """
        assert(self.length >= start and in_buffer.ndim == 2 and in_buffer.shape[0] == self.nchannels)
        to_write = np.minimum(length, self.length - start)  # how much space to fill
        self.buf[:, start:start + to_write] = in_buffer[:, in_offset:in_offset + to_write]
        return to_write

    def accumulate(self, length, start, in_buffer, in_offset=0, in_scale=1):
        """Sum the given samples to the buffer.

        Parameters
        ----------
        see AudioBuffer.write

        Returns
        -------
        see AudioBuffer.write
        """
        assert(self.length >= start and in_buffer.ndim == 2 and in_buffer.shape[0] == self.nchannels)
        to_write = np.minimum(length, self.length - start)  # how much space to fill
        self.buf[:, start:start + to_write] += in_scale * in_buffer[:, in_offset:in_offset + to_write]
        return to_write

    def read(self, length, start, out_buffer, out_offset=0):
        """Read from the buffer to out_buffer.

        Parameters
        ----------
        length : int
            number of samples to read
        start : int
            start position of the source buffer
        out_buffer : numpy.ndarray of shape (nchannels, n)
            output buffer
        out_offset : int
            start position of the destination buffer

        Returns
        -------
        int
            number of samples read
        """
        assert(self.length >= start and out_buffer.ndim == 2 and out_buffer.shape[0] == self.nchannels)
        to_read = np.minimum(length, self.length - start)  # how much space to fill
        out_buffer[:, out_offset:out_offset + to_read] = self.buf[:, start:start + to_read]
        return to_read


class RingBuffer:
    """
    Multi-channel ring buffer, with independent head and tail.

    * RingBuffer.write does advance the head
    * RingBuffer.accumulate does not advance the head, in this way the RingBuffer can be used as Overlapper
    * RingBuffer.read does not avance the tail, in this way the RingBuffer can be used as Framer

    usage as Framer:

    #. write a frame (incoming frames are non overlapping)
    #. advance_write_index(frame length)
    #. while available() > needed
      #. read a frame
      #. advance_read_index(hopsize)

    usage as Overlapper:

    #. accumulate a buffer of N samples
    #. advance_write_index(M) with M<N
    #. read M samples
    #. advance_read_index(M)
    """

    def __init__(self, nchannels, length):
        self._nchannels = nchannels
        self._length = length
        self._buf = AudioBuffer(self._nchannels, self._length)
        self._head = 0
        self._tail = 0
        self._available = 0

    def resize(self, length):
        """
        Resize the buffer to given length and reset its state.

        Parameters
        ----------
        length : int
            the new length of the buffer
        """
        self._length = length
        self._buf = AudioBuffer(self._nchannels, self._length)
        self.clear()

    def clear(self):
        """Reset the state of the buffer."""
        self._buf.clear()
        self._head = 0
        self._tail = 0
        self._available = 0

    def write(self, in_buffer):
        """
        Write on the buffer and advance write index.

        Parameters
        ----------
        in_buffer : numpy.ndarray of shape (nchannels, n)
            input buffer

        Returns
        -------
        int
            number of written samples
        """
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
        """
        Sum buffer to current content, does not advance write index.

        Parameters
        ----------
        in_buffer : numpy.ndarray of shape (nchannels, n)
            input buffer
        offset : int
            offset from current write index at which start writing
        in_scale : float
            multiply in_buffer when accumulating

        Returns
        -------
        int
            number of written samples
        """
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
        Advance writing (head) pointer.

        Parameters
        ----------
        n : int
            samples to advance

        Returns
        -------
        int
            samples advanced
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
        """
        Read to the given output buffer, does not advance read index.

        Parameters
        ----------
        out_buffer : numpy.ndarray of shape (nchannels, n)
            output buffer

        Returns
        -------
        int
            number of read samples
        """
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
        Advance reading (tail) pointer.

        Parameters
        ----------
        n : int
            samples to advance

        Returns
        -------
        int
            samples advanced
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
        """Return number of available samples."""
        return self._available

    def length(self):
        return self._length
