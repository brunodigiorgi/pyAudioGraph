class RingList:
    """
    A circular container using python list.

    >>> r = RingList(3)
    >>> r.push(1)
    >>> r.push(2)
    >>> print(r)
    [1, 2, None]

    >>> r.push(3)
    >>> r.push(4)
    >>> print(r)
    [4, 2, 3]

    >>> r.front()  # oldest element in list
    2

    >>> r.back()  # newest element in list
    4

    >>> r.clear()
    >>> print(r)
    [None, None, None]
    """

    def __init__(self, size):
        self.size = size
        self.l = []
        for i in range(size):
            self.l.append(None)
        self.curr = 0
        self.nElem = 0

    def clear(self):
        for i in range(self.size):
            self.l[i] = None
        self.curr = 0
        self.nElem = 0

    def push(self, in_elem):
        self.l[self.curr] = in_elem
        self.curr = (self.curr + 1) % self.size
        self.nElem = min(self.nElem + 1, self.size)

    def front(self):
        i_first = (self.curr - self.nElem) % self.size
        return self.l[i_first]

    def back(self):
        i_last = (self.curr - 1) % self.size
        return self.l[i_last]

    def __str__(self):
        return str(self.l)

    def __getitem__(self, k):
        # oldest for k=0, newest is for k=size-1
        # [None, None, oldest, ..., newest]
        i = (self.curr + k) % self.size
        return self.l[i]
