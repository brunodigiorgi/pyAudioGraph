from collections import deque


class Range:
    def __init__(self, range_min, range_max):
        assert(range_max >= range_min)
        self.min = range_min
        self.max = range_max
        self.length = range_max - range_min


class RangeQueue:
    def __init__(self):
        self.queue = deque()
        self.length = 0

    def push(self, r):
        """
        r is a Range
        """
        self.queue.append(r)
        self.length += r.length        

    def pushRangeQueue(self, rangeQueue):
        for r in rangeQueue.queue:
            self.push(r)

    def front(self):
        return self.queue[-1].max

    def back(self):
        return self.queue[0].min

    def clear(self):
        self.queue.clear()
        self.length = 0

    def __str__(self):
        out = ""
        for i in range(len(self.queue)):
            out += str(self.queue[i].min) + ' ' + str(self.queue[i].max)
            out += '\n'
        out[:-1]
        return out