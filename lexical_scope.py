class LexicalScope:
    """
    a linked list like data structure which will store information about the Variables
    declared in current scope!
    """
    def __init__(self):
        self.global_variables = {}   # variables declared in the scope!
        self.parent_ref = None   # reference to parent node (lexical environment!)
    
    def find(self, var_name: str):
        return var_name in self.global_variables

    def set(self, var_name: str):
        self.global_variables[var_name] = True

def searchVariableDeclaration(target_var: str, node: LexicalScope) -> bool:
    """
    search for variable from current scope to outermost scope!
    """
    temp = node
    while temp != None:
        if temp.find(target_var):
            return True
        temp = temp.parent_ref  # traverse to the parent node!
    return False

