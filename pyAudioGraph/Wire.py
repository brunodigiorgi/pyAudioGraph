import numpy as np


class OutWire:

    def __init__(self, parent, buf_len=1):
        self.parent = parent
        self._data = np.zeros((1, buf_len), dtype=np.float32)
        self.in_wires = []

    def set_data(self, in_data):
        self._data[:, :] = in_data

    def plug_into(self, in_wire):
        if self.parent == in_wire.parent:
            raise ValueError("trying to connect a node to itself")
        self.in_wires.append(in_wire)
        in_wire.out_wire = self


class InWire:

    def __init__(self, parent, default_data=None):
        self.parent = parent
        self._default_data = default_data
        self.out_wire = None  # not connected

    def get_data(self):
        if self.out_wire is None:  # not connected
            return self._default_data
        out_data = self.out_wire._data
        if all([s_ == 1 for s_ in out_data.shape]):  # control (scalar) out_data
            return np.squeeze(out_data)
        return out_data  # audio (vector) out_data


class ObjOutWire:

    def __init__(self, parent, buf_len=1):
        self.parent = parent
        self._data = None
        self.in_wires = []

    def set_data(self, in_data):
        self._data = in_data

    def plug_into(self, in_wire):
        if(self.parent == in_wire.parent):
            raise ValueError("trying to connect a node to itself")
        self.in_wires.append(in_wire)
        in_wire.out_wire = self


class ObjInWire:

    def __init__(self, parent, default_data=None):
        self.parent = parent
        self._default_data = default_data
        self.out_wire = None  # not connected

    def get_data(self):
        if self.out_wire is None:  # not connected
            return self._default_data
        return self.out_wire._data
