from ..AudioBuffer import RingBuffer
from ..AudioGraph import Node
from .. import InWire, OutWire
import numpy as np


class SamplerNode(Node):
    """

    Wires
    -----
    out_wires:
        w_out : OutWire
    in_wires:
        w_trigger_list : trigger_list = [(t_id, t_pos, t_scale), ...]
            t_id is the buffer id (int)
            t_pos is the sample offset (int)
            t_scale is a level coeff for accumulation (float)

    """
    def __init__(self, world, nchannels):
        super().__init__(world)

        self.nchannels = nout = nchannels
        self.buffers = []
        self.ringBuffer = RingBuffer(self.nchannels, world.buf_len)
        self.w_out = [OutWire(self, world.buf_len) for o in range(nout)]
        self.w_trigger_list = InWire(self)

        # add w_in_trigger (substitutes the method set_trigger)
        self.out_wires.extend(self.w_out)

        self.temp_out = np.zeros((nout, world.buf_len), dtype=np.float32)
        self.trigger_list = []

    def add_buffer(self, buf):
        assert(buf.shape[0] == self.nchannels)
        self.buffers.append(buf)
        new_len = buf.shape[1] + self.world.buf_len
        if(self.ringBuffer.length() < new_len):
            self.ringBuffer.resize(new_len)
        return len(self.buffers)

    def reset(self):
        self.ringBuffer.clear()

    def calc_func(self):

        nb = len(self.buffers)
        no = self.nchannels

        # pre-conditions
        if(nb == 0):
            for o in range(no):
                self.w_out[o].set_data(0)
            return

        trigger_list = self.w_trigger_list.get_data()
        for t_id, t_pos, t_sc in trigger_list:
            if(t_id < nb):
                self.ringBuffer.accumulate(self.buffers[t_id], offset=t_pos, in_scale=t_sc)

        self.ringBuffer.advance_write_index(self.world.buf_len)
        self.ringBuffer.read(self.temp_out)
        self.ringBuffer.advance_read_index(self.world.buf_len)

        for o in range(no):
            self.w_out[o].set_data(self.temp_out[o, :])
