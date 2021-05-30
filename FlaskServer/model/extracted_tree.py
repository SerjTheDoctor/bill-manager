from model.node import NodeType, Node
from typing import List

class ExtractedTree:
    def __init__(self):
        self.root = Node(NodeType.DOCUMENT, '', None, None, None)

    def __str__(self):
        return 'Tree {}'.format(self.root)

    def add_node(self, node: Node):
        for line in self.root.children:
            middle = int(line.top + line.height/2)

            if node.top <= middle <= node.bottom:
                node.parent = line
                line.add_children(node)
                return

        new_line = Node(NodeType.LINE, '', None, None, self.root)
        node.parent = new_line
        new_line.add_children(node)
        self.root.add_children(new_line)

    def get_lines(self) -> List[Node]:
        return self.root.children

    def get_words(self) -> List[Node]:
        return [word for line in self.root.children for word in line.children]
