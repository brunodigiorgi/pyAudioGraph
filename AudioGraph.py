class Node:
    def __init__(self, world):
        self.world = world
        self.enabled = True
        self.parent = None

    def calcFunc(self):
        pass

    def addAfter(self, node):
        assert(node.parent is not None)
        node.parent.insertAfter(self, node)

    def addBefore(self, node):
        assert(node.parent is not None)
        node.parent.insertBefore(self, node)


class Group(Node):
    def __init__(self, world):
        super().__init__(world)
        self.nodesList = []

    def addHead(self, node):
        node.parent = self
        self.nodesList.insert(0, node)

    def addTail(self, node):
        node.parent = self
        self.nodesList.append(node)

    def insertAfter(self, node1, node2):
        """ insert node1 after node2 """
        assert(node2.parent == self)
        i = self.nodesList.index(node2)
        node1.parent = self
        self.nodesList.insert(i + 1, node1)

    def insertBefore(self, node1, node2):
        """ insert node1 before node2 """
        assert(node2.parent == self)
        i = self.nodesList.index(node2)
        node1.parent = self
        self.nodesList.insert(i, node1)

    def calcFunc(self):
        for n in self.nodesList:
            n.calcFunc()

    def clear(self):
        self.nodesList = []
