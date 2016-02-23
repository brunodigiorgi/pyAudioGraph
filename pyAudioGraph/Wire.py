import numpy as np


class OutWire:
    def __init__(self, parent):
        self.parent = parent
        self._data = None
        self.in_wires = []

    def set_data(self, data):
        self._data = data

    def plug_into(self, in_wire):
        if(self.parent == in_wire.parent):
            raise ValueError("trying to connect a node to itself")
        self.in_wires.append(in_wire)
        in_wire.out_wire = self


class InWire:
    def __init__(self, parent, default_data=None):
        self.parent = parent
        self._default_data = default_data
        self.out_wire = None  # not connected

    def get_data(self):
        if(self.out_wire is None):  # not connected
            return self._default_data
        return self.out_wire._data


class AudioOutWire(OutWire):
    def __init__(self, parent, buf_len):
        super().__init__(parent)
        self.buf = np.zeros((1, buf_len), dtype=np.float32)
        self._data = self.buf

    def set_buffer(self, in_buffer):
        self.buf[0, :] = in_buffer[:]
