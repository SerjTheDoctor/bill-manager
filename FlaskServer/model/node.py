from enum import Enum

class NodeType(Enum):
    DOCUMENT = 0
    LINE = 1
    WORD = 2

class Node:
    def __init__(self, node_type: NodeType, text: str, box_start, box_end, parent=None):
        self.node_type = node_type
        self.text = text
        self.box_start = box_start
        self.box_end = box_end
        self.children = []
        self.parent = parent

    def __str__(self):
        return '{} ({})'.format(self.text, self.node_type.name)

    @property
    def height(self):
        return self.bottom - self.top

    @property
    def width(self):
        return self.right - self.left

    @property
    def left(self):
        return self.box_start[0]

    @property
    def top(self):
        return self.box_start[1]

    @property
    def right(self):
        return self.box_end[0]

    @property
    def bottom(self):
        return self.box_end[1]

    def add_children(self, node):
        self.children.append(node)

        if self.text is None or self.text is '':
            self.text = str(node.text).upper()
        else:
            self.text += ' ' + str(node.text).upper()

        if self.box_start is None:
            self.box_start = (node.left, node.top)
        else:
            self.box_start = (min(self.left, node.left), min(self.top, node.top))

        if self.box_end is None:
            self.box_end = (node.right, node.bottom)
        else:
            self.box_end = (max(self.right, node.right), max(self.bottom, node.bottom))
