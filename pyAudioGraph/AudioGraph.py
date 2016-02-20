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

    def add_after(self, node):
        assert(node.parent is not None)
        node.parent.insert_after(self, node)

    def add_before(self, node):
        assert(node.parent is not None)
        node.parent.insert_before(self, node)


class Group(Node):
    def __init__(self, world):
        super().__init__(world)
        self.nodesList = []

    def add_head(self, node):
        node.parent = self
        self.nodesList.insert(0, node)

    def add_tail(self, node):
        node.parent = self
        self.nodesList.append(node)

    def insert_after(self, node1, node2):
        """ insert node1 after node2 """
        assert(node2.parent == self)
        i = self.nodesList.index(node2)
        node1.parent = self
        self.nodesList.insert(i + 1, node1)

    def insert_before(self, node1, node2):
        """ insert node1 before node2 """
        assert(node2.parent == self)
        i = self.nodesList.index(node2)
        node1.parent = self
        self.nodesList.insert(i, node1)

    def calc_func(self):
        for n in self.nodesList:
            n.calc_func()

    def clear(self):
        self.nodesList = []

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
                for c in ow.connections:
                    assert(c.parent in nl)
                    i2 = nl.index(c.parent)
                    connections[i1, i2] = 1

        sorted_list = self._topological_sort(connections)
        self.nodesList = [self.nodesList[i] for i in sorted_list]
