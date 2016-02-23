import numpy as np


class Node:
    def __init__(self, world):
        self.world = world
        self.enabled = True
        self.parent = None

        self.in_wires = []
        self.out_wires = []

    def calc_func(self):
        pass


class Group(Node):
    def __init__(self, world):
        super().__init__(world)
        self.nodesList = []
        self.is_sorted = True

    def append(self, node):
        if(node in self.nodesList):
            print("Trying to append a node that is already in the group, doing nothing")
            return

        self.nodesList.append(node)
        self.is_sorted = False

    def calc_func(self):
        for n in self.nodesList:
            n.calc_func()

    def clear(self):
        self.nodesList = []
        self.is_sorted = True

    def _topological_sort_util(self, v, connections, visited, stack):
        visited[v] = True

        adj = np.where(connections[v] == 1)[0]
        for i in adj:
            if(not visited[i]):
                self._topological_sort_util(i, connections, visited, stack)

        stack.append(v)

    def _topological_sort(self, connections):
        stack = []

        assert(connections.ndim == 2 and connections.shape[0] == connections.shape[1])
        nnodes = connections.shape[0]
        visited = [False for i in range(nnodes)]

        for v in range(nnodes):
            if(not visited[v]):
                self._topological_sort_util(v, connections, visited, stack)

        stack.reverse()
        return stack

    def sort(self):
        nl = self.nodesList
        nnodes = len(nl)
        connections = np.zeros((nnodes, nnodes), dtype=int)
        for i1 in range(nnodes):
            for ow in nl[i1].out_wires:
                for iw in ow.in_wires:
                    assert(iw.parent in nl)
                    i2 = nl.index(iw.parent)
                    connections[i1, i2] = 1

        sorted_list = self._topological_sort(connections)
        self.nodesList = [self.nodesList[i] for i in sorted_list]

        self.is_sorted = True
