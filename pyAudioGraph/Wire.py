import numpy as np


class Wire:
    """
    used to connect two nodes.
    can be used for audioRate and controlRate signals
    can be an input wire or an output wire (output wires allocate memory)

    usage:
    1) in your node create input and output wires (use a common prefix, as "w_")
    2) connect them when creating the graph:
      diskInNode.w_out.plug_into(mixerNode.w_in[0])
      sineGenNode.w_out.plug_into(mixerNode.w_in[1])

    IMPORTANT!
    syntax
    since python do not have explicit pointer syntax,
    I encapsulated the behavior in the setter methods:
    wire.set_value(3)
    wire.set_buffer(numpy_ndarray)

    NEVER set value or buffer like this:
    wire._value = 3
    wire._buf = np.ndarray
    (I chose _value and _buf to be private members for this reason)

    However, getting directly _value and _buf is ok:
    print(wire._value)
    print(wire._buf)
    """

    controlRate = 0
    audioRate = 1

    wiretype_input = 2
    wiretype_output = 2

    def __init__(self, world, rate, wiretype):
        self.wiretype = wiretype
        self.rate = rate
        assert(self.rate in [Wire.controlRate, Wire.audioRate])

        # output wires allocate memory
        if(self.wiretype == Wire.wiretype_output):
            if(self.rate == Wire.audioRate):
                self._buf = np.zeros((1, world.buf_len), dtype=np.float32)
            elif(self.rate == Wire.controlRate):
                self._value = np.array([0], dtype=np.float32)

    def set_buffer(self, in_buffer):
        """
        in_buffer: numpy ndarray 1-dim, length=world.buf_len
        """
        self._buf[0, :] = in_buffer[:]

    def set_value(self, in_value):
        """
        in_value: scalar
        """
        self._value[0] = in_value

    def plug_into(self, wire):
        assert((wire is not None) and
               ((self.wiretype == Wire.wiretype_output) and
                (wire.wiretype == Wire.wiretype_input)) and
               (self.rate == wire.rate))

        if(self.rate == Wire.audioRate):
            wire._buf = self._buf
        if(self.rate == Wire.controlRate):
            wire._value = self._value
