"""NPArrayFlexible class."""
import numpy as np


class NPArrayFlexible:
    """
    An etherogeneous numpy array, can have different number of elements for each row.

    >>> n = NPArrayFlexible(n_rows=2, capacity=4)
    >>> n.new_row()
    >>> n.append(1)
    >>> n.append(2)
    >>> n[0,1]
    2

    >>> n.new_row()
    >>> n.append(3)
    >>> n.append(4)
    >>> n[1]
    [3, 4]

    >>> n.append_row(np.array([5, 6]))
    >>> n[-1]
    [5, 6]

    >>> n.n_rows()
    3


    """

    def __init__(self, n_rows=5, capacity=2048, dtype=np.int):
        """
        Create a NPArrayFlexible.

        Parameters
        ----------
        n_rows : int
            an estimate of the number of rows
        nElem : int
            an estimate of the total number of elements
        dtype : dtype
            the type of the elements
        """
        self.dtype = dtype
        self._elem_capacity = capacity
        self.x = np.zeros(capacity, dtype=dtype)
        self.xn = 0

        self._rows_capacity = n_rows
        self.xr = np.zeros(n_rows, dtype=np.int)
        self.xr_count = np.zeros(n_rows, dtype=np.int)
        self.xrn = 0

    def clear(self):
        self.xn = 0
        self.xrn = 0
        self.xr_count[:] = 0

    def new_row(self):
        if(self.xrn > self._rows_capacity - 1):
            self._extend_rows()
        self.xr[self.xrn] = self.xn
        self.xrn += 1

    def append(self, elem):
        if(self.xn > self._elem_capacity - 1):
            self._extend()
        self.x[self.xn] = elem
        self.xn += 1
        self.xr_count[self.xrn - 1] += 1

    def append_row(self, row):
        self.new_row()
        for elem in row:
            self.append(elem)

    def _extend(self):
        new_capacity = self._elem_capacity * 2
        self.x.resize(new_capacity)
        self._elem_capacity = new_capacity

    def _extend_rows(self):
        new_capacity = self._rows_capacity * 2
        self.xr.resize(new_capacity)
        self.xr_count.resize(new_capacity)
        self._rows_capacity = new_capacity

    def n_rows(self):
        return self.xrn

    def n_elems(self):
        return self.xn

    def back(self):
        return self[self.xrn - 1]

    def __len__(self):
        """Number of rows."""
        return self.xrn

    def _index_from_tuple(self, pos):
        r, c = pos
        i = self.xr[r] + c
        if(r >= self.xrn):
            raise IndexError("index %d is out of bounds for axis 0 with size %d" % (r, self.xrn))
        elif(c >= self.xr_count[r]):
            raise IndexError("index %d is out of bounds for row %d with size %d" % (c, r, self.xr_count[r]))
        return i

    def __setitem__(self, pos, value):
        """Assign [value] to the item in [pos]."""
        assert(isinstance(pos, tuple))
        i = self._index_from_tuple(pos)
        self.x[i] = value

    def __getitem__(self, pos):
        """Default container access."""
        if(isinstance(pos, int)):
            if(pos >= 0):
                r = pos
            else:
                r = self.xrn + pos
                if(r < 0):
                    raise IndexError("Index out of range")
            if(r >= self.xrn):
                raise IndexError("index %d is out of bounds for axis 0 with size %d" % (r, self.xrn))
            i = self.xr[r]
            c = self.xr_count[r]
            out = self.x[i:i + c]
            return out
        elif(isinstance(pos, tuple)):
            i = self._index_from_tuple(pos)
            return self.x[i]
