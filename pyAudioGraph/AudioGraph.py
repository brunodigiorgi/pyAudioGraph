class Node:
    def __init__(self, world):
        self.world = world
        self.enabled = True
        self.parent = None

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
