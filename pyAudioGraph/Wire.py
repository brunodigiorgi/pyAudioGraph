import numpy as np
from .AudioGraph import Node


class Op:
    """
    Encapsulate a generic operation as a node of the graph.
    Each time it is called generate a new node (OpNode) and returns its w_out

    Example:
        op = Op(np.add)
        w_out3 = op(w_out1, w_out2)
    """

    def __init__(self, fn):
        """

        Parameters
        ----------
        fn : callable fn(*ndarrays) -> ndarray
            combines a certain number of ndarrays producing a ndarray for output
        """
        self.fn = fn

    def __call__(self, *w_out_tuple):
        """

        Parameters
        ----------
        w_out_tuple : variable number of arguments of type OutWire
            these will be used as input to the new Node

        Returns
        -------
        out : OutWire
            the output of the newly created Node
        """
        n_w_out = len(w_out_tuple)
        assert (n_w_out > 0)
        max_len = 0
        w = w_out_tuple[0].parent.world
        for w_out in w_out_tuple:
            assert (w_out.__class__.__name__ == "OutWire")
            assert (w == w_out.parent.world)
            max_len = max(max_len, w_out.data().shape[1])

        op_node = OpNode(w, self.fn, n_in=n_w_out, out_len=max_len)
        return op_node(*w_out_tuple)


class OpNode(Node):
    """
    Generic operation node. Private class, used by Op.
    Creates a Node with the given function and n_in inputs, output buffer is out_len long
    """

    def __init__(self, world, fn, n_in, out_len):
        super().__init__(world)
        self.fn = fn
        self.n_in = n_in
        self.w_in = [InWire(self) for _ in range(n_in)]
        self.w_out = OutWire(self, out_len)

    def calc_func(self):
        in_arrays = [w_in_.get_data() for w_in_ in self.w_in]
        self.w_out.set_data(self.fn(*in_arrays))

    def __call__(self, *out_wires_tuple):
        nout_wires = len(out_wires_tuple)
        assert (nout_wires == self.n_in)
        for ow, iw in zip(out_wires_tuple, self.w_in):
            ow.plug_into(iw)
        return self.w_out


class OutWire:
    """
    To be safe, do not modify the object returned by InWire.get_data but only a copy of it.
    """

    def __init__(self, parent, buf_len=1):
        """
        
        Parameters
        ----------
        parent : Node
            the parent Node
            
        buf_len : int
            the length of the array
            usually this is world.buf_len for audio buffer, 1 (default) for control buffer
        """
        self.parent = parent
        self._data = np.zeros((1, buf_len), dtype=np.float32)
        self._in_wires = []
        self.parent.out_wires.append(self)

    def in_wires(self): return self._in_wires

    def set_data(self, in_data):
        """
        Set the internal buffer
        
        Parameters
        ----------
        in_data : ndarray (audio buffer) or float (control buffer)
            data that will be copied to the internal buffer
        """
        self._data[:, :] = in_data

    def data(self):
        return self._data

    def plug_into(self, in_wire):
        """
        Connect to a given InWire of another Node
        
        Parameters
        ----------
        in_wire : InWire
            the InWire where this OutWire is going to be connected
        """
        if self.parent == in_wire.parent:
            raise ValueError("trying to connect a node to itself")
        self._in_wires.append(in_wire)
        in_wire.set_out_wire(self)

    def __add__(self, other):
        if other.__class__.__name__ == "OutWire":
            op = Op(np.add)
            return op(self, other)
        else:
            op = Op(lambda x: x + other)
            return op(self)

    __radd__ = __add__

    def __mul__(self, other):
        if other.__class__.__name__ == "OutWire":
            op = Op(np.multiply)
            return op(self, other)
        else:
            op = Op(lambda x: x * other)
            return op(self)

    __rmul__ = __mul__

    def __sub__(self, other):
        if other.__class__.__name__ == "OutWire":
            op = Op(np.subtract)
            return op(self, other)
        else:
            op = Op(lambda x: x - other)
            return op(self)

    def __rsub__(self, other):
        if other.__class__.__name__ == "OutWire":
            op = Op(np.subtract)
            return op(other, self)
        else:
            op = Op(lambda x: other - x)
            return op(self)

    def __truediv__(self, other):
        if other.__class__.__name__ == "OutWire":
            op = Op(np.divide)
            return op(self, other)
        else:
            op = Op(lambda x: x / other)
            return op(self)

    def __rtruediv__(self, other):
        if other.__class__.__name__ == "OutWire":
            op = Op(np.divide)
            return op(other, self)
        else:
            op = Op(lambda x: other / x)
            return op(self)

    def clip(self, a_min, a_max):
        op = Op(lambda x: np.clip(x, a_min, a_max))
        return op(self)

    def range_to_unit(self, a_min, a_max, invert=False):
        a = 1 if invert else 0
        b = -1 if invert else 1
        op = Op(lambda x: a + b * (1 / (a_max - a_min)) * (np.clip(x, a_min, a_max) - a_min))
        return op(self)


class InWire:
    """
    When overriding calc_func in a new node, do not modify the object returned by InWire.get_data but only a copy of it.
    """

    def __init__(self, parent, default_data=None):
        self.parent = parent
        self._default_data = default_data
        self._out_wire = None  # not connected
        self.parent.in_wires.append(self)

    def get_data(self):
        if self._out_wire is None:  # not connected
            return self._default_data
        out_data = self._out_wire.data()
        if all([s_ == 1 for s_ in out_data.shape]):  # control (scalar) out_data
            return np.squeeze(out_data)
        return out_data  # audio (vector) out_data

    def set_out_wire(self, out_wire):
        self._out_wire = out_wire

    def out_wire(self):
        return self._out_wire


class ObjOutWire:
    """
    Similar to OutWire, but does not manage any numeric buffer.
    Its internal _data attribute is simply a pointer to data managed elsewhere (typically in the parent Node)
    Specifically, in case of immutable objects, they are copied. For mutable they are referenced.
    Do not modify the object returned by ObjInWire.get_data but only a copy of it.
    """

    def __init__(self, parent):
        self.parent = parent
        self._data = None
        self._in_wires = []
        self.parent.out_wires.append(self)

    def in_wires(self): return self._in_wires

    def set_data(self, in_data):
        self._data = in_data

    def data(self):
        return self._data

    def plug_into(self, in_wire):
        if self.parent == in_wire.parent:
            raise ValueError("trying to connect a node to itself")
        self._in_wires.append(in_wire)
        in_wire.set_out_wire(self)


class ObjInWire:
    """
    Similar to InWire, but used for objects instead of numpy arrays
    To be safe, do not modify the object returned by ObjInWire.get_data but only a copy of it.
    """

    def __init__(self, parent, default_data=None):
        """
        Create an ObjInWire from parent Node and a default_data object.
        
        - default_data object should be mandaged by the parent Node
        - when the node is connected, get_data() returns an object managed by the parent of the connected ObjOutWire
        
        Parameters
        ----------
        parent : Node
            parent Node
        default_data : object
            the object to use if no ObjOutWire was connected        
        """
        self.parent = parent
        self._default_data = default_data
        self._out_wire = None  # not connected
        self.parent.in_wires.append(self)

    def get_data(self):
        """
        Return the default data (if connected), or the object of the connected ObjOutWire
        
        Returns
        -------
        out : object
            default object if not connected, or the object of the connected ObjOutWire
        """
        if self._out_wire is None:  # not connected
            return self._default_data
        return self._out_wire.data()

    def set_out_wire(self, out_wire):
        self._out_wire = out_wire

    def out_wire(self):
        return self._out_wire


def pass_thru(parent, out_wire):
    """
    Connect out_wire though this unit.
    out_wire.parent Node will be connected through a dummy InWire: it will become a "dependency" of parent
    Creates a dummy InWire and adds it to parent.in_wires, for graph sorting.
    The out_wire is returned, for an understandable syntax.

    Parameters
    ----------
    parent: Node
    out_wire: OutWire

    Returns
    -------
    out_wire: OutWire
        the input parameter

    """
    w_in = InWire(parent)  # In wire is dummy used only for graph sorting
    out_wire.plug_into(w_in)
    return out_wire


class InWireAdaptor(InWire):
    """
    To be used in Group, to expose an InWire from an inner Node
    """

    def __init__(self, parent, in_wire):
        super().__init__(parent)
        self.in_wire = in_wire

    def get_data(self): return self.in_wire.get_data()

    def out_wire(self): return self.in_wire.out_wire()

    def set_out_wire(self, out_wire): self.in_wire.set_out_wire(out_wire)


class OutWireAdaptor(OutWire):
    """
    To be used in Group, to expose an OutWire from an inner Node
    """

    def __init__(self, parent, out_wire):
        super().__init__(parent)
        self.out_wire = out_wire

    def in_wires(self): return self.out_wire.in_wires()

    def set_data(self, in_data): self.out_wire.set_data(in_data)

    def data(self): return self.out_wire.data()

    def plug_into(self, in_wire): self.out_wire.plug_into(in_wire)


class ObjInWireAdaptor(ObjInWire):
    """
    To be used in Group, to expose an ObjInWire from an inner Node
    """

    def __init__(self, parent, in_wire):
        super().__init__(parent)
        self.in_wire = in_wire

    def get_data(self): return self.in_wire.get_data()

    def out_wire(self): return self.in_wire.out_wire()

    def set_out_wire(self, out_wire): self.in_wire.set_out_wire(out_wire)


class ObjOutWireAdaptor(ObjOutWire):
    """
    To be used in Group, to expose an ObjOutWire from an inner Node
    """

    def __init__(self, parent, out_wire):
        super().__init__(parent)
        self.out_wire = out_wire

    def in_wires(self): return self.out_wire.in_wires()

    def set_data(self, in_data): self.out_wire.set_data(in_data)

    def data(self): return self.out_wire.data()

    def plug_into(self, in_wire): self.out_wire.plug_into(in_wire)
