import ast
import colorama as col
from lexical_scope import LexicalScope, searchVariableDeclaration

class PythonToJavascript:
    def __init__(self):
        self.target_lang = str()
        self.global_lexicalenv = LexicalScope()   # global lexical environment!

    def ast_analyze(self, node: ast.AST):
        if isinstance(node, ast.FunctionDef):
            self.target_lang += self.transpile_function(node)
        elif isinstance(node, ast.Expr):
            self.target_lang += self.transpile_expression(node)
        elif isinstance(node, ast.Import):
            self.target_lang += self.transpile_import(node)
        elif isinstance(node, ast.ImportFrom):
            self.target_lang += self.transpile_fromImport(node)
        elif isinstance(node, ast.Assign):
            self.target_lang += self.transpile_assign(node)
        elif isinstance(node, ast.For):
            self.target_lang += self.transpile_for(node)
        elif isinstance(node, ast.ClassDef):
            self.target_lang += self.transpile_classDef(node)
        elif isinstance(node, ast.AugAssign):
            self.target_lang += self.transpile_AugAssign(node)
        elif isinstance(node, ast.AsyncFunctionDef):
            self.target_lang += self.transpile_function(node)
        elif isinstance(node, ast.If):
            self.target_lang += self.transpile_IfExp(node)
        elif isinstance(node, ast.While):
            self.target_lang += self.transpile_While(node)
        elif isinstance(node, ast.IfExp):
            self.target_lang += self.transpile_TernaryExp(node)

    def visit(self, node: ast.Module):
        for nodes in node.body:
            self.ast_analyze(nodes)

    def transpile_function(self, node: ast.FunctionDef, scope_level: int=1,isinclass=False):
        if node.name[0].isupper():
            raise TypeError(f"{col.Fore.RED}Error:{col.Fore.WHITE} function names must start in lower case!")
        arg_list = [item.arg for item in node.args.args if item.arg != "self"]
        GAP = "" if scope_level == 1 else " " * scope_level
        function_name = node.name
        if len(node.name) >= 2 and isinclass == True:
            if node.name[0] == "_" and node.name[1] == "_":
                function_name = f"#{node.name[2:]}"
        if isinstance(node, ast.AsyncFunctionDef):
            if isinclass == True:
                function_code = f"\n{GAP}async {function_name}({",".join(arg_list)})"
            else:
                function_code = f"\n{GAP}async function {function_name}({",".join(arg_list)})  {'{'}\n"
        else:
            if isinclass == True:
                if len(node.args.args) == 0 or node.args.args[0].arg != "self" and (node.decorator_list[0].id == "staticmethod" or node.decorator_list[0].id == "classmethod"):
                    function_code = f"\n{GAP}static {function_name}({",".join(arg_list)}) {'{'}\n"
                else:
                    function_code = f"\n{GAP}{function_name}({",".join(arg_list)}) {'{'}\n"
            else:
                function_code = f"\n{GAP}function {node.name}({",".join(arg_list)})  {'{'}\n"
        for content in node.body:
            if isinstance(content, ast.FunctionDef):
                function_code += self.transpile_function(content, scope_level + 1)
            elif isinstance(content, ast.AsyncFunctionDef):
                function_code += self.transpile_function(content, scope_level + 1)
            elif isinstance(content, ast.Assign):
                function_code += f" {GAP}{self.transpile_assign(content)}" 
            elif isinstance(content, ast.Return):
                function_code += f" {GAP} {self.transpile_Return(content)}"
            elif isinstance(content, ast.If):
                function_code += self.transpile_IfExp(content, scope_level + 1)
            elif isinstance(content, ast.For):
                function_code += self.transpile_for(content, scope_level + 1)
            elif isinstance(content, ast.Expr):
                function_code += f"{GAP} {self.transpile_expression(content)}"
            elif isinstance(content, ast.Match):
                function_code += f"{GAP} {self.transpile_Match(content)}"
        function_code += f"{GAP}{'}'}\n"
        return function_code

    def getBinaryOperator(self, node: ast.AST):
        if isinstance(node.op, ast.Add): 
            return "+"
        elif isinstance(node.op, ast.Sub): 
            return "-"
        elif isinstance(node.op, ast.Mult): 
            return "*"
        elif isinstance(node.op, ast.FloorDiv) or isinstance(node.op, ast.Div): 
            return "/"
        elif isinstance(node.op, ast.Pow): 
            return "**"
        elif isinstance(node.op, ast.BitAnd):
            return "&"
        elif isinstance(node.op, ast.BitXor):
            return "^"
        elif isinstance(node.op, ast.BitOr):
            return "|"
        elif isinstance(node.op, ast.Mod):
            return "%"
        elif isinstance(node.op, ast.LShift):
            return "<<"
        elif isinstance(node.op, ast.RShift):
            return ">>"
        elif isinstance(node.op, ast.Or):
            return "||"
        elif isinstance(node.op, ast.And):
            return "&&"

    def transpile_AugAssign(self, node: ast.AugAssign):
        target, value = self.transpile_expression(node.target), self.transpile_expression(node.value)
        _operator = self.getBinaryOperator(node)
        return f"{target} {_operator}= {value};\n"

    def transpile_lambda(self, node: ast.Lambda):
        arguments = ",".join([item.arg for item in node.args.args])
        return f"({arguments}) => {self.transpile_expression(node.body)}"
    
    def transpile_classDef(self, node: ast.ClassDef, scope_level: int=1, isinnerClass=False):
        if node.name[0].islower():
            raise TypeError(f"{col.Fore.RED}ERROR:{col.Fore.WHITE} class Names must be upper case!")
        gap = "" if scope_level == 1 else " " * scope_level
        if len(node.bases) != 0:
            class_def = f"{gap}class {node.name} extends {node.bases[0].id} {'{'}\n" if not isinnerClass else f"{gap}static {node.name} = class {'{'}\n"
        else:
            class_def = f"{gap}class {node.name if not isinnerClass else ""} {'{'}\n" if not isinnerClass else f"{gap}static {node.name} = class {'{'}\n"
        for child_nodes in node.body:
            if isinstance(child_nodes, ast.Assign):
                class_def += f"{gap} static {child_nodes.targets[0].id} = {self.transpile_expression(child_nodes.value)};\n"
            elif isinstance(child_nodes, ast.FunctionDef):
                if child_nodes.name == "__init__":  # declare construtor!
                    arguments = ", ".join([item.arg for item in child_nodes.args.args])
                    class_def += f"{gap} constructor({arguments}) {'{'}\n"
                    for code in child_nodes.body:
                        if isinstance(code, ast.Assign):
                            class_def += f"{gap}  {self.transpile_assign(code)}"
                    class_def += f"{gap} {'}'}\n"
                else:
                    class_def += f"{gap}{self.transpile_function(child_nodes,scope_level+1,True)}"
            elif isinstance(child_nodes, ast.ClassDef):
                class_def += self.transpile_classDef(child_nodes, scope_level + 1, True)
        class_def += f"{gap}{'}'}\n\n"
        return class_def

    def transpile_While(self, node: ast.While, scope_level:int=1, parent_scope=None):
        lexical_scope = LexicalScope()
        lexical_scope.parent_ref = self.global_lexicalenv if parent_scope == None else parent_scope
        GAP = "" if scope_level == 1 else " "* scope_level
        statement = f"{GAP}while ({self.transpile_expression(node.test)}) {'{'}\n"
        for code in node.body:
            if isinstance(code, ast.Expr):
                statement += f"{GAP}{self.transpile_expression(code)}"
            elif isinstance(code, ast.Assign):
                statement += f"{GAP}{self.transpile_assign(code, lexical_scope)}"
            elif isinstance(code, ast.While):
                statement += self.transpile_While(code, scope_level + 1, lexical_scope)
            elif isinstance(code, ast.If):
                statement += self.transpile_IfExp(code, scope_level + 1, parent_scope=lexical_scope)
            elif isinstance(code, ast.For):
                statement += self.transpile_for(code, scope_level+1, lexical_scope)
        statement += f"{GAP}{'}'}\n"
        return statement

    def transpile_for(self, node: ast.For, scope_level: int=1, parent_scope=None):
        lexical_scope = LexicalScope()
        lexical_scope.parent_ref = self.global_lexicalenv if parent_scope == None else parent_scope
        GAP = "" if scope_level == 1 else " " * scope_level
        statement = ""
        if isinstance(node.iter, ast.Call):
            if len(node.iter.args) == 1:
                first = self.transpile_expression(node.iter.args[0]).replace("\n", "").replace(";", "")
                statement = f"{GAP}for (let {node.target.id} = 0; {node.target.id} < {first}; {node.target.id}++) {'{'}\n"
            elif len(node.iter.args) == 2:
                first, second = self.transpile_expression(node.iter.args[0]), self.transpile_expression(node.iter.args[1])
                statement = f"{GAP}for (let {node.target.id} = {first}; {node.target.id} < {second}; {node.target.id}++) {'{'}\n"
            elif len(node.iter.args) == 3:
                first, second = self.transpile_expression(node.iter.args[0]), self.transpile_expression(node.iter.args[1])
                third = self.transpile_expression(node.iter.args[2])
                statement = f"{GAP}for (let {node.target.id} = {first}; {node.target.id} > {second}; {node.target.id} += {third})  {'{'}\n"
        elif isinstance(node.iter, ast.List) == True or isinstance(node.iter, ast.Tuple) == True:
            iterable = self.transpile_expression(iterable)
            arg_list = node.target.id
            statement += f"{GAP}for (let {arg_list} of {iterable}) {'{'}\n"
        for content in node.body:
            if isinstance(content, ast.For):
                statement += self.transpile_for(content, scope_level + 1, lexical_scope)
            elif isinstance(content, ast.If):
                statement += self.transpile_IfExp(content, scope_level + 1, lexical_scope)
            elif isinstance(content, ast.Expr):
                statement += f"{GAP} {self.transpile_expression(content.value)}"
            elif isinstance(content, ast.Assign):
                statement += f"{GAP} {self.transpile_assign(content, lexical_scope)}"
        statement += f"{GAP}{'}'}\n"
        return statement
    
    def transpile_Compare(self, node: ast.Compare):
        _left, _right = self.transpile_expression(node.left), self.transpile_expression(node.comparators[0])
        if isinstance(node.ops[0], ast.Eq):
            return f"{_left} === {_right}"
        elif isinstance(node.ops[0], ast.NotEq):
            return f"{_left} !== {_right}"
        elif isinstance(node.ops[0], ast.Is):
            return f"{_left} == {_right}"
        elif isinstance(node.ops[0], ast.IsNot):
            return f"{_left} != {_right}"
        elif isinstance(node.ops[0], ast.Gt):
            return f"{_left} > {_right}"
        elif isinstance(node.ops[0], ast.Lt):
            return f"{_left} < {_right}"
        elif isinstance(node.ops[0], ast.LtE):
            return f"{_left} <= {_right}"
        elif isinstance(node.ops[0], ast.GtE):
            return f"{_left} >= {_right}"

    def transpile_Subscript(self, node: ast.Subscript):
        if isinstance(node.slice, ast.Slice):
            _low, up = self.transpile_expression(node.slice.lower), self.transpile_expression(node.slice.upper)
            return f"{self.transpile_expression(node.value)}.slice({_low}, {_up})"
        return f"{self.transpile_expression(node.value)}[{self.transpile_expression(node.slice)}]"

    def transpile_JoinedStr(self, node: ast.JoinedStr):
        template_literal = "`"
        for args in node.values:
            if isinstance(args, ast.Constant):
                template_literal += args.value
            elif isinstance(args, ast.FormattedValue):
                template_literal += f"${'{'}{self.transpile_expression(args.value)}{'}'}"
        template_literal += "`"
        return template_literal

    def transpile_expression(self, node: ast.Expr):
        if isinstance(node, ast.BinOp):
            return self.handleBinOp(node)
        elif isinstance(node, ast.Call):
            return self.transpile_functionCall(node)
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Expr):
            return self.transpile_expression(node.value)
        elif isinstance(node, ast.Lambda):
            return self.transpile_lambda(node)
        elif isinstance(node, ast.BoolOp):
            return self.transpile_BooleanExp(node)
        elif isinstance(node, ast.Compare):
            return self.transpile_Compare(node)
        elif isinstance(node, ast.Subscript):
            return self.transpile_Subscript(node)
        elif isinstance(node, ast.JoinedStr):
            return self.transpile_JoinedStr(node)
        elif isinstance(node, ast.Await):
            return f"await {self.transpile_expression(node.value)}"
        elif isinstance(node, ast.IfExp):
            return self.transpile_TernaryExp(node)
        elif isinstance(node, ast.Attribute):
            top = self.transpile_expression(node.value)
            if top == 'self':
                return f"this.{node.attr}" 
            return f"{top}.{node.attr}"
        elif isinstance(node, ast.Constant):
            match node.value:
                case True:  return "true"
                case False: return "false"
                case None: return "null"
                case _:
                    if isinstance(node.value, str):
                        return f"\"{node.value}\""
                    return f"{node.value}"
        elif isinstance(node, ast.List) == True or isinstance(node, ast.Tuple) == True:
            lis_string = ", ".join([self.transpile_expression(item) for item in node.elts])
            return f"[{lis_string}]"
        elif isinstance(node, ast.Dict) == True:
            _dict = {f"{i.value}":self.transpile_expression(k) for i in node.keys for k in node.values}
            return f"{_dict}"
        elif isinstance(node, ast.UnaryOp):
            return self.handleUnaryExp(node)

    def transpile_Return(self, node: ast.Return):
        return f"return {self.transpile_expression(node.value)};\n"

    def transpile_TernaryExp(self, node: ast.IfExp):
        _compare_exp = self.transpile_expression(node.test)
        _else_cond = self.transpile_expression(node.orelse)
        return f"({_compare_exp})? {self.transpile_expression(node.body)}: {_else_cond}"

    def transpile_IfExp(self, node: ast.If,scope_level: int=1,iselif=False, parent_scope=None):
        lexical_scope = LexicalScope()
        lexical_scope.parent_ref = self.global_lexicalenv if parent_scope == None else parent_scope
        GAP = "" if scope_level == 1 else " "* scope_level
        result, exp = f"{GAP}", "else if" if iselif else "if"
        if isinstance(node.test, ast.BoolOp):
            result += f"{exp} ({self.transpile_BooleanExp(node.test)}) {'{'}\n"
        else:
            result += f"{exp} ({self.transpile_expression(node.test)}) {'{'}\n" 
        for expression in node.body:
            if isinstance(expression, ast.Expr):
                expression = expression.value
            if isinstance(expression, ast.If):
                result += self.transpile_IfExp(expression, scope_level + 1, False, lexical_scope)
            elif isinstance(expression, ast.Return):
                result += f"{GAP} {self.transpile_Return(expression)}"
            elif isinstance(expression, ast.Call):
                result += f"{GAP} {self.transpile_functionCall(expression)}"
            elif isinstance(expression, ast.For):
                result += f"{GAP} {self.transpile_for(expression, scope_level + 1, lexical_scope)}"
            elif isinstance(expression, ast.Break):
                result += f"{GAP} break;\n"
            elif isinstance(expression, ast.Continue):
                result += f"{GAP} continue;\n"
            elif isinstance(expression, ast.Import):
                result += f"{GAP} {self.transpile_import(expression)}"
            elif isinstance(expression, ast.Assign):
                result += f"{GAP} {self.transpile_assign(expression, lexical_scope)}"
        result += f"{GAP}{'}'}\n"
        if node.orelse == []:
            return result
        for code in node.orelse:
            if isinstance(code, ast.If):
                result += self.transpile_IfExp(code, scope_level, True, lexical_scope)
            else:
                result += f"{GAP}else {'{'}\n"
                if isinstance(code, ast.Expr):
                    result += f"{GAP} {self.transpile_expression(code)}"
                elif isinstance(code, ast.For):
                    result += f"{GAP}{self.transpile_for(code, scope_level, lexical_scope)}"
                elif isinstance(code, ast.Break):
                    result += f"{GAP}break;"
                elif isinstance(code, ast.Continue):
                    result += f"{GAP}continue;"
                elif isinstance(code, ast.Match):
                    result += f"{GAP}{self.transpile_match(code)}"
                elif isinstance(code, ast.Return):
                    result += f"{GAP} {self.transpile_Return(code)}"
                elif isinstance(code, ast.Assign):
                    result += f"{GAP} {self.transpile_assign(code, lexical_scope)}"
                result += f"{GAP}{'}'}\n"
        return result

    def transpile_Match(self, node: ast.Match, scope_level: int=1, parent_scope=None):
        _expression = self.transpile_expression(node.subject)
        lexical_scope = LexicalScope()
        lexical_scope.parent_ref = self.global_lexicalenv if parent_scope == None else parent_scope
        gap = "" if scope_level == 1 else " "*scope_level
        statement = f"{gap}switch ({expression}) {'{'}\n"
        for cases in node.cases:
            if isinstance(cases.pattern, ast.MatchValue):
                case_exp = self.transpile_expression(cases.pattern.value)
                statement += f"{gap}  case {case_exp}:\n"
            elif isinstance(cases.pattern, ast.MatchAs):
                statement += f"{gap}  default:\n"
            for _code in cases.body:
                if isinstance(_code, ast.Match):
                    statement += _self.transpile_Match(_code, scope_level + 1, lexical_scope)
                if isinstance(_code, ast.If):
                    statement += self.IfExp(_code, scope_level + 1, lexical_scope)
                if isinstance(_code, ast.For):
                    statement += self.transpile_For(_code, scope_level + 1, lexical_scope)
                if isinstance(_code, ast.Return):
                    statement += f"{gap}{self.transpile_Return(_code)}"
                if isinstance(_code, ast.Assign):
                    statement += f"{gap}{self.transpile_assign(_code)}"
            if isinstance(cases, ast.MatchValue):
                statement += f"{gap} break;\n"
            statement += f"{gap}{'}'}\n"
        statement += f"{gap}{'}'}\n"
        return statement

    def transpile_import(self, node: ast.Import):
        import_statement = ""
        if node.names[0].asname == None:
            import_statement = f"const {node.names[0].name} = require(\"{node.names[0].name}\");\n"
        else:
            import_statement = f"const {node.names[0].asname} = require(\"{node.names[0].name}\");\n"
        return import_statement

    def transpile_functionCall(self, node: ast.Call):
        function_name = self.transpile_expression(node.func)
        arguments = ",".join([self.transpile_expression(_args) for _args in node.args])
        if function_name == "print":
            return f"console.log({arguments});\n"
        if function_name[0].isupper():
            if function_name.rfind(".") != -1:
                return f"{function_name}({arguments})"
            return f"new {function_name}({arguments})"
        return f"{function_name}({arguments})"

    def transpile_BooleanExp(self, node: ast.BoolOp):
        _left, _right = self.transpile_expression(node.values[0]), self.transpile_expression(node.values[1])
        return f"({_left}) {self.getBinaryOperator(node)} ({_right})"

    def handleBinOp(self, node: ast.AST):
        _left, _right = self.transpile_expression(node.left), self.transpile_expression(node.right)
        if isinstance(node.left, ast.BinOp) == True and isinstance(node.right, ast.BinOp) == True:
            _left, _right = self.handleBinOp(node.left), self.handleBinOp(node.right)
        elif (not isinstance(node.left, ast.BinOp) or not isinstance(node.right, ast.UnaryOp)) and isinstance(node.right, ast.BinOp):
            _left, right = _left, self.handleBinOp(node.right)
        elif (not isinstance(node.right, ast.BinOp) == True or not isinstance(node.right, ast.UnaryOp)) and isinstance(node.left, ast.BinOp):
            _left, right = self.handleBinOp(node.left), _right
        return f"{_left} {self.getBinaryOperator(node)} {_right}"

    def handleUnaryExp(self, node: ast.AST):
        _operand = self.transpile_expression(node.operand)
        if isinstance(node.op, ast.Not):
            return f"!({_operand})"
        elif isinstance(node.op, ast.Invert):
            return f"~({_operand})"
        elif isinstance(node.op, ast.UAdd):
            return f"+({_operand})"
        elif isinstance(node.op, ast.USub):
            return f"(-{_operand})"

    def transpile_fromImport(self, node: ast.ImportFrom): 
        module_name = os.path.join(".", *node.module.split("."))
        imported_modules = []
        for item in node.names:
            if item.asname is not None: imported_modules.append(f"{item.name} as {item.asname}")
            else: imported_modules.append(f"{item.name}")
        imported_modules = ", ".join(imported_modules)
        from_import_statement = f"const {'{'} {imported_modules} {'}'} = require(\"{module_name}\");\n"
        return from_import_statement

    def transpile_assign(self, node: ast.Assign, parent_scope=None):
        var_name = self.transpile_expression(node.targets[0])
        declared = False
        var_id = var_name.split(".")[-1]
        if isinstance(node.targets[0], ast.Name):
            if parent_scope is None:
                if var_id != "this":
                    if self.global_lexicalenv.find(var_id) == False:
                        self.global_lexicalenv.set(var_id)
                    else:
                        declared = True
            else:
                declared = searchVariableDeclaration(var_id, parent_scope)
        elif isinstance(node.targets[0], ast.Tuple) == True or isinstance(node.targets[0], ast.List) == True:
            if isinstance(node.targets[0].elts[0], ast.Subscript):
                return f"{var_name} = {self.transpile_expression(node.value)};\n"
            return f"let {var_name} = {self.transpile_expression(node.value)};\n"
        if declared == False:
            if parent_scope is not None:
                if var_id != "this": parent_scope.set(var_id)
            else:
                if var_id != "this": self.global_lexicalenv.set(var_id)
            if var_name.rfind(".") != -1:
                return f"{var_name} = {self.transpile_expression(node.value)};\n"
            return f"let {var_name} = {self.transpile_expression(node.value)};\n"
        return f"{var_name} = {self.transpile_expression(node.value)};\n"




