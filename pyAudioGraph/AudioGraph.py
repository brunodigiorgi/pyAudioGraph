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

    def add_parents(self):
        """
        This function traverses the graph with depth first search
        Add all the nodes that are required by the nodes in self.nodesList
        Updates self.nodesList at the end with all the nodes in the graph
        """
        nl = self.nodesList
        visited, stack = set(), nl

        while(stack):
            inode = stack.pop()
            if(inode not in visited):
                # print("visiting " + str(inode.__class__.__name__))
                visited.add(inode)
                for iw in inode.in_wires:
                    ow = iw.out_wire
                    if(ow is not None and
                       (ow.parent not in stack) and
                       (ow.parent not in visited)):
                        # print("adding " + str(ow.parent.__class__.__name__))
                        stack.append(ow.parent)
        self.nodesList = list(visited)

    def sort(self):
        self.add_parents()  # add all the parents of the added nodes

        nl = self.nodesList
        nnodes = len(nl)
        connections = np.zeros((nnodes, nnodes), dtype=int)
        for i1 in range(nnodes):
            for ow in nl[i1].out_wires:
                for iw in ow.in_wires:
                    if(iw.parent not in nl):
                        raise ValueError(str(iw.parent.__class__.__name__) +
                                         " is not in the graph, although connected to " +
                                         str(ow.parent.__class__.__name__))
                    i2 = nl.index(iw.parent)
                    connections[i1, i2] = 1

        sorted_list = self._topological_sort(connections)
        self.nodesList = [self.nodesList[i] for i in sorted_list]

        self.is_sorted = True
