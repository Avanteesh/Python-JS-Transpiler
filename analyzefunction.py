from ast import NodeVisitor, FunctionDef, Yield

class AnalyzeFunctionDef(NodeVisitor):
    def __init__(self):
        self.is_generator = False

    def visit(self, node: FunctionDef):
        if isinstance(node, Yield):
            self.is_generator = True
            return
        self.generic_visit(node)

