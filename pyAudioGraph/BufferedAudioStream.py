import numpy as np
from .Range import RangeQueue
from .AudioStream import AudioStream
from .CmdQueue import LambdaCommand


class LoopableAudioStream(AudioStream):
    def __init__(self, stream):
        super().__init__()
        self.stream = stream
        self.nchannels = self.stream.nchannels
        self.length = self.stream.length
        self.sampleRate = self.stream.sampleRate

        self.loop_enabled = False
        self.loop_start = 0
        self.loop_end = self.length

    def enable_loop(self, flag):
        self.loop_enabled = flag
        if(self.loop_enabled and
           (self.stream.pos() > self.loop_end) or
           (self.stream.pos() < self.loop_start)):
            self.stream.seek(self.loop_start)

    def set_loop(self, loop_start, loop_end):
        assert(loop_end > loop_start)
        self.loop_start = loop_start
        self.loop_end = loop_end
        if(self.loop_enabled and
           (self.stream.pos() > self.loop_end) or
           (self.stream.pos() < self.loop_start)):
            self.stream.seek(self.loop_start)

    def read(self, out_buffer, start=0, length=None, out_range_queue=None):
        if(length is None):
            length = out_buffer.shape[1]
        assert(start + length <= out_buffer.shape[1])

        l_enabled = self.loop_enabled
        l_start = self.loop_start
        l_end = self.loop_end

        if(not l_enabled):
            return self.stream.read(out_buffer,
                                    start=start,
                                    length=length,
                                    out_range_queue=out_range_queue)
        else:
            remaining = length
            count = 0
            while(remaining):
                if(self.stream.pos() < l_end):
                    to_read = np.minimum(remaining, l_end - self.stream.pos())
                else:
                    to_read = remaining
                advance = self.stream.read(out_buffer,
                                           start=count,
                                           length=to_read,
                                           out_range_queue=out_range_queue)
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
    def __init__(self, nchannels, length):
        self.data = np.zeros((nchannels, length), dtype=np.float32)
        self.rangeQueue = RangeQueue()


class AudioFrameRingBuffer:
    def __init__(self, nframes, nchannels, frame_length):
        self.nframes = nframes
        self.nchannels = nchannels
        self.frame_length = frame_length
        self.frameList = [AudioFrame(self.nchannels, self.frame_length) for i in range(self.nframes)]
        self.buf_head = 0
        self.buf_tail = 0
        self.buf_available = 0
        self._need_refill = True

    def clear(self):
        self.buf_head = 0
        self.buf_tail = 0
        self.buf_available = 0

    def fill(self, stream):
        to_read = self.nframes - self.buf_available

        for i in range(to_read):
            self.frameList[self.buf_head].rangeQueue.clear()
            stream.read(self.frameList[self.buf_head].data, 0, None, self.frameList[self.buf_head].rangeQueue)

            self.buf_available += 1
            self.buf_head += 1
            if(self.buf_head == self.nframes):
                self.buf_head = 0

        self._need_refill = False

    def read(self, out_buffer, start=0, length=None, out_range_queue=None):
        assert(out_buffer.shape[0] == self.nchannels)
        assert(length == self.frame_length)

        if(self.buf_available > 0):
            out_buffer[:, start:start + length] = self.frameList[self.buf_tail].data
            if(out_range_queue is not None):
                out_range_queue.push_range_queue(self.frameList[self.buf_tail].rangeQueue)

            self.buf_available -= 1
            self.buf_tail += 1
            if(self.buf_tail == self.nframes):
                self.buf_tail = 0

        if(self.buf_available <= self.nframes / 2):
            self._need_refill = True

    def need_refill(self):
        return self._need_refill


class BufferedAudioStream(LoopableAudioStream):
    """
    reads from the hard drive in a worker thread
    """
    def __init__(self, stream, cmd_queue, frame_length, nframes=16):
        # type check
        assert(isinstance(stream, AudioStream))
        assert(not isinstance(stream, LoopableAudioStream))

        self.stream = LoopableAudioStream(stream)
        self.nchannels = self.stream.nchannels
        self.length = self.stream.length
        self.sampleRate = self.stream.sampleRate

        self.loop_enabled = self.stream.loop_enabled
        self.loop_start = self.stream.loop_start
        self.loop_end = self.stream.loop_end

        self.cmd_queue = cmd_queue
        self.ringBuffer = AudioFrameRingBuffer(nframes, self.nchannels, frame_length)

        self.needSeek = False
        self.needSeekPos = 0

    # LoopableAudioStream
    def enable_loop(self, flag):
        self.stream.enable_loop(flag)
        self.loop_enabled = self.stream.loop_enabled

    def set_loop(self, loop_start, loop_end):
        self.stream.set_loop(loop_start, loop_end)
        self.loop_start = self.stream.loop_start
        self.loop_end = self.stream.loop_end

    # AudioStream
    def read(self, out_buffer, start=0, length=None, out_range_queue=None):
        assert(out_buffer.shape[0] == self.nchannels)
        if(length is None):
            length = out_buffer.shape[1]
        assert(start + length <= out_buffer.shape[1])

        # ring buffer read
        self.ringBuffer.read(out_buffer, start=start, length=length, out_range_queue=out_range_queue)

        # async seek, if needed, and fill buffer
        if(self.ringBuffer.need_refill()):
            self._seek_fill_buffer(True)

        return length

    def seek(self, pos):
        self.needSeek = True
        self.needSeekPos = pos

    def pos(self):
        return self.stream.pos()

    # BufferedAudioStream
    def prime(self):
        # synchronously fill buffer. Do not call when audio thread is running
        self.cmd_queue.flush()
        self.ringBuffer.clear()
        self._seek_fill_buffer(False)  # seek and fill synchronously

    def _seek_fill_buffer(self, async):
        if(self.needSeek):
            self._seek_cmd(async)
            self.needSeek = False

        self._read_cmd(async)

    def _seek_cmd(self, async):
        cmd = LambdaCommand(self.stream.seek, args=(self.needSeekPos,))
        if(async):
            self.cmd_queue.push(cmd)
        else:
            cmd()

    def _read_cmd(self, async):
        cmd = LambdaCommand(self.ringBuffer.fill, args=(self.stream,))
        if(async):
            self.cmd_queue.push(cmd)
        else:
            cmd()
