import ast
import builtins

class UndefinedNameVisitor(ast.NodeVisitor):
    def __init__(self):
        self.scopes = [set(dir(builtins)) | {'app', 'filters', 'idle', 'client', 'message'}]
        self.imported_names = set()
        self.errors = []
        self.in_annotation = False

    def visit_Import(self, node):
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.scopes[-1].add(name.split('.')[0])
            self.imported_names.add(name.split('.')[0])

    def visit_ImportFrom(self, node):
        for alias in node.names:
            if alias.name == '*':
                pass
            else:
                name = alias.asname if alias.asname else alias.name
                self.scopes[-1].add(name)
                self.imported_names.add(name)

    def visit_FunctionDef(self, node):
        self.scopes[-1].add(node.name)
        for decorator in node.decorator_list:
            self.visit(decorator)
        for arg in node.args.args:
            if arg.annotation:
                self.in_annotation = True
                self.visit(arg.annotation)
                self.in_annotation = False
        if node.args.vararg and node.args.vararg.annotation:
            self.in_annotation = True
            self.visit(node.args.vararg.annotation)
            self.in_annotation = False
        if node.args.kwarg and node.args.kwarg.annotation:
            self.in_annotation = True
            self.visit(node.args.kwarg.annotation)
            self.in_annotation = False
        if node.returns:
            self.in_annotation = True
            self.visit(node.returns)
            self.in_annotation = False
        self.scopes.append(set())
        for arg in node.args.args:
            self.scopes[-1].add(arg.arg)
        if node.args.vararg:
            self.scopes[-1].add(node.args.vararg.arg)
        if node.args.kwarg:
            self.scopes[-1].add(node.args.kwarg.arg)
        for arg in node.args.kwonlyargs:
            if arg.annotation:
                self.in_annotation = True
                self.visit(arg.annotation)
                self.in_annotation = False
            self.scopes[-1].add(arg.arg)
        if node.args.posonlyargs:
            for arg in node.args.posonlyargs:
                if arg.annotation:
                    self.in_annotation = True
                    self.visit(arg.annotation)
                    self.in_annotation = False
                self.scopes[-1].add(arg.arg)
        for stmt in node.body:
            self.visit(stmt)
        self.scopes.pop()

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def visit_ClassDef(self, node):
        self.scopes[-1].add(node.name)
        for decorator in node.decorator_list:
            self.visit(decorator)
        for base in node.bases:
            self.visit(base)
        self.scopes.append(set())
        for stmt in node.body:
            self.visit(stmt)
        self.scopes.pop()

    def visit_Try(self, node):
        for stmt in node.body:
            self.visit(stmt)
        for handler in node.handlers:
            self.visit(handler)
        if node.orelse:
            for stmt in node.orelse:
                self.visit(stmt)
        if node.finalbody:
            for stmt in node.finalbody:
                self.visit(stmt)

    def visit_ExceptHandler(self, node):
        self.scopes.append(set())
        if node.name:
            self.scopes[-1].add(node.name)
        if node.type:
            self.visit(node.type)
        for stmt in node.body:
            self.visit(stmt)
        self.scopes.pop()

    def visit_Name(self, node):
        if self.in_annotation:
            return
        if isinstance(node.ctx, ast.Store):
            self.scopes[-1].add(node.id)
        elif isinstance(node.ctx, ast.Load):
            if not any(node.id in scope for scope in reversed(self.scopes)):
                self.errors.append((node.id, node.lineno))

    def visit_AnnAssign(self, node):
        if node.annotation:
            self.in_annotation = True
            self.visit(node.annotation)
            self.in_annotation = False
        if node.value:
            self.visit(node.value)
        if isinstance(node.target, ast.Name):
            self.scopes[-1].add(node.target.id)
        else:
            self.visit(node.target)

    def visit_arg(self, node):
        if node.annotation:
            self.in_annotation = True
            self.visit(node.annotation)
            self.in_annotation = False

    def visit_ListComp(self, node):
        self._handle_comprehension(node)

    def visit_SetComp(self, node):
        self._handle_comprehension(node)

    def visit_DictComp(self, node):
        self._handle_comprehension(node)

    def visit_GeneratorExp(self, node):
        self._handle_comprehension(node)

    def _handle_comprehension(self, node):
        self.scopes.append(set())
        for generator in node.generators:
            self.visit(generator.iter)
            self._visit_assignment_target(generator.target)
            for if_clause in generator.ifs:
                self.visit(if_clause)
        if isinstance(node, ast.DictComp):
            self.visit(node.key)
            self.visit(node.value)
        else:
            self.visit(node.elt)
        self.scopes.pop()

    def _visit_assignment_target(self, target):
        if isinstance(target, ast.Name):
            self.scopes[-1].add(target.id)
        elif isinstance(target, (ast.Tuple, ast.List)):
            for elt in target.elts:
                self._visit_assignment_target(elt)
        else:
            self.visit(target)

    def visit_Attribute(self, node):
        self.visit(node.value)

    def visit_Call(self, node):
        self.visit(node.func)
        for arg in node.args:
            self.visit(arg)
        for keyword in node.keywords:
            self.visit(keyword.value)

def get_context_lines(lines, lineno, context=2):
    start = max(0, lineno - 1 - context)
    end = min(len(lines), lineno + context)
    return "\n".join(f"{i + 1}: {lines[i]}" for i in range(start, end))

def check_code_safety(code_content, filename):
    lines = code_content.splitlines()
    try:
        tree = ast.parse(code_content, filename)
    except SyntaxError as e:
        context = get_context_lines(lines, e.lineno)
        return False, f"\n*SyntaxError di baris {e.lineno}*\n```\n{context}```\n*Error:* {str(e)}"
    visitor = UndefinedNameVisitor()
    visitor.visit(tree)
    if visitor.errors:
        undefined_name, lineno = visitor.errors[0]
        context = get_context_lines(lines, lineno)
        return False, f"\n*NameError di baris {lineno}*\n```\n{context}```\n*Error:* name '{undefined_name}' is not defined"
    return True, "Code is safe"
