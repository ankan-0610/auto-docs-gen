class ASTNode: 
    def __init__(self, node_type, value=None, children=None):
        self.node_type = node_type
        self.value = value
        self.children = children or []
        self.parent = None

        for child in self.children:
            child.parent = self

class ASTGraph:
    def __init__(self, root=None):
        self.root = root
        self.current_node = root

    def add_node(self, node, parent=None):
        if not parent:
            parent = self.current_node

        parent.children.append(node)
        node.parent = parent
        return node
    
    def traverse(self, node=None, depth=0):
        if node is None:
            node = self.root
        yield node, depth 
        for child in node.children:
            yield from self.traverse(child, depth + 1)
    
    def find_nodes(self, predicate):
        return [node for node, _ in self.traverse() if predicate(node)]
    
    def to_text(self, node=None, indent=0):
        if node is None:
            node = self.root
        result = " " * indent + f"{node.node_type}"
        if node.value is not None:
            result += f": {node.value}"
        result += "\n"
        for child in node.children:
            result += self.to_text(child, indent + 1)
        return result