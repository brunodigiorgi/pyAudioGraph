import numpy as np
from ..BufferedAudioStream import BufferedAudioStream
from ..AudioGraph import Node
from ..Wire import Wire
from ..Range import RangeQueue
from ..CmdQueue import AsyncCmdQueue


class DiskInNode(Node):
    """
    out_wires:
        - w_out : list, audioRate
    """

    def __init__(self, world, audio_stream, cmd_queue=None):
        super().__init__(world)
        self.nchannels = audio_stream.nchannels
        self.length = audio_stream.length
        self.sample_rate = audio_stream.sample_rate

        if(cmd_queue is None):
            cmd_queue = AsyncCmdQueue()

        self.baf = BufferedAudioStream(audio_stream, cmd_queue, frame_length=world.buf_len)
        self.rangeQueue = RangeQueue()  # rangeQueue of the last read segment

        self.outBuffer = np.zeros((self.baf.nchannels, world.buf_len))
        self.w_out = []
        for i in range(self.nchannels):
            self.w_out.append(Wire(self, Wire.audioRate, Wire.wiretype_output, world.buf_len))

        self.out_wires.extend(self.w_out)

    def calc_func(self):
        self.rangeQueue.clear()
        async = not self.world.nrt
        self.baf.read(self.outBuffer, out_range_queue=self.rangeQueue, async=async)
        for i in range(self.nchannels):
            self.w_out[i].set_buffer(self.outBuffer[i])

    def enable_loop(self, flag):
        self.baf.enable_loop(flag)

    def set_loop(self, loop_start, loop_end):
        self.baf.set_loop(loop_start, loop_end)

    def seek(self, pos):
        self.baf.seek(pos)

    def pos(self):
        return self.baf.pos()

    def prime(self):
        # synchronously fill buffer. Do not call when audio thread is running
        self.baf.prime()
